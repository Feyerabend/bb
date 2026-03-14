# Protocol Flow Diagrams

## Quick Reference: All Endpoints

```
┌─────────────────────────────────────────────────────────────┐
│                    File Server Endpoints                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GET /                  → List all files                    │
│  GET /stats             → Get SD card statistics            │
│  GET /file/{filename}   → Download file (chunked)           │
│  PUT /file/{filename}   → Upload file (chunked)             │
│  DELETE /file/{filename} → Delete file                      │
│  HEAD /file/{filename}  → Check if file exists              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                         Client Device                        │
│  (Browser / Python / cURL / Mobile App / Custom Client)      │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            │ HTTP/1.1
                            │ (WiFi Connection)
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                    Raspberry Pi Pico W                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐      │
│  │              Core 0 (Main Thread)                  │      │
│  │           TCP Server / HTTP Handler                │      │
│  │                                                    │      │
│  │  • Accept connections                              │      │
│  │  • Parse HTTP requests                             │      │
│  │  • Route to handlers                               │      │
│  │  • Send HTTP responses                             │      │
│  │  • Manage chunked transfers                        │      │
│  └────────────┬────────────────────────┬──────────────┘      │
│               │                        │                     │
│     request_queue              response_queue                │
│          (locked)                  (locked)                  │
│               │                        │                     │
│  ┌────────────▼────────────────────────▼──────────────┐      │
│  │         Core 1 (Background Thread)                 │      │
│  │            File Handler / SD Card I/O              │      │
│  │                                                    │      │
│  │  • Process file operations                         │      │
│  │  • Read/write chunks                               │      │
│  │  • Manage metadata                                 │      │
│  │  • Handle SD card access                           │      │
│  └────────────┬───────────────────────────────────────┘      │
│               │                                              │
│               │ SPI Bus                                      │
│               │                                              │
│  ┌────────────▼──────────────────────────────────────┐       │
│  │                   SD Card                         │       │
│  │         (FAT32 File System)                       │       │
│  │                                                   │       │
│  │  • Files stored as binary data                    │       │
│  │  • Metadata in .vfs_metadata.json                 │       │
│  └───────────────────────────────────────────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Upload Flow (PUT /file/{filename})

### High-Level Flow

```
Client                                    Pico W
  │                                          │
  │─────── PUT /file/video.mp4 ─────────────▶│
  │        Content-Length: 52428800          │
  │                                          │
  │                                          ├─── Parse request
  │                                          │
  │                                          ├─── Send to Core 1:
  │                                          │    PUT_START
  │                                          │    (filename, size)
  │                                          │
  │                                          ◀─── Core 1: Ready
  │                                          │
  │──────── Stream chunk 1 (8KB) ───────────▶│
  │                                          ├─── Send to Core 1:
  │                                          │    PUT_CHUNK
  │                                          │    (data, offset:0)
  │                                          │
  │                                          ◀─── Core 1: Written
  │                                          │
  │──────── Stream chunk 2 (8KB) ───────────▶│
  │                                          ├─── Send to Core 1:
  │                                          │    PUT_CHUNK
  │                                          │    (data, offset:8192)
  │                                          │
  │                                          ◀─── Core 1: Written
  │                                          │
  │         ... (6,398 more chunks) ...      │
  │                                          │
  │──────── Stream last chunk (8KB) ────────▶│
  │                                          ├─── Send to Core 1:
  │                                          │    PUT_CHUNK
  │                                          │    (data, offset:52420608)
  │                                          │
  │                                          ◀─── Core 1: Written
  │                                          │
  │                                          ├─── Send to Core 1:
  │                                          │    PUT_COMPLETE
  │                                          │
  │                                          ◀─── Core 1: Saved
  │                                          │
  │◀────── 201 Created ----------------------|
  │        {"message": "File saved"}         │
  │                                          │
