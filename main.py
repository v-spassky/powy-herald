#pylint: disable=missing-module-docstring
#pylint: disable=missing-function-docstring
#pylint: disable=broad-exception-caught


import argparse
import json
import sys
import time

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
ARGS = parser.parse_args()
HTTP_REQUEST_TIMEOUT = 10
SEND_LOG_EACH_N_CYCLES = 10
HISTORY_REQUEST_ARGS = {
    'peer': ARGS.TARGET_CHANNEL,
    'offset_id': 0,
    'offset_date': 0,
    'add_offset': 0,
    'limit': 10,
    'max_id': 0,
    'min_id': 0,
    'hash': 0,
}
SQS = boto3.client(
    'sqs',
    region_name='eu-central-1',
    aws_access_key_id=ARGS.ACCESS_ID,
    aws_secret_access_key= ARGS.ACCESS_KEY,
)


def send_log(message):
    message = f'[powy.herald] {message}'
    print(message)
    if ARGS.LOGTAIL_API_KEY:
        requests.post(
            'https://in.logtail.com',
            json={'message': message},
            headers={'Authorization': f'Bearer {ARGS.LOGTAIL_API_KEY}'},
            timeout=HTTP_REQUEST_TIMEOUT,
        )


def sent_msg_to_sqs(message):
    SQS.send_message(
        QueueUrl=ARGS.SQS_QUEUE_URL,
        MessageBody=message,
    )


def poll_forever():
    with TelegramClient('anon', ARGS.API_ID, ARGS.API_HASH) as client:
        cycles_count = 0
        while True:
            recent_messages = [
                {
                    'id': message.id,
                    'chat_id': message.chat_id,
                    'message': message.message,
                    'date': message.date.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                for message in
                client(GetHistoryRequest(**HISTORY_REQUEST_ARGS)).messages
            ]
            cycles_count += 1
            if cycles_count % SEND_LOG_EACH_N_CYCLES == 0:
                send_log(f'Sent {cycles_count} messages to SQS.')
            sent_msg_to_sqs(json.dumps(recent_messages, default=str))
            time.sleep(ARGS.PERIOD_MINUTES * 60)


def main():
    while True:
        try:
            poll_forever()
        except KeyboardInterrupt:
            send_log('Got `KeyboardInterrupt`, exiting...')
            sys.exit(0)
        except Exception as err:
            send_log(f'Got exception: {err}, restarting...')
            time.sleep(ARGS.PERIOD_MINUTES * 60)


if __name__ == '__main__':
    send_log('Starting myself...')
    main()
