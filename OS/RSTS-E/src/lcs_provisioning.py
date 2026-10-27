#!/usr/bin/env python3
"""
Legacy Computing Systems — Monetization, Clerk Identity & Enterprise WorkOS Provisioning Engine
Shared provisioning, webhook, and signup portal module for:
  - DEC RSTS/E V10.1-L HTTPS Access Point (:8411)
  - DEC VAX/VMS V5.5-2 & DECwindows X11 HTTPS Access Point (:8455)

Supports:
  1. Clerk Auth + Stripe Billing ($10/mo single-OS, $15/mo Dual-System Cluster Pass)
  2. WorkOS Enterprise SAML SSO & SCIM Directory Sync ($199/mo base w/ 15 active seats + $10/mo per additional active seat -> Group [300,*])
  3. Zero-Dependency Local Standalone Mode when cloud API keys are omitted
"""

import hashlib
import hmac
import importlib.util
import json
import os
import re
import secrets
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


DBA_NAME = "Legacy Computing Systems"
TAGLINE = "Authentic DEC Timesharing & Workstation Computing in the Cloud"

PRICING_TIERS = {
    "LCS_RSTS_10": {
        "id": "LCS_RSTS_10",
        "name": "PDP-11 RSTS/E Timesharing",
        "price_monthly": 10,
        "price_display": "$10 / month",
        "target_os": ["RSTS"],
        "quota": 25000,
        "group": 201,
        "description": "PDP-11/70 RSTS/E V10.1-L PPN [201,xxx] + username login, 25,000 blocks, 7 compilers & 33 apps (HTTPS :8411 & SSH :2211)",
    },
    "LCS_VMS_10": {
        "id": "LCS_VMS_10",
        "name": "VAX/VMS & DECwindows Workstation",
        "price_monthly": 10,
        "price_display": "$10 / month",
        "target_os": ["VMS"],
        "quota": 50000,
        "group": 200,
        "description": "VAX/VMS V5.5-2 SYSUAF UIC [200,xxx] + live DECwindows X11/Motif GUI, 50,000 blocks, 18 compilers & 52 apps (HTTPS :8455 & SSH :2255)",
    },
    "LCS_BUNDLE_15": {
        "id": "LCS_BUNDLE_15",
        "name": "DEC Dual-System Cluster Pass",
        "price_monthly": 15,
        "price_display": "$15 / month",
        "target_os": ["RSTS", "VMS"],
        "quota": 100000,
        "group": 201,
        "description": "Matched credentials provisioned simultaneously on both PDP-11 RSTS/E (:8411) and VAX/VMS (:8455) with 100,000 blocks per system",
    },
    "LCS_ENTERPRISE": {
        "id": "LCS_ENTERPRISE",
        "name": "Enterprise / University / Museum Site License",
        "price_monthly": 199,
        "base_price_monthly": 199,
        "included_active_seats": 15,
        "additional_seat_price_monthly": 10,
        "price_display": "$199/mo (15 seats) + $10/seat",
        "target_os": ["RSTS", "VMS"],
        "quota": 100000,
        "group": 300,
        "description": "$199/month base (includes 15 active seats) + $10/month per additional active seat; WorkOS Enterprise SAML SSO & SCIM Directory Sync mapped to Project/UIC Group [300,*]",
    },
}


def load_dotenv_files():
    """Load .env configuration from repository root or OS directory if present."""
    here = os.path.abspath(os.path.dirname(__file__))
    os_dir = os.path.abspath(os.path.join(here, ".."))
    dec_root = os.path.abspath(os.path.join(os_dir, "..", ".."))
    candidates = [
        os.path.join(dec_root, ".env"),
        os.path.join(os_dir, ".env"),
        "/opt/dec-rsts/.env",
        "/opt/dec-vms/.env",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "r") as f:
                    for raw in f:
                        line = raw.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        if line.startswith("export "):
                            line = line[7:].strip()
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass


load_dotenv_files()


SIGNUP_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Legacy Computing Systems — Subscribe & Provision DEC Account (__NODE_LABEL__)</title>
<style>
  :root {
    --fg: #33ff66;
    --fg-dim: #8ce6a3;
    --amber: #ffb000;
    --bg: #070d09;
    --card-bg: #0e1811;
    --border: #265c34;
    --glow: rgba(51, 255, 102, 0.3);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--fg);
    font-family: "DejaVu Sans Mono", "Courier New", monospace;
    min-height: 100vh;
    padding: 24px 16px 48px;
    line-height: 1.45;
  }
  .container {
    max-width: 980px;
    margin: 0 auto;
  }
  header {
    border: 1px solid var(--border);
    background: var(--card-bg);
    padding: 18px 22px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    box-shadow: 0 0 18px rgba(0, 0, 0, 0.65);
  }
  .dba-title {
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 0.8px;
    text-shadow: 0 0 8px var(--glow);
  }
  .dba-sub {
    color: var(--fg-dim);
    font-size: 12px;
    margin-top: 4px;
  }
  .badge-row {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
  }
  .badge {
    border: 1px solid var(--border);
    padding: 4px 10px;
    font-size: 11px;
    border-radius: 3px;
    background: #09120c;
  }
  .badge.amber {
    color: var(--amber);
    border-color: #775200;
  }
  a.btn-link, button {
    background: #112617;
    color: var(--fg);
    border: 1px solid var(--fg);
    padding: 8px 16px;
    font-family: inherit;
    font-size: 13px;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
    border-radius: 3px;
    display: inline-block;
  }
  a.btn-link:hover, button:hover {
    background: var(--fg);
    color: #050a06;
    box-shadow: 0 0 10px var(--glow);
  }
  .plans-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 22px;
  }
  .plan-card {
    border: 1px solid var(--border);
    background: var(--card-bg);
    padding: 14px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.15s ease;
  }
  .plan-card.selected {
    border: 2px solid var(--fg);
    box-shadow: 0 0 12px var(--glow);
    background: #132619;
  }
  .plan-price {
    color: var(--amber);
    font-size: 17px;
    font-weight: bold;
    margin: 4px 0 6px;
  }
  .plan-desc {
    color: var(--fg-dim);
    font-size: 11px;
  }
  .panel {
    border: 1px solid var(--border);
    background: var(--card-bg);
    padding: 20px 24px;
    margin-bottom: 18px;
    border-radius: 4px;
  }
  .panel h2 {
    font-size: 15px;
    margin-bottom: 14px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }
  .form-row {
    display: grid;
    grid-template-columns: 190px 1fr;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    font-size: 13px;
  }
  input, select {
    background: #060b07;
    color: var(--fg);
    border: 1px solid var(--border);
    padding: 8px 10px;
    font-family: inherit;
    font-size: 13px;
    border-radius: 3px;
    width: 100%;
  }
  input:focus, select:focus {
    outline: none;
    border-color: var(--fg);
    box-shadow: 0 0 6px var(--glow);
  }
  .hint {
    font-size: 11px;
    color: var(--fg-dim);
    margin-top: 3px;
  }
  #result-box {
    display: none;
    border: 2px solid var(--fg);
    background: #0d2113;
    padding: 18px 22px;
    margin-top: 16px;
    border-radius: 4px;
    box-shadow: 0 0 16px var(--glow);
  }
  #error-box {
    display: none;
    border: 1px solid #ff4d4d;
    background: #290a0a;
    color: #ff8080;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 12px;
  }
  .cred-table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px;
    font-size: 13px;
  }
  .cred-table td {
    padding: 6px 8px;
    border-bottom: 1px solid var(--border);
  }
  .cred-table td:first-child {
    color: var(--fg-dim);
    width: 210px;
  }
