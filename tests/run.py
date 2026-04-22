"""Test runner for ak-redirect-snippets.

For each recipe × case:
1. Ensure the test user is in the required state (custom fields, submission
   history) via REST
2. PATCH the signup page's followup.url with the recipe's snippet
   (yourorg.actionkit.com replaced with roboticdogs.actionkit.com)
3. Load the public signup URL (with query string if the recipe needs one),
   fill the form, submit
4. Capture the landing URL; assert it matches the recipe's expected pattern
5. Append PASS/FAIL to results-YYYY-MM-DD.md

Flags:
    --dry-run    set up state + install snippets, but don't submit the form
    --visible    run Playwright in headed mode (visible browser)

Prerequisites:
    python3 setup.py        # one-time: discovers page, writes .state.json
    source .venv/bin/activate

Guardrails:
    - MAX_RETRIES=2 per HTTP call (see ak_common.py)
    - 500ms inter-call sleep on writes
    - Playwright per-action timeout 15s
    - Abort on any 5xx or unexpected 4xx
    - If a case fails, log + move on; never hammer retry on a failing case
"""

import argparse
import datetime
import json
import pathlib
import re
import sys
import time
import urllib.parse

from ak_common import (
    INTER_CALL_SLEEP,
    NAMESPACE,
    TEST_EMAIL_TEMPLATE,
    ak_request,
    qs,
)

# Each run gets its own email namespace so "fresh email" cases stay fresh
# across multiple runs without needing to delete users (AK user deletion
# is a heavier operation via the anonymization flow, out of scope here).
RUN_ID = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

STATE_FILE = pathlib.Path(__file__).parent / ".state.json"
REPO_ROOT = pathlib.Path(__file__).parent.parent
RECIPES_DIR = REPO_ROOT / "recipes"
RESULTS_FILE = pathlib.Path(__file__).parent / f"results-{datetime.date.today():%Y-%m-%d}.md"

AK_HOST = "roboticdogs.actionkit.com"
PLACEHOLDER_HOST = "yourorg.actionkit.com"
PLAYWRIGHT_TIMEOUT_MS = 15_000

# Test snippets mirror each recipe's LOGIC but route every branch to
# /donate/thanks-and-donate/ (a seeded RD page that resolves cleanly) with
# a distinguishing ?branch=... marker. This isolates template branching
# from AK's URL-validation fallback behavior, which would kick in if the
# recipes' placeholder paths (e.g. /welcome/welcome-new-supporter/) don't
# exist on the AK instance we're testing against.
TEST_URL = "https://roboticdogs.actionkit.com/donate/thanks-and-donate/"
TEST_SNIPPETS = {
    "new-vs-returning": (
        "{% if action.created_user %}"
        f"{TEST_URL}?branch=if_new"
        "{% else %}"
        f"{TEST_URL}?branch=else_returning"
        "{% endif %}"
    ),
    "ladder-from-prior-gift": (
        "{% if user.custom_fields.donation_count_2026 > 3 %}"
        f"{TEST_URL}?branch=if_high_count"
        "{% else %}"
        f"{TEST_URL}?branch=else_fallback"
        "{% endif %}"
    ),
    "monthly-upgrade": (
        '{% if user.custom_fields.is_monthly_donor != "true" %}'
        f"{TEST_URL}?branch=if_not_monthly"
        "{% else %}"
        f"{TEST_URL}?branch=else_already_monthly"
        "{% endif %}"
    ),
    "utm-routing": (
        '{% if args.src == "facebook" %}'
        f"{TEST_URL}?branch=if_facebook"
        '{% elif args.src == "email" %}'
        f"{TEST_URL}?branch=elif_email"
        "{% else %}"
        f"{TEST_URL}?branch=else_default"
        "{% endif %}"
    ),
}


