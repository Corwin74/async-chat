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


async def register(reader, writer, nickname=None):
    logger.debug('Send empty line to obtain new token')
    writer.write('\n'.encode())
    await writer.drain()
    await handle_chat_reply(reader)
    if not nickname:
        nickname = input(f'[{get_datetime_now()}] '
                        'Введите nickname для регистрации:')
    nickname = sanitize_input(nickname)
    writer.write(f'{nickname}\n'.encode())
    await writer.drain()
    logger.debug('Send %s as nickname', nickname)
    reply = await handle_chat_reply(reader)
    parsed_reply = json.loads(reply)
    chat_token = parsed_reply['account_hash']
    registered_nickname = parsed_reply['nickname']
    logger.debug('Get new token: %s', chat_token)
    async with aiofiles.open('.token', 'w') as f:
        await f.write(chat_token)
    return chat_token, registered_nickname


async def authorise(reader, writer, chat_token):
    writer.write(f'{chat_token}\n'.encode())
    await writer.drain()
    authorization_reply = await handle_chat_reply(reader)
    logger.debug('Authorization reply: %s', authorization_reply)
    parsed_reply = json.loads(authorization_reply)
    if parsed_reply is None:
        print(f'[{get_datetime_now()}] Неизвестный токен: '
              '"{chat_token.rstrip()}". '
              'Проверьте его или зарегистрируйте заново.')
        logger.error('Token "%s" is not valid', {chat_token.rstrip()})
        return None
    await handle_chat_reply(reader)
    return parsed_reply['nickname']


async def handle_chat_reply(reader, echo=None):
    future = reader.readline()
    line = await asyncio.wait_for(future, READING_TIMEOUT)
    formatted_date = get_datetime_now()
    decoded_line = line.decode().rstrip()
    logger.debug('Recieve: %s', decoded_line)
    if echo:
        print(f'[{formatted_date}] {decoded_line}')
    return decoded_line


async def submit_message(options):
    reader, writer = await asyncio.open_connection(
        options.host,
        options.port,
    )
    await handle_chat_reply(reader)
    if options.user:
        chat_token, nickname = await register(reader, writer, options.user)
    elif options.token:
        nickname = await authorise(reader, writer, options.token)
    elif await os.path.exists('.token'):
        async with aiofiles.open('.token', 'r') as f:
            chat_token = await f.readline()
        logger.debug('Get token "%s" from file', chat_token.rstrip())
        nickname = await authorise(reader, writer, chat_token)
    else:
        logger.error('Access token not found and new username not specefied!')
        print('Токен доступа не найден и имя нового пользователя не указано!')
        return
    logger.debug('Log in chat as %s', nickname)
    print(f'[{get_datetime_now()}] Успешный вход в чат под именем: {nickname}')
    message = sanitize_input(options.message)
    writer.write(f'{message}\n'.encode())
    await writer.drain()
    writer.write('\n'.encode())
    await writer.drain()
    logger.debug('Send: %s', message)
    print(f'[{get_datetime_now()}] Cообщение отправлено')
    await handle_chat_reply(reader)
    writer.close()
    await writer.wait_closed()


def sanitize_input(message):
    return message.replace('\n', ' ')


def main():
    logging.basicConfig(
        filename='send_minechat.log',
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    parser = configargparse.ArgParser(
        default_config_files=['send_minechat.ini'],
        add_help=False
    )

    parser.add('message', help='Message to send')
    parser.add('-h', '--host', required=True, help='host to connection')
    parser.add('-p', '--port', required=True, help='port to connection')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--token', required=False, help='Access token')
    group.add_argument(
        '-u',
        '--user',
        required=False,
        help='New user to registration',
    )
    options = parser.parse_args()
    logger.debug('Host: %s, port: %s', options.host, options.port)
    asyncio.run(submit_message(options))


if __name__ == '__main__':
    main()
