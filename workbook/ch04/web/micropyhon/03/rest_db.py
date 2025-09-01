import network
import socket
import time
import json
import os
import machine
import sdcard
import uos


AP_SSID = "PicoDatabase"
AP_PASSWORD = None  # Open network for simplicity


log_buffer = []
max_log_lines = 20  # Store more logs since we'll show them in web interface
connection_count = 0
last_request_time = 0


def log(message, level="INFO"):
    # GET /api/status - System status
#    if method == "GET" and path == "/api/status":
#        global log_buffer, max_log_lines
    timestamp = time.ticks_ms() // 1000
    log_entry = f"{timestamp:>6} {level[:4]} {message}"
    print(f"[{level}] {message}")
    
    log_buffer.append({"timestamp": timestamp, "level": level, "message": message})
    if len(log_buffer) > max_log_lines:
        log_buffer.pop(0)


class MiniDB:
    def __init__(self, base="/sd", flush_every=1):
        self.base = base if base.endswith("/") else base + "/"
        self.flush_every = max(1, flush_every)
        self.buffers = {}

        try:
            # SD Card SPI setup
            cs = machine.Pin(1, machine.Pin.OUT)
            spi = machine.SPI(0,
                            baudrate=1000000,
                            polarity=0,
                            phase=0,
                            bits=8,
                            firstbit=machine.SPI.MSB,
                            sck=machine.Pin(2),
                            mosi=machine.Pin(3),
                            miso=machine.Pin(4))
            
            sd = sdcard.SDCard(spi, cs)
            vfs = uos.VfsFat(sd)
            uos.mount(vfs, "/sd")
            log("SD card mounted successfully")
        except Exception as e:
            raise RuntimeError(f"SD card init failed: {e}")


        try:
            os.listdir(self.base)
        except OSError:
            os.mkdir(self.base)
            log(f"Created base directory: {self.base}")

    def _path(self, name):
        return self.base + name + ".csv"

    # overwritten!
    def create_table(self, name, fields):
        try:
            with open(self._path(name), "w") as f:
                f.write(",".join(fields) + "\n")
                f.flush()
            self.buffers[name] = []
            log(f"Table '{name}' created")
            return True
        except OSError as e:
            log(f"Create table error: {e}", "ERROR")
            return False

    def insert(self, name, row):
        if not isinstance(row, (list, tuple)):
            return False
        if name not in self.buffers:
            self.buffers[name] = []
        self.buffers[name].append(row)
        if len(self.buffers[name]) >= self.flush_every:
            return self.commit(name)
        return True

    def commit(self, name):
        if name not in self.buffers or not self.buffers[name]:
            return False
        try:
            with open(self._path(name), "a") as f:
                for row in self.buffers[name]:
                    f.write(",".join(str(x) for x in row) + "\n")
                f.flush()
            count = len(self.buffers[name])
            self.buffers[name] = []
            log(f"Committed {count} rows to {name}")
            return True
        except OSError as e:
            log(f"Commit error: {e}", "ERROR")
            return False

    def all_rows(self, name):
        rows = []
        try:
            with open(self._path(name), "r") as f:
                header = f.readline().strip().split(",")
                if not header or header == ['']:
                    return rows
                for line in f:
                    values = line.strip().split(",")
                    if values == [''] or len(values) != len(header):
                        continue
                    rows.append(dict(zip(header, values)))
        except OSError:
            pass
        return rows

    def select(self, name, where=None):
        results = []
        for row in self.all_rows(name):
            if where:
                if all(row.get(k) == str(v) for k, v in where.items()):
                    results.append(row)
            else:
                results.append(row)
        return results

    def delete_rows(self, name, where=None):
        path = self._path(name)
        try:
            with open(path, "r") as f:
                header = f.readline().strip()
                if not header:
                    return False
                header_fields = header.split(",")
                rows = []
                deleted_count = 0
                
                for line in f:
                    values = line.strip().split(",")
                    if len(values) != len(header_fields):
                        continue
                    row = dict(zip(header_fields, values))
                    
                    should_delete = False
                    if where:
                        if all(row.get(k) == str(v) for k, v in where.items()):
                            should_delete = True
                            deleted_count += 1
                    
                    if not should_delete:
                        rows.append(values)

            # Rewrite file
            with open(path, "w") as f:
                f.write(header + "\n")
                for values in rows:
                    f.write(",".join(values) + "\n")
                f.flush()
            
            log(f"Deleted {deleted_count} rows from {name}")
            return deleted_count > 0
            
        except OSError as e:
            log(f"Delete error: {e}", "ERROR")
            return False

    def list_tables(self):
        tables = []
        try:
            for file in os.listdir(self.base):
                if file.endswith('.csv'):
                    tables.append(file[:-4])  # Remove .csv extension
        except OSError:
            pass
        return tables

    def table_info(self, name):
        try:
            with open(self._path(name), "r") as f:
                header = f.readline().strip().split(",")
                row_count = sum(1 for line in f if line.strip())
                return {"fields": header, "row_count": row_count}
        except OSError:
            return None


