import datetime
import socket
import asyncio
import logging
import aiofiles
import dotenv
import configargparse
from socket_manager import open_socket


READING_TIMEOUT = 600
RECONNECT_DELAY = 30
HISTORY_FILENAME = 'history.txt'

logger = logging.getLogger('minechat')


def get_datetime_now():
    return datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")


async def capture_chat(options):
    if options.history:
        history_filename = options.history
    else:
        history_filename = HISTORY_FILENAME
    async with open_socket(options.host, options.port_out) as s:
        reader, _ = s
        logger.debug('Start listening chat')
        async with aiofiles.open(history_filename, 'a') as f:
            while not reader.at_eof():
                future = reader.readline()
                line = await asyncio.wait_for(future, READING_TIMEOUT)
                formatted_date = get_datetime_now()
                decoded_line = line.decode()
                print(f'[{formatted_date}] {decoded_line}', end='')
                await f.write(f'[{formatted_date}] {decoded_line}')


async def reconnect(options):
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
        logger.debug('Pause for reconnect')
        await asyncio.sleep(RECONNECT_DELAY)


def main():
    logging.basicConfig(
        filename='listen_minechat.log',
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    dotenv.load_dotenv()
    parser = configargparse.ArgParser()
    parser.add(
        '-host',
        required=True,
        help='host to connection',
        env_var='HOST',
    )
    parser.add(
        '-port_out',
        required=True,
        help='port to connection',
        env_var='PORT_OUT',
    )
    parser.add(
        '-history',
        required=False,
        help='history filename',
        env_var='MINECHAT_HISTORY',
    )

    options = parser.parse_args()
    logger.debug('Host: %s, port: %s', options.host, options.port_out)
    asyncio.run(reconnect(options))


if __name__ == '__main__':
    main()