</style>
__CLERK_SCRIPT_TAG__
</head>
<body>
<div class="container">
  <header>
    <div>
      <div class="dba-title">LEGACY COMPUTING SYSTEMS</div>
      <div class="dba-sub">Authentic DEC Timesharing & Workstation Computing in the Cloud — __NODE_LABEL__</div>
    </div>
    <div class="badge-row">
      <span class="badge">Clerk Auth: __CLERK_MODE_LABEL__</span>
      <span class="badge amber">WorkOS Enterprise SSO/SCIM: __WORKOS_MODE_LABEL__</span>
      <a class="btn-link" href="/">RETURN TO TERMINAL</a>
    </div>
  </header>

  <div class="plans-grid">
    <div class="plan-card __SEL_RSTS__" id="card-LCS_RSTS_10" onclick="selectPlan('LCS_RSTS_10')">
      <div><strong>PDP-11 RSTS/E Timesharing</strong></div>
      <div class="plan-price">$10 / month</div>
      <div class="plan-desc">Dedicated PPN <code>[201,xxx]</code> + Username login, 25,000 blocks on <code>DK0:</code>, 7 PDP-11 compilers &amp; 33 apps (HTTPS :8411 &amp; SSH :2211).</div>
    </div>
    <div class="plan-card __SEL_VMS__" id="card-LCS_VMS_10" onclick="selectPlan('LCS_VMS_10')">
      <div><strong>VAX/VMS &amp; DECwindows</strong></div>
      <div class="plan-price">$10 / month</div>
      <div class="plan-desc">Dedicated <code>SYSUAF</code> UIC <code>[200,xxx]</code>, 50,000 blocks on <code>DKA0:</code>, Live DECwindows X11/Motif GUI, 18 compilers &amp; 52 apps (:8455).</div>
    </div>
    <div class="plan-card" id="card-LCS_BUNDLE_15" onclick="selectPlan('LCS_BUNDLE_15')">
      <div><strong>DEC Dual-System Cluster Pass</strong></div>
      <div class="plan-price">$15 / month</div>
      <div class="plan-desc">Simultaneous provisioning on <strong>both</strong> PDP-11 RSTS/E (:8411) and VAX/VMS (:8455) with matched credentials &amp; 100,000 blocks.</div>
    </div>
    <div class="plan-card" id="card-LCS_ENTERPRISE" onclick="selectPlan('LCS_ENTERPRISE')">
      <div><strong>Enterprise / University Site</strong></div>
      <div class="plan-price">$199 / mo + $10 / seat</div>
      <div class="plan-desc">Includes <strong>15 active seats</strong> (+$10/mo per additional active seat). WorkOS SAML 2.0 SSO &amp; SCIM Directory Sync mapped to Group <code>[300,*]</code>.</div>
    </div>
  </div>

  <div class="panel">
    <h2>1. Subscriber Identity &amp; DEC Terminal Credentials</h2>
    <div id="clerk-mount" style="margin-bottom:12px;"></div>
    <div id="error-box"></div>
    <form id="signup-form" onsubmit="submitSignup(event)">
      <input type="hidden" id="plan-input" value="__DEFAULT_PLAN__" />
      <div class="form-row">
        <label for="email-input">Subscriber Email:</label>
        <div>
          <input id="email-input" type="email" required placeholder="engineer@example.com" />
        </div>
      </div>
      <div class="form-row">
        <label for="username-input">DEC Username (1-12 chars):</label>
        <div>
          <input id="username-input" type="text" required maxlength="12" pattern="[A-Za-z][A-Za-z0-9_$]{0,11}" placeholder="JSMITH" oninput="checkAvailability(this.value)" />
          <div id="avail-hint" class="hint">Used at RSTS/E <code>User:</code> prompt, VAX/VMS <code>Username:</code> prompt, DECwindows X11 &amp; SSH.</div>
        </div>
      </div>
      <div class="form-row">
        <label for="password-input">DEC Terminal Password:</label>
        <div>
          <input id="password-input" type="password" required minlength="3" placeholder="••••••••" />
          <div class="hint">Assigned directly to <code>$ACCT.SYS</code> and/or <code>SYSUAF.DAT</code> for interactive terminal login.</div>
        </div>
      </div>
      <div class="form-row">
        <label for="coupon-input">Discount Coupon (Optional):</label>
        <div>
          <input id="coupon-input" type="text" maxlength="6" pattern="[0-9]{6}" placeholder="6-digit code (e.g. 482915)" oninput="checkCoupon(this.value)" />
          <div id="coupon-hint" class="hint">Enter a 6-digit promotional discount code (supports fractional percentages up to 100.00%).</div>
        </div>
      </div>
      <div class="form-row" id="enterprise-row" style="display:none;">
        <label for="workos-org-input">WorkOS Organization ID:</label>
        <div style="display:flex; gap:8px;">
          <input id="workos-org-input" type="text" placeholder="org_01HXYZ_MIT_CS_DEPT" />
          <a class="btn-link" href="/auth/workos/login" style="white-space:nowrap;">WORKOS SAML SSO</a>
        </div>
      </div>
      <div style="margin-top:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <span class="hint">Instant provisioning via Clerk Billing / Stripe &amp; HTTPS Access Point API (<code>POST /api/v1/signup</code>)</span>
        <button type="submit" id="submit-btn">SUBSCRIBE &amp; PROVISION DEC ACCOUNT</button>
      </div>
    </form>

    <div id="result-box">
      <div style="font-size:16px; font-weight:bold; margin-bottom:6px;">%LCS-S-PROVISIONED, DEC Timesharing Account(s) Active!</div>
      <table class="cred-table" id="cred-table"></table>
      <div style="display:flex; gap:10px; flex-wrap:wrap;">
        <a class="btn-link" id="launch-term-btn" href="/">LAUNCH HTTPS TERMINAL NOW</a>
        <a class="btn-link" href="/api/v1/status" target="_blank">VIEW NODE STATUS JSON</a>
      </div>
    </div>
  </div>
</div>