# Init database
db = None

def create_access_point():
    log("Setting up Access Point")
    
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    time.sleep(1)
    
    ap.active(True)
    time.sleep(2)
    
    ap.config(essid=AP_SSID)
    
    timeout = 10
    while not ap.active() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        log(f"AP starting... {timeout}s")
    
    if not ap.active():
        log("AP activation FAILED", "ERROR")
        return None
    
    config = ap.ifconfig()
    ip = config[0]
    
    log(f"AP Ready: {ip}")
    return ip

def create_response(status_code, data=None, message=None):
    response_data = {
        "status": status_code,
        "timestamp": time.ticks_ms(),
        "connection_count": connection_count
    }
    
    if data is not None:
        response_data["data"] = data
    if message:
        response_data["message"] = message
    
    json_response = json.dumps(response_data)
    
    status_text = {
        200: "OK", 201: "Created", 400: "Bad Request", 
        404: "Not Found", 405: "Method Not Allowed", 500: "Internal Server Error"
    }.get(status_code, "Unknown")
    
    headers = f"HTTP/1.1 {status_code} {status_text}\r\n"
    headers += "Content-Type: application/json\r\n"
    headers += "Access-Control-Allow-Origin: *\r\n"
    headers += f"Content-Length: {len(json_response)}\r\n"
    headers += "Connection: close\r\n\r\n"
    
    return headers + json_response

def handle_rest_request(method, path, params, json_body):
    global db
    
    # GET /api/tables - List all tables
    if method == "GET" and path == "/api/tables":
        tables = db.list_tables()
        return create_response(200, {"tables": tables})
    
    # POST /api/tables/{name} - Create new table
    elif method == "POST" and path.startswith("/api/tables/"):
        table_name = path.split("/")[-1]
        fields = json_body.get("fields", [])
        
        if not fields:
            return create_response(400, message="Fields required")
        
        if db.create_table(table_name, fields):
            return create_response(201, message=f"Table '{table_name}' created")
        else:
            return create_response(500, message="Failed to create table")
    
    # GET /api/tables/{name} - Get table info and data
    elif method == "GET" and path.startswith("/api/tables/"):
        table_name = path.split("/")[-1]
        
        # Get table info
        info = db.table_info(table_name)
        if info is None:
            return create_response(404, message=f"Table '{table_name}' not found")
        
        # Get data with optional filtering
        where = {}
        for key, value in params.items():
            if key.startswith("where_"):
                field = key[6:]  # Remove "where_" prefix
                where[field] = value
        
        rows = db.select(table_name, where if where else None)
        
        return create_response(200, {
            "table": table_name,
            "info": info,
            "rows": rows,
            "count": len(rows)
        })
    
    # POST /api/tables/{name}/rows - Insert new row
    elif method == "POST" and path.startswith("/api/tables/") and path.endswith("/rows"):
        table_name = path.split("/")[-2]
        row_data = json_body.get("row", [])
        
        if not row_data:
            return create_response(400, message="Row data required")
        
        if db.insert(table_name, row_data):
            return create_response(201, message="Row inserted")
        else:
            return create_response(500, message="Failed to insert row")
    
    # DELETE /api/tables/{name}/rows - Delete rows
    elif method == "DELETE" and path.startswith("/api/tables/") and path.endswith("/rows"):
        table_name = path.split("/")[-2]
        
        # Build where conditions from JSON body or params
        where = json_body.get("where", {})
        if not where:
            for key, value in params.items():
                if key.startswith("where_"):
                    field = key[6:]
                    where[field] = value
        
        if db.delete_rows(table_name, where if where else None):
            return create_response(200, message="Rows deleted")
        else:
            return create_response(404, message="No rows deleted")
    
    # POST /api/tables/{name}/commit - Force commit buffered data
    elif method == "POST" and path.startswith("/api/tables/") and path.endswith("/commit"):
        table_name = path.split("/")[-2]
        
        if db.commit(table_name):
            return create_response(200, message="Data committed")
        else:
            return create_response(404, message="Nothing to commit")
    
    # GET /api/logs - Get recent logs with web display
    elif method == "GET" and path == "/api/logs":
        return create_response(200, {
            "logs": log_buffer,
            "count": len(log_buffer),
            "connections": connection_count,
            "uptime": time.ticks_ms() // 1000
        })
