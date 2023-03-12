import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def open_socket(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()
