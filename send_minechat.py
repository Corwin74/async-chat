import json
import asyncio
import logging
import aiofiles
from aiofiles import os
import configargparse
from listen_minechat import get_datetime_now


READING_TIMEOUT = 600
RECONNECT_DELAY = 30
HISTORY_FILENAME = 'history.txt'

logger = logging.getLogger(__file__)


async def get_chat_token(reader, writer):
    if await os.path.exists('.token'):
        async with aiofiles.open('.token', 'r') as f:
            chat_token = await f.readline()
        logger.debug('Get token "%s" from file', chat_token)
    else:
        logger.debug('Send empty line to obtain new token')
        writer.write('\n'.encode())
        await writer.drain()
        await handle_chat_reply(reader)
        nickname = input('Введите nickname:')
        logger.debug('Send %s as nickname', nickname)
        writer.write(f'{nickname}\n'.encode())
        await writer.drain()
        reply = await handle_chat_reply(reader)
        chat_token = json.loads(reply)['account_hash']
        logger.debug('Get new token: %s', chat_token.rstrip())
        async with aiofiles.open('.token', 'w') as f:
            await f.write(chat_token)
    logger.debug('Return token: %s', chat_token.rstrip())
    return chat_token


async def handle_chat_reply(reader, echo=None):
    future = reader.readline()
    line = await asyncio.wait_for(future, READING_TIMEOUT)
    formatted_date = get_datetime_now()
    decoded_line = line.decode().rstrip()
    logger.debug('Recieve: %s', decoded_line)
    if echo:
        print(f'[{formatted_date}] {decoded_line}')
    return decoded_line


async def reconnect(options):
    reader, writer = await asyncio.open_connection(
        options.host,
        options.port_in,
    )
    await handle_chat_reply(reader)
    chat_token = await get_chat_token(reader, writer)
    writer.write(chat_token.encode())
    await writer.drain()
    authorization_reply = await handle_chat_reply(reader)
    logger.debug('Authorization reply: %s', authorization_reply)
    if json.loads(authorization_reply) is None:
        print(f'Неизвестный токен: "{chat_token.rstrip()}". '
              'Проверьте его или зарегистрируйте заново.')
        logger.error('Token "%s" is not valid', {chat_token.rstrip()})
        return
    await handle_chat_reply(reader)
    while not reader.at_eof():
        message = input('Ввведите сообщение: ') + '\n'
        writer.write(message.encode())
        await writer.drain()
        logger.debug('Send: %s', message.rstrip().decode())
        writer.write('\n'.encode())
        await writer.drain()
        await handle_chat_reply(reader)


def main():
    logging.basicConfig(
        filename='send_minechat.log',
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    parser = configargparse.ArgParser(
        default_config_files=['minechat.ini']
    )
    parser.add('--host', required=True, help='host to connection')
    parser.add('--port_in', required=True, help='port to connection')
    parser.add('--port_out', required=False, help='port to connection')

    options = parser.parse_args()
    logger.debug('Host: %s, port: %s', options.host, options.port_in)
    asyncio.run(reconnect(options))


if __name__ == '__main__':
    main()