#        return create_response(200, {
#            "uptime": time.ticks_ms(),
#            "connections": connection_count,
#            "ap_ssid": AP_SSID,
#            "tables": len(db.list_tables()),
#            "sd_mounted": True
#        })
    
    # Simple web interface
    elif method == "GET" and path == "/":
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Pico Database REST API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; background: white; border-radius: 5px; }
        .status-section { background: #e8f5e8; }
        button { padding: 8px 15px; margin: 5px; cursor: pointer; background: #007cba; color: white; border: none; border-radius: 3px; }
        button:hover { background: #005a87; }
        input, select, textarea { padding: 5px; margin: 5px; border: 1px solid #ccc; border-radius: 3px; }
        pre { background: #f0f0f0; padding: 10px; overflow-x: auto; border-radius: 3px; }
        .result { margin: 10px 0; padding: 10px; background: #e8f5e8; border-radius: 3px; }
        .error { background: #ffe8e8; }
        .logs { height: 300px; overflow-y: scroll; background: #000; color: #0f0; padding: 10px; font-family: monospace; }
        .log-entry { margin: 2px 0; }
        .log-INFO { color: #0f0; }
        .log-WARN { color: #ff0; }
        .log-ERROR { color: #f00; }
        .log-SUCCESS { color: #0af; }
        h1 { color: #333; text-align: center; }
        h3 { color: #007cba; border-bottom: 2px solid #007cba; padding-bottom: 5px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pico Database REST API</h1>
        
        <div class="section status-section">
            <h3>System Status & Logs</h3>
            <button onclick="refreshStatus()">Refresh Status</button>
            <button onclick="refreshLogs()">Refresh Logs</button>
            <div id="status" style="margin: 10px 0;"></div>
            <div class="logs" id="logs">Loading logs...</div>
        </div>
        
        <div class="grid">
            <div class="section">
                <h3>Table Management</h3>
                <input type="text" id="tableName" placeholder="Table name" value="test_table">
                <br>
                <button onclick="createTable()">Create Table</button>
                <button onclick="listTables()">List Tables</button>
                <button onclick="getTable()">View Table</button>
                <button onclick="deleteTable()">Delete Table</button>
                <div id="tableResult" class="result" style="display:none;"></div>
            </div>
            
            <div class="section">
                <h3>Data Operations</h3>
                <input type="text" id="insertTable" placeholder="Table name" value="test_table">
                <br>
                <textarea id="insertData" placeholder='Row data: ["value1","value2","value3"]' rows="3" style="width: 90%;">["test","123","' + new Date().toISOString() + '"]</textarea>
                <br>
                <button onclick="insertRow()">Insert Row</button>
                <button onclick="commitTable()">Commit Buffer</button>
                <div id="dataResult" class="result" style="display:none;"></div>
            </div>
        </div>
        
        <div class="section">
            <h3>Query & Filter</h3>
            <input type="text" id="queryTable" placeholder="Table name" value="test_table">
            <input type="text" id="queryField" placeholder="Field name (optional)">
            <input type="text" id="queryValue" placeholder="Field value (optional)">
            <button onclick="queryTable()">Query</button>
            <div id="queryResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h3>Delete Operations</h3>
            <input type="text" id="deleteTable" placeholder="Table name" value="test_table">
            <input type="text" id="deleteField" placeholder="Field name (optional)">
            <input type="text" id="deleteValue" placeholder="Field value (optional)">
            <button onclick="deleteRows()">Delete Rows</button>
            <small>Leave field/value empty to delete ALL rows</small>
            <div id="deleteResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h3>API Documentation</h3>
            <pre>
🔗 REST Endpoints:
GET    /api/tables              - List all tables
POST   /api/tables/{name}       - Create table (body: {"fields": ["col1","col2"]})
GET    /api/tables/{name}       - Get table data & info
POST   /api/tables/{name}/rows  - Insert row (body: {"row": ["val1","val2"]})
DELETE /api/tables/{name}/rows  - Delete rows (body: {"where": {"col":"val"}})
POST   /api/tables/{name}/commit- Force commit buffered data
GET    /api/status              - Get system status
GET    /api/logs                - Get system logs
            </pre>
        </div>
    </div>
    
    <script>
        function showResult(elementId, data, isError = false) {
            const element = document.getElementById(elementId);
            element.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            element.className = 'result ' + (isError ? 'error' : '');
            element.style.display = 'block';
            
            // Auto-hide after 10 seconds if not an error
            if (!isError) {
                setTimeout(() => {
                    element.style.display = 'none';
                }, 10000);
            }
        }
        
        function refreshStatus() {
            fetch('/api/status')
            .then(r => r.json())
            .then(data => {
                const uptime = Math.floor(data.data.uptime / 1000);
                document.getElementById('status').innerHTML = `
                    <strong>Uptime:</strong> ${uptime}s | 
                    <strong>Connections:</strong> ${data.data.connections} | 
                    <strong>Tables:</strong> ${data.data.tables} | 
                    <strong>AP SSID:</strong> ${data.data.ap_ssid}
                `;
            })
            .catch(e => console.error('Status error:', e));
        }
        
        function refreshLogs() {
            fetch('/api/logs')
            .then(r => r.json())
            .then(data => {
                const logsDiv = document.getElementById('logs');
                logsDiv.innerHTML = '';
                data.data.logs.forEach(log => {
                    const div = document.createElement('div');
                    div.className = 'log-entry log-' + log.level;
                    div.textContent = `${log.timestamp.toString().padStart(6)} ${log.level.padEnd(4)} ${log.message}`;
                    logsDiv.appendChild(div);
                });
                logsDiv.scrollTop = logsDiv.scrollHeight;
            })
            .catch(e => console.error('Logs error:', e));
        }
        
        function createTable() {
            const name = document.getElementById('tableName').value;
            if (!name) { alert('Please enter table name'); return; }
            
            fetch(`/api/tables/${name}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({fields: ['name', 'value', 'timestamp']})
            })
            .then(r => r.json())
            .then(data => showResult('tableResult', data))
            .catch(e => showResult('tableResult', {error: e.message}, true));
        }
        
        function listTables() {
            fetch('/api/tables')
            .then(r => r.json())
            .then(data => showResult('tableResult', data))
            .catch(e => showResult('tableResult', {error: e.message}, true));
        }
        
        function getTable() {
            const name = document.getElementById('tableName').value;
            if (!name) { alert('Please enter table name'); return; }
            
            fetch(`/api/tables/${name}`)
            .then(r => r.json())
            .then(data => showResult('tableResult', data))
            .catch(e => showResult('tableResult', {error: e.message}, true));
        }
        
        function deleteTable() {
            const name = document.getElementById('tableName').value;
            if (!name) { alert('Please enter table name'); return; }
            if (!confirm(`Are you sure you want to delete table '${name}'?`)) return;
            
            // Note: This would require a DELETE /api/tables/{name} endpoint
            alert('Table deletion not implemented in this demo! Delete manually from SD card.');
        }
        
        function insertRow() {
            const table = document.getElementById('insertTable').value;
            const data = document.getElementById('insertData').value;
            
            if (!table) { alert('Please enter table name'); return; }
            
            try {
                const rowData = JSON.parse(data);
                fetch(`/api/tables/${table}/rows`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({row: rowData})
                })
                .then(r => r.json())
                .then(data => showResult('dataResult', data))
                .catch(e => showResult('dataResult', {error: e.message}, true));
            } catch (e) {
                showResult('dataResult', {error: 'Invalid JSON format'}, true);
            }
        }
        
        function commitTable() {
            const table = document.getElementById('insertTable').value;
            if (!table) { alert('Please enter table name'); return; }
            
            fetch(`/api/tables/${table}/commit`, {method: 'POST'})
            .then(r => r.json())
            .then(data => showResult('dataResult', data))
            .catch(e => showResult('dataResult', {error: e.message}, true));
        }
        
        function queryTable() {
            const table = document.getElementById('queryTable').value;
            const field = document.getElementById('queryField').value;
            const value = document.getElementById('queryValue').value;
            
            if (!table) { alert('Please enter table name'); return; }
            
            let url = `/api/tables/${table}`;
            if (field && value) {
                url += `?where_${field}=${encodeURIComponent(value)}`;
            }
            
            fetch(url)
            .then(r => r.json())
            .then(data => showResult('queryResult', data))
            .catch(e => showResult('queryResult', {error: e.message}, true));
        }
        
        function deleteRows() {
            const table = document.getElementById('deleteTable').value;
            const field = document.getElementById('deleteField').value;
            const value = document.getElementById('deleteValue').value;
            
            if (!table) { alert('Please enter table name'); return; }
            
            let confirmMsg = `Delete rows from table '${table}'`;
            if (field && value) {
                confirmMsg += ` where ${field}='${value}'`;
            } else {
                confirmMsg += ' (ALL ROWS)';
            }
            
            if (!confirm(confirmMsg + '?')) return;
            
            const body = {};
            if (field && value) {
                body.where = {};
                body.where[field] = value;
            }
            
            fetch(`/api/tables/${table}/rows`, {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            })
            .then(r => r.json())
            .then(data => showResult('deleteResult', data))
            .catch(e => showResult('deleteResult', {error: e.message}, true));
        }
        
        // Auto-refresh status and logs
        setInterval(refreshStatus, 5000);
        setInterval(refreshLogs, 3000);
        
        // Initial load
        refreshStatus();
        refreshLogs();
    </script>
</body>
</html>"""
        
        headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
        headers += f"Content-Length: {len(html)}\r\n\r\n"
        return headers + html
    
    else:
        return create_response(404, message=f"Endpoint not found: {method} {path}")

def parse_json_body(request_data):
    try:
        if '\r\n\r\n' in request_data:
            body = request_data.split('\r\n\r\n', 1)[1]
            if body.strip():
                return json.loads(body)
    except Exception as e:
        log(f"JSON parse error: {e}", "ERROR")
    return {}

def parse_request(request_data):
    lines = request_data.split('\n')
    if not lines:
        return None, None, {}, {}
    
    request_line = lines[0].strip()
    parts = request_line.split(' ')
    
    if len(parts) < 2:
        return None, None, {}, {}
    
    method = parts[0]
    full_path = parts[1]
    
    if '?' in full_path:
        path, query_string = full_path.split('?', 1)
        params = {}
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value.replace('%20', ' ').replace('+', ' ')
    else:
        path = full_path
        params = {}
    
    json_body = {}
    if method in ['POST', 'PUT', 'DELETE']:
        json_body = parse_json_body(request_data)
    
    return method, path, params, json_body

def main():
    global connection_count, db
    
    log("Starting Pico Database Server")
    
    # Init database
    try:
        db = MiniDB("/sd", flush_every=2)
        log("Database initialized")
    except Exception as e:
        log(f"DB init failed: {e}", "ERROR")
        return
    
    # Create access point
    ip = create_access_point()
    if not ip:
        log("Failed to create AP", "ERROR")
        return
    
    # Setup web server
    try:
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(3)
        log(f"Server listening on {ip}:80")
    except Exception as e:
        log(f"Server setup failed: {e}", "ERROR")
        return
    
    # Main server loop
    while True:
        client_socket = None
        try:
            client_socket, client_addr = s.accept()
            connection_count += 1
            
            log(f"Connection #{connection_count}")
            
            client_socket.settimeout(15.0)
            request_data = client_socket.recv(4096).decode('utf-8')
            
            if not request_data:
                continue
            
            method, path, params, json_body = parse_request(request_data)
            
            if method and path:
                log(f"{method} {path[:15]}")
                response = handle_rest_request(method, path, params, json_body)
                client_socket.send(response.encode('utf-8'))
            else:
                error_response = create_response(400, message="Invalid request")
                client_socket.send(error_response.encode('utf-8'))
                
        except OSError as e:
            error_code = e.args[0] if e.args else 0
            if error_code in [104, 110]:  # Connection reset/timeout
                log("Client disconnected", "WARN")
            else:
                log(f"Connection error: {error_code}", "ERROR")
                
        except Exception as e:
            log(f"Server error: {str(e)[:15]}", "ERROR")
            
        finally:
            if client_socket:
                try:
                    client_socket.close()
                except:
                    pass

if __name__ == "__main__":
    main()
