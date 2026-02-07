# BinLog Format

Each topic has its own append-only binary log file.

## File Layout
- Header: `payload_size` (uint32)
- Then repeated Transaction entries.

## Transaction Entry (current)
- timestamp (uint32)
- topic_length (uint32)
- topic (bytes)
- message_id_length (uint32)
- message_id (bytes)
- producer_name_length (uint32)
- producer_name (bytes)
- producer_host_length (uint32)
- producer_host (bytes)
- producer_port (uint32)
- payload_size (uint32)
- payload (bytes)
- crc32 (uint32)

## Legacy Compatibility
Older logs did not include message_id. Decoder falls back to legacy format
when CRC fails with the new format.
