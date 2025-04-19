import socket
from fastapi import FastAPI, HTTPException

from ISO8583 import ISO8583
from modules.evaluator import FUNCTIONS
from modules.receiver import get_resp

def gen_echo_xlink(variant, stan):
    iso = ISO8583.ISO8583()
    iso.setMTI("0800")
    iso.setBit(7, FUNCTIONS["now"]("MMDDhhmmss"))
    iso.setBit(11, stan)
    iso.setBit(32, "5555")
    iso.setBit(33, "5555")
    iso.setBit(70, "301")
    message = iso.getNetworkISO(variant)
    return message

def new_router(app: FastAPI, HOST_XLINK, PORT_XLINK):
    sn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sn.connect((HOST_XLINK, PORT_XLINK))

    @app.get("/")
    async def read_root():
        return {"Hello": "World"}

    @app.get("/xlink/echo")
    async def read_root():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST_XLINK, PORT_XLINK))

        stan = FUNCTIONS["randn"]([6, 500])
        iso_msg = gen_echo_xlink('xlink', stan)
        sn.send(iso_msg)
        response = get_resp(sn)

        return response

    @app.get("/xlink/echo/fixed")
    async def read_root():

        stan = FUNCTIONS["randn"]([6, 500])
        iso_msg = gen_echo_xlink('xlink', stan)

        sn.send(iso_msg)
        response = get_resp(sn)
        # pack = ISO8583.ISO8583()
        # pack.setNetworkISO(response, 'xlink')
        # v1 = pack.getBitsAndValues()

        return response