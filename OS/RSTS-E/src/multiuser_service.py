#!/usr/bin/env python3
"""
DEC Multi-User Terminal Concentrator (DHV11 / DECserver SSH & HTTPS Web VT100/VT220)
Provides:
  1. Multi-session HTTPS + Secure WebSocket (WSS) VT100/VT220 Browser Terminal Server
     spawning an independent PTY and OS terminal line (KB1:..KB31: or FTA1:..FTA64:) per connection.
  2. Multi-session OpenSSH (sshd) daemon configuration & startup on configurable port.
"""

import asyncio
import base64
import fcntl
import hashlib
import os
import pty
import signal
import ssl
import struct
import subprocess
import sys
import termios
import urllib.parse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import lcs_provisioning


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
  :root {
    --fg: #33ff66;
    --bg: #08100a;
    --glow: rgba(51, 255, 102, 0.35);
    --bar-bg: #141c16;
    --border: #265c34;
  }
  body.amber {
    --fg: #ffb000;
    --bg: #120c02;
    --glow: rgba(255, 176, 0, 0.35);
    --bar-bg: #1f1606;
    --border: #664600;
  }
  body.white {
    --fg: #e8eef2;
    --bg: #0b0e12;
    --glow: rgba(232, 238, 242, 0.25);
    --bar-bg: #161b22;
    --border: #3b4654;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--fg);
    font-family: "DejaVu Sans Mono", "Courier New", monospace;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  header {
    background: var(--bar-bg);
    border-bottom: 1px solid var(--border);
    padding: 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
    user-select: none;
  }
  .brand {
    font-weight: bold;
    letter-spacing: 0.6px;
    text-shadow: 0 0 6px var(--glow);
  }
  .controls {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  button, select {
    background: var(--bg);
    color: var(--fg);
    border: 1px solid var(--border);
    padding: 4px 10px;
    font-family: inherit;
    font-size: 12px;
    cursor: pointer;
    border-radius: 3px;
  }
  button:hover, select:hover {
    border-color: var(--fg);
    box-shadow: 0 0 6px var(--glow);
  }
  #status {
    padding: 2px 8px;
    border-radius: 3px;
    border: 1px solid var(--border);
    font-size: 11px;
  }
  #term-wrap {
    flex: 1;
    padding: 14px 18px;
    overflow-y: auto;
    position: relative;
    cursor: text;
  }
  #screen {
    white-space: pre-wrap;
    word-break: break-all;
    font-size: 15px;
    line-height: 1.35;
    text-shadow: 0 0 5px var(--glow);
    outline: none;
  }
  .cursor {
    display: inline-block;
    width: 9px;
    height: 16px;
    background: var(--fg);
    vertical-align: text-bottom;
    animation: blink 1s step-end infinite;
    box-shadow: 0 0 6px var(--glow);
  }
  @keyframes blink { 50% { opacity: 0; } }
  #hidden-input {
    position: fixed;
    opacity: 0;
    pointer-events: none;
    left: -9999px;
  }
</style>
</head>
<body>
<header>
  <div class="brand">__HEADER_TITLE__</div>
  <div class="controls">
    <span id="status">CONNECTING...</span>
    <select id="phosphor" onchange="setTheme(this.value)">
      <option value="green">P1 Green Phosphor</option>
      <option value="amber">P3 Amber Phosphor</option>
      <option value="white">P4 White Phosphor</option>
    </select>
    <button onclick="sendKey('\\r')">RETURN</button>
    <button onclick="sendKey('\\x03')">CTRL+C</button>
    <button onclick="sendKey('\\x1a')">CTRL+Z</button>
    <button onclick="clearScreen()">CLEAR</button>
    <button onclick="connectWS()">NEW SESSION</button>
    <button onclick="window.location.href='/signup'" style="border-color:#ffb000;color:#ffb000;font-weight:bold;">SIGN UP ($10/MO)</button>
  </div>
</header>
<div id="term-wrap" onclick="focusTerm()">
  <span id="screen"></span><span class="cursor"></span>
  <input id="hidden-input" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" />
