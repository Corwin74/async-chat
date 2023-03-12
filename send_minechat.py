import datetime
import json
import asyncio
import logging
import os
import dotenv
import aiofiles
from aiofiles import os as aio_os
import configargparse


READING_TIMEOUT = 600
RECONNECT_DELAY = 30
HISTORY_FILENAME = 'history.txt'

logger = logging.getLogger(__file__)


def get_datetime_now():
    return datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")


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
    if not await aio_os.path.exists('.env'):
        async with aiofiles.open('.env', mode='w') as f:
            await f.write('# File created by send_minechat.py\n')
            logger.debug('Create .env file')
    dotenv.set_key('.env', "MINECHAT_TOKEN", chat_token)
    logger.debug('Save chat access token to .env file')
    return chat_token, registered_nickname


async def authorise(reader, writer, chat_token):
    writer.write(f'{chat_token}\n'.encode())
    await writer.drain()
    authorization_reply = await handle_chat_reply(reader)
    logger.debug('Authorization reply: %s', authorization_reply)
    parsed_reply = json.loads(authorization_reply)
    if parsed_reply is None:
        print(f'[{get_datetime_now()}] Неизвестный токен: '
              f'"{chat_token.rstrip()}". '
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
    elif chat_token := os.getenv('MINECHAT_TOKEN'):
        logger.debug('Get token "%s" from env', chat_token.rstrip())
        nickname = await authorise(reader, writer, chat_token)
    else:
        chat_token, nickname = await register(reader, writer)
    if not nickname:
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
    return


def sanitize_input(message):
    return message.replace('\n', ' ')


def main():
    dotenv.load_dotenv()
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
    parser.add(
        '-host',
        required=True,
        help='host to connection',
        env_var='HOST',
        )
    parser.add(
        '-port',
        required=True,
        help='port to connection',
        env_var='PORT',
        )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-token',
        required=False,
        help='Access token',
        env_var='MINECHAT_TOKEN',
        )
    group.add_argument(
        '-user',
        required=False,
        help='New user to registration',
    )
    options = parser.parse_args()
    logger.debug('Host: %s, port: %s', options.host, options.port)
    asyncio.run(submit_message(options))


if __name__ == '__main__':
    main()
