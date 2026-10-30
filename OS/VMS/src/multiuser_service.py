#!/usr/bin/env python3
"""
DEC Multi-User Terminal Concentrator & DECwindows X11 Web Workstation Server
Provides:
  1. Multi-session HTTPS + Secure WebSocket (WSS) VT100/VT220 Browser Terminal Server
     spawning an independent PTY and OS terminal line (KB1:..KB31: or FTA1:..FTA64:) per connection.
  2. Authenticated Live X11 / DECwindows OSF/Motif 1.1 Web Workstation (<canvas> over WSS /ws-x11)
     requiring valid VAX/VMS SYSUAF credentials before any X11 application can be launched or used.
  3. Multi-session OpenSSH (sshd) daemon configuration & startup on configurable port.
"""

import asyncio
import base64
import ctypes
import fcntl
import hashlib
import json
import os
import pty
import signal
import ssl
import struct
import subprocess
import sys
import termios
import time
import urllib.parse
import zlib

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
    padding: 7px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
    user-select: none;
    flex-wrap: wrap;
    gap: 8px;
  }
  .brand {
    font-weight: bold;
    letter-spacing: 0.5px;
    text-shadow: 0 0 6px var(--glow);
  }
  .controls {
    display: flex;
    gap: 6px;
    align-items: center;
    flex-wrap: wrap;
  }
  button, select {
    background: var(--bg);
    color: var(--fg);
    border: 1px solid var(--border);
    padding: 4px 9px;
    font-family: inherit;
    font-size: 11px;
    cursor: pointer;
    border-radius: 3px;
  }
  button:hover:not(:disabled), select:hover:not(:disabled), button.active-mode {
    border-color: var(--fg);
    box-shadow: 0 0 6px var(--glow);
  }
  button:disabled, select:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
  button.active-mode {
    background: var(--border);
    font-weight: bold;
  }
  #status {
    padding: 2px 8px;
    border-radius: 3px;
    border: 1px solid var(--border);
    font-size: 11px;
  }
  #workspace {
    flex: 1;
    display: flex;
    flex-direction: row;
    overflow: hidden;
    position: relative;
  }
  #term-wrap {
    flex: 1;
    padding: 14px 18px;
    overflow-y: auto;
    position: relative;
    cursor: text;
    min-width: 280px;
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
  /* DECwindows X11 Motif Graphical Workstation Panel */
  #x11-pane {
    display: none;
    flex: 1.25;
    flex-direction: column;
    background: #233445;
    border-left: 2px solid var(--border);
    overflow: hidden;
    position: relative;
  }
  #x11-toolbar {
    background: #2e4358;
    color: #e8eef2;
    border-bottom: 1px solid #5c7893;
    padding: 5px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 11px;
    gap: 8px;
    user-select: none;
  }
  #x11-toolbar button, #x11-toolbar select {
    background: #3b5368;
    color: #ffffff;
    border: 1px solid #7c9ab8;
    padding: 3px 8px;
    font-size: 11px;
  }
  #x11-toolbar button:hover:not(:disabled), #x11-toolbar select:hover:not(:disabled) {
    background: #4d6b85;
    box-shadow: 0 0 5px rgba(255,255,255,0.35);
  }
  #x11-viewport {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1b2836;
    overflow: auto;
    padding: 6px;
    position: relative;
  }
  #x11-canvas {
    background: #3b5368;
    border: 2px solid #7c9ab8;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.65);
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    cursor: default;
    outline: none;
  }
  #x11-canvas.focused {
    border-color: #33ff66;
  }
  /* Authentic DECwindows OSF/Motif 1.1 Start Session Login Gate */
  #decw-login-overlay {
    position: absolute;
    inset: 0;
    background: rgba(24, 38, 52, 0.88);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 20;
  }
  .motif-dialog {
    width: 440px;
    background: #aeb8c4;
    color: #10161d;
    border-top: 3px solid #e6edf5;
    border-left: 3px solid #e6edf5;
    border-right: 3px solid #485460;
    border-bottom: 3px solid #485460;
    box-shadow: 0 12px 32px rgba(0,0,0,0.75);
    padding: 4px;
    font-family: "DejaVu Sans Mono", monospace;
  }
  .motif-titlebar {
    background: #3b5368;
    color: #ffffff;
    padding: 6px 10px;
    font-weight: bold;
    font-size: 13px;
    border-top: 2px solid #6b89a4;
    border-left: 2px solid #6b89a4;
    border-right: 2px solid #1d2b38;
    border-bottom: 2px solid #1d2b38;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .motif-body {
    padding: 16px 18px;
  }
  .motif-banner {
    font-size: 12px;
    font-weight: bold;
    color: #1e3246;
    margin-bottom: 6px;
  }
  .motif-sub {
    font-size: 11px;
    color: #2c3a47;
    margin-bottom: 14px;
  }
  .motif-field {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    font-size: 12px;
    font-weight: bold;
  }
  .motif-field label {
    width: 105px;
    color: #10161d;
  }
  .motif-field input {
    flex: 1;
    background: #ffffff;
    color: #000000;
    border-top: 2px solid #485460;
    border-left: 2px solid #485460;
    border-right: 2px solid #e6edf5;
    border-bottom: 2px solid #e6edf5;
    padding: 5px 8px;
    font-family: inherit;
    font-size: 13px;
    outline: none;
  }
  .motif-error {
    min-height: 18px;
    color: #8b0000;
    font-size: 11px;
    font-weight: bold;
    margin: 6px 0 10px 0;
  }
  .motif-actions {
    display: flex;
    justify-content: space-around;
    padding-top: 8px;
    border-top: 2px groove #d0d8e0;
  }
  .motif-btn {
    background: #aeb8c4;
    color: #10161d;
    border-top: 2px solid #e6edf5;
    border-left: 2px solid #e6edf5;
    border-right: 2px solid #485460;
    border-bottom: 2px solid #485460;
    padding: 5px 22px;
    font-weight: bold;
    font-size: 12px;
    cursor: pointer;
  }
  .motif-btn:hover {
    background: #bcc6d2;
    box-shadow: none;
    border-color: #e6edf5 #485460 #485460 #e6edf5;
  }
  .motif-btn:active {
    border-top: 2px solid #485460;
    border-left: 2px solid #485460;
    border-right: 2px solid #e6edf5;
    border-bottom: 2px solid #e6edf5;
  }
  .x11-only-ctrl {
    display: __X11_CTRL_DISPLAY__;
  }
