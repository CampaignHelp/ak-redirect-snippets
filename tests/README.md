# Tests

End-to-end tests for every recipe in this repo, exercising the real AK redirect URL template against a live AK instance.

## Approach

The tests install each recipe snippet on a single AK signup page, submit the form as a Playwright-driven browser, and capture where the redirect lands. Each recipe's logic is verified by routing every branch to the same known-good landing page with a distinguishing `?branch=...` marker — this isolates "did the right branch fire" from "does the destination URL exist on this instance."

## Prerequisites

1. **An AK instance you can test against.** These tests were written against `roboticdogs.actionkit.com` (ActionKit's public test instance, available to AK customers). You can point them at your own instance by changing `AK_HOST` in `ak_common.py`.

2. **REST API credentials.** Set these in your environment (or `~/.secrets.env`):

   ```bash
   export AK_ROBOTICDOGS_USER="your-admin-username"
   export AK_ROBOTICDOGS_PASS="your-admin-password"
   ```

3. **A signup page named `ch-redirect-test1`** created via the AK admin UI. Required once — AK's REST API won't persist a newly-POSTed signup page without a signupform/templateset wired up, which the admin UI handles cleanly. Any minimal signup page works; the test setup will strip all follow-up emails and put it on a dedicated test list.

4. **Python 3.12+, Playwright, and Chromium.**

   ```bash
   cd tests
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

## Running

```bash
source .venv/bin/activate
python3 setup.py      # one-time: discovers the page, registers custom fields,
                      # parks followup.url on a neutral placeholder
python3 run.py        # runs the full 9-case matrix
python3 cleanup.py    # resets followup.url to the placeholder
```

`run.py --dry-run` exercises all REST setup without submitting any forms.
`run.py --visible` runs Playwright in headed mode so you can watch.

## What the tests cover

Nine cases across four recipes:

| Recipe | Cases |
|---|---|
| `new-vs-returning` | fresh email (if-branch) · existing email (else-branch) |
| `ladder-from-prior-gift` | low count (else-branch) · no prior gift (else-branch) |
| `monthly-upgrade` | not monthly (if-branch) · is monthly (else-branch) |
| `utm-routing` | `?src=facebook` (if) · `?src=email` (elif) · no src (else) |

**Skipped:** the ladder recipe's populated-amounts case requires a user with real donation history (`user.highest_previous_contribution` is AK-computed from orders, not PATCHable via REST). Its branch syntax is identical to the tested fallback.

## Guardrails

Built into `ak_common.py` so setup/run/cleanup all share the same rules:

- **MAX_RETRIES = 2** per HTTP call — fail fast, never hammer
- **Abort on any 5xx** immediately
- **Abort on unexpected 4xx** (expected 404 only during existence probes)
- **500ms sleep** between write operations; **2s wait** after a snippet PATCH before submitting (AK appears to cache `followup.url` briefly)
- **Playwright per-action timeout: 15s**
- **Never log credentials** — auth headers and Basic Auth blobs are not written anywhere
- **Fresh browser context per case** — prevents cookie / session bleed across recipes
- **Test users namespaced** `ch-redirect-test+*@campaign.help` (the `+` aliasing means bounces land in the campaign.help inbox, not a dead address)
- **Dedicated test list** (`ch-redirect-test`) isolates test submissions from any real subscriber list
- **All followup `send_*` flags forced off** — no thank-you emails, TAF, notifications, or pushes fire from test submissions
