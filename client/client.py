import asyncio
import json
import os
import threading
import logging
import uvicorn
import ISO8583.ISO8583
import os

from modules import router
from modules.thread_safe_dict import ThreadSafeDict
from modules.evaluator import manufacture_iso_class

logging.basicConfig(level=logging.DEBUG)

class AsyncIsoClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.stop_flag = False
        self.safe_dict = ThreadSafeDict()
        self.message_queue = asyncio.Queue()
        self.queue_lock = asyncio.Lock()
        self.echo_file_path = os.path.join(".", "inputs", "zte-echo.json")
        self.echo_json_data = self.read_input_file(self.echo_file_path)
        self.reader = None
        self.writer = None
        self.max_retries = 9999

    async def connect(self):
        retries = 0
        delay = 1  # initial delay in seconds

        while not self.stop_flag:
            try:
                logging.info(f"Attempting to connect to {self.host}:{self.port}")
                self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
                logging.info("Connected to ISO8583 server")
                return
            except (ConnectionRefusedError, OSError) as e:
                logging.warning(f"Connection failed: {e}. Retrying in {delay}s...")
                retries += 1
                if retries >= self.max_retries:
                    logging.error(f"Failed to connect after {self.max_retries} attempts.")
                    raise e
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30)  # Exponential backoff, max 30s

    async def reconnect(self):
        self.reader = None
        self.writer = None
        logging.info("Reconnecting...")
        await self.connect()

    async def write(self, data):
        if self.writer is not None:
            self.writer.write(data)
            await self.writer.drain()

    async def read_forever(self):
        while not self.stop_flag and self.reader is not None:
            if not self.reader:
                await asyncio.sleep(1)
                continue

            try:
                data_len = await self.reader.readexactly(4)
                length = int(data_len)
                data = await self.reader.readexactly(length)
                if not data_len:
                    break
                msg = data.decode('utf-8')
                logging.debug(f"received {msg}")

                await self.message_queue.put(msg)
            except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError) as e:
                logging.warning(f"Read error: {e}, reconnecting...")
                await self.reconnect()
            except Exception as e:
                logging.error(f"Unexpected error in read_forever: {e}")
                await self.reconnect()

    async def queue_consumer(self):
        while True:
            msg = await self.message_queue.get()

            iso_obj = ISO8583.ISO8583.ISO8583(msg)
            mti = iso_obj.getMTI()
            stan = iso_obj.getBit(11)
            logging.debug(f"received {mti} value: {iso_obj.getRawIso()}")

            self.safe_dict.set(stan, iso_obj.getRawIso())

    async def send_echo(self):
        while not self.stop_flag:
            try:
                await asyncio.sleep(10)
                if not self.writer:
                    continue

                message = self.get_echo_message()
                logging.debug(f"sending: {message}")
                async with self.queue_lock:
                    self.writer.write(message)
                    await self.writer.drain()
            except (ConnectionResetError, BrokenPipeError) as e:
                logging.warning(f"Write error: {e}, reconnecting...")
                await self.reconnect()
            except Exception as e:
                logging.error(f"Unexpected error in send_echo: {e}")
                await self.reconnect()

    def get_echo_message(self):
        iso_class = manufacture_iso_class(self.echo_json_data)
        iso_msg = iso_class.get_iso()
        logging.debug(f"iso_class: {iso_class.variant} mti: {iso_class.mti} message: {iso_msg.getNetworkISO()}")
        return iso_msg.getNetworkISO()

    def read_input_file(self, file):
        # Read and parse JSON file
        with open(file, "r") as file:
            data = json.load(file)

            if data["meta"] is None or data["data"] is None:
                raise Exception("Wrong JSON format")

        return data

    def stop(self):
        self.stop_flag = True


def start_fastapi(app):
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


async def main(asc):
    await asc.connect()
    app = router.router(asc, logging)

    # Start FastAPI in a separate thread
    threading.Thread(target=start_fastapi, args=[app], daemon=True).start()

    read_task = asyncio.create_task(asc.read_forever())
    consume_queue_task = asyncio.create_task(asc.queue_consumer())
    send_task = asyncio.create_task(asc.send_echo())

    done, pending = await asyncio.wait([send_task, read_task, consume_queue_task], return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

if __name__ == '__main__':
    host = os.getenv("HOST")
    port = os.getenv("PORT")

    if host is None:
        host = '127.0.0.1'

    if port is None:
        port = 5000

    sock_client = AsyncIsoClient(host,port)
    try:
        asyncio.run(main(sock_client))
    except KeyboardInterrupt:
        logging.debug("Shutting down.")
        sock_client.stop()

