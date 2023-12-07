
A script to poll a Telegram channel for new messages and send them to a SQS queue.

#### Running locally with Poetry

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

#### Running QA checks

> **Note**
>
> These commands are meant to be ran under a Poetry shell after all dependencies
> (including dev dependencies) have been installed.

Linting:

```bash
poe lint
```

Typechecking:

```bash
poe typecheck
```

Running all QA checks:

```bash
poe check-all
```

#### Running locally with Docker

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
