# Escalation ladder by prior action

Route signers to the *next* step in your engagement ladder based on what they've already done. If they've already taken the harder ask, send them to the next one up.

## What it does

Uses AK's built-in `actiontaken` template filter to check whether the user has previously taken action on a specific page. The classic use is post-petition routing: if a signer has already called their rep, send them straight to the donation page — don't ask them to call again. If they haven't called yet, route them to the call page to escalate.

## Variables used

- `user|actiontaken:PAGE_ID` — AK-native template filter. Returns `1` if the user has any prior action on the given page id, `0` otherwise. Works on every AK instance; no custom setup, integration, or per-user field maintenance required.

## Why this is portable

Unlike custom-field patterns (`user.custom_fields.signed_petition_xyz`), `actiontaken` reads directly from the action history AK already tracks. There's nothing for the organization to wire up — no "User Update" after-action, no integration writing a flag, no per-page boilerplate. Drop the recipe in, swap the page id, ship.

## Finding the page id

`actiontaken` takes a numeric page id, not a slug. To find a page's id in ActionKit:

- **Admin UI:** open the page in the AK admin. The URL ends in `/admin/cms/signuppage/<id>/` — that's your page id.
- **REST API:** `GET /rest/v1/signuppage/?name=<slug>&format=json` returns `objects[0].id`.

The id is stable across the page's lifetime — safe to hardcode in a redirect URL snippet.

## Snippet

See `snippet.txt`. Replace `yourorg.actionkit.com` with your subdomain, swap `PRIOR_PAGE_ID` for the actual page id you're gating on, and update the destination slugs.

## Use cases

- **Petition → call → donate.** Signers who haven't called yet → call page. Signers who already called → donate page. (Three-step ladder below.)
- **Avoid asking the same thing twice.** Don't send someone who already RSVP'd to an event back to the event page; send them to a "bring a friend" share page instead.
- **Reward existing supporters.** If they already donated this cycle, skip the donation ask and send them to a high-value organizing page (volunteer signup, host an event, etc.).

## Going further — three-step ladder

The recipe above is binary. For a longer ladder, chain `actiontaken` checks with `{% elif %}`, ordered from highest commitment down:

```django
{% if user|actiontaken:DONATE_PAGE_ID %}
https://yourorg.actionkit.com/share/thanks-and-share/
{% elif user|actiontaken:CALL_PAGE_ID %}
https://yourorg.actionkit.com/donate/donate/
{% else %}
https://yourorg.actionkit.com/call/call-your-rep/
{% endif %}
```

Read top-to-bottom: "If they've already donated → send to share. Else if they've already called → escalate to donate. Else → escalate to call." Put your strongest ask at the top so signers who've done it skip past; weaker asks fall through to it.

## Tag-based variation

If your "prior action" is really a set of pages (e.g., "any of our 2026 climate petitions"), tag those pages in the AK admin and use `tagged` instead:

```django
{% if user|tagged:"climate-petition" %}
https://yourorg.actionkit.com/call/call-on-climate/
{% else %}
https://yourorg.actionkit.com/petition/sign-climate-petition/
{% endif %}
```

`{{ user|tagged:"name" }}` returns 1 if the user has taken action on *any* page tagged with that name. Useful when you care about the campaign, not the specific page.

## Fallback

The `{% else %}` branch is the fallback for everyone who hasn't taken the gated action. Keep it pointed at a real, valid URL — every signer who hits the page for the first time will hit this branch, so it has to work.

## Gotchas

- **The current submission usually counts.** When the user submits page X, by the time the redirect URL template evaluates, AK has already created the action on X. So `user|actiontaken:X_ID` returns 1 from the *first* submission of page X onward. This is fine for cross-page laddering (the common case — "did they call before submitting this petition?"), but be careful if you ever check `actiontaken` against the *same* page the snippet is installed on — every signer will look like a returning user.
- **Page ids are numeric.** `user|actiontaken:"climate-petition"` does not work — pass the integer id, not the slug.
- **Page ids are not portable across instances.** Page id 42 on your staging instance is a different page on production. If you sync content between instances, the recipe needs different ids on each side.
- **No per-action filtering.** `actiontaken` only tells you whether the user has *ever* taken action on the page — not when, not how many times, not from which source. If you need "called in the last 30 days" granularity, you're back to either a custom field (set by a workflow/integration) or a query-driven email send instead of a redirect.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-05-15. Both branches pass via the automated Playwright matrix in `tests/`:
- A fresh user submitting against an unrelated page id → `{% else %}` branch (no prior action).
- A returning user submitting again, with the snippet checking the page they previously submitted → `{% if %}` branch (prior action recorded).
