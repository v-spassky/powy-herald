"""
This script fetches recent messages from a Telegram channel using the Telegram API and sends them to an SQS queue.

It utilizes `Telethon` for interacting with Telegram and `boto3` for AWS SQS. The script is designed to be run
continuously, fetching messages at a specified interval and handling exceptions gracefully. Logging and external
notification support is provided for monitoring and debugging.

Usage:
    See `README.md`.
"""

import argparse
import json
import sys
import time
from logging import Logger
from types import MappingProxyType
from typing import NoReturn

import boto3
import requests
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

parser = argparse.ArgumentParser()
parser.add_argument('--api-id', dest='API_ID', type=int)
parser.add_argument('--api-hash', dest='API_HASH', type=str)
parser.add_argument('--period-minutes', dest='PERIOD_MINUTES', type=int)
parser.add_argument('--target-channel', dest='TARGET_CHANNEL', type=str)
parser.add_argument('--logtail-api-key', dest='LOGTAIL_API_KEY', type=str, default=None)
parser.add_argument('--sqs-queue-url', dest='SQS_QUEUE_URL', type=str)
parser.add_argument('--access-id', dest='ACCESS_ID', type=str)
parser.add_argument('--access-key', dest='ACCESS_KEY', type=str)

logger = Logger('powy.herald')

ARGS = parser.parse_args()
HTTP_REQUEST_TIMEOUT = 10
SEND_LOG_EACH_N_CYCLES = 10
HISTORY_REQUEST_ARGS = MappingProxyType({
    'peer': ARGS.TARGET_CHANNEL,
    'offset_id': 0,
    'offset_date': 0,
    'add_offset': 0,
    'limit': 10,
    'max_id': 0,
    'min_id': 0,
    'hash': 0,
})
SQS = boto3.client(
    'sqs',
    region_name='eu-central-1',
    aws_access_key_id=ARGS.ACCESS_ID,
    aws_secret_access_key=ARGS.ACCESS_KEY,
)


def send_log(message: str) -> None:
    """
    Send a log message to both the local logger and, if configured, to an external logging service (Logtail).

    The function formats the message with a predefined prefix before logging and sending it.

    Args:
        message (str): The message to be logged and sent.
    """
    message = '[powy.herald] {0}'.format(message)
    logger.info(message)
    if ARGS.LOGTAIL_API_KEY:
        requests.post(
            'https://in.logtail.com',
            json={'message': message},
            headers={'Authorization': 'Bearer {0}'.format(ARGS.LOGTAIL_API_KEY)},
            timeout=HTTP_REQUEST_TIMEOUT,
        )


def send_msg_to_sqs(message: str) -> None:
    """
    Send a message to the configured AWS SQS queue.

    Args:
        message (str): The message to be sent to the SQS queue.
    """
    SQS.send_message(
        QueueUrl=ARGS.SQS_QUEUE_URL,
        MessageBody=message,
    )


def fetch_messages() -> None:
    """Fetch recent messages from the specified Telegram channel and send them to the SQS queue defined globally."""
    with TelegramClient('anon', ARGS.API_ID, ARGS.API_HASH) as client:
        recent_messages = [
            {
                'id': message.id,
                'chat_id': message.chat_id,
                'message': message.message,
                'date': message.date.strftime('%Y-%m-%dT%H:%M:%S'),
            }
            for message in client(GetHistoryRequest(**HISTORY_REQUEST_ARGS)).messages
        ]
        send_msg_to_sqs(json.dumps(recent_messages, default=str))
        time.sleep(ARGS.PERIOD_MINUTES * 60)


def main() -> NoReturn:
    """
    Script entrypoint.

    This function runs in a continuous loop, fetching messages and handling exceptions. It keeps track of
    the number of cycles (fetching attempts) and logs this information periodically. The script can be
    interrupted with a `KeyboardInterrupt`, upon which it will exit gracefully.
    """
    cycles_count = 0
    while True:
        try:
            fetch_messages()
        except KeyboardInterrupt:
            send_log('Got `KeyboardInterrupt`, exiting...')
            sys.exit(0)
        except Exception as err:
            send_log('Got exception: {0}, restarting...'.format(err))
            time.sleep(ARGS.PERIOD_MINUTES * 60)
        cycles_count += 1
        if cycles_count % SEND_LOG_EACH_N_CYCLES == 0:
            send_log('Sent {0} messages to SQS.'.format(cycles_count))


if __name__ == '__main__':
    send_log('Starting myself...')
    main()