```

### Detailed Core Communication

```
Core 0 (TCP Server)                    Core 1 (File Handler)
       │                                        │
       │                                        │
       ├── Receive HTTP headers                 │
       │   Content-Length: 52428800             │
       │                                        │
       ├── Add to request_queue:                │
       │   {                                    │
       │     id: 12345,                         │
       │     cmd: "PUT_START",                  │
       │     filename: "video.mp4",             │
       │     size: 52428800                     │
       │   }                                    │
       │                                        │
       │                                        ├── Pop from queue
       │                                        │
       │                                        ├── Create empty file:
       │                                        │   /sd/video.mp4
       │                                        │
       │                                        ├── Add to metadata:
       │                                        │   {size: 0,
       │                                        │    expected: 52428800}
       │                                        │
       │                                        ├── Add to response_queue:
       │                                        │   {id: 12345,
       │                                        │    status: "OK"}
       │                                        │
       ├── Wait for response...                 │
       │                                        │
       ├── Found response (id: 12345)           │
       │                                        │
       ├── Receive 8KB from TCP socket          │
       │   bytes_received = 8192                │
       │                                        │
       ├── Add to request_queue:                │
       │   {                                    │
       │     id: 12346,                         │
       │     cmd: "PUT_CHUNK",                  │
       │     filename: "video.mp4",             │
       │     data: [8192 bytes],                │
       │     offset: 0                          │
       │   }                                    │
       │                                        │
       │                                        ├── Pop from queue
       │                                        │
       │                                        ├── Open file in r+b mode
       │                                        │
       │                                        ├── Seek to offset 0
       │                                        │
       │                                        ├── Write 8192 bytes
       │                                        │
       │                                        ├── Update metadata:
       │                                        │   size = 8192
       │                                        │
       │                                        ├── Add to response_queue:
       │                                        │   {id: 12346,
       │                                        │    status: "OK"}
       │                                        │
       ├── gc.collect()                         │
       │                                        │
       ├── Receive next 8KB from TCP            │
       │   bytes_received = 16384               │
       │                                        │
       ├── Add to request_queue:                │
       │   {id: 12347, cmd: "PUT_CHUNK",        │
       │    offset: 8192, ...}                  │
       │                                        │
       │       ... repeat 6,398 times ...       │
       │                                        │
       ├── All data received                    │
       │   bytes_received = 52428800            │
       │                                        │
       ├── Add to request_queue:                │
       │   {                                    │
       │     id: 19745,                         │
       │     cmd: "PUT_COMPLETE",               │
       │     filename: "video.mp4"              │
       │   }                                    │
       │                                        │
       │                                        ├── Pop from queue
       │                                        │
       │                                        ├── Get actual file size:
       │                                        │   stat() = 52428800
       │                                        │
       │                                        ├── Update metadata:
       │                                        │   {size: 52428800,
       │                                        │    modified: now()}
       │                                        │
       │                                        ├── Save metadata to:
       │                                        │   .vfs_metadata.json
       │                                        │
       │                                        ├── Add to response_queue:
       │                                        │   {id: 19745,
       │                                        │    status: "OK",
       │                                        │    message: "File saved"}
       │                                        │
       ├── Wait for response...                 │
       │                                        │
       ├── Found response (id: 19745)           │
       │                                        │
       ├── Send HTTP response:                  │
       │   HTTP/1.1 201 Created                 │
       │   {"message": "File 'video.mp4' saved"}│
       │                                        │
```

## Download Flow (GET /file/{filename})

### High-Level Flow

```
Client                                    Pico W
  │                                          │
  │─────── GET /file/video.mp4 ─────────────▶│
  │                                          │
  │                                          ├─── Parse request
  │                                          │
  │                                          ├─── Send to Core 1:
  │                                          │    GET
  │                                          │    (filename)
  │                                          │
  │                                          ◀─── Core 1: File info
  │                                          │    (size: 52428800)
  │                                          │
  │◀───── HTTP Headers ──────────────────-───│
  │       Content-Length: 52428800           │
  │                                          │
  │                                          ├─── Send to Core 1:
  │                                          │    GET_CHUNK
  │                                          │    (offset: 0)
  │                                          │
  │                                          ◀─── Core 1: 8KB data
  │                                          │
  │◀──────── Chunk 1 (8KB) ──────────────────│
  │                                          │
  │                                          ├─── Send to Core 1:
  │                                          │    GET_CHUNK
  │                                          │    (offset: 8192)
  │                                          │
  │                                          ◀─── Core 1: 8KB data
  │                                          │
  │◀──────── Chunk 2 (8KB) ──────────────────│
  │                                          │
  │         ... (6,398 more chunks) ...      │
  │                                          │
  │                                          ├─── Send to Core 1:
  │                                          │    GET_CHUNK
  │                                          │    (offset: 52420608)
  │                                          │
  │                                          ◀─── Core 1: last chunk
  │                                          │    (eof: true)
  │                                          │
  │◀──────── Last chunk (8KB) ───────────────│
  │                                          │
  │◀────── Connection closed ────────────────│
  │                                          │
