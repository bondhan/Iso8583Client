import asyncio
import logging
from ISO8583.ISO8583 import ISO8583

logging.basicConfig(level=logging.DEBUG)

class AsyncIsoServer():
    def __init__(self):
        self.reader = None
        self.writer = None
        self.addr = None
        self.client_id = None
        self.message_queue = asyncio.Queue(maxsize=100)

    async def send_echo(self):
        try:
            while True:
                # file_path = os.path.join("..", "inputs", "zte-echo.json")
                # message = get_echo_message(file_path)
                # logging.debug(f"sending: {message}")
                # writer.write(message)
                # await writer.drain()
                await asyncio.sleep(0.01)
        except (asyncio.CancelledError, ConnectionResetError):
            logging.debug("Send task cancelled or connection reset.")
        except (FileNotFoundError):
            logging.debug("file not found.")
        finally:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()

    async def read_from_client(self):
        try:
            while True:
                data_len = await self.reader.readexactly(4)
                if not data_len:
                    break
                data = await self.reader.readexactly(int(data_len))
                if not data_len:
                    break
                msg = data.decode('utf-8')
                logging.debug(f"received {msg}")
                await self.message_queue.put(msg)

        except (asyncio.CancelledError, ConnectionResetError):
            logging.debug(f"Read task cancelled or connection reset for {self.client_id}")
        except Exception as e:
            logging.debug(e)

    async def consume_queue(self):
        try:
            while True:
                msg = await self.message_queue.get()
                iso_obj = ISO8583(msg)
                mti = iso_obj.getMTI()
                if mti == '0100':
                    iso_obj.setMTI('0110')
                elif mti == '0200':
                    iso_obj.setMTI('0210')
                elif mti == '0400':
                    iso_obj.setMTI('0410')
                elif mti == '0420':
                    iso_obj.setMTI('0430')
                elif mti == '0800':
                    iso_obj.setMTI('0810')

                iso_obj.setBit(39, '00')
                resp_msg = iso_obj.getNetworkISO()
                logging.debug(f"sent {resp_msg}")
                self.writer.write(resp_msg)
        except (asyncio.CancelledError, ConnectionResetError):
            logging.debug(f"Read task cancelled or connection reset for {self.client_id}")
        except Exception as e:
            logging.debug(e)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    async_server = AsyncIsoServer()
    async_server.reader = reader
    async_server.writer = writer

    async_server.addr = writer.get_extra_info('peername')
    async_server.client_id = f"{async_server.addr[0]}:{async_server.addr[1]}"
    logging.debug(f"Client connected: {async_server.client_id}")

    send_task = asyncio.create_task(async_server.send_echo())
    consume_queue_task = asyncio.create_task(async_server.consume_queue())
    read_task = asyncio.create_task(async_server.read_from_client())

    await asyncio.wait([send_task, read_task, consume_queue_task], return_when=asyncio.FIRST_COMPLETED)

    send_task.cancel()
    read_task.cancel()
    logging.debug(f"Client disconnected: {async_server.client_id}")

    if async_server.writer:
        await async_server.writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 5000)
    logging.debug("Server started on 0.0.0.0:5000")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
