# ACK State Persistence

## Goal
Persist unacknowledged message state so queue delivery is resilient to server restarts.

## Current Behavior
- Unacked state is in memory only.
- On restart, all binlog messages are reloaded into the queue.

## Proposed Persistence (Design)
Store unacked state in a per-topic "ack log" and rebuild it on startup.

### Data Model
- `unacked/<topic>.aql` (append-only log)
- Each entry:
  - timestamp_ms (uint64)
  - message_id (string)
  - consumer_id (string)
  - deadline_ms (uint64)
  - state (byte) 0=assigned, 1=acked, 2=nacked, 3=expired
  - crc32

### On Assign
- Append an entry with `state=assigned` and `deadline_ms`.
- Add to in-memory unacked map.

### On Ack
- Append entry `state=acked`.
- Remove from in-memory unacked map.

### On Nack
- Append entry `state=nacked`.
- Remove from unacked map and re-queue message.

### On Timeout
- Append entry `state=expired`.
- Remove from unacked map and re-queue message.

### On Startup
- Rebuild in-memory unacked map by replaying the ack log in order.
- For any message with latest state `assigned`, re-queue if `deadline_ms` already passed.

## Open Decisions
- Ack log compaction policy (e.g., periodic snapshot or rewrite).
- Whether to store message payload in ack log (not required if binlog is source of truth).

## Compaction (Implemented)
- `compact_acklog(topic)` rewrites the ack log keeping only the latest entry per `message_id`.
- Safe to run periodically or on startup to bound file size.