</style>
</head>
<body>
<header>
  <div class="brand">__HEADER_TITLE__</div>
  <div class="controls">
    <span id="status">CONNECTING...</span>
    <span class="x11-only-ctrl" style="gap:4px; align-items:center;">
      <button id="mode-vt" class="active-mode" onclick="setViewMode('vt')">VT220</button>
      <button id="mode-split" onclick="setViewMode('split')">SPLIT (VT220 + X11)</button>
      <button id="mode-x11" onclick="setViewMode('x11')">DECWINDOWS X11 (WSA0:)</button>
      <button id="btn-launch-decw" onclick="launchX11App('decwx11')" title="Open DECwindows Motif Session Manager">LAUNCH DECWINDOWS</button>
    </span>
    <select id="phosphor" onchange="setTheme(this.value)">
      <option value="green">P1 Green Phosphor</option>
      <option value="amber">P3 Amber Phosphor</option>
      <option value="white">P4 White Phosphor</option>
    </select>
    <button onclick="sendKey('\\r')">RETURN</button>
    <button onclick="sendKey('\\x03')">CTRL+C</button>
    <button onclick="sendKey('\\x1a')">CTRL+Z</button>
    <button onclick="clearScreen()">CLEAR</button>
    <button onclick="newSession()">NEW SESSION</button>
    <button onclick="window.location.href='/signup'" style="border-color:#ffb000;color:#ffb000;font-weight:bold;">SIGN UP ($10/MO)</button>
    <button id="btn-sys-admin" onclick="openSystemAdmin()" style="display:none;border-color:#33ff66;color:#33ff66;font-weight:bold;">SYSTEM ADMIN</button>
  </div>
