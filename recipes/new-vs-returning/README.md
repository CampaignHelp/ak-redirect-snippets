# New vs. returning user redirect

Route first-time supporters (newly created by this action) to a welcome page. Route returning supporters to a follow-up ask.

## What it does

- `{% if action.created_user %}` is `True` when the action just created a new user record in ActionKit — i.e. this is someone's first interaction.
- `{% else %}` covers users who were already in the database.

## Variables used

- `action.created_user` — `True` if this action created a new user, `False` if the user already existed.

## Snippet

See `snippet.txt`. Replace `yourorg.actionkit.com` and the page slugs with your own.

## Use cases

- Onboard first-time signers with a welcome message before asking for anything else.
- Skip the welcome for returning users and go straight to a second ask.
- A/B-test whether new signers convert better when given a welcome versus an immediate follow-up.

## Fallback

The `{% else %}` branch is the fallback — it covers every user `action.created_user` evaluates to `False` for, which is the overwhelming majority. Don't remove it.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22. Both branches pass via the automated Playwright matrix in `tests/`. Note: when piloting this on your own instance, make sure the welcome URL actually resolves to a real page — AK silently falls back to a default thank-you URL if the rendered redirect points to a path that 404s on your subdomain.
