"""Reset the test rig on Robotic Dogs after a run.

Parks the test page's followup.url on a neutral placeholder so any
incidental traffic hitting `/signup/ch-redirect-test1/` lands cleanly.

Test users (`ch-redirect-test+*@campaign.help`) are left on the dedicated
`ch-redirect-test` list — intentional, so you can inspect past test
submissions in the AK admin afterward. The list is isolated from any
real subscribers, so they're harmless.

Run `python3 cleanup.py` — no args.
"""

import json
import pathlib
import sys

from ak_common import ak_request

STATE_FILE = pathlib.Path(__file__).parent / ".state.json"
PLACEHOLDER_URL = "https://roboticdogs.actionkit.com/thanks/"


def main():
    if not STATE_FILE.exists():
        sys.exit("FATAL: .state.json missing — nothing to clean up")
    state = json.loads(STATE_FILE.read_text())
    print(f"parking followup.url for {state['page_name']} → {PLACEHOLDER_URL}")
    ak_request(
        "PATCH",
        f"{state['followup_uri']}?format=json",
        body={"url": PLACEHOLDER_URL},
    )
    print("done")


if __name__ == "__main__":
    main()
