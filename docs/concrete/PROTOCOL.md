# Protocol (JSON over TCP)

## Transport
- TCP with 4-byte length prefix framing.
- Payload is UTF-8 JSON.

## Common Fields
- `type`: request/response type.
- `topic`: topic name.
- `mode`: `broadcast` or `queue` (request side only).
- `status`: `ok` or `error` (response side).
- `error`: error code string (response side).

## Produce
Request
```
{
  "type": "produce",
  "topic": "<topic>",
  "payload_b64": "<base64 bytes>",
  "producer": {"host": "...", "ip": "...", "port": 1234}
}
```
Response
```
{
  "status": "ok",
  "type": "produce_ack",
  "topic": "<topic>",
  "message_id": "<server-issued id>"
}
```

## Consume (Broadcast)
Request
```
{
  "type": "consume",
  "topic": "<topic>",
  "mode": "broadcast",
  "offset": 123
}
```
Response
```
{
  "status": "ok",
  "type": "consume",
  "mode": "broadcast",
  "topic": "<topic>",
  "messages": [
    {"message_id": "...", "timestamp": 1700000000, "payload_b64": "..."}
  ],
  "next_offset": 124
}
```

## Consume (Queue)
Request
```
{
  "type": "consume",
  "topic": "<topic>",
  "mode": "queue",
  "consumer_id": "<consumer>",
  "ack_mode": "auto|manual",
  "ack_timeout_ms": 60000
}
```
Response (message)
```
{
  "status": "ok",
  "type": "consume",
  "mode": "queue",
  "topic": "<topic>",
  "message": {"message_id": "...", "timestamp": 1700000000, "payload_b64": "..."}
}
```
Response (empty)
```
{
  "status": "ok",
  "type": "consume",
  "mode": "queue",
  "topic": "<topic>",
  "status": "empty"
}
```

## ACK / NACK (Queue)
Request
```
{
  "type": "ack",
  "topic": "<topic>",
  "mode": "queue",
  "consumer_id": "<consumer>",
  "message_id": "<message_id>"
}
```
Response
```
{
  "status": "ok",
  "type": "ack",
  "topic": "<topic>",
  "message_id": "<message_id>"
}
```

NACK is identical but `type` is `nack`.
