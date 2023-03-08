import datetime
import socket
import asyncio
import aiofiles
import configargparse
from listen_minechat import get_datetime_now


READING_TIMEOUT = 600
RECONNECT_DELAY = 30
HISTORY_FILENAME = 'history.txt'


def get_chat_token():
    return '14fbbdfa-b8c6-11ed-ad76-0242ac110002\n'


async def tcp_reconnect(options):
    reader, writer = await asyncio.open_connection(
        options.host,
        options.port_in,
    )
    chat_token = get_chat_token()
    future = reader.readline()
    line = await asyncio.wait_for(future, READING_TIMEOUT)
    decoded_line = line.decode()
    formatted_date = get_datetime_now()
    print(f'[{formatted_date}] {decoded_line}', end='')
    writer.write(chat_token.encode())
    await writer.drain()
    future = reader.readline()
    line = await asyncio.wait_for(future, READING_TIMEOUT)
    decoded_line = line.decode()
    formatted_date = get_datetime_now()
    print(f'[{formatted_date}] {decoded_line}', end='')
    future = reader.readline()
    line = await asyncio.wait_for(future, READING_TIMEOUT)
    decoded_line = line.decode()
    formatted_date = get_datetime_now()
    print(f'[{formatted_date}] {decoded_line}', end='')
    while not reader.at_eof():
        message = input('Ввведите сообщение: ') + '\n'
        writer.write(message.encode())
        await writer.drain()
        writer.write('\n'.encode())
        await writer.drain()
        future = reader.readline()
        line = await asyncio.wait_for(future, READING_TIMEOUT)
        decoded_line = line.decode()
        formatted_date = get_datetime_now()
        print(f'[{formatted_date}] {decoded_line}', end='')


def main():
    parser = configargparse.ArgParser(
        default_config_files=['minechat.ini']
    )
    parser.add('--host', required=True, help='host to connection')
    parser.add('--port_in', required=True, help='port to connection')
    parser.add('--port_out', required=False, help='port to connection')

    options = parser.parse_args()
    asyncio.run(tcp_reconnect(options))


if __name__ == '__main__':
    main()
