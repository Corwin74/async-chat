import datetime
import socket
import asyncio
import aiofiles
import configargparse
from .listen_minechat import get_datetime_now


READING_TIMEOUT = 600
RECONNECT_DELAY = 30
HISTORY_FILENAME = 'history.txt'


def get_chat_token():
    return '14fbbdfa-b8c6-11ed-ad76-0242ac110002'


async def tcp_reconnect(options):
    reader, writer = await asyncio.open_connection(
        options.host,
        options.port_in,
    )
    chat_token = get_chat_token()
    while not reader.at_eof():
        future = reader.readline()
        line = await asyncio.wait_for(future, READING_TIMEOUT)
        print(f'[{formatted_date}] {decoded_line}', end='')
        


def main():
    parser = configargparse.ArgParser(
        default_config_files=['minechat.ini']
    )
    parser.add('--host', required=True, help='host to connection')
    parser.add('--port_in', required=True, help='port to connection')

    options = parser.parse_args()
    asyncio.run(tcp_reconnect(options))
