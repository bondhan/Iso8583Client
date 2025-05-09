# Async ISO8583 client-server mock up

Inspired from:
- https://alovak.com/2024/08/27/mastering-iso-8583-message-networking-with-golang/

but in python

## Logics
- **CLIENT** established a socket connection to an **ISO8583-SERVER**
- Multiple HTTP calls are sent to the **CLIENT** and served by fastAPI http server
- FastAPI HTTP server's handler then makes a socket call to the **ISO8583-SERVER**
- The **ISO8583-SERVER** sends response via the socket/buffer to the **CLIENT**
- The **CLIENT** then reads the buffer and inserts it into a safe thread map/dict
- The fastAPI handler then read from the safe threaded map/dict by matching the STAN (element 11)
- The safe-threaded map will schedule to clean up any expired map/dict
- If **CLIENT** gets disconnected, it will retry to reconnect

![draft-flow.png](drawings/draft-flow.png)

### ToDo:
- Use Redis instead of internal map


## How To Run
### In cmd

change the PYTHONPATH to whichever directory you are working on

```bash
  make run-server
```
```bash
  make run-client 
```

### Using Docker
```bash
  docker-compose up -d
```
### Test
```bash
  curl --location 'http://localhost:8000/echo?value=080080200000000000000400000000000000RANDOM301'
```
Response
```json
{
    "sent": "080080200000000000000400000000000000423482301",
    "resp": "08108020000002000000040000000000000042348200301"
}
```

### Load Test
![load-test-1.png](drawings/load-test-1.png)


### Reference:
1. https://github.com/Seedstars/python-iso8583
