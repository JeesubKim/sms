# Queue vs Broadcast

## Broadcast
- All messages are appended to binlog per topic.
- Consumers provide their own `offset`.
- Server reads binlog from `offset` and returns a batch.
- Server does not track per-consumer state.

## Queue
- All messages are appended to binlog per topic.
- Server maintains an in-memory queue for delivery.
- Each message is assigned to at most one consumer at a time.
- ACK required to remove message from in-memory unacked state.
- NACK or timeout re-queues the message.

## ACK Timing
- auto-ack: server marks as ACKed immediately on delivery.
- manual-ack: consumer sends ACK/NACK explicitly.

## Timeout
- Manual ACK timeout default: 60 seconds.
- Timeout triggers re-queue.
