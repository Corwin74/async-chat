import asyncio


async def monitor_chat():
    reader, _ = await asyncio.open_connection(
        'minechat.dvmn.org', 5000)

    while not reader.at_eof():
        data = await reader.readline()
        print(f'{data.decode()}')

asyncio.run(monitor_chat())
