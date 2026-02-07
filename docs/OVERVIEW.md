# SMS (Simple Message Service)

## Project Overview
SMS is a lightweight message queue service with two delivery modes per topic:
- Broadcast: consumers manage their own offsets and can replay messages.
- Queue: server assigns each message to exactly one consumer and requires ACK/NACK.

The system uses JSON over TCP for network requests/responses and stores all messages
as append-only binary logs per topic.

## Functional Requirements
- Broadcast and Queue modes per topic.
- Each message is appended to a per-topic binlog.
- Producers can publish messages to a topic.
- Consumers can consume messages based on mode.
- Broadcast mode: each consumer keeps its own offset.
- Queue mode: only one consumer can consume a message.
- Queue mode: messages are marked unacknowledged until ACK is received.
- Queue mode: unacknowledged messages are not available to other consumers.
- Queue mode: on NACK or timeout, messages are re-queued.
- ACK timing policy is configurable:
  - auto-ack: message is ACKed immediately on delivery.
  - manual-ack: message must be ACKed by consumer, with timeout.

## Non-Functional Requirements
- Primary and secondary nodes should replicate per-topic logs.
- Leader election and failover should be based on RAFT and quorum.

## Current Direction
- External API: JSON protocol over TCP with length framing.
- Internal storage: binary append-only binlogs per topic.
- Server issues message_id for all messages.
- Client systems may embed their own IDs in their own payloads.
