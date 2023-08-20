
A script to poll a Telegram channel for new messages and send them to a SQS queue.

To run locally:

```bash
poetry shell
```

```bash
poetry install
```

```bash
python main.py \
    --api-id 29411405 \
    --api-hash ka38snf8kmdgdy73qdys56dnkfy37s7sf \
    --period-minutes 5 \
    --target-channel some_tg_channel \
    --logtail-api-key 8h89smgNNGne5YFCxjGentLe \
    --sqs-queue-url https://sqs.mars.amazonaws.com/84672562/some-queue \
    --access-id DJ24S34FJ3J543346ND \
    --access-key 8h89smgNNGne5YFCxjGentLe
```

To build and run ith Docker:

```bash
docker build -t powy-herald .
```

```bash
docker run --name powy-herald -it powy-herald \
    --api-id 29411405 \
    --api-hash ka38snf8kmdgdy73qdys56dnkfy37s7sf \
    --period-minutes 5 \
    --target-channel some_tg_channel \
    --logtail-api-key 8h89smgNNGne5YFCxjGentLe \
    --sqs-queue-url https://sqs.mars.amazonaws.com/84672562/some-queue \
    --access-id DJ24S34FJ3J543346ND \
    --access-key 8h89smgNNGne5YFCxjGentLe
```
