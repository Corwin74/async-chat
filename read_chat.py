import datetime
import asyncio
import aiofiles
import socket


def get_datetime_now():
    return datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")


async def capture_chat():
    reader, _ = await asyncio.open_connection(
        'minechat.dvmn.org', 5000)
    async with aiofiles.open('secret_chat.txt', 'a') as f:
        while not reader.at_eof():
            future = reader.readline()
            data = await asyncio.wait_for(future, 30)
            formatted_date = get_datetime_now()
            print(f'[{formatted_date}] {data.decode()}')
            await f.writelines(f'[{formatted_date}]  {data}')


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
            print(f'[{get_datetime_now()}] Caught exception socket.error : {exc}')
        else:
            print(f'[{get_datetime_now()}] Connection to chat is closed.')
        await asyncio.sleep(5)


asyncio.run(tcp_reconnect())
