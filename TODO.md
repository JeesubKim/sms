# TODO

## Remaining Development
1. Queue delivery semantics
- Decide and document delivery guarantee (at-least-once vs exactly-once).
- Define behavior for duplicate deliveries on retry.

2. ACK log compaction policy
- Define trigger (size threshold, time interval, or manual).
- Implement automatic compaction scheduling.

3. Binlog indexing for broadcast
- Add index file to support efficient offset reads.
- Define index format and rebuild strategy.

4. Protocol versioning
- Add `version` field to JSON protocol.
- Document backward compatibility rules.

5. Concurrency and race conditions
- Add tests for simultaneous queue consumers.
- Verify ACK/NACK correctness under contention.

6. Restart recovery tests
- Add tests for unacked state recovery and timeout requeue after restart.

7. Replication and RAFT
- Design log replication between primary and secondaries.
- Implement leader election and quorum handling.
