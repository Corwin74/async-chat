import datetime
import socket
import asyncio
import aiofiles


READING_TIMEOUT = 600
RECONNECT_DELAY = 30


def get_datetime_now():
    return datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")


async def capture_chat():
    reader, _ = await asyncio.open_connection(
        'minechat.dvmn.org', 5000)
    async with aiofiles.open('secret_chat.txt', 'a') as f:
        while not reader.at_eof():
            future = reader.readline()
            line = await asyncio.wait_for(future, READING_TIMEOUT)
            formatted_date = get_datetime_now()
            print(f'[{formatted_date}] {line.decode()}')
            await f.writelines(f'[{formatted_date}]  {line}')


async def tcp_reconnect():
    while True:
        print(f'[{get_datetime_now()}] Connecting to chat...')
        try:
            await capture_chat()
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
        await asyncio.sleep(RECONNECT_DELAY)


if __name__ == '__main__':
    asyncio.run(tcp_reconnect())