</header>
<div id="workspace">
  <div id="term-wrap" onclick="focusTerm()">
    <span id="screen"></span><span class="cursor"></span>
    <input id="hidden-input" type="text" autocomplete="off" autocapitalize="off" spellcheck="false" />
  </div>
  <div id="x11-pane">
    <div id="x11-toolbar">
      <div>
        <strong>DECwindows OSF/Motif 1.1 (WSA0: :99.0)</strong>
        <span id="x11-auth-badge" style="margin-left:8px; color:#ffb000;">[LOCKED - LOGIN REQUIRED]</span>
        <span id="x11-win-status" style="margin-left:6px; color:#b8d0e8;">[0 Windows]</span>
      </div>
      <div style="display:flex; gap:6px; align-items:center;">
        <select id="x11-app-picker" disabled>
          <option value="decwx11">Session Manager (DECW$SESSION)</option>
          <option value="clock">Clock (DECW$CLOCK)</option>
          <option value="calculator">Calculator (DECW$CALC)</option>
          <option value="calendar">Calendar (DECW$CALENDAR)</option>
          <option value="cardfiler">Cardfiler (DECW$CARDFILER)</option>
          <option value="notepad">Notepad (DECW$NOTEPAD)</option>
          <option value="fileview">FileView (VUE$MASTER)</option>
          <option value="dxmail">Mail (DECW$MAIL)</option>
          <option value="bookreader">Bookreader (DECW$BOOKREADER)</option>
          <option value="cdaviewer">CDA Viewer (DECW$CDAVIEWER)</option>
          <option value="decsound">DECsound (DECW$SOUND)</option>
          <option value="decterm">DECterm (DECW$DECTERM)</option>
        </select>
        <button id="btn-open-app" onclick="launchSelectedX11App()" disabled>OPEN APP</button>
        <button id="btn-esc-win" onclick="sendX11Key('Escape')" disabled title="Send Escape to close active Motif window">ESC (CLOSE WIN)</button>
        <button id="btn-close-all" onclick="closeAllX11()" disabled title="Close all open X11 windows">CLOSE ALL</button>
        <button id="btn-x11-logout" onclick="logoutX11()" disabled title="End DECwindows Session & Log Out">LOGOUT</button>
      </div>
    </div>
    <div id="x11-viewport" onclick="focusX11()">
      <canvas id="x11-canvas" width="1024" height="720" tabindex="0"></canvas>
      <div id="decw-login-overlay">
        <div class="motif-dialog" onclick="event.stopPropagation()">
          <div class="motif-titlebar">
            <span>[=] DECwindows Start Session (DECW$STARTLOGIN)</span>
            <span>VAX01::WSA0:</span>
          </div>
          <div class="motif-body">
            <div class="motif-banner">Digital Equipment Corporation — VAX/VMS V5.5-2</div>
            <div class="motif-sub">Enter your VAX/VMS SYSUAF Username and Password (or log in at the VT220 prompt) to unlock DECwindows X11 applications.</div>
            <div class="motif-field">
              <label for="decw-user">Username:</label>
              <input id="decw-user" type="text" autocomplete="off" spellcheck="false" onkeydown="onLoginKey(event)" />
            </div>
            <div class="motif-field">
              <label for="decw-pass">Password:</label>
              <input id="decw-pass" type="password" autocomplete="off" onkeydown="onLoginKey(event)" />
            </div>
            <div id="decw-login-err" class="motif-error"></div>
            <div class="motif-actions">
              <button class="motif-btn" onclick="submitDecwLogin()">OK</button>
              <button class="motif-btn" onclick="clearDecwLogin()">Clear</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
  const ENABLE_X11 = __ENABLE_X11_JS__;
  const screenEl = document.getElementById('screen');
  const wrapEl = document.getElementById('term-wrap');
  const statusEl = document.getElementById('status');
  const inputEl = document.getElementById('hidden-input');
  const x11PaneEl = document.getElementById('x11-pane');
  const canvasEl = document.getElementById('x11-canvas');
  const x11WinStatusEl = document.getElementById('x11-win-status');
  const x11AuthBadgeEl = document.getElementById('x11-auth-badge');
  const loginOverlayEl = document.getElementById('decw-login-overlay');
  const decwUserEl = document.getElementById('decw-user');
  const decwPassEl = document.getElementById('decw-pass');
  const decwErrEl = document.getElementById('decw-login-err');
  const sysAdminBtnEl = document.getElementById('btn-sys-admin');
  const ctx = canvasEl.getContext('2d');

  let sessionId = sessionStorage.getItem('lcs_terminal_sid') || (Math.random().toString(36).slice(2) + Date.now().toString(36));
  sessionStorage.setItem('lcs_terminal_sid', sessionId);
  let ws = null;
  let wsX11 = null;
  let textBuf = "";
  let activeFocus = "vt"; // "vt" or "x11"
  let viewMode = "vt";    // "vt", "split", or "x11"
  let x11Authenticated = false;
  let x11User = "";
  let lastWinCount = 0;
  let mouseDownOnX11 = false;
  let lastMoveSent = 0;
  let authPollTimer = null;

  function updateSysAdminMenu(isSystemLoggedIn, token) {
    if (!sysAdminBtnEl) return;
    if (isSystemLoggedIn) {
      sysAdminBtnEl.style.display = 'inline-block';
      if (token) {
        sessionStorage.setItem('lcs_admin_token', token);
      }
    } else {
      sysAdminBtnEl.style.display = 'none';
      sessionStorage.removeItem('lcs_admin_token');
    }
  }

  function syncTerminalSystemAuth() {
    fetch('/api/v1/admin/session?sid=' + encodeURIComponent(sessionId))
      .then(function(r) { return r.json(); })
      .then(function(d) {
        updateSysAdminMenu(Boolean(d && d.authenticated), d ? d.admin_token : '');
      })
      .catch(function() {});
  }

  function scheduleAuthCheck() {
    if (authPollTimer) clearTimeout(authPollTimer);
    authPollTimer = setTimeout(syncTerminalSystemAuth, 200);
  }

  function openSystemAdmin() {
    window.location.href = '/admin?sid=' + encodeURIComponent(sessionId);
  }

  function setTheme(t) {
    document.body.className = (t === 'green') ? '' : t;
    focusTerm();
  }

  function focusTerm() {
    activeFocus = "vt";
    canvasEl.classList.remove('focused');
    inputEl.focus();
  }

  function focusX11() {
    if (!x11Authenticated) {
      decwUserEl.focus();
      return;
    }
    activeFocus = "x11";
    canvasEl.classList.add('focused');
    canvasEl.focus();
  }

  function updateX11AuthUI(authenticated, username) {
    x11Authenticated = !!authenticated;
    x11User = username || "";
    const appPicker = document.getElementById('x11-app-picker');
    const btnOpen = document.getElementById('btn-open-app');
    const btnEsc = document.getElementById('btn-esc-win');
    const btnCloseAll = document.getElementById('btn-close-all');
    const btnLogout = document.getElementById('btn-x11-logout');

    appPicker.disabled = !x11Authenticated;
    btnOpen.disabled = !x11Authenticated;
    btnEsc.disabled = !x11Authenticated;
    btnCloseAll.disabled = !x11Authenticated;
    btnLogout.disabled = !x11Authenticated;

    if (x11Authenticated) {
      loginOverlayEl.style.display = 'none';
      x11AuthBadgeEl.style.color = '#33ff66';
      x11AuthBadgeEl.textContent = '[User: ' + x11User + ']';
      decwErrEl.textContent = '';
      scheduleAuthCheck();
    } else {
      loginOverlayEl.style.display = 'flex';
      x11AuthBadgeEl.style.color = '#ffb000';
      x11AuthBadgeEl.textContent = '[LOCKED - LOGIN REQUIRED]';
      drawStandbyX11Banner();
      updateSysAdminMenu(false, '');
    }
  }

  function setViewMode(mode) {
    viewMode = mode;
    document.getElementById('mode-vt').classList.toggle('active-mode', mode === 'vt');
    document.getElementById('mode-split').classList.toggle('active-mode', mode === 'split');
    document.getElementById('mode-x11').classList.toggle('active-mode', mode === 'x11');

    if (mode === 'vt') {
      wrapEl.style.display = 'block';
      x11PaneEl.style.display = 'none';
      focusTerm();
    } else if (mode === 'split') {
      wrapEl.style.display = 'block';
      x11PaneEl.style.display = 'flex';
    } else if (mode === 'x11') {
      wrapEl.style.display = 'none';
      x11PaneEl.style.display = 'flex';
      focusX11();
    }
  }

  function clearScreen() {
    textBuf = "";
    screenEl.textContent = "";
    focusTerm();
  }

  function appendOutput(raw) {
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

  function newSession() {
    sessionId = Math.random().toString(36).slice(2) + Date.now().toString(36);
    sessionStorage.setItem('lcs_terminal_sid', sessionId);
    updateSysAdminMenu(false, '');
    updateX11AuthUI(false, "");
    connectWS();
    connectX11WS();
  }

  function connectWS() {
    if (ws) {
      try { ws.close(); } catch (e) {}
    }
    const proto = (location.protocol === 'https:') ? 'wss:' : 'ws:';
    ws = new WebSocket(proto + '//' + location.host + '/ws?sid=' + encodeURIComponent(sessionId));
    statusEl.textContent = 'CONNECTING...';

    ws.onopen = function() {
      statusEl.textContent = ENABLE_X11 ? 'ONLINE (VT220 + X11)' : 'ONLINE (WSS PTY)';
      scheduleAuthCheck();
      focusTerm();
    };
    ws.onmessage = function(ev) {
      appendOutput(typeof ev.data === 'string' ? ev.data : '');
      scheduleAuthCheck();
    };
    ws.onclose = function() {
      statusEl.textContent = 'DISCONNECTED';
      updateSysAdminMenu(false, '');
      updateX11AuthUI(false, "");
      appendOutput('\\n[Terminal carrier dropped - click NEW SESSION to reconnect]\\n');
    };
    ws.onerror = function() {
      statusEl.textContent = 'LINK ERROR';
    };
  }

  setInterval(syncTerminalSystemAuth, 1500);

  /* ================= DECwindows X11 Canvas Client ================= */
  function drawStandbyX11Banner() {
    ctx.fillStyle = '#3b5368';
    ctx.fillRect(0, 0, canvasEl.width, canvasEl.height);
    ctx.strokeStyle = '#7c9ab8';
    ctx.lineWidth = 2;
    ctx.strokeRect(20, 20, canvasEl.width - 40, canvasEl.height - 40);
    ctx.fillStyle = '#e8eef2';
    ctx.font = 'bold 18px "DejaVu Sans Mono", monospace';
    ctx.fillText('DECwindows XUI / OSF/Motif 1.1 Workstation Server (WSA0: :99.0)', 60, 80);
    ctx.font = '14px "DejaVu Sans Mono", monospace';
    ctx.fillStyle = '#c5d8eb';
    ctx.fillText('Run any DECwindows application from DCL (e.g. $ DECWINDOWS, $ CLOCK, $ CALCULATOR)', 60, 115);
    ctx.fillText('or click "OPEN APP" / "LAUNCH DECWINDOWS" in the toolbar above.', 60, 140);
  }

  function connectX11WS() {
    if (!ENABLE_X11) return;
    if (wsX11) {
      try { wsX11.close(); } catch (e) {}
    }
    drawStandbyX11Banner();
    const proto = (location.protocol === 'https:') ? 'wss:' : 'ws:';
    wsX11 = new WebSocket(proto + '//' + location.host + '/ws-x11?sid=' + encodeURIComponent(sessionId));
    wsX11.binaryType = 'blob';

    wsX11.onmessage = function(ev) {
      if (typeof ev.data === 'string') {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === 'auth') {
            updateX11AuthUI(msg.authenticated, msg.user);
          } else if (msg.type === 'auth_error') {
            decwErrEl.textContent = msg.error || '%LOGIN-F-NOTVALID, user authorization failure';
            decwPassEl.value = '';
            decwPassEl.focus();
          } else if (msg.type === 'windows') {
            x11WinStatusEl.textContent = '[' + msg.count + (msg.count === 1 ? ' Window]' : ' Windows]');
            if (msg.count > 0 && lastWinCount === 0 && viewMode === 'vt' && x11Authenticated) {
              setViewMode('split');
              focusX11();
            }
            if (msg.count === 0 && lastWinCount > 0) {
              drawStandbyX11Banner();
            }
            lastWinCount = msg.count;
          }
        } catch (e) {}
      } else if (ev.data instanceof Blob && x11Authenticated) {
        const url = URL.createObjectURL(ev.data);
        const img = new Image();
        img.onload = function() {
          if (x11Authenticated) {
            ctx.drawImage(img, 0, 0);
          }
          URL.revokeObjectURL(url);
        };
        img.src = url;
      }
    };
    wsX11.onclose = function() {
      setTimeout(connectX11WS, 2000);
    };
  }

  function onLoginKey(e) {
    e.stopPropagation();
    if (e.key === 'Enter') {
      e.preventDefault();
      submitDecwLogin();
    }
  }

  function submitDecwLogin() {
    const u = (decwUserEl.value || '').trim();
    const p = decwPassEl.value || '';
    if (!u) {
      decwErrEl.textContent = '%LOGIN-F-NOSUCHUSER, enter a valid VAX/VMS Username';
      decwUserEl.focus();
      return;
    }
    if (wsX11 && wsX11.readyState === WebSocket.OPEN) {
      wsX11.send(JSON.stringify({
        type: 'login',
        username: u,
        password: p
      }));
      decwPassEl.value = '';
    }
  }

  function clearDecwLogin() {
    decwUserEl.value = '';
    decwPassEl.value = '';
    decwErrEl.textContent = '';
    decwUserEl.focus();
  }

  function logoutX11() {
    if (wsX11 && wsX11.readyState === WebSocket.OPEN) {
      wsX11.send(JSON.stringify({ type: 'logout' }));
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('\\x03\\nLOGOUT\\n');
    }
  }

  function getCanvasCoords(e) {
    const rect = canvasEl.getBoundingClientRect();
    const x = Math.round((e.clientX - rect.left) * (canvasEl.width / Math.max(1, rect.width)));
    const y = Math.round((e.clientY - rect.top) * (canvasEl.height / Math.max(1, rect.height)));
    return {
      x: Math.max(0, Math.min(canvasEl.width - 1, x)),
      y: Math.max(0, Math.min(canvasEl.height - 1, y))
    };
  }

  function mapMouseButton(b) {
    if (b === 2) return 3;
    if (b === 1) return 2;
    return 1;
  }

  canvasEl.addEventListener('contextmenu', function(e) {
    e.preventDefault();
  });

  canvasEl.addEventListener('mousedown', function(e) {
    e.preventDefault();
    if (!x11Authenticated) {
      decwUserEl.focus();
      return;
    }
    focusX11();
    mouseDownOnX11 = true;
    if (!wsX11 || wsX11.readyState !== WebSocket.OPEN) return;
    const pt = getCanvasCoords(e);
    wsX11.send(JSON.stringify({
      type: 'mousedown',
      x: pt.x,
      y: pt.y,
      button: mapMouseButton(e.button)
    }));
  });

  window.addEventListener('mousemove', function(e) {
    if (!x11Authenticated || !wsX11 || wsX11.readyState !== WebSocket.OPEN) return;
    if (viewMode === 'vt') return;
    const now = performance.now();
    if (!mouseDownOnX11 && (now - lastMoveSent < 45)) return;
    lastMoveSent = now;
    const pt = getCanvasCoords(e);
    wsX11.send(JSON.stringify({
      type: 'mousemove',
      x: pt.x,
      y: pt.y
    }));
  });

  window.addEventListener('mouseup', function(e) {
    if (!mouseDownOnX11) return;
    mouseDownOnX11 = false;
    if (!x11Authenticated || !wsX11 || wsX11.readyState !== WebSocket.OPEN) return;
    const pt = getCanvasCoords(e);
    wsX11.send(JSON.stringify({
      type: 'mouseup',
      x: pt.x,
      y: pt.y,
      button: mapMouseButton(e.button)
    }));
  });

  function sendX11Key(keyName, ctrl, shift) {
    if (!x11Authenticated) return;
    if (wsX11 && wsX11.readyState === WebSocket.OPEN) {
      wsX11.send(JSON.stringify({
        type: 'keydown',
        key: keyName,
        ctrl: !!ctrl,
        shift: !!shift
      }));
    }
  }

  function launchX11App(appName) {
    if (viewMode === 'vt') {
      setViewMode('split');
    }
    if (!x11Authenticated) {
      decwErrEl.textContent = '%DECW-W-AUTHREQ, please log in to start DECwindows applications';
      decwUserEl.focus();
      return;
    }
    focusX11();
    if (wsX11 && wsX11.readyState === WebSocket.OPEN) {
      wsX11.send(JSON.stringify({
        type: 'launch',
        app: appName
      }));
    }
  }

  function launchSelectedX11App() {
    const sel = document.getElementById('x11-app-picker');
    if (sel && sel.value) {
      launchX11App(sel.value);
    }
  }

  function closeAllX11() {
    if (!x11Authenticated) return;
    if (wsX11 && wsX11.readyState === WebSocket.OPEN) {
      wsX11.send(JSON.stringify({ type: 'close_all' }));
    }
  }

  window.addEventListener('keydown', function(e) {
    const tag = document.activeElement ? document.activeElement.tagName : '';
    if (tag === 'SELECT' || (tag === 'INPUT' && document.activeElement.id !== 'hidden-input')) {
      return;
    }

    if (ENABLE_X11 && activeFocus === 'x11' && viewMode !== 'vt') {
      if (!x11Authenticated) return;
      e.preventDefault();
      sendX11Key(e.key, e.ctrlKey, e.shiftKey);
      return;
    }

    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    if (e.ctrlKey && !e.altKey && !e.metaKey) {
      const k = e.key.toUpperCase();
      if (k === 'C') {
        if (window.getSelection().toString()) return;
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
    const tag = document.activeElement ? document.activeElement.tagName : '';
    if (tag === 'INPUT' && document.activeElement.id !== 'hidden-input') return;
    if (activeFocus === 'x11') return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const txt = (e.clipboardData || window.clipboardData).getData('text');
    if (txt) {
      e.preventDefault();
      ws.send(txt);
      appendOutput(txt);
    }
  });

  connectWS();
  connectX11WS();
</script>
</body>
</html>
"""

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _png_chunk(chunk_type, data):
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack("!I", len(data)) + chunk_type + data + struct.pack("!I", crc)


def encode_bgra_to_png(raw_bgra, width, height):
    """Fast pure-Python BGRA (X11 ZPixmap 32bpp) to RGBA PNG encoder."""
    buf = bytearray(raw_bgra)
    mv = memoryview(buf)
    b_chan = bytes(mv[0::4])
    mv[0::4] = mv[2::4]
    mv[2::4] = b_chan
    mv[3::4] = b"\xff" * (width * height)

    stride = width * 4
    scanlines = b"".join(
        b"\x00" + mv[y * stride : (y + 1) * stride].tobytes() for y in range(height)
    )
    compressed = zlib.compress(scanlines, 1)

    ihdr = struct.pack("!IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", compressed)
        + _png_chunk(b"IEND", b"")
    )


class X11DisplayBridge:
    """Interfaces with Xvfb :99 via ctypes (libX11.so.6 + libXtst.so.6)."""

    ALLOWED_APPS = {
        "decwx11",
        "dxsession",
        "decwindows",
        "decterm",
        "bookreader",
        "calendar",
        "cardfiler",
        "cdaviewer",
        "calculator",
        "clock",
        "decsound",
        "dxmail",
        "fileview",
        "notepad",
    }

    KEY_MAP = {
        "Enter": ("Return", False),
        "Backspace": ("BackSpace", False),
        "Tab": ("Tab", False),
        "Escape": ("Escape", False),
        "Delete": ("Delete", False),
        "ArrowUp": ("Up", False),
        "ArrowDown": ("Down", False),
        "ArrowLeft": ("Left", False),
        "ArrowRight": ("Right", False),
        "PageUp": ("Prior", False),
        "PageDown": ("Next", False),
        "Home": ("Home", False),
        "End": ("End", False),
        "F1": ("F1", False),
        "F2": ("F2", False),
        "F3": ("F3", False),
        "F4": ("F4", False),
        "F5": ("F5", False),
        "F6": ("F6", False),
        "F7": ("F7", False),
        "F8": ("F8", False),
        "F9": ("F9", False),
        "F10": ("F10", False),
        "F11": ("F11", False),
        "F12": ("F12", False),
        " ": ("space", False),
        "!": ("exclam", True),
        "@": ("at", True),
        "#": ("numbersign", True),
        "$": ("dollar", True),
        "%": ("percent", True),
        "^": ("asciicircum", True),
        "&": ("ampersand", True),
        "*": ("asterisk", True),
        "(": ("parenleft", True),
        ")": ("parenright", True),
        "-": ("minus", False),
        "_": ("underscore", True),
        "=": ("equal", False),
        "+": ("plus", True),
        "[": ("bracketleft", False),
        "{": ("braceleft", True),
        "]": ("bracketright", False),
        "}": ("braceright", True),
        "\\": ("backslash", False),
        "|": ("bar", True),
        ";": ("semicolon", False),
        ":": ("colon", True),
        "'": ("apostrophe", False),
        '"': ("quotedbl", True),
        ",": ("comma", False),
        "<": ("less", True),
        ".": ("period", False),
        ">": ("greater", True),
        "/": ("slash", False),
        "?": ("question", True),
        "`": ("grave", False),
        "~": ("asciitilde", True),
    }

    def __init__(self, display_name=":99", width=1024, height=720, sys_bin="/opt/dec-vms/system/bin"):
        self.display_name = display_name
        self.width = width
        self.height = height
        self.sys_bin = sys_bin
        self.sys_lib = os.path.abspath(os.path.join(sys_bin, "..", "lib"))
        self.dpy = None
        self.root = 0
        self._drag_state = None
        self._x11 = None
        self._xtst = None
        self._err_cb = None
        self._init_xlib()

    def _init_xlib(self):
        try:
            self._x11 = ctypes.CDLL("libX11.so.6")
            self._xtst = ctypes.CDLL("libXtst.so.6")

            ERR_HANDLER = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
            self._err_cb = ERR_HANDLER(lambda dpy, err: 0)
            self._x11.XSetErrorHandler.argtypes = [ERR_HANDLER]
            self._x11.XSetErrorHandler.restype = ctypes.c_void_p
            self._x11.XSetErrorHandler(self._err_cb)

            self._x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
            self._x11.XOpenDisplay.restype = ctypes.c_void_p

            self._x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
            self._x11.XDefaultRootWindow.restype = ctypes.c_ulong

            self._x11.XSetWindowBackground.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong]
            self._x11.XClearWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            self._x11.XFlush.argtypes = [ctypes.c_void_p]

            self._x11.XGetImage.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_uint,
                ctypes.c_uint,
                ctypes.c_ulong,
                ctypes.c_int,
            ]
            self._x11.XGetImage.restype = ctypes.c_void_p

            self._x11.XDestroyImage.argtypes = [ctypes.c_void_p]
            self._x11.XDestroyImage.restype = ctypes.c_int

            self._x11.XQueryTree.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.POINTER(ctypes.c_ulong),
                ctypes.POINTER(ctypes.c_ulong),
                ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)),
                ctypes.POINTER(ctypes.c_uint),
            ]
            self._x11.XQueryTree.restype = ctypes.c_int

            self._x11.XGetWindowAttributes.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.c_void_p,
            ]
            self._x11.XGetWindowAttributes.restype = ctypes.c_int

            self._x11.XFree.argtypes = [ctypes.c_void_p]
            self._x11.XRaiseWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            self._x11.XMoveWindow.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.c_int,
                ctypes.c_int,
            ]
            self._x11.XSetInputFocus.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.c_int,
                ctypes.c_ulong,
            ]
            self._x11.XDestroyWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

            self._x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
            self._x11.XStringToKeysym.restype = ctypes.c_ulong
            self._x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            self._x11.XKeysymToKeycode.restype = ctypes.c_ubyte

            self._xtst.XTestFakeMotionEvent.argtypes = [
                ctypes.c_void_p,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_ulong,
            ]
            self._xtst.XTestFakeButtonEvent.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.c_ulong,
            ]
            self._xtst.XTestFakeKeyEvent.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint,
                ctypes.c_int,
                ctypes.c_ulong,
            ]
        except Exception:
            self._x11 = None

    def ensure_connected(self):
        if not self._x11:
            return False
        if self.dpy:
            return True
        self.dpy = self._x11.XOpenDisplay(self.display_name.encode("ascii"))
        if not self.dpy:
            return False
        self.root = self._x11.XDefaultRootWindow(self.dpy)
        self._x11.XSetWindowBackground(self.dpy, self.root, 0x3B5368)
        self._x11.XClearWindow(self.dpy, self.root)
        self._x11.XFlush(self.dpy)
        return True

    def get_mapped_windows(self):
        if not self.ensure_connected():
            return []
        root_ret = ctypes.c_ulong()
        parent_ret = ctypes.c_ulong()
        children_ptr = ctypes.POINTER(ctypes.c_ulong)()
        nchildren = ctypes.c_uint()
        ok = self._x11.XQueryTree(
            self.dpy,
            self.root,
            ctypes.byref(root_ret),
            ctypes.byref(parent_ret),
            ctypes.byref(children_ptr),
            ctypes.byref(nchildren),
        )
        if not ok or nchildren.value == 0 or not children_ptr:
            return []
        result = []
        attr_buf = ctypes.create_string_buffer(160)
        try:
            for i in range(nchildren.value):
                win_id = children_ptr[i]
                if self._x11.XGetWindowAttributes(self.dpy, win_id, attr_buf) != 0:
                    x, y, w, h = struct.unpack_from("=iiii", attr_buf.raw, 0)
                    map_state = struct.unpack_from("=i", attr_buf.raw, 92)[0]
                    if map_state == 2 and w >= 50 and h >= 50:
                        result.append((win_id, x, y, w, h))
        finally:
            self._x11.XFree(children_ptr)
        return result

    def capture_raw_bgra(self):
        if not self.ensure_connected():
            return None
        img_ptr = self._x11.XGetImage(
            self.dpy,
            self.root,
            0,
            0,
            self.width,
            self.height,
            0xFFFFFFFFFFFFFFFF,
            2,
        )
        if not img_ptr:
            return None
        try:
            data_ptr = ctypes.c_void_p.from_address(img_ptr + 16).value
            bytes_per_line = ctypes.c_int.from_address(img_ptr + 44).value
            if not data_ptr or bytes_per_line <= 0:
                return None
            raw = ctypes.string_at(data_ptr, bytes_per_line * self.height)
            return raw
        finally:
            self._x11.XDestroyImage(img_ptr)

    def inject_mouse(self, ev_type, x, y, button=1):
        if not self.ensure_connected() or not self._xtst:
            return
        x = max(0, min(self.width - 1, int(x)))
        y = max(0, min(self.height - 1, int(y)))
        button = int(button) if button in (1, 2, 3) else 1

        if ev_type == "mousedown":
            wins = self.get_mapped_windows()
            for win_id, wx, wy, ww, wh in reversed(wins):
                if wx <= x < wx + ww and wy <= y < wy + wh:
                    self._x11.XRaiseWindow(self.dpy, win_id)
                    self._x11.XSetInputFocus(self.dpy, win_id, 1, 0)
                    rel_x = x - wx
                    rel_y = y - wy
                    if button == 1 and 42 <= rel_x <= ww - 75 and 4 <= rel_y <= 34:
                        self._drag_state = (win_id, rel_x, rel_y)
                        self._x11.XFlush(self.dpy)
                        return
                    break
            self._xtst.XTestFakeMotionEvent(self.dpy, -1, x, y, 0)
            self._xtst.XTestFakeButtonEvent(self.dpy, button, 1, 0)
            self._x11.XFlush(self.dpy)

        elif ev_type == "mousemove":
            if self._drag_state:
                win_id, off_x, off_y = self._drag_state
                nx = max(0, min(self.width - 80, x - off_x))
                ny = max(0, min(self.height - 40, y - off_y))
                self._x11.XMoveWindow(self.dpy, win_id, nx, ny)
                self._x11.XFlush(self.dpy)
                return
            self._xtst.XTestFakeMotionEvent(self.dpy, -1, x, y, 0)
            self._x11.XFlush(self.dpy)

        elif ev_type == "mouseup":
            if self._drag_state:
                self._drag_state = None
                return
            self._xtst.XTestFakeMotionEvent(self.dpy, -1, x, y, 0)
            self._xtst.XTestFakeButtonEvent(self.dpy, button, 0, 0)
            self._x11.XFlush(self.dpy)

    def inject_key(self, key_str, ctrl=False, shift=False):
        if not self.ensure_connected() or not self._xtst or not key_str:
            return
        wins = self.get_mapped_windows()
        if wins:
            top_win = wins[-1][0]
            self._x11.XSetInputFocus(self.dpy, top_win, 1, 0)

        need_shift = bool(shift)
        if key_str in self.KEY_MAP:
            ks_name, sym_shift = self.KEY_MAP[key_str]
            need_shift = need_shift or sym_shift
        elif len(key_str) == 1 and key_str.isalpha():
            ks_name = key_str
            if key_str.isupper():
                need_shift = True
        elif len(key_str) == 1 and key_str.isdigit():
            ks_name = key_str
        else:
            return

        ks = self._x11.XStringToKeysym(ks_name.encode("ascii"))
        if not ks:
            return
        kc = self._x11.XKeysymToKeycode(self.dpy, ks)
        if not kc:
            return

        ctrl_kc = self._x11.XKeysymToKeycode(self.dpy, self._x11.XStringToKeysym(b"Control_L"))
        shift_kc = self._x11.XKeysymToKeycode(self.dpy, self._x11.XStringToKeysym(b"Shift_L"))

        if ctrl and ctrl_kc:
            self._xtst.XTestFakeKeyEvent(self.dpy, ctrl_kc, 1, 0)
        if need_shift and shift_kc:
            self._xtst.XTestFakeKeyEvent(self.dpy, shift_kc, 1, 0)

        self._xtst.XTestFakeKeyEvent(self.dpy, kc, 1, 0)
        self._xtst.XTestFakeKeyEvent(self.dpy, kc, 0, 0)

        if need_shift and shift_kc:
            self._xtst.XTestFakeKeyEvent(self.dpy, shift_kc, 0, 0)
        if ctrl and ctrl_kc:
            self._xtst.XTestFakeKeyEvent(self.dpy, ctrl_kc, 0, 0)

        self._x11.XFlush(self.dpy)

    def launch_app(self, app_name):
        clean = str(app_name).strip().lower()
        if clean not in self.ALLOWED_APPS:
            return
        exe = os.path.join(self.sys_bin, clean)
        if not os.path.isfile(exe):
            return
        env = os.environ.copy()
        env["DISPLAY"] = self.display_name
        env["DECW_FORCE_X11"] = "1"
        env["DECW_FONT_SIZE"] = "1"
        env["PATH"] = f"{self.sys_bin}:{env.get('PATH', '')}"
        env["LD_LIBRARY_PATH"] = f"{self.sys_lib}:{env.get('LD_LIBRARY_PATH', '')}"
        subprocess.Popen(
            [exe, "--x11"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def close_all_windows(self):
        if not self.ensure_connected():
            return
        for win_id, _, _, _, _ in self.get_mapped_windows():
            self._x11.XDestroyWindow(self.dpy, win_id)
        self._x11.XClearWindow(self.dpy, self.root)
        self._x11.XFlush(self.dpy)


def _can_open_x11_display(display=":99"):
    try:
        x11 = ctypes.CDLL("libX11.so.6")
        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XOpenDisplay.restype = ctypes.c_void_p
        x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
        dpy = x11.XOpenDisplay(display.encode("ascii"))
        if dpy:
            x11.XCloseDisplay(dpy)
            return True
    except Exception:
        pass
    return False


def ensure_xvfb_display(display=":99", width=1024, height=720):
    if _can_open_x11_display(display):
        return True
    disp_num = display.lstrip(":").split(".")[0]
    for stale in (f"/tmp/.X{disp_num}-lock", f"/tmp/.X11-unix/X{disp_num}"):
        try:
            if os.path.exists(stale):
                os.unlink(stale)
        except OSError:
            pass
    try:
        subprocess.Popen(
            [
                "Xvfb",
                display,
                "-screen",
                "0",
                f"{width}x{height}x24",
                "-ac",
                "-nolisten",
                "tcp",
                "-noreset",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        for _ in range(30):
            if _can_open_x11_display(display):
                return True
            time.sleep(0.1)
    except Exception:
        pass
    return _can_open_x11_display(display)


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
    DEFAULT_SYSUAF = {
        "SYSTEM": {"username": "SYSTEM", "uic": "[1,4]", "password": "MANAGER", "flags": "NODISUSER"},
        "DECW": {"username": "DECW", "uic": "[100,1]", "password": "MOTIF", "flags": "NODISUSER"},
        "GUEST": {"username": "GUEST", "uic": "[200,200]", "password": "", "flags": "NODISUSER"},
    }

    def __init__(
        self,
        emu_cmd,
        os_title,
        header_title,
        https_port,
        enable_x11=False,
        cert_dir="/tmp/dec_tls",
    ):
        self.emu_cmd = emu_cmd
        self.os_title = os_title
        self.header_title = header_title
        self.https_port = int(https_port)
        self.enable_x11 = bool(enable_x11)
        self.cert_path, self.key_path = ensure_tls_cert(cert_dir)
        self.os_dir = os.path.abspath(os.path.join(os.path.dirname(emu_cmd[0]), ".."))
        self.fs_root = os.environ.get("VMS_FS_ROOT", os.path.join(self.os_dir, "fs"))
        self.sessions_path = os.path.join(self.fs_root, ".vms_sessions.json")
        self.sysuaf_path = os.path.join(self.fs_root, "dka0", "sys0", "syscommon", "sysexe", "SYSUAF.JSON")
        self.provisioning = lcs_provisioning.LCSProvisioningEngine(
            primary_os="VMS",
            os_dir=self.os_dir,
            fs_root=self.fs_root,
            https_port=self.https_port,
        )
        self.provisioning.terminal_server = self

        # Track per-browser-tab session ID -> (proc, master_fd) and authenticated username
        self.sid_procs = {}
        self.sid_auth_users = {}
        self.sid_prev_pty_logged = {}

        self.x11_bridge = None
        if self.enable_x11:
            ensure_xvfb_display(":99", 1024, 720)
            sys_bin = os.path.join(self.os_dir, "system", "bin")
            self.x11_bridge = X11DisplayBridge(display_name=":99", width=1024, height=720, sys_bin=sys_bin)

        self.html_bytes = (
            HTML_TEMPLATE.replace("__TITLE__", os_title)
            .replace("__HEADER_TITLE__", header_title)
            .replace("__X11_CTRL_DISPLAY__", "inline-flex" if self.enable_x11 else "none")
            .replace("__ENABLE_X11_JS__", "true" if self.enable_x11 else "false")
            .encode("utf-8")
        )

    def _load_sysuaf(self):
        users = {k: dict(v) for k, v in self.DEFAULT_SYSUAF.items()}
        if os.path.isfile(self.sysuaf_path):
            try:
                with open(self.sysuaf_path, "r") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, dict) and "username" in v:
                            users[k.upper()] = v
            except Exception:
                pass
        return users

    def verify_sysuaf_credentials(self, username, password):
        users = self._load_sysuaf()
        s = (username or "").strip().upper()
        if not s:
            return False, None, "%LOGIN-F-NOSUCHUSER, no such user"
        matched_user = None
        if s in users:
            matched_user = s
        else:
            norm_uic = s if s.startswith("[") else f"[{s}]"
            for uname, uinfo in users.items():
                if uinfo.get("uic") == norm_uic:
                    matched_user = uname
                    break
        if not matched_user:
            return False, None, "%LOGIN-F-NOSUCHUSER, no such user"

        uinfo = users[matched_user]
        flags_list = [fl.strip().upper() for fl in uinfo.get("flags", "").split(",") if fl.strip()]
        status_str = str(uinfo.get("status", "ACTIVE")).upper()
        if ("DISUSER" in flags_list and "NODISUSER" not in flags_list) or status_str in ("DISUSER", "SUSPENDED", "DISABLED"):
            return False, None, "%LOGIN-F-DISUSER, account is disabled"

        expected_pw = uinfo.get("password", "")
        given_pw = (password or "").strip()
        if expected_pw:
            if given_pw.upper() != expected_pw.upper():
                return False, None, "%LOGIN-F-NOTVALID, user authorization failure"
        return True, matched_user, ""

    def get_session_auth_user(self, sid):
        """Return authenticated SYSUAF username for sid, syncing with VT220 PTY login state."""
        pty_logged_user = None
        proc_entry = self.sid_procs.get(sid)
        if proc_entry:
            proc, _ = proc_entry
            if proc.poll() is None and os.path.isfile(self.sessions_path):
                try:
                    with open(self.sessions_path, "r") as f:
                        sessions = json.load(f)
                    s_info = sessions.get(str(proc.pid))
                    if isinstance(s_info, dict) and s_info.get("logged_in"):
                        pty_logged_user = s_info.get("username", "SYSTEM")
                except Exception:
                    pass

        was_pty_logged = self.sid_prev_pty_logged.get(sid, False)
        if pty_logged_user:
            self.sid_prev_pty_logged[sid] = True
            self.sid_auth_users[sid] = pty_logged_user
            return pty_logged_user
        else:
            if was_pty_logged:
                # User logged out from VT220 (LOGOUT / BYE) -> revoke X11 auth and close X11 windows
                self.sid_prev_pty_logged[sid] = False
                self.sid_auth_users.pop(sid, None)
                if self.x11_bridge:
                    self.x11_bridge.close_all_windows()
                return None
            return self.sid_auth_users.get(sid)

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
        parsed = urllib.parse.urlsplit(raw_path.replace("#", "%23"))
        path = urllib.parse.unquote(parsed.path)
        qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        sid = (qs.get("sid", ["default"])[0] or "default").strip()

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
            if path.startswith("/ws-x11") and self.enable_x11:
                await self._bridge_websocket_x11(reader, writer, sid)
            else:
                await self._bridge_websocket_pty(reader, writer, sid)
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

    async def _bridge_websocket_x11(self, reader, writer, sid):
        if not self.x11_bridge:
            writer.close()
            return

        async def stream_x11_frames():
            last_raw = None
            last_win_count = -1
            last_auth_state = None
            while True:
                auth_user = self.get_session_auth_user(sid)
                cur_auth = (bool(auth_user), auth_user or "")
                if cur_auth != last_auth_state:
                    last_auth_state = cur_auth
                    last_raw = None
                    last_win_count = -1
                    auth_msg = json.dumps({
                        "type": "auth",
                        "authenticated": bool(auth_user),
                        "user": auth_user or "",
                    }).encode("utf-8")
                    writer.write(encode_ws_frame(auth_msg, opcode=0x01))
                    await writer.drain()

                if auth_user:
                    wins = self.x11_bridge.get_mapped_windows()
                    win_count = len(wins)
                    if win_count != last_win_count:
                        last_win_count = win_count
                        msg = json.dumps({"type": "windows", "count": win_count}).encode("utf-8")
                        writer.write(encode_ws_frame(msg, opcode=0x01))
                        await writer.drain()

                    if win_count > 0:
                        raw = self.x11_bridge.capture_raw_bgra()
                        if raw and raw != last_raw:
                            last_raw = raw
                            png_bytes = encode_bgra_to_png(
                                raw, self.x11_bridge.width, self.x11_bridge.height
                            )
                            writer.write(encode_ws_frame(png_bytes, opcode=0x02))
                            await writer.drain()
                    else:
                        last_raw = None
                    await asyncio.sleep(0.08 if win_count > 0 else 0.2)
                else:
                    await asyncio.sleep(0.2)

        async def handle_x11_input():
            while True:
                opcode, data = await read_ws_frame(reader)
                if opcode == 0x08:
                    break
                if opcode == 0x09:
                    writer.write(encode_ws_frame(data, opcode=0x0A))
                    await writer.drain()
                    continue
                if opcode == 0x01 and data:
                    try:
                        ev = json.loads(data.decode("utf-8", errors="replace"))
                        etype = ev.get("type", "")

                        if etype == "login":
                            ok, uname, err = self.verify_sysuaf_credentials(
                                ev.get("username", ""), ev.get("password", "")
                            )
                            if ok:
                                self.sid_auth_users[sid] = uname
                                # Also log in paired VT220 PTY if it is waiting at Username:
                                proc_entry = self.sid_procs.get(sid)
                                if proc_entry and not self.sid_prev_pty_logged.get(sid, False):
                                    _, m_fd = proc_entry
                                    pw_str = (ev.get("password", "") or "").strip()
                                    try:
                                        os.write(m_fd, f"{uname}\n".encode("utf-8"))
                                        if pw_str:
                                            os.write(m_fd, f"{pw_str}\n".encode("utf-8"))
                                    except OSError:
                                        pass
                                auth_msg = json.dumps({
                                    "type": "auth",
                                    "authenticated": True,
                                    "user": uname,
                                }).encode("utf-8")
                                writer.write(encode_ws_frame(auth_msg, opcode=0x01))
                                await writer.drain()
                                self.x11_bridge.launch_app("decwx11")
                            else:
                                err_msg = json.dumps({
                                    "type": "auth_error",
                                    "error": err,
                                }).encode("utf-8")
                                writer.write(encode_ws_frame(err_msg, opcode=0x01))
                                await writer.drain()
                            continue

                        if etype == "logout":
                            self.sid_auth_users.pop(sid, None)
                            self.sid_prev_pty_logged[sid] = False
                            self.x11_bridge.close_all_windows()
                            auth_msg = json.dumps({
                                "type": "auth",
                                "authenticated": False,
                                "user": "",
                            }).encode("utf-8")
                            writer.write(encode_ws_frame(auth_msg, opcode=0x01))
                            await writer.drain()
                            continue

                        # Block all X11 actions if session is not authenticated
                        if not self.get_session_auth_user(sid):
                            err_msg = json.dumps({
                                "type": "auth_error",
                                "error": "%DECW-F-NOTLOGGEDIN, login required to access DECwindows X11",
                            }).encode("utf-8")
                            writer.write(encode_ws_frame(err_msg, opcode=0x01))
                            await writer.drain()
                            continue

                        if etype in ("mousedown", "mousemove", "mouseup"):
                            self.x11_bridge.inject_mouse(
                                etype,
                                ev.get("x", 0),
                                ev.get("y", 0),
                                ev.get("button", 1),
                            )
                        elif etype == "keydown":
                            self.x11_bridge.inject_key(
                                ev.get("key", ""),
                                ctrl=ev.get("ctrl", False),
                                shift=ev.get("shift", False),
                            )
                        elif etype == "launch":
                            self.x11_bridge.launch_app(ev.get("app", "decwx11"))
                        elif etype == "close_all":
                            self.x11_bridge.close_all_windows()
                    except Exception:
                        pass

        t1 = asyncio.create_task(stream_x11_frames())
        t2 = asyncio.create_task(handle_x11_input())
        try:
            await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
        finally:
            t1.cancel()
            t2.cancel()
            writer.close()

    async def _bridge_websocket_pty(self, reader, writer, sid="default"):
        master_fd, slave_fd = pty.openpty()
        try:
            attrs = termios.tcgetattr(slave_fd)
            attrs[3] = attrs[3] & ~termios.ECHO
            termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)
        except Exception:
            pass

        env = os.environ.copy()
        env["TERM"] = "vt100"
        env["DEC_SESSION_SOURCE"] = "HTTPS"
        if self.enable_x11:
            env["DISPLAY"] = ":99"
            env["DECW_FORCE_X11"] = "1"
            env["DECW_FONT_SIZE"] = "1"

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

        self.sid_procs[sid] = (proc, master_fd)
        self.sid_prev_pty_logged[sid] = False
        self.provisioning.sid_system_auth[sid] = False

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
            was_sys = (str(self.get_session_auth_user(sid) or "").upper() == "SYSTEM")
            self.provisioning.sid_system_auth[sid] = was_sys
            self.sid_procs.pop(sid, None)
            self.sid_auth_users.pop(sid, None)
            self.sid_prev_pty_logged.pop(sid, None)
            if self.x11_bridge and not self.sid_auth_users:
                self.x11_bridge.close_all_windows()
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


def start_background_daemons(emu_bin_path, os_title, header_title, ssh_port, https_port, enable_x11=False):
    """Spawn SSH daemon, Xvfb :99 (if enable_x11), and HTTPS Web Terminal server."""
    configure_and_start_sshd(emu_bin_path, ssh_port)
    if enable_x11:
        ensure_xvfb_display(":99", 1024, 720)

    script_path = os.path.abspath(__file__)
    cmd = [
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
    ]
    if enable_x11:
        cmd.append("--enable-x11")

    subprocess.Popen(
        cmd,
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
    parser.add_argument("--enable-x11", action="store_true", help="Enable DECwindows X11 Canvas WebSocket bridge")
    args = parser.parse_args()

    if args.serve_https:
        srv = MultiUserTerminalServer(
            emu_cmd=[args.emu],
            os_title=args.title,
            header_title=args.header,
            https_port=args.port,
            enable_x11=args.enable_x11,
        )
        asyncio.run(srv.serve_forever())


if __name__ == "__main__":
    main()
