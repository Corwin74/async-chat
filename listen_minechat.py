import datetime
import socket
import asyncio
import aiofiles
import configargparse


READING_TIMEOUT = 600
RECONNECT_DELAY = 30
HISTORY_FILENAME = 'history.txt'


def get_datetime_now():
    return datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")


async def capture_chat(options):
    if not options.history:
        history_filename = HISTORY_FILENAME
    reader, _ = await asyncio.open_connection(
        options.host,
        options.port,
    )
    async with aiofiles.open(history_filename, 'a') as f:
        while not reader.at_eof():
            future = reader.readline()
            line = await asyncio.wait_for(future, READING_TIMEOUT)
            formatted_date = get_datetime_now()
            decoded_line = line.decode()
            print(f'[{formatted_date}] {decoded_line}', end='')
            await f.writelines(f'[{formatted_date}] {decoded_line}')


async def tcp_reconnect(options):
    while True:
        print(f'[{get_datetime_now()}] Connecting to chat...')
        try:
            await capture_chat(options)
        except ConnectionRefusedError:
            print(f'[{get_datetime_now()}] Connection to chat failed!')
        except asyncio.TimeoutError:
            print(f'[{get_datetime_now()}] Connection to chat timed out!')
        except socket.error as exc:
            print(
                  f'[{get_datetime_now()}] '
                  f'Caught exception socket.error : {exc}'
            )
        else:
            print(f'[{get_datetime_now()}] Connection to chat is closed.')


def main():
    parser = configargparse.ArgParser(
        default_config_files=['listen-minechat.ini']
    )
    parser.add('--host', required=True, help='host to connection')
    parser.add('--port', required=True, help='port to connection')
    parser.add('--history', required=False, help='history filename')

    options = parser.parse_args()

    if not options.history:
        print('dd')
    asyncio.run(tcp_reconnect(options))


if __name__ == '__main__':
    main()