</div>
<script>
  const screenEl = document.getElementById('screen');
  const wrapEl = document.getElementById('term-wrap');
  const statusEl = document.getElementById('status');
  const inputEl = document.getElementById('hidden-input');
  let ws = null;
  let textBuf = "";

  function setTheme(t) {
    document.body.className = (t === 'green') ? '' : t;
    focusTerm();
  }

  function focusTerm() {
    inputEl.focus();
  }

  function clearScreen() {
    textBuf = "";
    screenEl.textContent = "";
    focusTerm();
  }

  function appendOutput(raw) {
    // Strip basic ANSI clear-screen sequences and handle backspace/CR
    let s = raw.replace(/\\x1b\\[[0-9;]*[HJK]/g, function(m) {
      if (m.endsWith('J')) { textBuf = ""; }
      return "";
    }).replace(/\\x1b\\[[0-9;?]*[a-zA-Z]/g, "");

    for (let i = 0; i < s.length; i++) {
      const ch = s[i];
      if (ch === '\\b' || ch === '\\x7f') {
        if (textBuf.length > 0 && !textBuf.endsWith('\\n')) {
          textBuf = textBuf.slice(0, -1);
        }
      } else if (ch === '\\r') {
        // Ignore bare CR before LF
      } else {
        textBuf += ch;
      }
    }
    if (textBuf.length > 120000) {
      textBuf = textBuf.slice(textBuf.length - 100000);
    }
    screenEl.textContent = textBuf;
    wrapEl.scrollTop = wrapEl.scrollHeight;
  }

  function sendKey(seq) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(seq);
    }
    focusTerm();
  }

  function connectWS() {
    if (ws) {
      try { ws.close(); } catch (e) {}
    }
    const proto = (location.protocol === 'https:') ? 'wss:' : 'ws:';
    ws = new WebSocket(proto + '//' + location.host + '/ws');
    statusEl.textContent = 'CONNECTING...';

    ws.onopen = function() {
      statusEl.textContent = 'ONLINE (WSS PTY)';
      focusTerm();
    };
    ws.onmessage = function(ev) {
      appendOutput(typeof ev.data === 'string' ? ev.data : '');
    };
    ws.onclose = function() {
      statusEl.textContent = 'DISCONNECTED';
      appendOutput('\\n[Terminal carrier dropped - click NEW SESSION to reconnect]\\n');
    };
    ws.onerror = function() {
      statusEl.textContent = 'LINK ERROR';
    };
  }

  window.addEventListener('keydown', function(e) {
    if (document.activeElement && document.activeElement.tagName === 'SELECT') return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    if (e.ctrlKey && !e.altKey && !e.metaKey) {
      const k = e.key.toUpperCase();
      if (k === 'C') {
        if (window.getSelection().toString()) return; // allow copy
        e.preventDefault();
        ws.send('\\x03');
        return;
      }
      if (k === 'Z') {
        e.preventDefault();
        ws.send('\\x1a');
        return;
      }
      if (k === 'D') {
        e.preventDefault();
        ws.send('\\x04');
        return;
      }
      if (k === 'U') {
        e.preventDefault();
        ws.send('\\x15');
        return;
      }
    }

    if (e.key === 'Enter') {
      e.preventDefault();
      ws.send('\\n');
      appendOutput('\\n');
    } else if (e.key === 'Backspace') {
      e.preventDefault();
      ws.send('\\x7f');
      appendOutput('\\b');
    } else if (e.key === 'Tab') {
      e.preventDefault();
      ws.send('\\t');
      appendOutput('    ');
    } else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      ws.send(e.key);
      appendOutput(e.key);
    }
  });

  window.addEventListener('paste', function(e) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const txt = (e.clipboardData || window.clipboardData).getData('text');
    if (txt) {
      e.preventDefault();
      ws.send(txt);
      appendOutput(txt);
    }
  });

  connectWS();
