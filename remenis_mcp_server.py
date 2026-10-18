import sys
import json
import sqlite3
import hmac
import hashlib
import time
import os
import base64

# Standard MCP JSON-RPC Server Wrapper for Remenis Memory Middleware
class RemenisMCPServer:
    def __init__(self, db_path="remenis_mcp.db"):
        self.db_path = db_path
        self.master_secret = os.environ.get("REMENIS_HMAC_KEY", "default-secure-sentinel-key-change-in-prod").encode('utf-8')
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zero_trust_ledger (
                sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                namespace TEXT NOT NULL,
                memory_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                prev_hash TEXT NOT NULL,
                signature TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _compute_hmac(self, data: str) -> str:
        return hmac.new(self.master_secret, data.encode('utf-8'), hashlib.sha256).hexdigest()

    def _get_last_hash(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT signature FROM zero_trust_ledger ORDER BY sequence_id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        if not row:
            return hashlib.sha256(b"REMENIS_MCP_GENESIS").hexdigest()
        return row[0]

    def handle_request(self, request_str: str) -> str:
        try:
            req = json.loads(request_str)
            method = req.get("method")
            params = req.get("params", {})
            req_id = req.get("id", 1)

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "remenis-mcp-server", "version": "1.0.0"}
                    },
                    "id": req_id
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "tools": [
                            {
                                "name": "remenis_store_memory",
                                "description": "Securely anchor an immutable memory block into a cryptographically chained namespace.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "namespace": {"type": "string"},
                                        "memory_id": {"type": "string"},
                                        "content": {"type": "string"}
                                    },
                                    "required": ["namespace", "memory_id", "content"]
                                }
                            },
                            {
                                "name": "remenis_retrieve_memory",
                                "description": "Retrieve verified memory from an isolated namespace with integrity checks.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "namespace": {"type": "string"},
                                        "memory_id": {"type": "string"}
                                    },
                                    "required": ["namespace", "memory_id"]
                                }
                            }
                        ]
                    },
                    "id": req_id
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "remenis_store_memory":
                    ns = args["namespace"]
                    mid = args["memory_id"]
                    content = args["content"]
                    
                    timestamp = time.time()
                    prev_hash = self._get_last_hash()
                    raw_data = f"{prev_hash}:{ns}:{mid}:{content}:{timestamp}"
                    sig = self._compute_hmac(raw_data)

                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO zero_trust_ledger (namespace, memory_id, content, timestamp, prev_hash, signature) VALUES (?, ?, ?, ?, ?, ?)',
                                   (ns, mid, content, timestamp, prev_hash, sig))
                    conn.commit()
                    conn.close()

                    response = {
                        "jsonrpc": "2.0",
                        "result": {"content": [{"type": "text", "text": f"Successfully anchored memory '{mid}' in namespace '{ns}' with cryptographic chain linkage."}]},
                        "id": req_id
                    }
                elif tool_name == "remenis_retrieve_memory":
                    ns = args["namespace"]
                    mid = args["memory_id"]

                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT content, timestamp, prev_hash, signature FROM zero_trust_ledger WHERE namespace = ? AND memory_id = ?', (ns, mid))
                    row = cursor.fetchone()
                    conn.close()

                    if not row:
                        res_text = f"Memory '{mid}' not found in namespace '{ns}'."
                    else:
                        content, timestamp, prev_hash, stored_sig = row
                        raw_data = f"{prev_hash}:{ns}:{mid}:{content}:{timestamp}"
                        if hmac.compare_digest(self._compute_hmac(raw_data), stored_sig):
                            res_text = f"[VERIFIED SECURE MEMORY]: {content}"
                        else:
                            res_text = "[CRITICAL SECURITY ALERT]: Ledger tampering detected!"

                    response = {
                        "jsonrpc": "2.0",
                        "result": {"content": [{"type": "text", "text": res_text}]},
                        "id": req_id
                    }
                else:
                    response = {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}, "id": req_id}
            else:
                response = {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method not found: {method}"}, "id": req_id}

            return json.dumps(response)
        except Exception as e:
            return json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": 1})

    def start_stdio_loop(self):
        """Runs the MCP JSON-RPC stdio event loop for Cursor and Claude Desktop integration."""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            resp = self.handle_request(line.strip())
            sys.stdout.write(resp + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    server = RemenisMCPServer()
    server.start_stdio_loop()
