import select

def get_resp(sck, timeout=10):
    response = b""
    ready, _, _ = select.select([sck], [], [], 10)  # Wait up to 10 seconds for data
    if ready:
        response = sck.recv(2048)
        return response
    else:
        Exception("Timeout waiting for response")