<script>
  let selectedPlan = "__DEFAULT_PLAN__";
  let checkTimer = null;
  let couponTimer = null;

  function selectPlan(planId) {
    selectedPlan = planId;
    document.getElementById('plan-input').value = planId;
    const ids = ['LCS_RSTS_10', 'LCS_VMS_10', 'LCS_BUNDLE_15', 'LCS_ENTERPRISE'];
    ids.forEach(function(id) {
      const el = document.getElementById('card-' + id);
      if (el) el.classList.toggle('selected', id === planId);
    });
    document.getElementById('enterprise-row').style.display = (planId === 'LCS_ENTERPRISE') ? 'grid' : 'none';
    const cVal = document.getElementById('coupon-input').value;
    if (cVal) checkCoupon(cVal);
  }

  function checkCoupon(val) {
    clearTimeout(couponTimer);
    const hint = document.getElementById('coupon-hint');
    const clean = (val || '').trim();
    if (!clean) {
      hint.style.color = '#8ce6a3';
      hint.textContent = 'Enter a 6-digit promotional discount code (supports fractional percentages up to 100.00%).';
      return;
    }
    if (!/^[0-9]{6}$/.test(clean)) {
      hint.style.color = '#ffb000';
      hint.textContent = 'Discount coupon code must be 6 digits (000000-999999).';
      return;
    }
    couponTimer = setTimeout(function() {
      fetch('/api/v1/coupons/validate?code=' + encodeURIComponent(clean) + '&plan=' + encodeURIComponent(selectedPlan))
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data.valid) {
            hint.style.color = '#33ff66';
            hint.textContent = '✓ Coupon ' + data.code + ' applied: ' + data.discount_percent_display + ' off (' + data.discounted_price_display + ')!';
          } else {
            hint.style.color = '#ff8080';
            hint.textContent = '✗ ' + (data.reason || 'Invalid or expired coupon code');
          }
        })
        .catch(function() {});
    }, 180);
  }

  function checkAvailability(val) {
    clearTimeout(checkTimer);
    const hint = document.getElementById('avail-hint');
    const clean = (val || '').trim().toUpperCase();
    if (!clean) {
      hint.style.color = '#8ce6a3';
      hint.textContent = 'Enter a 1-12 character DEC Username (e.g. JSMITH).';
      return;
    }
    checkTimer = setTimeout(function() {
      fetch('/api/v1/users/check?username=' + encodeURIComponent(clean))
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data.available) {
            hint.style.color = '#33ff66';
            hint.textContent = '✓ Username ' + data.username + ' is available!';
          } else {
            hint.style.color = '#ff8080';
            hint.textContent = '✗ ' + (data.reason || 'Username unavailable');
          }
        })
        .catch(function() {});
    }, 180);
  }

  function submitSignup(e) {
    e.preventDefault();
    const errBox = document.getElementById('error-box');
    const resBox = document.getElementById('result-box');
    const btn = document.getElementById('submit-btn');
    errBox.style.display = 'none';
    resBox.style.display = 'none';
    btn.disabled = true;

    const payload = {
      plan: selectedPlan,
      email: document.getElementById('email-input').value.trim(),
      username: document.getElementById('username-input').value.trim().toUpperCase(),
      password: document.getElementById('password-input').value,
      coupon_code: document.getElementById('coupon-input').value.trim(),
      workos_org_id: document.getElementById('workos-org-input').value.trim()
    };

    fetch('/api/v1/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function(r) { return r.json().then(function(d) { return { status: r.status, body: d }; }); })
      .then(function(res) {
        btn.disabled = false;
        if (res.status >= 400 || !res.body.ok) {
          errBox.textContent = res.body.error || 'Provisioning failed';
          errBox.style.display = 'block';
          return;
        }
        const d = res.body;
        let rows = '';
        rows += '<tr><td>DBA / Provider:</td><td><strong>' + (d.dba || 'Legacy Computing Systems') + '</strong></td></tr>';
        rows += '<tr><td>Subscription Plan:</td><td>' + d.plan + ' (' + (d.price_display || '$10/mo') + ')</td></tr>';
        if (d.coupon_applied) {
          rows += '<tr><td>Discount Coupon:</td><td><strong>' + d.coupon_applied.code + '</strong> (' + d.coupon_applied.discount_percent_display + ' off &rarr; <strong>' + d.coupon_applied.discounted_price_display + '</strong>)</td></tr>';
        }
        rows += '<tr><td>DEC Username:</td><td><strong>' + d.username + '</strong></td></tr>';
        if (d.rsts_account) {
          rows += '<tr><td>PDP-11 RSTS/E PPN:</td><td><strong>' + d.rsts_account.ppn + '</strong> (' + d.rsts_account.dir_spec + ', Quota: ' + d.rsts_account.quota + ' blocks)</td></tr>';
        }
        if (d.vms_account) {
          rows += '<tr><td>VAX/VMS SYSUAF UIC:</td><td><strong>' + d.vms_account.uic + '</strong> (' + d.vms_account.dir_spec + ', Quota: ' + d.vms_account.quota + ' blocks, DECW$USERS)</td></tr>';
        }
        if (d.enterprise_billing) {
          const eb = d.enterprise_billing;
          rows += '<tr><td>Enterprise Seat Metering:</td><td><strong>' + eb.active_seats + ' active seat(s)</strong> (Includes ' + eb.included_active_seats + ' seats @ $' + eb.base_price_monthly + '/mo + ' + eb.additional_active_seats + ' extra @ $' + eb.additional_seat_price_monthly + '/mo = <strong>' + eb.monthly_total_display + '</strong>)</td></tr>';
        }
        document.getElementById('cred-table').innerHTML = rows;
        document.getElementById('launch-term-btn').href = '/?user=' + encodeURIComponent(d.username);
        resBox.style.display = 'block';
      })
      .catch(function(err) {
        btn.disabled = false;
        errBox.textContent = 'Network error: ' + err;
        errBox.style.display = 'block';
      });
  }
</script>
</body>
</html>
"""


class LCSProvisioningEngine:
    """
    Unified account provisioning, Clerk Identity + Stripe Billing, and WorkOS Enterprise
    SCIM/SSO handler for RSTS/E (:8411) and VAX/VMS (:8455).
    """

    def __init__(self, primary_os, os_dir, fs_root, https_port):
        self.primary_os = primary_os.upper()  # "RSTS" or "VMS"
        self.os_dir = os.path.abspath(os_dir)
        self.fs_root = os.path.abspath(fs_root)
        self.https_port = int(https_port)
        self.dec_root = os.path.abspath(os.path.join(self.os_dir, "..", ".."))

    @property
    def clerk_publishable_key(self):
        if not (os.environ.get("CLERK_PUBLISHABLE_KEY") or os.environ.get("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")):
            load_dotenv_files()
        return (
            os.environ.get("CLERK_PUBLISHABLE_KEY")
            or os.environ.get("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
            or ""
        ).strip()

    @property
    def clerk_secret_key(self):
        if not os.environ.get("CLERK_SECRET_KEY"):
            load_dotenv_files()
        return os.environ.get("CLERK_SECRET_KEY", "").strip()

    @property
    def clerk_webhook_secret(self):
        if not os.environ.get("CLERK_WEBHOOK_SECRET"):
            load_dotenv_files()
        return os.environ.get("CLERK_WEBHOOK_SECRET", "").strip()

    @property
    def workos_api_key(self):
        if not os.environ.get("WORKOS_API_KEY"):
            load_dotenv_files()
        return os.environ.get("WORKOS_API_KEY", "").strip()

    @property
    def workos_client_id(self):
        if not os.environ.get("WORKOS_CLIENT_ID"):
            load_dotenv_files()
        return os.environ.get("WORKOS_CLIENT_ID", "").strip()

    @property
    def workos_webhook_secret(self):
        if not os.environ.get("WORKOS_WEBHOOK_SECRET"):
            load_dotenv_files()
        return os.environ.get("WORKOS_WEBHOOK_SECRET", "").strip()

    @property
    def lcs_api_secret(self):
        return os.environ.get("LCS_API_SECRET", "lcs-dev-hmac-secret-key").strip()

    def get_public_base_url(self, headers=None):
        """
        Determine the external HTTPS base URL for this node (supporting Tailscale Funnel
        where RSTS/E :8411 is served on public port 443 and VAX/VMS :8455 is served on :8443).
        """
        env_key = "LCS_RSTS_PUBLIC_URL" if self.primary_os == "RSTS" else "LCS_VMS_PUBLIC_URL"
        explicit_url = os.environ.get(env_key, "").strip()
        if headers:
            req_host = (headers.get("x-forwarded-host") or headers.get("host") or "").strip()
            if req_host and not req_host.startswith("127.0.0.1") and not req_host.startswith("localhost"):
                # Preserve exact Host header sent by browser/Funnel (e.g. ssadvisor-ser.tail8d2674.ts.net or :8443)
                return f"https://{req_host}"
        if explicit_url:
            return explicit_url.rstrip("/")
        pub_host = os.environ.get("LCS_PUBLIC_HOST", "ssadvisor-ser.tail8d2674.ts.net").strip() or "localhost"
        if pub_host.endswith(".ts.net"):
            if self.primary_os == "RSTS":
                return f"https://{pub_host}"
            else:
                funnel_port = os.environ.get("LCS_VMS_FUNNEL_PORT", "8443").strip() or "8443"
                return f"https://{pub_host}:{funnel_port}"
        return f"https://{pub_host}:{self.https_port}"

    def compute_enterprise_seat_Summary(self, org_id=None):
        """
        Compute active enterprise seat count and metered monthly billing across RSTS/E and VAX/VMS.
        Pricing model: $199/mo base (includes 15 active seats) + $10/mo per additional active seat.
        """
        ent_tier = PRICING_TIERS["LCS_ENTERPRISE"]
        base_price = int(ent_tier.get("base_price_monthly", 199))
        included_seats = int(ent_tier.get("included_active_seats", 15))
        extra_seat_price = int(ent_tier.get("additional_seat_price_monthly", 10))

        org_users = {}  # org_id -> {"active_users": set(), "suspended_users": set()}

        def _scan_record(uname, rec, is_rsts=False):
            if not isinstance(rec, dict):
                return
            w_org = str(rec.get("workos_org_id") or "").strip()
            plan_val = str(rec.get("plan") or "").strip().upper()
            ppn_or_uic = str(rec.get("ppn" if is_rsts else "uic") or "").strip("[]")
            grp_prefix = ppn_or_uic.split(",", 1)[0].strip() if "," in ppn_or_uic else ""
            is_ent = bool(w_org or "ENTERPRISE" in plan_val or grp_prefix == "300")
            if not is_ent:
                return
            org_key = w_org or "org_enterprise_300"
            bucket = org_users.setdefault(org_key, {"active_users": set(), "suspended_users": set()})
            flags_str = str(rec.get("flags") or "").upper()
            status_str = str(rec.get("status") or "ACTIVE").upper()
            is_disabled = (
                ("DISUSER" in flags_str and "NODISUSER" not in flags_str)
                or status_str in ("DISUSER", "SUSPENDED", "DISABLED")
            )
            clean_u = (uname or rec.get("username") or rec.get("name") or "").strip().upper()
            if not clean_u:
                return
            if is_disabled:
                bucket["suspended_users"].add(clean_u)
            else:
                bucket["active_users"].add(clean_u)

        rsts_emu = self._load_rsts_emulator()
        if rsts_emu:
            for _, acct in rsts_emu.accounts.items():
                _scan_record(acct.get("username") or acct.get("name"), acct, is_rsts=True)

        vms_emu = self._load_vms_emulator()
        if vms_emu:
            for uname, uinfo in vms_emu.users.items():
                _scan_record(uname, uinfo, is_rsts=False)

        def _build_org_billing(o_key):
            b = org_users.get(o_key, {"active_users": set(), "suspended_users": set()})
            active_list = sorted(b["active_users"])
            suspended_list = sorted(b["suspended_users"] - b["active_users"])
            active_count = len(active_list)
            extra_seats = max(0, active_count - included_seats)
            monthly_total = base_price + (extra_seats * extra_seat_price)
            return {
                "organization_id": o_key,
                "base_price_monthly": base_price,
                "included_active_seats": included_seats,
                "additional_seat_price_monthly": extra_seat_price,
                "active_seats": active_count,
                "suspended_seats": len(suspended_list),
                "remaining_included_seats": max(0, included_seats - active_count),
                "additional_active_seats": extra_seats,
                "monthly_total_usd": monthly_total,
                "monthly_total_display": f"${monthly_total} / month",
                "active_usernames": active_list,
            }

        if org_id:
            return _build_org_billing(str(org_id).strip() or "org_enterprise_300")

        all_orgs = {k: _build_org_billing(k) for k in sorted(org_users.keys())}
        return {
            "base_price_monthly": base_price,
            "included_active_seats": included_seats,
            "additional_seat_price_monthly": extra_seat_price,
            "organizations": all_orgs,
        }

    # ------------------------------------------------------------------
    # Discount Coupon Engine (6-digit random code, 0.01% - 100.00%,
    # expiry: 'never', or days <= 365, or months <= 12)
    # ------------------------------------------------------------------
    def _coupons_file_paths(self):
        paths = [os.path.join(self.fs_root, ".lcs_coupons.json")]
        rsts_fs = os.path.join(self.dec_root, "OS", "RSTS-E", "fs", ".lcs_coupons.json")
        vms_fs = os.path.join(self.dec_root, "OS", "VMS", "fs", ".lcs_coupons.json")
        for p in (rsts_fs, vms_fs, "/opt/dec-rsts/fs/.lcs_coupons.json", "/opt/dec-vms/fs/.lcs_coupons.json"):
            if p not in paths and os.path.isdir(os.path.dirname(p)):
                paths.append(p)
        return paths

    def load_coupons(self):
        merged = {}
        for p in self._coupons_file_paths():
            if os.path.isfile(p):
                try:
                    with open(p, "r") as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        merged.update(data)
                except Exception:
                    pass
        return merged

    def save_coupons(self, coupons_dict):
        for p in self._coupons_file_paths():
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w") as f:
                    json.dump(coupons_dict, f, indent=2)
            except Exception:
                pass

    def _sync_coupon_to_peer(self, coupon_record):
        peer_os = "RSTS" if self.primary_os == "VMS" else "VMS"
        payload = json.dumps({
            "code": coupon_record["code"],
            "discount_percent": coupon_record["discount_percent"],
            "duration_unit": coupon_record["duration_unit"],
            "duration_value": coupon_record.get("duration_value"),
            "description": coupon_record.get("description", ""),
            "created_at": coupon_record.get("created_at"),
            "expires_at": coupon_record.get("expires_at"),
            "local_only": True,
        }).encode("utf-8")
        sig = self.compute_hmac_signature(payload)
        ctx = ssl._create_unverified_context()
        for base in self._peer_base_urls(peer_os):
            try:
                req = urllib.request.Request(
                    f"{base.rstrip('/')}/api/v1/coupons",
                    data=payload,
                    method="POST",
                    headers={
                        "Content-Type": "application/json",
                        "X-LCS-Signature": sig,
                    },
                )
                with urllib.request.urlopen(req, context=ctx, timeout=2.0) as _:
                    return True
            except Exception:
                continue
        return False

    def create_discount_coupon(
        self,
        discount_percent,
        duration_unit="never",
        duration_value=None,
        description="",
        code=None,
        created_at=None,
        expires_at=None,
        local_only=False,
    ):
        """
        Generate or register a 6-digit discount coupon code.
        - code: 6 random digits (000000 - 999999)
        - discount_percent: percentage > 0 and <= 100.00 (up to 100ths place, e.g. 12.75, 33.33, 100.00)
        - duration_unit: 'never' (non-expiring), 'days' (1..365), or 'months' (1..12)
        """
        if discount_percent is None or str(discount_percent).strip() == "":
            raise ValueError("discount_percent is required")
        raw_pct = str(discount_percent).strip().rstrip("%").strip()
        try:
            dec_pct = Decimal(raw_pct)
        except InvalidOperation:
            raise ValueError(f"Invalid discount_percent '{discount_percent}': must be a valid percentage number")

        if dec_pct <= Decimal("0") or dec_pct > Decimal("100"):
            raise ValueError("discount_percent must be greater than 0% and at most 100.00%")

        # Check at most 2 decimal places (100ths place)
        quant_pct = dec_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if dec_pct != quant_pct:
            raise ValueError("discount_percent supports up to the 100ths place (at most 2 decimal places, e.g. 25.75)")

        unit = str(duration_unit or "never").strip().lower()
        if unit in ("never", "none", "forever", "non-expiring", "non_expiring", "no_expiration", "permanent"):
            norm_unit = "never"
            norm_val = None
            exp_iso = None
        elif unit in ("day", "days", "d"):
            norm_unit = "days"
            if duration_value is None or str(duration_value).strip() == "":
                raise ValueError("duration_value is required when duration_unit is 'days'")
            try:
                days_val = int(duration_value)
            except ValueError:
                raise ValueError("duration_value for 'days' must be an integer between 1 and 365")
            if days_val < 1 or days_val > 365:
                raise ValueError("Coupon age in days cannot exceed 1 year (must be between 1 and 365 days)")
            norm_val = days_val
            now_dt = datetime.now(timezone.utc)
            exp_iso = expires_at or (now_dt + timedelta(days=days_val)).isoformat()
        elif unit in ("month", "months", "mo", "m"):
            norm_unit = "months"
            if duration_value is None or str(duration_value).strip() == "":
                raise ValueError("duration_value is required when duration_unit is 'months'")
            try:
                months_val = int(duration_value)
            except ValueError:
                raise ValueError("duration_value for 'months' must be an integer between 1 and 12")
            if months_val < 1 or months_val > 12:
                raise ValueError("Coupon age in months cannot exceed 1 year (must be between 1 and 12 months)")
            norm_val = months_val
            now_dt = datetime.now(timezone.utc)
            # 12 months == 365 days max
            days_equiv = 365 if months_val == 12 else months_val * 30
            exp_iso = expires_at or (now_dt + timedelta(days=days_equiv)).isoformat()
        else:
            raise ValueError("duration_unit must be 'never', 'days' (1-365), or 'months' (1-12)")

        coupons = self.load_coupons()
        if code is not None and str(code).strip() != "":
            clean_code = str(code).strip()
            if not re.match(r"^[0-9]{6}$", clean_code):
                raise ValueError("Coupon code must be exactly 6 digits (000000-999999)")
        else:
            clean_code = f"{secrets.randbelow(1000000):06d}"
            attempts = 0
            while clean_code in coupons and attempts < 50:
                clean_code = f"{secrets.randbelow(1000000):06d}"
                attempts += 1

        pct_float = float(quant_pct)
        pct_str = f"{quant_pct:.2f}".rstrip("0").rstrip(".") if "." in f"{quant_pct:.2f}" else f"{quant_pct}"
        now_iso = created_at or datetime.now(timezone.utc).isoformat()

        rec = {
            "code": clean_code,
            "discount_percent": pct_float,
            "discount_percent_exact": f"{quant_pct:.2f}",
            "discount_percent_display": f"{pct_str}%",
            "duration_unit": norm_unit,
            "duration_value": norm_val,
            "never_expires": norm_unit == "never",
            "created_at": now_iso,
            "expires_at": exp_iso,
            "status": "ACTIVE",
            "description": str(description or f"{pct_str}% off Legacy Computing Systems subscription"),
        }
        coupons[clean_code] = rec
        self.save_coupons(coupons)
        if not local_only:
            self._sync_coupon_to_peer(rec)
        return rec

    def validate_and_apply_coupon(self, code, plan=None, base_price_usd=None):
        """
        Validate a 6-digit coupon code, check expiration, and compute the discounted price
        accurate to the 100ths place ($0.01).
        """
        clean_code = str(code or "").strip()
        if not re.match(r"^[0-9]{6}$", clean_code):
            return {
                "ok": True,
                "valid": False,
                "code": clean_code,
                "reason": "Coupon code must be 6 digits (000000-999999)",
            }

        coupons = self.load_coupons()
        rec = coupons.get(clean_code)
        if not rec:
            return {
                "ok": True,
                "valid": False,
                "code": clean_code,
                "reason": f"Coupon code '{clean_code}' not found",
            }

        if str(rec.get("status", "ACTIVE")).upper() != "ACTIVE":
            return {
                "ok": True,
                "valid": False,
                "code": clean_code,
                "reason": f"Coupon code '{clean_code}' is disabled",
            }

        exp_at = rec.get("expires_at")
        if exp_at and not rec.get("never_expires", False):
            try:
                exp_dt = datetime.fromisoformat(exp_at)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > exp_dt:
                    return {
                        "ok": True,
                        "valid": False,
                        "code": clean_code,
                        "expired": True,
                        "expires_at": exp_at,
                        "reason": f"Coupon code '{clean_code}' expired on {exp_at}",
                    }
            except Exception:
                pass

        plan_upper = (plan or ("LCS_RSTS_10" if self.primary_os == "RSTS" else "LCS_VMS_10")).strip().upper()
        tier = PRICING_TIERS.get(plan_upper, PRICING_TIERS["LCS_RSTS_10" if self.primary_os == "RSTS" else "LCS_VMS_10"])
        orig_dec = Decimal(str(base_price_usd if base_price_usd is not None else tier["price_monthly"])).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        pct_dec = Decimal(str(rec.get("discount_percent_exact") or rec["discount_percent"])).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        discount_amt = (orig_dec * (pct_dec / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        final_dec = max(Decimal("0.00"), orig_dec - discount_amt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "ok": True,
            "valid": True,
            "code": clean_code,
            "discount_percent": float(pct_dec),
            "discount_percent_exact": f"{pct_dec:.2f}",
            "discount_percent_display": rec.get("discount_percent_display", f"{pct_dec}%"),
            "duration_unit": rec.get("duration_unit", "never"),
            "duration_value": rec.get("duration_value"),
            "never_expires": bool(rec.get("never_expires", rec.get("duration_unit") == "never")),
            "created_at": rec.get("created_at"),
            "expires_at": exp_at,
            "plan": plan_upper,
            "original_price_usd": float(orig_dec),
            "discount_amount_usd": float(discount_amt),
            "discounted_price_usd": float(final_dec),
            "discounted_price_exact": f"{final_dec:.2f}",
            "discounted_price_display": f"${final_dec:.2f} / month",
        }

    def _peer_base_urls(self, peer_os):
        if peer_os == "VMS":
            env_url = os.environ.get("LCS_VMS_URL", "").strip()
            urls = [env_url] if env_url else []
            urls.extend(["https://dec-vms:8455", "https://host.docker.internal:8455", "https://127.0.0.1:8455"])
            return urls
        else:
            env_url = os.environ.get("LCS_RSTS_URL", "").strip()
            urls = [env_url] if env_url else []
            urls.extend(["https://dec-rsts-e:8411", "https://host.docker.internal:8411", "https://127.0.0.1:8411"])
            return urls

    def _provision_peer_over_https(
        self,
        peer_os,
        username,
        password,
        email,
        plan,
        clerk_user_id,
        workos_org_id,
        workos_user_id,
        group,
        quota,
    ):
        payload = json.dumps({
            "username": username,
            "password": password,
            "email": email,
            "plan": plan,
            "target_os": peer_os,
            "clerk_user_id": clerk_user_id,
            "workos_org_id": workos_org_id,
            "workos_user_id": workos_user_id,
            "group": group,
            "quota": quota,
        }).encode("utf-8")
        sig = self.compute_hmac_signature(payload)
        ctx = ssl._create_unverified_context()
        for base in self._peer_base_urls(peer_os):
            try:
                req = urllib.request.Request(
                    f"{base.rstrip('/')}/api/v1/users",
                    data=payload,
                    method="POST",
                    headers={
                        "Content-Type": "application/json",
                        "X-LCS-Signature": sig,
                    },
                )
                with urllib.request.urlopen(req, context=ctx, timeout=2.5) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    if peer_os == "VMS" and data.get("vms_account"):
                        return data["vms_account"]
                    if peer_os == "RSTS" and data.get("rsts_account"):
                        return data["rsts_account"]
            except Exception:
                continue
        return None

    def _update_peer_over_https(self, peer_os, identifier, status=None, password=None, quota=None, plan=None):
        payload = json.dumps({
            "status": status,
            "password": password,
            "quota": quota,
            "plan": plan,
            "local_only": True,
        }).encode("utf-8")
        sig = self.compute_hmac_signature(payload)
        ctx = ssl._create_unverified_context()
        for base in self._peer_base_urls(peer_os):
            try:
                req = urllib.request.Request(
                    f"{base.rstrip('/')}/api/v1/users/{urllib.parse.quote(str(identifier))}",
                    data=payload,
                    method="PATCH",
                    headers={
                        "Content-Type": "application/json",
                        "X-LCS-Signature": sig,
                    },
                )
                with urllib.request.urlopen(req, context=ctx, timeout=2.5) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    if peer_os == "VMS" and data.get("vms_account"):
                        return data["vms_account"]
                    if peer_os == "RSTS" and data.get("rsts_account"):
                        return data["rsts_account"]
            except Exception:
                continue
        return None

    def _load_rsts_emulator(self):
        candidates = [
            os.path.join(self.os_dir, "src", "rsts_os.py") if self.primary_os == "RSTS" else "",
            os.path.join(self.dec_root, "OS", "RSTS-E", "src", "rsts_os.py"),
            "/opt/dec-rsts/src/rsts_os.py",
        ]
        for path in candidates:
            if path and os.path.isfile(path):
                spec = importlib.util.spec_from_file_location("rsts_os_mod", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                root = self.fs_root if self.primary_os == "RSTS" else os.environ.get(
                    "RSTS_FS_ROOT", os.path.join(os.path.dirname(os.path.dirname(path)), "fs")
                )
                return mod.RSTSEmulator(root_dir=root)
        return None

    def _load_vms_emulator(self):
        candidates = [
            os.path.join(self.os_dir, "src", "vms_os.py") if self.primary_os == "VMS" else "",
            os.path.join(self.dec_root, "OS", "VMS", "src", "vms_os.py"),
            "/opt/dec-vms/src/vms_os.py",
        ]
        for path in candidates:
            if path and os.path.isfile(path):
                spec = importlib.util.spec_from_file_location("vms_os_mod", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                root = self.fs_root if self.primary_os == "VMS" else os.environ.get(
                    "VMS_FS_ROOT", os.path.join(os.path.dirname(os.path.dirname(path)), "fs")
                )
                return mod.VMSEmulator(root_dir=root)
        return None

    def verify_hmac_signature(self, raw_body, signature_header, secret):
        """Verify HMAC-SHA256 signature for X-LCS-Signature, Clerk/Svix, or WorkOS webhooks."""
        if not signature_header:
            return False
        sig_clean = signature_header.strip()
        ts_val = ""
        if "v1=" in sig_clean and "," in sig_clean:
            # WorkOS header: t=<timestamp>, v1=<hex_hmac_of_"{timestamp}.{raw_body}">
            for part in sig_clean.split(","):
                p = part.strip()
                if p.startswith("t="):
                    ts_val = p[2:].strip()
                elif p.startswith("v1="):
                    sig_clean = p[3:].strip()
        elif sig_clean.lower().startswith("sha256="):
            sig_clean = sig_clean.split("=", 1)[1].strip()

        sec_bytes = secret.encode("utf-8")
        # 1. Standard raw_body HMAC
        expected_hex = hmac.new(sec_bytes, raw_body, hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected_hex.lower(), sig_clean.lower()):
            return True
        # 2. WorkOS timestamped payload format: "{timestamp}.{raw_body}"
        if ts_val:
            signed_payload = ts_val.encode("utf-8") + b"." + raw_body
            expected_wos = hmac.new(sec_bytes, signed_payload, hashlib.sha256).hexdigest()
            if hmac.compare_digest(expected_wos.lower(), sig_clean.lower()):
                return True
        return False

    def compute_hmac_signature(self, raw_body, secret=None):
        sec = (secret or self.lcs_api_secret).encode("utf-8")
        return hmac.new(sec, raw_body, hashlib.sha256).hexdigest()

    def sync_clerk_public_metadata(self, clerk_user_id, metadata):
        """Sync provisioned DEC credentials metadata to Clerk Backend API when CLERK_SECRET_KEY is set."""
        if not self.clerk_secret_key or not clerk_user_id:
            return {"synced": False, "mode": "standalone", "publicMetadata": metadata}
        url = f"https://api.clerk.com/v1/users/{urllib.parse.quote(clerk_user_id)}/metadata"
        body = json.dumps({"public_metadata": metadata}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="PATCH",
            headers={
                "Authorization": f"Bearer {self.clerk_secret_key}",
                "Content-Type": "application/json",
                "User-Agent": "LegacyComputingSystems/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return {"synced": resp.status < 300, "mode": "clerk_cloud", "publicMetadata": metadata}
        except Exception as e:
            return {"synced": False, "mode": "clerk_cloud_error", "error": str(e), "publicMetadata": metadata}

    def render_signup_html(self):
        default_plan = "LCS_RSTS_10" if self.primary_os == "RSTS" else "LCS_VMS_10"
        node_label = "PDP-11/70 RSTS/E V10.1-L (:8411)" if self.primary_os == "RSTS" else "VAX/VMS V5.5-2 & DECwindows (:8455)"
        clerk_mode = "Cloud Live" if self.clerk_publishable_key else "Standalone / Ready"
        workos_mode = "Cloud Live" if (self.workos_api_key or self.workos_client_id) else "Standalone / Ready"
        clerk_script = ""
        if self.clerk_publishable_key:
            clerk_script = (
                f'<script async crossorigin="anonymous" '
                f'data-clerk-publishable-key="{self.clerk_publishable_key}" '
                f'src="https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"></script>'
            )
        html = (
            SIGNUP_HTML_TEMPLATE.replace("__NODE_LABEL__", node_label)
            .replace("__DEFAULT_PLAN__", default_plan)
            .replace("__SEL_RSTS__", "selected" if self.primary_os == "RSTS" else "")
            .replace("__SEL_VMS__", "selected" if self.primary_os == "VMS" else "")
            .replace("__CLERK_MODE_LABEL__", clerk_mode)
            .replace("__WORKOS_MODE_LABEL__", workos_mode)
            .replace("__CLERK_SCRIPT_TAG__", clerk_script)
        )
        return html.encode("utf-8")

    def check_username(self, username):
        clean = (username or "").strip().upper()
        if self.primary_os == "RSTS":
            emu = self._load_rsts_emulator()
        else:
            emu = self._load_vms_emulator()
        ok, reason = emu.check_username_available(clean)
        return {
            "ok": True,
            "username": clean,
            "available": ok,
            "reason": reason,
            "os": self.primary_os,
        }

    def provision_across_targets(
        self,
        username,
        password,
        email="",
        plan="LCS_RSTS_10",
        target_os=None,
        clerk_user_id="",
        workos_org_id="",
        workos_user_id="",
        group=None,
        quota=None,
        coupon_code="",
    ):
        plan_upper = (plan or ("LCS_RSTS_10" if self.primary_os == "RSTS" else "LCS_VMS_10")).strip().upper()
        tier_info = PRICING_TIERS.get(plan_upper, PRICING_TIERS["LCS_RSTS_10" if self.primary_os == "RSTS" else "LCS_VMS_10"])

        coupon_applied = None
        clean_coupon = (coupon_code or "").strip()
        if clean_coupon:
            c_res = self.validate_and_apply_coupon(clean_coupon, plan=plan_upper)
            if not c_res.get("valid"):
                raise ValueError(c_res.get("reason") or f"Invalid coupon code '{clean_coupon}'")
            coupon_applied = c_res

        if target_os:
            if isinstance(target_os, str):
                t_up = target_os.strip().upper()
                if t_up in ("BOTH", "ALL", "BUNDLE"):
                    targets = ["RSTS", "VMS"]
                elif "RSTS" in t_up and "VMS" in t_up:
                    targets = ["RSTS", "VMS"]
                elif "RSTS" in t_up:
                    targets = ["RSTS"]
                elif "VMS" in t_up:
                    targets = ["VMS"]
                else:
                    targets = list(tier_info["target_os"])
            elif isinstance(target_os, list):
                targets = [str(x).upper() for x in target_os]
            else:
                targets = list(tier_info["target_os"])
        else:
            targets = list(tier_info["target_os"])

        rsts_res = None
        vms_res = None

        if "RSTS" in targets:
            rsts_emu = self._load_rsts_emulator()
            if rsts_emu:
                rsts_res = rsts_emu.provision_subscriber_account(
                    username=username,
                    password=password,
                    email=email,
                    plan=plan_upper,
                    clerk_user_id=clerk_user_id,
                    workos_org_id=workos_org_id,
                    workos_user_id=workos_user_id,
                    project_group=group,
                    quota=quota,
                )
            elif self.primary_os != "RSTS":
                rsts_res = self._provision_peer_over_https(
                    "RSTS", username, password, email, plan_upper,
                    clerk_user_id, workos_org_id, workos_user_id, group, quota
                )

        if "VMS" in targets:
            vms_emu = self._load_vms_emulator()
            if vms_emu:
                vms_res = vms_emu.provision_subscriber_account(
                    username=username,
                    password=password,
                    email=email,
                    plan=plan_upper,
                    clerk_user_id=clerk_user_id,
                    workos_org_id=workos_org_id,
                    workos_user_id=workos_user_id,
                    uic_group=group,
                    quota=quota,
                )
            elif self.primary_os != "VMS":
                vms_res = self._provision_peer_over_https(
                    "VMS", username, password, email, plan_upper,
                    clerk_user_id, workos_org_id, workos_user_id, group, quota
                )

        # Ensure primary OS is always provisioned when invoked directly on that node's /api/v1/users
        if self.primary_os == "RSTS" and rsts_res is None and vms_res is None:
            rsts_emu = self._load_rsts_emulator()
            rsts_res = rsts_emu.provision_subscriber_account(
                username=username,
                password=password,
                email=email,
                plan=plan_upper,
                clerk_user_id=clerk_user_id,
                workos_org_id=workos_org_id,
                workos_user_id=workos_user_id,
                project_group=group,
                quota=quota,
            )
        elif self.primary_os == "VMS" and vms_res is None and rsts_res is None:
            vms_emu = self._load_vms_emulator()
            vms_res = vms_emu.provision_subscriber_account(
                username=username,
                password=password,
                email=email,
                plan=plan_upper,
                clerk_user_id=clerk_user_id,
                workos_org_id=workos_org_id,
                workos_user_id=workos_user_id,
                uic_group=group,
                quota=quota,
            )

        clean_user = (username or "").strip().upper()
        subscribed_os = []
        if rsts_res:
            subscribed_os.append("RSTS_E")
        if vms_res:
            subscribed_os.append("VAX_VMS")

        clerk_metadata = {
            "dba": DBA_NAME,
            "plan": plan_upper,
            "subscribed_os": subscribed_os,
            "dec_username": clean_user,
            "rsts_ppn": rsts_res["ppn"] if rsts_res else None,
            "vms_uic": vms_res["uic"] if vms_res else None,
            "coupon_code": coupon_applied["code"] if coupon_applied else None,
            "discount_percent": coupon_applied["discount_percent"] if coupon_applied else None,
            "account_status": "ACTIVE",
        }
        clerk_sync = self.sync_clerk_public_metadata(clerk_user_id, clerk_metadata)

        base_url = self.get_public_base_url()
        primary_rec = rsts_res if (self.primary_os == "RSTS" and rsts_res) else (vms_res or rsts_res)
        is_ent = bool(workos_org_id or workos_user_id or "ENTERPRISE" in plan_upper)
        enterprise_billing = (
            self.compute_enterprise_seat_Summary(workos_org_id or "org_enterprise_300")
            if is_ent
            else None
        )
        if enterprise_billing and coupon_applied:
            coupon_applied = self.validate_and_apply_coupon(
                coupon_applied["code"],
                plan=plan_upper,
                base_price_usd=enterprise_billing["monthly_total_usd"],
            )
            enterprise_billing["coupon_applied"] = coupon_applied
            enterprise_billing["discounted_monthly_total_usd"] = coupon_applied["discounted_price_usd"]
            enterprise_billing["discounted_monthly_total_display"] = coupon_applied["discounted_price_display"]

        if coupon_applied:
            effective_price_display = coupon_applied["discounted_price_display"]
        elif enterprise_billing:
            effective_price_display = enterprise_billing["monthly_total_display"]
        else:
            effective_price_display = tier_info["price_display"]

        return {
            "ok": True,
            "dba": DBA_NAME,
            "plan": plan_upper,
            "price_display": effective_price_display,
            "original_price_display": (
                enterprise_billing["monthly_total_display"]
                if enterprise_billing
                else tier_info["price_display"]
            ),
            "coupon_applied": coupon_applied,
            "discount_amount_usd": coupon_applied["discount_amount_usd"] if coupon_applied else None,
            "discounted_price_usd": coupon_applied["discounted_price_usd"] if coupon_applied else None,
            "username": clean_user,
            "ppn": rsts_res["ppn"] if rsts_res else None,
            "uic": vms_res["uic"] if vms_res else None,
            "quota": primary_rec["quota"] if primary_rec else tier_info["quota"],
            "status": "ACTIVE",
            "flags": "NODISUSER",
            "rsts_account": rsts_res,
            "vms_account": vms_res,
            "enterprise_billing": enterprise_billing,
            "clerk_metadata": clerk_metadata,
            "clerk_sync": clerk_sync,
            "terminal_url": f"{base_url}/?user={clean_user}",
        }

    def update_across_targets(self, identifier, status=None, password=None, quota=None, plan=None, local_only=False):
        updated_rsts = None
        updated_vms = None
        errors = []

        rsts_emu = self._load_rsts_emulator()
        if rsts_emu:
            try:
                updated_rsts = rsts_emu.update_subscriber_account(
                    identifier=identifier,
                    status=status,
                    password=password,
                    quota=quota,
                    plan=plan,
                )
            except Exception as e:
                errors.append(str(e))
        elif not local_only and self.primary_os != "RSTS":
            updated_rsts = self._update_peer_over_https("RSTS", identifier, status, password, quota, plan)

        vms_emu = self._load_vms_emulator()
        if vms_emu:
            try:
                updated_vms = vms_emu.update_subscriber_account(
                    identifier=identifier,
                    status=status,
                    password=password,
                    quota=quota,
                    plan=plan,
                )
            except Exception as e:
                errors.append(str(e))
        elif not local_only and self.primary_os != "VMS":
            updated_vms = self._update_peer_over_https("VMS", identifier, status, password, quota, plan)

        if not updated_rsts and not updated_vms:
            raise KeyError(f"Subscriber account '{identifier}' not found ({'; '.join(errors)})")

        primary = updated_rsts if (self.primary_os == "RSTS" and updated_rsts) else (updated_vms or updated_rsts)
        return {
            "ok": True,
            "dba": DBA_NAME,
            "username": primary["username"],
            "ppn": updated_rsts["ppn"] if updated_rsts else None,
            "uic": updated_vms["uic"] if updated_vms else None,
            "status": primary["status"],
            "flags": primary["flags"],
            "quota": primary["quota"],
            "plan": primary["plan"],
            "rsts_account": updated_rsts,
            "vms_account": updated_vms,
        }

    def derive_dec_username(self, raw_username="", email="", fallback_id=""):
        cand = (raw_username or "").strip().upper()
        if not cand and email and "@" in email:
            cand = email.split("@", 1)[0].strip().upper()
        cand = re.sub(r"[^A-Z0-9_$]", "", cand)
        if not cand or not cand[0].isalpha():
            cand = "U" + cand
        cand = cand[:12]
        if cand in {"SYSTEM", "LIBRARY", "PBS", "DIBS", "DECW", "GUEST", "ROOT", "ADMIN"}:
            suffix = re.sub(r"[^A-Z0-9]", "", (fallback_id or "1").upper())[-3:] or "1"
            cand = (cand[:8] + "_" + suffix)[:12]
        return cand

    def handle_clerk_webhook(self, payload):
        """Process Clerk & Stripe lifecycle events (user.created, subscription.canceled, invoice.paid, etc.)."""
        event_type = (payload.get("type") or "").strip().lower()
        data = payload.get("data") or {}
        pub_meta = data.get("public_metadata") or data.get("publicMetadata") or {}
        unsafe_meta = data.get("unsafe_metadata") or data.get("unsafeMetadata") or {}
        meta = {**unsafe_meta, **pub_meta}

        clerk_user_id = str(data.get("id") or data.get("user_id") or meta.get("clerk_user_id") or "")
        email = ""
        if isinstance(data.get("email_addresses"), list) and data["email_addresses"]:
            email = data["email_addresses"][0].get("email_address", "")
        elif data.get("email"):
            email = str(data["email"])

        raw_uname = (
            meta.get("dec_username")
            or data.get("username")
            or meta.get("username")
            or ""
        )
        plan = meta.get("plan") or data.get("plan") or (
            "LCS_RSTS_10" if self.primary_os == "RSTS" else "LCS_VMS_10"
        )
        password = meta.get("dec_password") or data.get("password") or "DEC$PASS1"

        if event_type in (
            "user.deleted",
            "subscription.canceled",
            "subscription.cancelled",
            "subscription.deleted",
            "invoice.payment_failed",
        ):
            ident = raw_uname or clerk_user_id
            updated = self.update_across_targets(ident, status="DISUSER")
            return {
                "ok": True,
                "webhook": "clerk",
                "event_type": event_type,
                "action": "SUSPENDED",
                "account": updated,
            }

        if event_type in ("subscription.updated", "invoice.paid"):
            ident = raw_uname or clerk_user_id
            new_status = "DISUSER" if str(data.get("status", "")).lower() in ("canceled", "unpaid", "past_due") else "ACTIVE"
            try:
                updated = self.update_across_targets(ident, status=new_status, plan=plan)
                # If upgraded to LCS_BUNDLE_15, ensure both systems are provisioned
                if "BUNDLE" in str(plan).upper() and new_status == "ACTIVE":
                    uname = updated["username"]
                    self.provision_across_targets(
                        username=uname,
                        password=password,
                        email=email,
                        plan=plan,
                        target_os="BOTH",
                        clerk_user_id=clerk_user_id,
                    )
                return {
                    "ok": True,
                    "webhook": "clerk",
                    "event_type": event_type,
                    "action": "REACTIVATED" if new_status == "ACTIVE" else "SUSPENDED",
                    "account": updated,
                }
            except KeyError:
                pass

        # Default for user.created / subscription.created / checkout.session.completed
        dec_user = self.derive_dec_username(raw_uname, email=email, fallback_id=clerk_user_id)
        prov = self.provision_across_targets(
            username=dec_user,
            password=password,
            email=email,
            plan=plan,
            clerk_user_id=clerk_user_id,
        )
        return {
            "ok": True,
            "webhook": "clerk",
            "event_type": event_type or "user.created",
            "action": "PROVISIONED",
            "account": prov,
        }

    def handle_workos_webhook(self, payload):
        """Process WorkOS Enterprise SCIM Directory Sync events (dsync.user.created, dsync.user.deleted, etc.)."""
        event_type = (payload.get("event") or payload.get("type") or "").strip().lower()
        data = payload.get("data") or {}
        workos_user_id = str(data.get("id") or data.get("idp_id") or "")
        workos_org_id = str(
            data.get("organization_id")
            or data.get("directory_id")
            or payload.get("organization_id")
            or "org_enterprise_300"
        )
        state = str(data.get("state") or "active").strip().lower()

        email = ""
        if isinstance(data.get("emails"), list) and data["emails"]:
            first_em = data["emails"][0]
            email = first_em.get("value", "") if isinstance(first_em, dict) else str(first_em)
        elif data.get("email"):
            email = str(data["email"])

        raw_uname = data.get("username") or ""
        if not raw_uname and (data.get("first_name") or data.get("last_name")):
            fn = str(data.get("first_name") or "")[:1]
            ln = str(data.get("last_name") or "")
            raw_uname = f"{fn}{ln}"

        dec_user = self.derive_dec_username(raw_uname, email=email, fallback_id=workos_user_id)

        if event_type in ("dsync.user.deleted", "dsync.user.suspended") or state in ("suspended", "inactive", "deleted"):
            ident = workos_user_id if workos_user_id else dec_user
            try:
                updated = self.update_across_targets(ident, status="DISUSER")
            except KeyError:
                updated = self.update_across_targets(dec_user, status="DISUSER")
            ent_billing = self.compute_enterprise_seat_Summary(workos_org_id)
            return {
                "ok": True,
                "webhook": "workos",
                "event": event_type,
                "action": "SUSPENDED",
                "organization_id": workos_org_id,
                "enterprise_billing": ent_billing,
                "account": updated,
            }

        temp_password = data.get("password") or f"WOS${(workos_user_id[-4:] if len(workos_user_id) >= 4 else '3001').upper()}"
        prov = self.provision_across_targets(
            username=dec_user,
            password=temp_password,
            email=email,
            plan="LCS_ENTERPRISE",
            target_os="BOTH",
            workos_org_id=workos_org_id,
            workos_user_id=workos_user_id,
            group=300,
            quota=100000,
        )
        return {
            "ok": True,
            "webhook": "workos",
            "event": event_type or "dsync.user.created",
            "action": "PROVISIONED",
            "organization_id": workos_org_id,
            "temporary_password": temp_password,
            "enterprise_billing": prov.get("enterprise_billing") or self.compute_enterprise_seat_Summary(workos_org_id),
            "account": prov,
        }

    def get_status_summary(self):
        if self.primary_os == "RSTS":
            emu = self._load_rsts_emulator()
            accounts_count = len(emu.accounts) if emu else 0
            sessions_count = len(emu._load_live_sessions()) if emu else 0
            os_version = "DEC RSTS/E V10.1-L (PDP-11/70)"
        else:
            emu = self._load_vms_emulator()
            accounts_count = len(emu.users) if emu else 0
            sessions_count = len(emu._load_live_sessions()) if emu else 0
            os_version = "DEC VAX/VMS V5.5-2 (VAXstation 4000-90)"

        pub_base = self.get_public_base_url()
        return {
            "ok": True,
            "dba": DBA_NAME,
            "tagline": TAGLINE,
            "primary_os": self.primary_os,
            "os_version": os_version,
            "https_port": self.https_port,
            "public_base_url": pub_base,
            "workos_callback_url": f"{pub_base}/auth/workos/callback",
            "accounts_total": accounts_count,
            "active_sessions": sessions_count,
            "auth_providers": {
                "clerk": {
                    "configured": bool(self.clerk_secret_key or self.clerk_publishable_key),
                    "mode": "cloud" if (self.clerk_secret_key or self.clerk_publishable_key) else "standalone",
                },
                "workos": {
                    "configured": bool(self.workos_api_key or self.workos_client_id),
                    "mode": "cloud" if (self.workos_api_key or self.workos_client_id) else "standalone",
                },
            },
            "pricing_tiers": PRICING_TIERS,
            "enterprise_seat_metering": self.compute_enterprise_seat_Summary(),
        }

    def handle_http_request(self, method, path, query_params, headers, body_bytes):
        """
        Dispatch /signup, /auth/workos/*, and /api/v1/* HTTP requests.
        Returns (status_code, status_text, content_type, response_bytes) or None if path is not handled here.
        """
        method = method.upper()

        if method == "GET" and path in ("/signup", "/signup/"):
            return (200, "OK", "text/html; charset=utf-8", self.render_signup_html())

        if method == "GET" and path == "/auth/workos/login":
            org = (query_params.get("org", ["org_enterprise_300"])[0] or "org_enterprise_300").strip()
            pub_base = self.get_public_base_url(headers=headers)
            redirect_uri = f"{pub_base}/auth/workos/callback"
            if self.workos_client_id:
                sso_url = (
                    "https://api.workos.com/sso/authorize?"
                    + urllib.parse.urlencode({
                        "client_id": self.workos_client_id,
                        "organization": org,
                        "redirect_uri": redirect_uri,
                        "response_type": "code",
                    })
                )
            else:
                sso_url = f"/auth/workos/callback?code=standalone_sso_code&org={urllib.parse.quote(org)}&user=ENTUSER1"
            body = json.dumps({
                "ok": True,
                "redirect_url": sso_url,
                "redirect_uri": redirect_uri,
                "organization_id": org,
            }).encode("utf-8")
            return (200, "OK", "application/json; charset=utf-8", body)

        if method == "GET" and path == "/auth/workos/callback":
            code = (query_params.get("code", [""])[0] or "").strip()
            org = (query_params.get("org", ["org_enterprise_300"])[0] or "org_enterprise_300").strip()
            uname = (query_params.get("user", ["ENTUSER1"])[0] or "ENTUSER1").strip().upper()
            email = f"{uname.lower()}@enterprise.local"
            wos_uid = f"wos_{uname.lower()}"
            pub_base = self.get_public_base_url(headers=headers)
            redirect_uri = f"{pub_base}/auth/workos/callback"
            if code and code != "standalone_sso_code" and self.workos_api_key and self.workos_client_id:
                try:
                    token_body = urllib.parse.urlencode({
                        "client_id": self.workos_client_id,
                        "client_secret": self.workos_api_key,
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri,
                    }).encode("utf-8")
                    req_tok = urllib.request.Request(
                        "https://api.workos.com/sso/token",
                        data=token_body,
                        method="POST",
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded",
                            "User-Agent": "LegacyComputingSystems/1.0",
                        },
                    )
                    with urllib.request.urlopen(req_tok, timeout=5.0) as resp_tok:
                        tok_data = json.loads(resp_tok.read().decode("utf-8"))
                        profile = tok_data.get("profile") or {}
                        if profile.get("email"):
                            email = profile["email"]
                        if profile.get("organization_id"):
                            org = profile["organization_id"]
                        if profile.get("id"):
                            wos_uid = profile["id"]
                        uname = self.derive_dec_username(
                            raw_username=profile.get("first_name", ""),
                            email=email,
                            fallback_id=wos_uid,
                        )
                except Exception:
                    pass
            prov = self.provision_across_targets(
                username=uname,
                password="SSO$300",
                email=email,
                plan="LCS_ENTERPRISE",
                target_os="BOTH",
                workos_org_id=org,
                workos_user_id=wos_uid,
                group=300,
                quota=100000,
            )
            return (200, "OK", "application/json; charset=utf-8", json.dumps(prov, indent=2).encode("utf-8"))

        if method == "GET" and path == "/api/v1/status":
            data = self.get_status_summary()
            return (200, "OK", "application/json; charset=utf-8", json.dumps(data, indent=2).encode("utf-8"))

        if method == "GET" and path == "/api/v1/enterprise/seats":
            org = (query_params.get("org", [""])[0] or "").strip() or None
            seat_data = self.compute_enterprise_seat_Summary(org_id=org)
            return (
                200,
                "OK",
                "application/json; charset=utf-8",
                json.dumps({"ok": True, "dba": DBA_NAME, "seat_metering": seat_data}, indent=2).encode("utf-8"),
            )

        if method == "GET" and path == "/api/v1/coupons":
            coupons = self.load_coupons()
            return (
                200,
                "OK",
                "application/json; charset=utf-8",
                json.dumps({"ok": True, "dba": DBA_NAME, "coupons": coupons}, indent=2).encode("utf-8"),
            )

        if method == "GET" and path == "/api/v1/coupons/validate":
            c_code = (query_params.get("code", [""])[0] or "").strip()
            c_plan = (query_params.get("plan", [""])[0] or "").strip() or None
            v_res = self.validate_and_apply_coupon(c_code, plan=c_plan)
            return (
                200,
                "OK",
                "application/json; charset=utf-8",
                json.dumps(v_res, indent=2).encode("utf-8"),
            )

        if method == "POST" and path == "/api/v1/coupons":
            sig_hdr = headers.get("x-lcs-signature", "")
            if sig_hdr or os.environ.get("LCS_REQUIRE_SIGNATURE") == "1":
                if not self.verify_hmac_signature(body_bytes, sig_hdr, self.lcs_api_secret):
                    err = {"ok": False, "error": "Invalid X-LCS-Signature HMAC-SHA256 signature"}
                    return (401, "Unauthorized", "application/json; charset=utf-8", json.dumps(err).encode("utf-8"))
            try:
                payload = json.loads(body_bytes.decode("utf-8") if body_bytes else "{}")
            except Exception:
                return (
                    400,
                    "Bad Request",
                    "application/json; charset=utf-8",
                    json.dumps({"ok": False, "error": "Invalid JSON body"}).encode("utf-8"),
                )
            try:
                created_c = self.create_discount_coupon(
                    discount_percent=payload.get("discount_percent"),
                    duration_unit=payload.get("duration_unit", "never"),
                    duration_value=payload.get("duration_value"),
                    description=payload.get("description", ""),
                    code=payload.get("code"),
                    created_at=payload.get("created_at"),
                    expires_at=payload.get("expires_at"),
                    local_only=bool(payload.get("local_only")),
                )
                return (
                    201,
                    "Created",
                    "application/json; charset=utf-8",
                    json.dumps({"ok": True, "dba": DBA_NAME, "coupon": created_c}, indent=2).encode("utf-8"),
                )
            except ValueError as ve:
                return (
                    400,
                    "Bad Request",
                    "application/json; charset=utf-8",
                    json.dumps({"ok": False, "error": str(ve)}).encode("utf-8"),
                )

        if method == "GET" and path == "/api/v1/users/check":
            uname = (query_params.get("username", [""])[0] or "").strip()
            res = self.check_username(uname)
            return (200, "OK", "application/json; charset=utf-8", json.dumps(res, indent=2).encode("utf-8"))

        if method == "GET" and path == "/api/v1/users":
            if self.primary_os == "RSTS":
                emu = self._load_rsts_emulator()
                sanitized = {
                    k: {kk: vv for kk, vv in v.items() if kk != "password"}
                    for k, v in emu.accounts.items()
                }
            else:
                emu = self._load_vms_emulator()
                sanitized = {
                    k: {kk: vv for kk, vv in v.items() if kk != "password"}
                    for k, v in emu.users.items()
                }
            return (
                200,
                "OK",
                "application/json; charset=utf-8",
                json.dumps({"ok": True, "os": self.primary_os, "users": sanitized}, indent=2).encode("utf-8"),
            )

        if path in ("/api/v1/signup", "/api/v1/users") and method == "POST":
            # Verify HMAC signature if X-LCS-Signature header is provided or LCS_REQUIRE_SIGNATURE=1
            sig_hdr = headers.get("x-lcs-signature", "")
            if sig_hdr or os.environ.get("LCS_REQUIRE_SIGNATURE") == "1":
                if not self.verify_hmac_signature(body_bytes, sig_hdr, self.lcs_api_secret):
                    err = {"ok": False, "error": "Invalid X-LCS-Signature HMAC-SHA256 signature"}
                    return (401, "Unauthorized", "application/json; charset=utf-8", json.dumps(err).encode("utf-8"))

            try:
                payload = json.loads(body_bytes.decode("utf-8") if body_bytes else "{}")
            except Exception:
                return (
                    400,
                    "Bad Request",
                    "application/json; charset=utf-8",
                    json.dumps({"ok": False, "error": "Invalid JSON body"}).encode("utf-8"),
                )

            username = (payload.get("username") or "").strip().upper()
            password = payload.get("password") or ""
            email = payload.get("email") or ""
            plan = payload.get("plan") or ("LCS_RSTS_10" if self.primary_os == "RSTS" else "LCS_VMS_10")
            target_os = payload.get("target_os")
            if path == "/api/v1/users" and not target_os and "plan" not in payload:
                target_os = self.primary_os
            clerk_user_id = payload.get("clerk_user_id") or ""
            workos_org_id = payload.get("workos_org_id") or ""
            workos_user_id = payload.get("workos_user_id") or ""
            group = payload.get("group")
            quota = payload.get("quota")
            coupon_code = payload.get("coupon_code") or payload.get("coupon") or ""

            try:
                res = self.provision_across_targets(
                    username=username,
                    password=password,
                    email=email,
                    plan=plan,
                    target_os=target_os,
                    clerk_user_id=clerk_user_id,
                    workos_org_id=workos_org_id,
                    workos_user_id=workos_user_id,
                    group=group,
                    quota=quota,
                    coupon_code=coupon_code,
                )
                return (201, "Created", "application/json; charset=utf-8", json.dumps(res, indent=2).encode("utf-8"))
            except ValueError as ve:
                return (
                    400,
                    "Bad Request",
                    "application/json; charset=utf-8",
                    json.dumps({"ok": False, "error": str(ve)}).encode("utf-8"),
                )

        if path.startswith("/api/v1/users/") and method in ("PATCH", "PUT", "POST"):
            target_user = urllib.parse.unquote(path[len("/api/v1/users/"):]).strip()
            if target_user and target_user.lower() != "check":
                sig_hdr = headers.get("x-lcs-signature", "")
                if sig_hdr or os.environ.get("LCS_REQUIRE_SIGNATURE") == "1":
                    if not self.verify_hmac_signature(body_bytes, sig_hdr, self.lcs_api_secret):
                        err = {"ok": False, "error": "Invalid X-LCS-Signature HMAC-SHA256 signature"}
                        return (401, "Unauthorized", "application/json; charset=utf-8", json.dumps(err).encode("utf-8"))

                try:
                    payload = json.loads(body_bytes.decode("utf-8") if body_bytes else "{}")
                except Exception:
                    return (
                        400,
                        "Bad Request",
                        "application/json; charset=utf-8",
                        json.dumps({"ok": False, "error": "Invalid JSON body"}).encode("utf-8"),
                    )

                try:
                    res = self.update_across_targets(
                        identifier=target_user,
                        status=payload.get("status"),
                        password=payload.get("password"),
                        quota=payload.get("quota"),
                        plan=payload.get("plan"),
                        local_only=bool(payload.get("local_only")),
                    )
                    return (200, "OK", "application/json; charset=utf-8", json.dumps(res, indent=2).encode("utf-8"))
                except KeyError as ke:
                    return (
                        404,
                        "Not Found",
                        "application/json; charset=utf-8",
                        json.dumps({"ok": False, "error": str(ke)}).encode("utf-8"),
                    )
                except PermissionError as pe:
                    return (
                        403,
                        "Forbidden",
                        "application/json; charset=utf-8",
                        json.dumps({"ok": False, "error": str(pe)}).encode("utf-8"),
                    )

        if path == "/api/v1/webhooks/clerk" and method == "POST":
            sig_hdr = headers.get("svix-signature") or headers.get("x-clerk-signature") or ""
            if self.clerk_webhook_secret or headers.get("x-clerk-signature"):
                secret = self.clerk_webhook_secret or self.lcs_api_secret
                if not self.verify_hmac_signature(body_bytes, sig_hdr, secret):
                    return (
                        401,
                        "Unauthorized",
                        "application/json; charset=utf-8",
                        json.dumps({"ok": False, "error": "Invalid Clerk webhook signature"}).encode("utf-8"),
                    )
            try:
                payload = json.loads(body_bytes.decode("utf-8") if body_bytes else "{}")
                res = self.handle_clerk_webhook(payload)
                return (200, "OK", "application/json; charset=utf-8", json.dumps(res, indent=2).encode("utf-8"))
            except Exception as e:
                return (
                    400,
                    "Bad Request",
                    "application/json; charset=utf-8",
                    json.dumps({"ok": False, "error": str(e)}).encode("utf-8"),
                )

        if path == "/api/v1/webhooks/workos" and method == "POST":
            sig_hdr = headers.get("workos-signature") or headers.get("x-workos-signature") or ""
            if self.workos_webhook_secret or headers.get("x-workos-signature"):
                secret = self.workos_webhook_secret or self.lcs_api_secret
                if not self.verify_hmac_signature(body_bytes, sig_hdr, secret):
                    return (
                        401,
                        "Unauthorized",
                        "application/json; charset=utf-8",
                        json.dumps({"ok": False, "error": "Invalid WorkOS webhook signature"}).encode("utf-8"),
                    )
            try:
                payload = json.loads(body_bytes.decode("utf-8") if body_bytes else "{}")
                res = self.handle_workos_webhook(payload)
                return (200, "OK", "application/json; charset=utf-8", json.dumps(res, indent=2).encode("utf-8"))
            except Exception as e:
                return (
                    400,
                    "Bad Request",
                    "application/json; charset=utf-8",
                    json.dumps({"ok": False, "error": str(e)}).encode("utf-8"),
                )

        return None
