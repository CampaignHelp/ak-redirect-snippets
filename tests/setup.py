"""Idempotent setup for the ak-redirect-snippets test rig on Robotic Dogs.

Prerequisites — Jordan creates these once in the AK admin UI:
- Signup page named `ch-redirect-test1` (AK REST POST won't stick without
  a signupform/templateset wired up; admin UI handles that cleanly)

This script then:
1. Discovers the page and the dedicated `ch-redirect-test` list
2. Moves the page onto the dedicated list (isolation — test submissions
   don't pollute any default list)
3. Forces every followup.send_* flag off and blanks followup.url
4. Writes .state.json with resource IDs for the runner to pick up

Run `python3 setup.py` — no args.
"""

import json
import pathlib
import sys

from ak_common import NAMESPACE, PAGE_NAME, ak_request, qs

# Custom user fields the recipes reference. AK requires these to be
# registered as AllowedUserField rows before they can be set on users.
REQUIRED_CUSTOM_FIELDS = ["donation_count_2026", "is_monthly_donor"]

STATE_FILE = pathlib.Path(__file__).parent / ".state.json"


def find_by_name(collection, name):
    path = f"/rest/v1/{collection}/?{qs({'name': name, 'format': 'json'})}"
    data = ak_request("GET", path)
    objs = data.get("objects", [])
    if len(objs) > 1:
        sys.exit(f"FATAL: {len(objs)} {collection} records named {name!r} — ambiguous")
    return objs[0] if objs else None


def ensure_allowed_user_fields():
    """AK rejects user.fields writes unless the field name is registered."""
    for name in REQUIRED_CUSTOM_FIELDS:
        existing = find_by_name("alloweduserfield", name)
        if existing:
            print(f"[field] reusing {name}")
            continue
        ak_request("POST", "/rest/v1/alloweduserfield/?format=json", body={"name": name})
        refreshed = find_by_name("alloweduserfield", name)
        if not refreshed:
            sys.exit(f"FATAL: created AllowedUserField {name!r} but could not find it back")
        print(f"[field] registered {name}")


def find_page():
    page = find_by_name("signuppage", PAGE_NAME)
    if not page:
        sys.exit(
            f"FATAL: signup page {PAGE_NAME!r} not found on Robotic Dogs.\n"
            f"       Create it once in the AK admin UI, then re-run setup."
        )
    print(f"[page] found → id={page['id']} status={page['status']} hidden={page['hidden']}")
    return page


def ensure_list():
    existing = find_by_name("list", NAMESPACE)
    if existing:
        print(f"[list] reusing existing → {existing['resource_uri']}")
        return existing
    print(f"[list] creating new list {NAMESPACE!r}")
    ak_request("POST", "/rest/v1/list/?format=json", body={"name": NAMESPACE})
    refreshed = find_by_name("list", NAMESPACE)
    if not refreshed:
        sys.exit("FATAL: created list but could not find it back")
    print(f"[list] created → {refreshed['resource_uri']}")
    return refreshed


def align_page_to_list(page, list_uri):
    if page.get("list") == list_uri:
        print(f"[page] already on dedicated list {list_uri}")
        return
    ak_request(
        "PATCH",
        f"{page['resource_uri']}?format=json",
        body={"list": list_uri},
    )
    print(f"[page] moved onto dedicated list {list_uri}")


def ensure_page_settings(page):
    """Force never_spam_check=True + allow_multiple_responses=True.

    AK's spam filter flags automated submissions as spam; when an action
    is spam, AK skips redirect-URL template eval and falls back to a
    default URL. Must be off for testing."""
    patches = {}
    if not page.get("never_spam_check"):
        patches["never_spam_check"] = True
    if not page.get("allow_multiple_responses"):
        patches["allow_multiple_responses"] = True
    if not patches:
        print("[page] settings already correct")
        return
    ak_request("PATCH", f"{page['resource_uri']}?format=json", body=patches)
    print(f"[page] patched → {patches}")


def reset_followup(page):
    followup = page.get("followup") or {}
    followup_uri = followup.get("resource_uri")
    if not followup_uri:
        sys.exit("FATAL: signup page has no followup resource")
    # followup.url is REQUIRED by AK — can't blank. Park it on a safe
    # placeholder between runs so unrelated traffic hitting the page
    # lands on a neutral page, not a half-configured recipe.
    placeholder = "https://roboticdogs.actionkit.com/thanks/"
    patch = {
        "send_email": False,
        "send_taf": False,
        "send_notifications": False,
        "send_pushes": False,
        "send_texts": False,
        "url": placeholder,
    }
    ak_request("PATCH", f"{followup_uri}?format=json", body=patch)
    print(f"[followup] sends off + url → placeholder → {followup_uri}")
    return followup_uri


def main():
    print("=== ak-redirect-snippets test rig setup ===")
    page = find_page()
    list_obj = ensure_list()
    ensure_allowed_user_fields()
    align_page_to_list(page, list_obj["resource_uri"])
    # Re-fetch page so spam/multi-response flags reflect post-list-swap state
    page = ak_request("GET", f"{page['resource_uri']}?format=json")
    ensure_page_settings(page)
    followup_uri = reset_followup(page)

    # Re-fetch page so state reflects the list swap
    page = ak_request("GET", f"{page['resource_uri']}?format=json")

    state = {
        "list_uri": list_obj["resource_uri"],
        "list_id": list_obj["id"],
        "page_uri": page["resource_uri"],
        "page_id": page["id"],
        "page_name": page["name"],
        "followup_uri": followup_uri,
        "public_url": f"https://roboticdogs.actionkit.com/signup/{page['name']}/",
    }
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
    print()
    print(f"state written → {STATE_FILE}")
    print(f"public URL    → {state['public_url']}")


if __name__ == "__main__":
    main()
