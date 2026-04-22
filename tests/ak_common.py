"""Shared helpers for the ak-redirect-snippets test runner.

Guardrails live here so setup/run/cleanup all share the same rules:
- MAX_RETRIES = 2 per HTTP call
- Abort on 5xx or unexpected 4xx
- 500ms sleep between write operations
- No secret logging, ever
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AK_HOST = os.environ.get("AK_HOST", "roboticdogs.actionkit.com")
AK_USER = os.environ.get("AK_ROBOTICDOGS_USER") or os.environ.get("AK_USER")
AK_PASS = os.environ.get("AK_ROBOTICDOGS_PASS") or os.environ.get("AK_PASS")

MAX_RETRIES = 2
INTER_CALL_SLEEP = 0.5
REQUEST_TIMEOUT = 15

NAMESPACE = "ch-redirect-test"
# The admin-created signup page on Robotic Dogs. We discover, don't create —
# signup page POST via REST appears to silently roll back without a
# signupform/templateset wired in, so Jordan created this one in the AK admin UI.
PAGE_NAME = "ch-redirect-test1"
TEST_EMAIL_TEMPLATE = "ch-redirect-test+{case}@campaign.help"


def _auth_header():
    if not AK_USER or not AK_PASS:
        sys.exit("FATAL: AK_ROBOTICDOGS_USER / AK_ROBOTICDOGS_PASS not set")
    blob = base64.b64encode(f"{AK_USER}:{AK_PASS}".encode()).decode()
    return f"Basic {blob}"


def _sleep_between_calls():
    time.sleep(INTER_CALL_SLEEP)


def ak_request(method, path, body=None, allow_404=False):
    """REST call with retries and hard-abort guardrails.

    - Retries transient errors up to MAX_RETRIES times
    - Aborts the process on 5xx immediately (no retry)
    - Aborts on 4xx unless allow_404=True and the status is 404
    """
    url = f"https://{AK_HOST}{path}"
    headers = {
        "Authorization": _auth_header(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                raw = resp.read().decode()
                if not raw:
                    return {"_status": resp.status, "_location": resp.headers.get("Location")}
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"_status": resp.status, "_raw": raw}
        except urllib.error.HTTPError as e:
            # 5xx → abort the whole run immediately
            if 500 <= e.code < 600:
                sys.exit(f"FATAL 5xx from AK: {method} {path} → HTTP {e.code}")
            # expected 404 for existence probes
            if e.code == 404 and allow_404:
                return None
            # other 4xx → abort
            err_body = ""
            try:
                err_body = e.read().decode()[:500]
            except Exception:
                pass
            sys.exit(f"FATAL 4xx from AK: {method} {path} → HTTP {e.code} {err_body}")
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                time.sleep(1)
                continue
            sys.exit(f"FATAL transport error after {MAX_RETRIES} attempts: {method} {path} → {e}")
        finally:
            if method in ("POST", "PATCH", "PUT", "DELETE"):
                _sleep_between_calls()

    sys.exit(f"FATAL unreachable retry exit: {last_err}")


def preview(obj, maxlen=200):
    """Safe preview that never exposes credentials."""
    s = json.dumps(obj, default=str)
    if len(s) > maxlen:
        s = s[:maxlen] + "..."
    return s


def qs(params):
    """Build a URL-encoded query string. `+` in emails must stay as `+`,
    not get decoded to space, so always route through urlencode."""
    return urllib.parse.urlencode(params)