```

## List Files Flow (GET /)

```
Client                        Core 0              Core 1
  │                              │                   │
  │──── GET / ──────────────────▶│                   │
  │                              │                   │
  │                              ├─── request:       │
  │                              │    {id: 1,        │
  │                              │     cmd: "LIST"}  │
  │                              │                   │
  │                              │                   ├─── Iterate metadata
  │                              │                   │
  │                              │                   ├─── Build array:
  │                              │                   │    [{name, size,...}]
  │                              │                   │
  │                              │    response: ────◀│
  │                              │    {status: "OK", │
  │                              │     data: [...]}  │
  │                              │                   │
  │                              ├─── Format JSON    │
  │                              │                   │
  │◀─── 200 OK ────────────────-─│                   │
  │     [{name: "video.mp4",     │                   │
  │       size: 52428800}, ...]  │                   │
  │                              │                   │
```

## Get Stats Flow (GET /stats)

```
Client                        Core 0              Core 1
  │                              │                   │
  │──── GET /stats ─────────────▶│                   │
  │                              │                   │
  │                              ├─── request:       │
  │                              │    {id: 2,        │
  │                              │     cmd: "STATS"} │
  │                              │                   │
  │                              │                   ├─── Count files
  │                              │                   │
  │                              │                   ├─── Sum sizes
  │                              │                   │
  │                              │                   ├─── Call statvfs()
  │                              │                   │
  │                              │                   ├─── Calculate:
  │                              │                   │    • total_space
  │                              │                   │    • free_space
  │                              │                   │    • used_percent
  │                              │                   │
  │                              │    response: ────◀│
  │                              │    {status: "OK", │
  │                              │     data: {...}}  │
  │                              │                   │
  │◀─── 200 OK ────────────────-─│                   │
  │     {files: 10,              │                   │
  │      used_by_vfs: 52428800,  │                   │
  │      total_space: 8000000000,│                   │
  │      free_space: 7947571200, │                   │
  │      used_percent: 0.655,    │                   │
  │      chunk_size: 8192}       │                   │
  │                              │                   │
