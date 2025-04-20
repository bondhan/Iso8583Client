import asyncio
import random

from fastapi import FastAPI, status
from starlette.responses import JSONResponse

import ISO8583.ISO8583

async def generate_stan():
    return f"{random.randint(0, 999999):06d}"

async def wait_on_queue(shared_dict, key, timeout=5):
    start = asyncio.get_event_loop().time()
    while True:
        if key in shared_dict:
            return shared_dict.remove(key)
        if asyncio.get_event_loop().time() - start > timeout:
            raise asyncio.TimeoutError()
        await asyncio.sleep(0.1)  # avoid tight loop

def router(asck, log):
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"Hello": "World"}

    @app.get("/message")
    async def string(value: str):
        try:
            log.debug(value)
            iso_msg = ISO8583.ISO8583.ISO8583(value)
            iso_msg.setIsoContent(value)
            stan = iso_msg.getBit(11)
            msg = iso_msg.getNetworkISO()
            await asck.write(msg)

            # 🔥 await the async function to block and wait
            resp = await wait_on_queue(asck.safe_dict, stan)  # assuming you're matching with STAN
        except asyncio.CancelledError as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"CancelledError": str(e)}
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"sent": f"{value}", "resp": "timeout"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"sent": f"{value}", "resp": f"{e}"}
            )

        return {"sent": f"{value}", "resp": f"{resp[0]}"}


    @app.get("/echo")
    async def string(value: str):
        try:
            log.debug(value)
            iso_msg = ISO8583.ISO8583.ISO8583(value)
            iso_msg.setIsoContent(value)
            stan_str = await generate_stan()
            iso_msg.setBit(11, stan_str)
            value = iso_msg.getRawIso()
            msg = iso_msg.getNetworkISO()
            await asck.write(msg)

            # 🔥 await the async function to block and wait
            resp = await wait_on_queue(asck.safe_dict, stan_str)  # assuming you're matching with STAN
        except asyncio.CancelledError as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"CancelledError": str(e)}
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"sent": f"{value}", "resp": "timeout"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"sent": f"{value}", "resp": f"{e}"}
            )

        return {"sent": f"{value}", "resp": f"{resp[0]}"}


    @app.post("/send")
    async def send():
        pass

    @app.post("/raw")
    async def send():
       pass

    @app.post("/ascii")
    async def send():
        pass

    return app