</script>
</body>
</html>
"""

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def ensure_tls_cert(cert_dir="/tmp/dec_tls"):
    os.makedirs(cert_dir, exist_ok=True)
    cert_path = os.path.join(cert_dir, "cert.pem")
    key_path = os.path.join(cert_dir, "key.pem")
    if not (os.path.isfile(cert_path) and os.path.isfile(key_path)):
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-keyout",
                key_path,
                "-out",
                cert_path,
                "-days",
                "3650",
                "-subj",
                "/CN=dec-timesharing.local/O=Digital Equipment Corporation",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    return cert_path, key_path


def encode_ws_frame(payload_bytes, opcode=0x01):
    length = len(payload_bytes)
    header = bytearray([0x80 | opcode])
    if length < 126:
        header.append(length)
    elif length < 65536:
        header.append(126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(127)
        header.extend(struct.pack("!Q", length))
    return bytes(header) + payload_bytes


async def read_ws_frame(reader):
    hdr = await reader.readexactly(2)
    b1, b2 = hdr[0], hdr[1]
    opcode = b1 & 0x0F
    masked = bool(b2 & 0x80)
    length = b2 & 0x7F
    if length == 126:
        ext = await reader.readexactly(2)
        length = struct.unpack("!H", ext)[0]
    elif length == 127:
        ext = await reader.readexactly(8)
        length = struct.unpack("!Q", ext)[0]
    mask_key = await reader.readexactly(4) if masked else b""
    data = await reader.readexactly(length) if length > 0 else b""
    if masked and data:
        data = bytes(b ^ mask_key[i % 4] for i, b in enumerate(data))
    return opcode, data


class MultiUserTerminalServer:
    def __init__(self, emu_cmd, os_title, header_title, https_port, cert_dir="/tmp/dec_tls"):
        self.emu_cmd = emu_cmd
        self.os_title = os_title
        self.header_title = header_title
        self.https_port = int(https_port)
        self.cert_path, self.key_path = ensure_tls_cert(cert_dir)
        self.os_dir = os.path.abspath(os.path.join(os.path.dirname(emu_cmd[0]), ".."))
        self.fs_root = os.environ.get("RSTS_FS_ROOT", os.path.join(self.os_dir, "fs"))
        self.provisioning = lcs_provisioning.LCSProvisioningEngine(
            primary_os="RSTS",
            os_dir=self.os_dir,
            fs_root=self.fs_root,
            https_port=self.https_port,
        )
        self.html_bytes = (
            HTML_TEMPLATE.replace("__TITLE__", os_title)
            .replace("__HEADER_TITLE__", header_title)
            .encode("utf-8")
        )

    async def handle_client(self, reader, writer):
        try:
            raw_req = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=10.0)
        except Exception:
            writer.close()
            return

        req_text = raw_req.decode("latin-1", errors="replace")
        lines = req_text.split("\r\n")
        first_line = lines[0] if lines else ""
        parts = first_line.split()
        method = parts[0].upper() if len(parts) >= 1 else "GET"
        raw_path = parts[1] if len(parts) >= 2 else "/"
        parsed = urllib.parse.urlsplit(raw_path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        headers = {}
        for ln in lines[1:]:
            if ":" in ln:
                k, v = ln.split(":", 1)
                headers[k.strip().lower()] = v.strip()

        content_length = 0
        try:
            content_length = int(headers.get("content-length", "0"))
        except ValueError:
            content_length = 0
        body_bytes = b""
        if content_length > 0:
            try:
                body_bytes = await asyncio.wait_for(reader.readexactly(content_length), timeout=10.0)
            except Exception:
                writer.close()
                return

        if headers.get("upgrade", "").lower() == "websocket" or path.startswith("/ws"):
            ws_key = headers.get("sec-websocket-key", "")
            accept_raw = (ws_key + WS_GUID).encode("ascii")
            accept_val = base64.b64encode(hashlib.sha1(accept_raw).digest()).decode("ascii")
            resp = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_val}\r\n\r\n"
            )
            writer.write(resp.encode("ascii"))
            await writer.drain()
            await self._bridge_websocket_pty(reader, writer)
            return

        # Dispatch Legacy Computing Systems /signup and /api/v1/* endpoints
        api_resp = self.provisioning.handle_http_request(method, path, qs, headers, body_bytes)
        if api_resp is not None:
            st_code, st_text, ctype, resp_body = api_resp
            resp_hdr = (
                f"HTTP/1.1 {st_code} {st_text}\r\n"
                f"Content-Type: {ctype}\r\n"
                f"Content-Length: {len(resp_body)}\r\n"
                "Cache-Control: no-store\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii")
            writer.write(resp_hdr + resp_body)
            await writer.drain()
            writer.close()
            return

        # Standard HTTPS GET response serving the VT100/VT220 Web Terminal
        resp_hdr = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(self.html_bytes)}\r\n"
            "Cache-Control: no-store\r\n"
            "Connection: close\r\n\r\n"
        ).encode("ascii")
        writer.write(resp_hdr + self.html_bytes)
        await writer.drain()
        writer.close()

    async def _bridge_websocket_pty(self, reader, writer):
        master_fd, slave_fd = pty.openpty()
        # Disable duplicate ECHO on the PTY slave so WebSocket terminal controls echoing cleanly
        try:
            attrs = termios.tcgetattr(slave_fd)
            attrs[3] = attrs[3] & ~termios.ECHO
            termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)
        except Exception:
            pass

        env = os.environ.copy()
        env["TERM"] = "vt100"
        env["DEC_SESSION_SOURCE"] = "HTTPS"

        proc = subprocess.Popen(
            self.emu_cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            start_new_session=True,
            env=env,
            close_fds=True,
        )
        os.close(slave_fd)

        fl = fcntl.fcntl(master_fd, fcntl.F_GETFL)
        fcntl.fcntl(master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        loop = asyncio.get_running_loop()
        out_queue = asyncio.Queue()

        def on_pty_readable():
            try:
                chunk = os.read(master_fd, 4096)
                if chunk:
                    out_queue.put_nowait(chunk)
                else:
                    out_queue.put_nowait(None)
            except OSError:
                out_queue.put_nowait(None)

        loop.add_reader(master_fd, on_pty_readable)

        async def pty_to_ws():
            while True:
                chunk = await out_queue.get()
                if chunk is None:
                    break
                text = chunk.decode("utf-8", errors="replace").encode("utf-8")
                writer.write(encode_ws_frame(text, opcode=0x01))
                await writer.drain()

        async def ws_to_pty():
            while True:
                opcode, data = await read_ws_frame(reader)
                if opcode == 0x08:  # Close
                    break
                if opcode == 0x09:  # Ping -> Pong
                    writer.write(encode_ws_frame(data, opcode=0x0A))
                    await writer.drain()
                    continue
                if opcode in (0x01, 0x02) and data:
                    os.write(master_fd, data)

        t1 = asyncio.create_task(pty_to_ws())
        t2 = asyncio.create_task(ws_to_pty())
        try:
            await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
        finally:
            t1.cancel()
            t2.cancel()
            loop.remove_reader(master_fd)
            try:
                os.close(master_fd)
            except OSError:
                pass
            if proc.poll() is None:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except OSError:
                    pass
            writer.close()

    async def serve_forever(self):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile=self.cert_path, keyfile=self.key_path)
        server = await asyncio.start_server(
            self.handle_client, host="0.0.0.0", port=self.https_port, ssl=ssl_ctx
        )
        async with server:
            await server.serve_forever()


def configure_and_start_sshd(emu_bin_path, ssh_port):
    """Configure and launch OpenSSH daemon inside Docker container if available."""
    sshd_bin = "/usr/sbin/sshd"
    if not os.path.isfile(sshd_bin) or os.geteuid() != 0:
        return False

    os.makedirs("/run/sshd", exist_ok=True)
    subprocess.run(["ssh-keygen", "-A"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

    ports = {22, int(ssh_port)}
    port_lines = "\n".join(f"Port {p}" for p in sorted(ports))
    conf_dir = "/etc/ssh/sshd_config.d"
    os.makedirs(conf_dir, exist_ok=True)
    conf_path = os.path.join(conf_dir, "dec-multiuser.conf")
    with open(conf_path, "w") as f:
        f.write(
            f"{port_lines}\n"
            "PermitRootLogin yes\n"
            "PasswordAuthentication yes\n"
            "PermitEmptyPasswords yes\n"
            "UsePAM no\n"
            "PrintMotd no\n"
            "PrintLastLog no\n"
            f"ForceCommand {emu_bin_path}\n"
        )

    subprocess.Popen([sshd_bin], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True


def start_background_daemons(emu_bin_path, os_title, header_title, ssh_port, https_port):
    """Spawn SSH daemon and HTTPS Web Terminal server as background daemon processes."""
    configure_and_start_sshd(emu_bin_path, ssh_port)

    # Launch HTTPS Web Terminal Server in a detached child process
    script_path = os.path.abspath(__file__)
    subprocess.Popen(
        [
            sys.executable,
            script_path,
            "--serve-https",
            "--emu",
            emu_bin_path,
            "--title",
            os_title,
            "--header",
            header_title,
            "--port",
            str(https_port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DEC Multi-User HTTPS & SSH Terminal Concentrator")
    parser.add_argument("--serve-https", action="store_true", help="Run HTTPS WebSocket VT100/VT220 server")
    parser.add_argument("--emu", required=True, help="Path to OS emulator executable")
    parser.add_argument("--title", default="DEC Timesharing Terminal", help="Page title")
    parser.add_argument("--header", default="DEC VT100/VT220 Terminal", help="Header banner title")
    parser.add_argument("--port", type=int, default=8411, help="HTTPS listen port")
    args = parser.parse_args()

    if args.serve_https:
        srv = MultiUserTerminalServer(
            emu_cmd=[args.emu],
            os_title=args.title,
            header_title=args.header,
            https_port=args.port,
        )
        asyncio.run(srv.serve_forever())


if __name__ == "__main__":
    main()