```

## Delete File Flow (DELETE /file/{filename})

```
Client                        Core 0              Core 1
  │                              │                   │
  │── DELETE /file/old.txt ─────▶│                   │
  │                              │                   │
  │                              ├─── request:       │
  │                              │    {id: 3,        │
  │                              │     cmd: "DELETE",│
  │                              │     filename:     │
  │                              │     "old.txt"}    │
  │                              │                   │
  │                              │                   ├─── Check metadata
  │                              │                   │
  │                              │                   ├─── Remove file:
  │                              │                   │    /sd/old.txt
  │                              │                   │
  │                              │                   ├─── Delete from
  │                              │                   │    metadata
  │                              │                   │
  │                              │                   ├─── Save metadata
  │                              │                   │
  │                              │    response: ────◀│
  │                              │    {status: "OK", │
  │                              │     message: ".."}│
  │                              │                   │
  │◀─── 200 OK ────────────────-─│                   │
  │     {"message": "File        │                   │
  │      'old.txt' deleted"}     │                   │
  │                              │                   │
```

## File Exists Check (HEAD /file/{filename})

```
Client                        Core 0              Core 1
  │                              │                   │
  │── HEAD /file/test.jpg ──────▶│                   │
  │                              │                   │
  │                              ├─── request:       │
  │                              │    {id: 4,        │
  │                              │     cmd: "EXISTS",│
  │                              │     filename:     │
  │                              │     "test.jpg"}   │
  │                              │                   │
  │                              │                   ├─── Check if in
  │                              │                   │    metadata dict
  │                              │                   │
  │                              │    response: ────◀│
  │                              │    {status: "OK", │
  │                              │     exists: true} │
  │                              │                   │
  │◀─── 200 OK ─────────────────-│                   │
  │     (no body)                │                   │
  │                              │                   │
```

## Memory Management During Upload

```
┌─────────────────────────────────────────────────────────┐
│                    Memory Usage Timeline                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Start Upload                                           │
│  ├─ RAM Usage: ~10 KB (baseline)                        │
│  │                                                      │
│  Receive Chunk 1 (8KB)                                  │
│  ├─ RAM Usage: ~18 KB (+8KB for chunk)                  │
│  │                                                      │
│  Send to Core 1                                         │
│  ├─ RAM Usage: ~18 KB (chunk in queue)                  │
│  │                                                      │
│  Core 1 writes chunk                                    │
│  ├─ RAM Usage: ~18 KB                                   │
│  │                                                      │
│  Core 0 receives confirmation                           │
│  ├─ RAM Usage: ~18 KB                                   │
│  │                                                      │
│  gc.collect()                                           │
│  ├─ RAM Usage: ~10 KB (chunk freed)  ◄── Back to baseline│
│  │                                                       │
│  Receive Chunk 2 (8KB)                                  │
│  ├─ RAM Usage: ~18 KB                                   │
│  │                                                      │
│  ... repeat ...                                         │
│  │                                                      │
│  After 6,400 chunks                                     │
│  ├─ RAM Usage: ~10 KB (still baseline!)                 │
│  │                                                      │
│  Total File: 50 MB uploaded                             │
│  Peak RAM: ~18 KB (constant throughout)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘

Key Insight: RAM usage is CONSTANT regardless of file size!
```

## Queue-Based Inter-Core Communication

```
┌──────────────────────────────────────────────────────────┐
│              request_queue (Core 0 → Core 1)             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Core 0 (with lock):                                     │
│    request_queue.append({                                │
│      id: 12345,                                          │
│      cmd: "PUT_CHUNK",                                   │
│      filename: "video.mp4",                              │
│      data: [8192 bytes],                                 │
│      offset: 0                                           │
│    })                                                    │
│                                                          │
│  Core 1 (with lock):                                     │
│    if len(request_queue) > 0:                            │
│      request = request_queue.pop(0)                      │
│      # Process request...                                │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│              response_queue (Core 1 → Core 0)            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Core 1 (with lock):                                     │
│    response_queue.append({                               │
│      id: 12345,                                          │
│      status: "OK",                                       │
│      message: "Chunk written"                            │
│    })                                                    │
│                                                          │
│  Core 0 (with lock):                                     │
│    for response in response_queue:                       │
│      if response['id'] == waiting_id:                    │
│        return response_queue.pop(index)                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Error Flow Examples

### File Not Found

```
Client                        Core 0              Core 1
  │                              │                   │
  │── GET /file/missing.jpg ────▶│                   │
  │                              │                   │
  │                              ├─── request:       │
  │                              │    GET missing.jpg│
  │                              │                   │
  │                              │                   ├─── Check metadata
  │                              │                   │
  │                              │                   ├─── Not found!
  │                              │                   │
  │                              │    response: ────◀│
  │                              │    {status: "ERROR",
  │                              │     message: "File
  │                              │     'missing.jpg'
  │                              │     not found"}
  │                              │                   │
  │◀─── 404 Not Found ─────────-─│                   │
  │     {"error": "File          │                   │
  │      'missing.jpg'           │                   │
  │      not found"}             │                   │
  │                              │                   │
```

### Core 1 Timeout

```
Client                        Core 0              Core 1
  │                              │                   │
  │── GET /file/test.jpg ───────▶│                   │
  │                              │                   │
  │                              ├─── request:       │
  │                              │    GET test.jpg   │
  │                              │                   │
  │                              ├─── Wait for       │
  │                              │    response...    │
  │                              │                   X (HUNG/CRASHED)
  │                              │                   │
  │                              ├─── Wait...        │
  │                              │                   │
  │                              ├─── Wait...        │
  │                              │                   │
  │                              ├─── 10 seconds     │
  │                              │    elapsed        │
  │                              │                   │
  │                              ├─── TIMEOUT!       │
  │                              │                   │
  │◀─── 500 Error ────────────-──│                   │
  │     {"error": "Timeout"}     │                   │
  │                              │                   │
```

## Metadata Structure

```
/sd/.vfs_metadata.json

{
  "photo.jpg": {
    "size": 2048576,
    "created": 1234567890,
    "modified": 1234567895
  },
  "document.txt": {
    "size": 1024,
    "created": 1234567800,
    "modified": 1234567800
  },
  "video.mp4": {
    "size": 52428800,
    "created": 1234568000,
    "modified": 1234568100
  }
}
```

## File System Layout

```
/sd/
├── .vfs_metadata.json         # Metadata for all tracked files
├── photo.jpg                  # User file 1
├── document.txt               # User file 2
├── video.mp4                  # User file 3
├── data/                      # User directory (future)
│   └── report.pdf
└── backups/                   # User directory (future)
    └── old_data.zip
```
