# File Server Protocol Specification v1.0

## Overview

This document describes the HTTP-based protocol used by the MicroPython File Server for client-server communication. The protocol is designed to be simple, RESTful, and memory-efficient for embedded systems.

---

## Table of Contents

1. [Protocol Basics](#protocol-basics)
2. [Endpoint Reference](#endpoint-reference)
3. [Request/Response Formats](#requestresponse-formats)
4. [Chunked Transfer Protocol](#chunked-transfer-protocol)
5. [Error Handling](#error-handling)
6. [Example Implementations](#example-implementations)
7. [Extension Points](#extension-points)

---

## Protocol Basics

### Transport
- **Protocol**: HTTP/1.1
- **Default Port**: 80 (Access Point mode) or 8080 (Station mode)
- **Encoding**: UTF-8 for headers/JSON, binary for file data
- **Connection**: Close after each request (HTTP/1.1 without keep-alive)

### Content Types
- **JSON responses**: `application/json`
- **File data**: `application/octet-stream`
- **All responses include**: `Access-Control-Allow-Origin: *` for CORS

### URL Structure
```
http://{server_ip}:{port}/{endpoint}
```

Examples:
- `http://192.168.4.1/` - List files
- `http://192.168.4.1/stats` - Get statistics
- `http://192.168.4.1/file/photo.jpg` - File operations

---

## Endpoint Reference

### 1. List Files
**Endpoint**: `GET /`

**Description**: Retrieves a list of all files on the SD card with metadata.

**Request**:
```http
GET / HTTP/1.1
Host: 192.168.4.1
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 234
Access-Control-Allow-Origin: *
Connection: close

[
  {
    "name": "photo.jpg",
    "size": 2048576,
    "created": 1234567890,
    "modified": 1234567895
  },
  {
    "name": "document.txt",
    "size": 1024,
    "created": 1234567800,
    "modified": 1234567800
  }
]
```

**Response Fields**:
| Field    | Type    | Description                           |
|----------|---------|---------------------------------------|
| name     | string  | Filename (no path, just basename)     |
| size     | integer | File size in bytes                    |
| created  | integer | Unix timestamp (seconds since epoch)  |
| modified | integer | Unix timestamp of last modification   |

**Notes**:
- Returns empty array `[]` if no files exist
- Files are not sorted by default
- Timestamps are in seconds (not milliseconds)

---

### 2. Get Statistics
**Endpoint**: `GET /stats`

**Description**: Retrieves SD card usage statistics and server configuration.

**Request**:
```http
GET /stats HTTP/1.1
Host: 192.168.4.1
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 156
Access-Control-Allow-Origin: *
Connection: close

{
  "files": 42,
  "used_by_vfs": 5242880,
  "total_space": 8000000000,
  "free_space": 7994757120,
  "used_percent": 0.065536,
  "chunk_size": 8192
}
```

**Response Fields**:
| Field        | Type  | Description                                |
|--------------|-------|--------------------------------------------|
| files        | int   | Total number of files managed by VFS       |
| used_by_vfs  | int   | Bytes used by tracked files                |
| total_space  | int   | Total SD card capacity in bytes            |
| free_space   | int   | Available space in bytes                   |
| used_percent | float | Percentage of space used (0-100)           |
| chunk_size   | int   | Server's chunk size for transfers (bytes)  |

**Notes**:
- `used_by_vfs` only counts files tracked in metadata
- `chunk_size` tells clients the server's preferred chunk size
- All sizes are in bytes

---

### 3. Check File Existence
**Endpoint**: `HEAD /file/{filename}`

**Description**: Check if a file exists without downloading it.

**Request**:
```http
HEAD /file/photo.jpg HTTP/1.1
Host: 192.168.4.1
```

**Response (exists)**:
```http
HTTP/1.1 200 OK
Content-Length: 0
Connection: close

```

**Response (not found)**:
```http
HTTP/1.1 404 Not Found
Content-Length: 0
Connection: close

```

**Notes**:
- No response body
- Use for quick existence checks
- Saves bandwidth compared to GET

---

### 4. Download File (Chunked)
**Endpoint**: `GET /file/{filename}`

**Description**: Download a file from the server. Large files are automatically streamed in chunks.

**Request**:
```http
GET /file/photo.jpg HTTP/1.1
Host: 192.168.4.1
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/octet-stream
Content-Length: 2048576
Content-Disposition: attachment; filename="photo.jpg"
Access-Control-Allow-Origin: *
Connection: close

[binary file data - 2048576 bytes]
```

**Response Headers**:
| Header              | Description                           |
|---------------------|---------------------------------------|
| Content-Type        | Always `application/octet-stream`     |
| Content-Length      | Total file size in bytes              |
| Content-Disposition | Suggests filename for browser         |

**Server-Side Chunking Process**:
1. Server reads file info (total size)
2. Server sends HTTP headers with total Content-Length
3. Server reads file in 8KB chunks
4. Server sends each chunk directly to TCP socket
5. Repeat until entire file sent
6. Connection closes

**Client Implementation**:
```javascript
// Client receives complete file as single stream
fetch('http://192.168.4.1/file/photo.jpg')
  .then(response => response.blob())
  .then(blob => {
    // File is complete, save it
  });
```

**Notes**:
- Chunking is transparent to client
- Client receives file as continuous stream
- Server manages memory by reading/sending in chunks
- If file not found, returns 404 with JSON error

**Error Response (404)**:
```http
HTTP/1.1 404 Error
Content-Type: application/json
Content-Length: 45
Access-Control-Allow-Origin: *
Connection: close

{"error": "File 'photo.jpg' not found"}
```

---

### 5. Upload File (Chunked)
**Endpoint**: `PUT /file/{filename}`

**Description**: Upload a file to the server. Large files are automatically received in chunks.

**Request**:
```http
PUT /file/photo.jpg HTTP/1.1
Host: 192.168.4.1
Content-Type: application/octet-stream
Content-Length: 2048576

[binary file data - 2048576 bytes]
```

**Response (success)**:
```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Length: 58
Access-Control-Allow-Origin: *
Connection: close

{"message": "File 'photo.jpg' saved"}
```

**Response (error)**:
```http
HTTP/1.1 500 Error
Content-Type: application/json
Content-Length: 48
Access-Control-Allow-Origin: *
Connection: close

{"error": "Failed to write file"}
```

**Server-Side Chunking Process**:
1. Server receives HTTP headers (gets Content-Length)
2. Server sends "PUT_START" to Core 1 (file handler)
3. Server receives data in chunks from TCP socket
4. For each chunk received:
   - Sends "PUT_CHUNK" to Core 1 with data
   - Core 1 writes chunk to SD card
   - Garbage collection runs
5. When all data received, sends "PUT_COMPLETE" to Core 1
6. Server responds 201 Created

**Client Implementation**:
```javascript
// Client sends file as single request
const fileData = await file.arrayBuffer();
fetch('http://192.168.4.1/file/photo.jpg', {
  method: 'PUT',
  body: fileData,
  headers: {
    'Content-Type': 'application/octet-stream'
  }
});
```

**Notes**:
- Client sends entire file in one request
- Server handles chunking internally (transparent to client)
- If file exists, it will be overwritten
- Creates file if it doesn't exist
- Updates metadata (size, modified timestamp)

---

### 6. Delete File
**Endpoint**: `DELETE /file/{filename}`

**Description**: Delete a file from the SD card.

**Request**:
```http
DELETE /file/photo.jpg HTTP/1.1
Host: 192.168.4.1
```

**Response (success)**:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 50
Access-Control-Allow-Origin: *
Connection: close

{"message": "File 'photo.jpg' deleted"}
```

**Response (not found)**:
```http
HTTP/1.1 404 Error
Content-Type: application/json
Content-Length: 45
Access-Control-Allow-Origin: *
Connection: close

{"error": "File 'photo.jpg' not found"}
```

**Notes**:
- Deletes both file and metadata
- Irreversible operation
- Returns 404 if file doesn't exist

---

## Chunked Transfer Protocol

### Internal Architecture

The server uses an internal chunked transfer mechanism between Core 0 (network) and Core 1 (file I/O) to handle large files without running out of memory.

### Internal Commands (Core 0 ↔ Core 1)

These are internal commands used between cores. Clients don't send these directly, but understanding them helps with protocol design.

#### Command Structure
```python
{
  "id": 12345,           # Unique request ID (timestamp in ms)
  "cmd": "COMMAND_NAME", # Command name
  # ... additional fields depending on command
}
```

#### Response Structure
```python
{
  "id": 12345,           # Matching request ID
  "status": "OK",        # "OK" or "ERROR"
  # ... additional fields depending on command
}
```

### Upload Sequence Diagram

```
Client              Core 0 (TCP)           Core 1 (File I/O)         SD Card
  |                      |                       |                      |
  |--PUT /file/big.bin-->|                       |                      |
  |  Content-Length:     |                       |                      |
  |  52428800 (50MB)     |                       |                      |
  |                      |                       |                      |
  |                      |--{PUT_START}--------->|                      |
  |                      |  filename: big.bin    |                      |
  |                      |  size: 52428800       |                      |
  |                      |                       |--create file-------->|
  |                      |<--{OK, Ready}---------|                      |
  |                      |                       |                      |
  |--[8192 bytes]------->|                       |                      |
  |                      |--{PUT_CHUNK}--------->|                      |
  |                      |  data: [8192 bytes]   |                      |
  |                      |  offset: 0            |                      |
  |                      |                       |--write 8KB @0------->|
  |                      |<--{OK}----------------|                      |
  |                      | [gc.collect()]        |                      |
  |                      |                       |                      |
  |--[8192 bytes]------->|                       |                      |
  |                      |--{PUT_CHUNK}--------->|                      |
  |                      |  data: [8192 bytes]   |                      |
  |                      |  offset: 8192         |                      |
  |                      |                       |--write 8KB @8192---->|
  |                      |<--{OK}----------------|                      |
  |                      | [gc.collect()]        |                      |
  |                      |                       |                      |
  ... (repeat ~6,400 times for 50MB file)
  |                      |                       |                      |
  |--[last chunk]------->|                       |                      |
  |                      |--{PUT_CHUNK}--------->|                      |
  |                      |                       |--write last chunk--->|
  |                      |<--{OK}----------------|                      |
  |                      |                       |                      |
  |                      |--{PUT_COMPLETE}------>|                      |
  |                      |  filename: big.bin    |                      |
  |                      |                       |--save metadata------>|
  |                      |<--{OK, Saved}---------|                      |
  |                      |                       |                      |
  |<--201 Created--------|                       |                      |
  |  {"message": ...}    |                       |                      |
```

### Download Sequence Diagram

```
Client              Core 0 (TCP)           Core 1 (File I/O)         SD Card
  |                      |                       |                      |
  |--GET /file/big.bin-->|                       |                      |
  |                      |                       |                      |
  |                      |--{GET}--------------->|                      |
  |                      |  filename: big.bin    |                      |
  |                      |                       |--get file info------>|
  |                      |<--{OK, size:50MB}-----|                      |
  |                      |                       |                      |
  |<--HTTP Headers-------|                       |                      |
  |  Content-Length:     |                       |                      |
  |  52428800            |                       |                      |
  |                      |                       |                      |
  |                      |--{GET_CHUNK}--------->|                      |
  |                      |  filename: big.bin    |                      |
  |                      |  offset: 0            |                      |
  |                      |                       |--read 8KB @0-------->|
  |                      |<--{OK, data:[8KB]}---|                      |
  |<--[8192 bytes]-------|                       |                      |
  |                      | [gc.collect()]        |                      |
  |                      |                       |                      |
  |                      |--{GET_CHUNK}--------->|                      |
  |                      |  filename: big.bin    |                      |
  |                      |  offset: 8192         |                      |
  |                      |                       |--read 8KB @8192----->|
  |                      |<--{OK, data:[8KB]}---|                      |
  |<--[8192 bytes]-------|                       |                      |
  |                      | [gc.collect()]        |                      |
  |                      |                       |                      |
  ... (repeat ~6,400 times)
  |                      |                       |                      |
  |                      |--{GET_CHUNK}--------->|                      |
  |                      |  offset: 52420608     |                      |
  |                      |                       |--read last chunk---->|
  |                      |<--{OK, eof:true}------|                      |
  |<--[last chunk]-------|                       |                      |
  |                      |                       |                      |
  |<--connection close---|                       |                      |
```

---

## Error Handling

### Error Response Format

All errors return JSON with an `error` field:

```json
{
  "error": "Description of what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning           | When Used                                    |
|------|-------------------|----------------------------------------------|
| 200  | OK                | Successful GET, DELETE, HEAD (found)         |
| 201  | Created           | Successful PUT (file uploaded)               |
| 404  | Not Found         | File doesn't exist, invalid endpoint         |
| 500  | Internal Error    | File I/O error, timeout, unexpected error    |

### Common Error Messages

```json
// File not found
{"error": "File 'photo.jpg' not found"}

// File not found in VFS
{"error": "File 'photo.jpg' not found in VFS"}

// Timeout (Core 1 didn't respond)
{"error": "Timeout"}

// Unknown command (internal error)
{"error": "Unknown command: INVALID"}

// Generic write error
{"error": "Failed to write file"}
```

### Client Error Handling Best Practices

```javascript
async function uploadFile(filename, data) {
  try {
    const response = await fetch(`http://192.168.4.1/file/${filename}`, {
      method: 'PUT',
      body: data
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('Upload failed:', error.error);
      return false;
    }
    
    const result = await response.json();
    console.log('Success:', result.message);
    return true;
    
  } catch (err) {
    console.error('Network error:', err);
    return false;
  }
}
```

---

## Example Implementations

### Python Client (Complete Example)

```python
import requests
import os

class FileServerClient:
    def __init__(self, host='192.168.4.1', port=80):
        self.base_url = f'http://{host}:{port}'
    
    def list_files(self):
        """Get list of all files"""
        response = requests.get(f'{self.base_url}/')
        response.raise_for_status()
        return response.json()
    
    def get_stats(self):
        """Get SD card statistics"""
        response = requests.get(f'{self.base_url}/stats')
        response.raise_for_status()
        return response.json()
    
    def file_exists(self, filename):
        """Check if file exists"""
        response = requests.head(f'{self.base_url}/file/{filename}')
        return response.status_code == 200
    
    def upload_file(self, local_path, remote_name=None):
        """Upload a file to the server"""
        if remote_name is None:
            remote_name = os.path.basename(local_path)
        
        with open(local_path, 'rb') as f:
            response = requests.put(
                f'{self.base_url}/file/{remote_name}',
                data=f,
                headers={'Content-Type': 'application/octet-stream'}
            )
        
        response.raise_for_status()
        return response.json()
    
    def download_file(self, filename, local_path=None):
        """Download a file from the server"""
        if local_path is None:
            local_path = filename
        
        response = requests.get(f'{self.base_url}/file/{filename}')
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        return local_path
    
    def delete_file(self, filename):
        """Delete a file from the server"""
        response = requests.delete(f'{self.base_url}/file/{filename}')
        response.raise_for_status()
        return response.json()

# Usage
client = FileServerClient()

# List files
files = client.list_files()
print(f"Files: {files}")

# Get stats
stats = client.get_stats()
print(f"Free space: {stats['free_space'] / 1024 / 1024:.2f} MB")

# Upload
client.upload_file('photo.jpg')

# Download
client.download_file('photo.jpg', 'downloaded_photo.jpg')

# Delete
client.delete_file('photo.jpg')
```

### JavaScript Client (Browser)

```javascript
class FileServerClient {
  constructor(host = '192.168.4.1', port = 80) {
    this.baseUrl = `http://${host}:${port}`;
  }
  
  async listFiles() {
    const response = await fetch(`${this.baseUrl}/`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }
  
  async getStats() {
    const response = await fetch(`${this.baseUrl}/stats`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  }
  
  async fileExists(filename) {
    const response = await fetch(`${this.baseUrl}/file/${encodeURIComponent(filename)}`, {
      method: 'HEAD'
    });
    return response.ok;
  }
  
  async uploadFile(file, onProgress = null) {
    // Note: Browser handles chunking automatically via fetch/XHR
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseUrl}/file/${encodeURIComponent(file.name)}`, {
      method: 'PUT',
      body: await file.arrayBuffer()
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    return await response.json();
  }
  
  async downloadFile(filename) {
    const response = await fetch(`${this.baseUrl}/file/${encodeURIComponent(filename)}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const blob = await response.blob();
    
    // Trigger download
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
  
  async deleteFile(filename) {
    const response = await fetch(`${this.baseUrl}/file/${encodeURIComponent(filename)}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    return await response.json();
  }
}

// Usage
const client = new FileServerClient();

// List files
const files = await client.listFiles();
console.log('Files:', files);

// Get stats
const stats = await client.getStats();
console.log(`Free space: ${(stats.free_space / 1024 / 1024).toFixed(2)} MB`);

// Upload from <input type="file">
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  const result = await client.uploadFile(file);
  console.log('Uploaded:', result);
});

// Download
await client.downloadFile('photo.jpg');

// Delete
await client.deleteFile('photo.jpg');
```

### cURL Examples

```bash
# List files
curl http://192.168.4.1/

# Get stats
curl http://192.168.4.1/stats

# Check if file exists
curl -I http://192.168.4.1/file/photo.jpg

# Upload file
curl -X PUT \
  --data-binary @photo.jpg \
  http://192.168.4.1/file/photo.jpg

# Download file
curl http://192.168.4.1/file/photo.jpg -o downloaded.jpg

# Delete file
curl -X DELETE http://192.168.4.1/file/photo.jpg
```

---

## Extension Points

### 1. Adding Authentication

Add an `Authorization` header check:

```python
def _handle_client(self, conn):
    # ... existing code ...
    
    # Check for authorization
    auth_header = None
    for line in lines:
        if line.lower().startswith('authorization:'):
            auth_header = line.split(':', 1)[1].strip()
    
    if auth_header != "Bearer YOUR_SECRET_TOKEN":
        self._send_error(conn, 401, "Unauthorized")
        return
    
    # ... continue with request handling ...
```

Client usage:
```javascript
fetch('http://192.168.4.1/', {
  headers: {
    'Authorization': 'Bearer YOUR_SECRET_TOKEN'
  }
});
```

### 2. Adding File Metadata

Extend the metadata structure:

```python
self.metadata[filename] = {
    "size": file_size,
    "created": utime.time(),
    "modified": utime.time(),
    "mime_type": "image/jpeg",  # NEW
    "tags": ["photo", "2024"],   # NEW
    "owner": "user1"             # NEW
}
```

Return in file list:
```json
{
  "name": "photo.jpg",
  "size": 2048576,
  "created": 1234567890,
  "modified": 1234567895,
  "mime_type": "image/jpeg",
  "tags": ["photo", "2024"],
  "owner": "user1"
}
```

### 3. Adding Directory Support

Add new endpoints:

```python
# List directory
GET /dir/{path}

# Create directory
POST /dir/{path}

# Delete directory
DELETE /dir/{path}
```

Modify file paths to support subdirectories:
```python
# Current: /file/photo.jpg
# With dirs: /file/2024/photos/photo.jpg
```

### 4. Adding File Search

Add search endpoint:

```python
GET /search?q=photo&type=jpg&size_min=1000000
```

Implementation:
```python
elif method == "GET" and path.startswith("search"):
    # Parse query parameters
    self._handle_search(conn, query_params)
```

### 5. Adding Compression

Add compression support:

Request:
```http
GET /file/large.txt HTTP/1.1
Accept-Encoding: gzip
```

Response:
```http
HTTP/1.1 200 OK
Content-Encoding: gzip
Content-Length: 512  # compressed size

[gzipped data]
```

### 6. Adding Resumable Uploads

Use `Range` header for resume:

```http
PUT /file/large.bin HTTP/1.1
Content-Range: bytes 8192-16383/52428800
Content-Length: 8192

[chunk data]
```

Server tracks partial uploads in metadata:
```python
self.metadata[filename] = {
    "size": 52428800,
    "uploaded": 16384,  # bytes uploaded so far
    "status": "partial"
}
```

### 7. Adding Batch Operations

Delete multiple files:

```http
POST /batch/delete HTTP/1.1
Content-Type: application/json

{
  "files": ["file1.jpg", "file2.jpg", "file3.jpg"]
}
```

Response:
```json
{
  "success": ["file1.jpg", "file2.jpg"],
  "failed": [
    {"file": "file3.jpg", "error": "File not found"}
  ]
}
```

### 8. Adding WebSocket Support

For real-time updates:

```javascript
const ws = new WebSocket('ws://192.168.4.1:8080/ws');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // { "event": "file_uploaded", "filename": "photo.jpg" }
  // { "event": "file_deleted", "filename": "old.txt" }
};
```

### 9. Adding File Versioning

Track multiple versions:

```python
self.metadata[filename] = {
    "size": 1024,
    "current_version": 3,
    "versions": [
        {"version": 1, "size": 512, "timestamp": 1234567890},
        {"version": 2, "size": 768, "timestamp": 1234567900},
        {"version": 3, "size": 1024, "timestamp": 1234567910}
    ]
}
```

Access specific version:
```http
GET /file/document.txt?version=2
```

### 10. Adding Thumbnails

For images, auto-generate thumbnails:

```http
GET /file/photo.jpg?thumbnail=true&size=200x200
```

Server generates and caches thumbnail:
```python
# Cache thumbnails
self.metadata[filename] = {
    "size": 2048576,
    "thumbnail": "/sd/.thumbs/photo_200x200.jpg"
}
```

---

## Protocol Versioning

### Version Header

Add version to all responses:

```http
HTTP/1.1 200 OK
X-FileServer-Version: 1.0
```

### Version Negotiation

Client requests specific version:

```http
GET / HTTP/1.1
X-FileServer-Version: 1.0
```

Server responds with supported version:
```http
HTTP/1.1 200 OK
X-FileServer-Version: 1.0
```

If version mismatch:
```http
HTTP/1.1 400 Bad Request
X-FileServer-Version: 1.0

{"error": "Unsupported client version 2.0, server supports 1.0"}
```

---

## Performance Considerations

### Chunk Size Optimization

| Scenario           | Recommended Chunk Size |
|--------------------|------------------------|
| Pico W (2MB RAM)   | 4KB - 8KB              |
| ESP32 (520KB RAM)  | 2KB - 4KB              |
| Fast SD card       | 16KB - 32KB            |
| Slow SD card       | 4KB - 8KB              |
| WiFi unstable      | 2KB - 4KB              |
| WiFi stable        | 8KB - 16KB             |

### Connection Timeout

Default timeout values:
```python
# Accept connection timeout
s.settimeout(1.0)  # 1 second

# Client read timeout
conn.settimeout(2.0)  # 2 seconds

# Response wait timeout
timeout_ms = 10000  # 10 seconds
```

Adjust based on file sizes and network speed.

---

## Summary

This protocol provides:
- ✅ **Simple REST API** - Easy to implement in any language
- ✅ **Chunked transfers** - Handle files larger than RAM
- ✅ **JSON responses** - Easy to parse
- ✅ **CORS support** - Works from browsers
- ✅ **Error handling** - Clear error messages
- ✅ **Extensible** - Multiple extension points

The protocol is designed for embedded systems with limited resources while maintaining compatibility with standard HTTP clients.
