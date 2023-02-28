import asyncio
import aiofiles


async def listen_chat():
    reader, _ = await asyncio.open_connection(
        'minechat.dvmn.org', 5000)
    async with aiofiles.open('secret_chat.txt', 'a') as f:
        while not reader.at_eof():
            data = await reader.readline()
            data = data.decode()
            print(data)
            await f.writelines(data)


async def tcp_reconnect():
    while True:
        print('Connecting to chat...')
        try:
            await listen_chat()
        except ConnectionRefusedError:
            print('Connection to chat failed!')
        except asyncio.TimeoutError:
            print('Connection to chat timed out!')
        else:
            print('Connection to chat is closed.')


asyncio.run(tcp_reconnect())