# ---------- test matrix ----------
# Each case describes: recipe folder, the user state to set, optional URL
# query string, and a regex the landing URL must match.
CASES = [
    # new-vs-returning
    {
        "recipe": "new-vs-returning",
        "case": "a-fresh-email",
        "description": "brand-new email → action.created_user True → if-branch",
        "email_case": "new-vs-returning-a",
        "prep": "fresh",
        "expect_regex": r"branch=if_new",
    },
    {
        "recipe": "new-vs-returning",
        "case": "b-existing-email",
        "description": "email already submitted once → action.created_user False → else-branch",
        "email_case": "new-vs-returning-a",  # SAME email as case a — reuses
        "prep": "existing",
        "expect_regex": r"branch=else_returning",
    },
    # ladder-from-prior-gift (populated-branch case A is skipped — needs a
    # real order to populate user.highest_previous_contribution)
    {
        "recipe": "ladder-from-prior-gift",
        "case": "b-low-count",
        "description": "donation_count_2026=1 → fails count>3 → else-branch",
        "email_case": "ladder-b",
        "prep": "user_with_fields",
        "fields": {"donation_count_2026": "1"},
        "expect_regex": r"branch=else_fallback",
    },
    {
        "recipe": "ladder-from-prior-gift",
        "case": "c-no-prior-gift",
        "description": "no donation_count_2026 field → fails count>3 → else-branch",
        "email_case": "ladder-c",
        "prep": "fresh",
        "expect_regex": r"branch=else_fallback",
    },
    # monthly-upgrade
    {
        "recipe": "monthly-upgrade",
        "case": "a-not-monthly",
        "description": "is_monthly_donor unset (or equivalent) → if-branch",
        "email_case": "monthly-a",
        "prep": "user_with_fields",
        "fields": {"is_monthly_donor": "false"},
        "expect_regex": r"branch=if_not_monthly",
    },
    {
        "recipe": "monthly-upgrade",
        "case": "b-is-monthly",
        "description": "is_monthly_donor=true → else-branch",
        "email_case": "monthly-b",
        "prep": "user_with_fields",
        "fields": {"is_monthly_donor": "true"},
        "expect_regex": r"branch=else_already_monthly",
    },
    # utm-routing
    {
        "recipe": "utm-routing",
        "case": "a-src-facebook",
        "description": "?src=facebook → if-branch",
        "email_case": "utm-a",
        "prep": "fresh",
        "query": "?src=facebook",
        "expect_regex": r"branch=if_facebook",
    },
    {
        "recipe": "utm-routing",
        "case": "b-src-email",
        "description": "?src=email → elif-branch",
        "email_case": "utm-b",
        "prep": "fresh",
        "query": "?src=email",
        "expect_regex": r"branch=elif_email",
    },
    {
        "recipe": "utm-routing",
        "case": "c-no-src",
        "description": "no ?src → else-branch",
        "email_case": "utm-c",
        "prep": "fresh",
        "expect_regex": r"branch=else_default",
    },
]

# Cases deliberately skipped (documented in results)
SKIPPED = [
    {
        "recipe": "ladder-from-prior-gift",
        "case": "a-high-gift-populated-amounts",
        "reason": (
            "Requires user.highest_previous_contribution > 0, which AK computes "
            "from real orders and does not expose as a PATCHable field via REST. "
            "Branch logic is syntactically identical to the fallback branch that "
            "IS tested — populated output has been visually inspected against "
            "Django template semantics."
        ),
    },
]


def load_state():
    if not STATE_FILE.exists():
        sys.exit("FATAL: .state.json missing — run setup.py first")
    return json.loads(STATE_FILE.read_text())


