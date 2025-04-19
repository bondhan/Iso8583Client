// main.go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net"
	"net/http"
	"sync"
	"time"

	"github.com/moov-io/iso8583"
	"github.com/moov-io/iso8583/field"
)

var (
	pendingResponses sync.Map // map[string]chan []byte
	tcpConn          net.Conn
)

func main() {
	spec := buildSpec()
	initTCPConnection("localhost:5000")
	go socketListener(spec)

	http.HandleFunc("/send", func(w http.ResponseWriter, r *http.Request) {
		handleRequest(w, r, spec)
	})

	fmt.Println("REST API listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleRequest(w http.ResponseWriter, r *http.Request, spec *iso8583.MessageSpec) {
	defer r.Body.Close()

	var req map[string]string
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	stan := generateSTAN()
	msg := iso8583.NewMessage(spec)
	msg.MTI("0200")
	msg.Field(11, field.NewString(stan))
	msg.Field(41, field.NewString("TERMID01")) // Terminal ID
	msg.Field(3, field.NewString("000000"))    // Processing code
	msg.Field(4, field.NewString(req["amount"])) // Amount

	packed, err := msg.Pack()
	if err != nil {
		http.Error(w, "Failed to pack message", http.StatusInternalServerError)
		return
	}

	// Add length prefix
	prefix := []byte{byte(len(packed) >> 8), byte(len(packed) & 0xff)}
	fullMsg := append(prefix, packed...)

	respCh := make(chan []byte, 1)
	pendingResponses.Store(stan, respCh)
	_, err = tcpConn.Write(fullMsg)
	if err != nil {
		http.Error(w, "Failed to write to switch", http.StatusBadGateway)
		return
	}

	select {
	case resp := <-respCh:
		isoResp := iso8583.NewMessage(spec)
		_ = isoResp.Unpack(resp)
		responseMap := map[string]string{
			"mti":    isoResp.MTI(),
			"field39": isoResp.GetString(39),
		}
		json.NewEncoder(w).Encode(responseMap)
	case <-time.After(3 * time.Second):
		pendingResponses.Delete(stan)
		http.Error(w, "Timeout", http.StatusGatewayTimeout)
	}
}

func initTCPConnection(address string) {
	var err error
	tcpConn, err = net.Dial("tcp", address)
	if err != nil {
		log.Fatalf("Failed to connect to ISO8583 server: %v", err)
	}
	fmt.Println("Connected to ISO8583 switch")
}

func socketListener(spec *iso8583.MessageSpec) {
	for {
		head := make([]byte, 2)
		_, err := tcpConn.Read(head)
		if err != nil {
			log.Printf("Error reading length: %v", err)
			continue
		}
		length := int(head[0])<<8 + int(head[1])
		body := make([]byte, length)
		_, err = tcpConn.Read(body)
		if err != nil {
			log.Printf("Error reading body: %v", err)
			continue
		}
		msg := iso8583.NewMessage(spec)
		_ = msg.Unpack(body)
		stan, _ := msg.GetString(11)
		if chRaw, ok := pendingResponses.Load(stan); ok {
			ch := chRaw.(chan []byte)
			ch <- body
			pendingResponses.Delete(stan)
		} else {
			log.Println("No pending request for STAN:", stan)
		}
	}
}

func generateSTAN() string {
	return fmt.Sprintf("%06d", rand.Intn(1000000))
}

func buildSpec() *iso8583.MessageSpec {
	return &iso8583.MessageSpec{
		Fields: map[int]field.Field{
			2:  &field.String{Length: 19, Pref: &field.Prefixed{Length: 2, Type: field.PrefTypeASCII}},
			3:  &field.String{Length: 6, Pref: &field.Prefixed{Length: 0}},
			4:  &field.String{Length: 12, Pref: &field.Prefixed{Length: 0}},
			11: &field.String{Length: 6, Pref: &field.Prefixed{Length: 0}},
			39: &field.String{Length: 2, Pref: &field.Prefixed{Length: 0}},
			41: &field.String{Length: 8, Pref: &field.Prefixed{Length: 0}},
		},
	}
}