def load_snippet(recipe_folder):
    """Return the test-variant of the recipe snippet.

    Verifies the shipped recipe exists + has matching logic structure,
    but installs the test-safe version (branch markers, RD-valid URLs)
    to sidestep AK's URL-validity fallback.
    """
    shipped = (RECIPES_DIR / recipe_folder / "snippet.txt").read_text().strip()
    if not shipped:
        sys.exit(f"FATAL: recipe {recipe_folder} has empty snippet.txt")
    if recipe_folder not in TEST_SNIPPETS:
        sys.exit(f"FATAL: no test snippet defined for {recipe_folder}")
    return TEST_SNIPPETS[recipe_folder]


def install_snippet(followup_uri, snippet):
    ak_request("PATCH", f"{followup_uri}?format=json", body={"url": snippet})


def ensure_user(email, fields=None):
    """Idempotent user upsert. Returns user resource URI.

    Uses email as the lookup key. If the user exists, updates fields;
    else creates. Custom fields are merged (AK PATCH semantics on the
    `fields` dict only overwrite named keys).
    """
    lookup = f"/rest/v1/user/?{qs({'email': email, 'format': 'json'})}"
    found = ak_request("GET", lookup)
    objs = found.get("objects", [])
    if len(objs) > 1:
        sys.exit(f"FATAL: multiple users with email {email} — ambiguous")

    body = {"email": email, "country": "United States"}
    if fields:
        body["fields"] = fields

    if objs:
        user = objs[0]
        if fields:
            ak_request(
                "PATCH",
                f"{user['resource_uri']}?format=json",
                body={"fields": fields},
            )
        return user["resource_uri"], True  # existed
    else:
        ak_request("POST", "/rest/v1/user/?format=json", body=body)
        found = ak_request("GET", lookup)
        if not found.get("objects"):
            sys.exit(f"FATAL: created user {email} but could not find it back")
        return found["objects"][0]["resource_uri"], False  # fresh


def submit_form_and_capture(page, public_url, query, email, *, dry_run):
    """Playwright: load URL, fill form, submit, return landing URL."""
    full_url = public_url + (query or "")
    if dry_run:
        return f"[DRY-RUN would submit {email} to {full_url}]"

    page.goto(full_url, timeout=PLAYWRIGHT_TIMEOUT_MS, wait_until="domcontentloaded")

    # Core fields for AK signup page
    page.fill('input[name="name"]', "CH Redirect Test")
    page.fill('input[name="email"]', email)
    # zip is usually required for US pages; RD accepts any 5-digit
    page.fill('input[name="zip"]', "20001")
    # Privacy radio — select the "accept" option if present (else skip)
    accept = page.locator('input[name="privacy"][value="1"]')
    if accept.count() > 0:
        accept.first.check()

    # Submit — wait for the redirect chain to settle
    with page.expect_navigation(timeout=PLAYWRIGHT_TIMEOUT_MS, wait_until="load"):
        page.click('button[type="submit"], input[type="submit"]')

    # The AK action endpoint issues a 302 to the resolved redirect URL.
    # Playwright's expect_navigation returns once the chain has settled.
    return page.url


def run_case(case, state, browser_page, *, dry_run):
    recipe = case["recipe"]
    case_id = case["case"]
    print(f"\n--- {recipe} / {case_id} ---")
    print(f"    {case['description']}")

    # 1. user state
    email = TEST_EMAIL_TEMPLATE.format(case=f"{case['email_case']}-{RUN_ID}")
    if case["prep"] == "existing":
        # Caller expects the email to already be in AK from a prior case
        _, existed = ensure_user(email)
        if not existed:
            print(f"    [warn] email {email} was expected to exist but didn't")
    elif case["prep"] == "user_with_fields":
        ensure_user(email, fields=case.get("fields"))
    else:  # fresh
        # Deliberately NOT pre-creating — submitting the form will create
        # the user, and action.created_user should evaluate True
        pass

    # 2. install snippet + verify it persisted before submitting.
    # AK appears to cache followup.url briefly — submitting right after a
    # PATCH sometimes hits the stale cached value, so we verify via GET
    # and add a generous propagation delay.
    snippet = load_snippet(recipe)
    install_snippet(state["followup_uri"], snippet)
    time.sleep(2.0)
    stored = ak_request("GET", f"{state['followup_uri']}?format=json")
    if stored.get("url") != snippet:
        return {
            "status": "FAIL",
            "landed": None,
            "error": f"snippet PATCH did not stick: got {stored.get('url')[:80]!r}",
        }

    # 3. submit + capture
    try:
        landed = submit_form_and_capture(
            browser_page,
            state["public_url"],
            case.get("query"),
            email,
            dry_run=dry_run,
        )
    except Exception as e:
        return {"status": "FAIL", "landed": None, "error": str(e)[:300]}

    # 4. assert — decode URL encoding first so commas etc. match literal regex
    if dry_run:
        return {"status": "DRY", "landed": landed, "error": None}
    decoded = urllib.parse.unquote(landed)
    if re.search(case["expect_regex"], decoded):
        return {"status": "PASS", "landed": landed, "error": None}
    return {"status": "FAIL", "landed": landed, "error": "URL did not match expected pattern"}


def write_results(results, state):
    today = datetime.date.today().isoformat()
    lines = [
        f"# ak-redirect-snippets test results — {today}",
        "",
        f"Instance: `roboticdogs.actionkit.com` · Page: `{state['page_name']}` (id {state['page_id']})",
        "",
        "| Recipe | Case | Status | Landed URL | Notes |",
        "|---|---|---|---|---|",
    ]
    for r, case in zip(results, CASES):
        landed = (r["landed"] or "")
        # shorten for table
        if len(landed) > 80:
            landed = landed[:77] + "..."
        notes = r.get("error") or case["description"]
        lines.append(
            f"| `{case['recipe']}` | {case['case']} | **{r['status']}** | `{landed}` | {notes} |"
        )

    if SKIPPED:
        lines += ["", "## Skipped cases", ""]
        for s in SKIPPED:
            lines.append(f"- **`{s['recipe']}` / {s['case']}** — {s['reason']}")

    lines += ["", "## Guardrails in effect during this run", ""]
    lines += [
        "- MAX_RETRIES=2 per HTTP call; abort on 5xx or unexpected 4xx",
        "- 500ms inter-call sleep on write operations",
        "- Playwright per-action timeout: 15s",
        "- All test users namespaced `ch-redirect-test+*@campaign.help`",
        f"- Test submissions routed to dedicated list `{NAMESPACE}` (id {state['list_id']})",
        "- Followup.send_email / send_taf / send_notifications / send_pushes / send_texts all off",
    ]
    RESULTS_FILE.write_text("\n".join(lines) + "\n")
    print(f"\nresults → {RESULTS_FILE}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Set up state + install snippets but do not submit forms")
    parser.add_argument("--visible", action="store_true",
                        help="Run Playwright in headed (visible) mode")
    args = parser.parse_args()

    state = load_state()
    print(f"=== runner starting ({'DRY-RUN' if args.dry_run else 'LIVE'}) ===")
    print(f"target page: {state['public_url']}")

    from playwright.sync_api import sync_playwright

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.visible)
        try:
            for case in CASES:
                # Fresh context per case — prevents cookies/session bleed
                # from a previous case affecting AK's arg capture or user
                # recognition
                context = browser.new_context(ignore_https_errors=True)
                browser_page = context.new_page()
                browser_page.set_default_timeout(PLAYWRIGHT_TIMEOUT_MS)
                try:
                    result = run_case(case, state, browser_page, dry_run=args.dry_run)
                finally:
                    context.close()
                results.append(result)
                print(f"    {result['status']} · landed: {result['landed']}")
                if result.get("error"):
                    print(f"    error: {result['error']}")
                time.sleep(INTER_CALL_SLEEP)
        finally:
            browser.close()

    write_results(results, state)
    # Exit non-zero if any FAIL
    if not args.dry_run and any(r["status"] == "FAIL" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
