# UTM-aware routing

Send users who arrived from different campaigns to different follow-up pages. Useful for tailoring the second ask to the audience that brought them in.

## What it does

`{{ args.* }}` exposes URL parameters present on the original action URL. If a user signed via a link with `?src=facebook`, the redirect can read that parameter and route to a Facebook-tailored follow-up.

## Variables used

- `{{ args.src }}` (or `{{ args.utm_campaign }}`, or any URL parameter you use for campaign tracking).

## Snippet

See `snippet.txt`. Adjust the parameter name and the branches to match your tracking conventions.

## Use cases

- Send Facebook-sourced users to a share-to-Facebook follow-up.
- Send email-sourced users straight to a donation page.
- Preserve the source parameter in the destination URL so downstream actions can be attributed.

## Fallback

Always include `{% else %}` for users who arrive without the tracking parameter. This happens whenever someone shares a link, an email client strips parameters, or a user types the URL manually.

## Gotcha

URL parameters are user-controllable — don't use `{{ args.* }}` values in security-sensitive logic. If you concatenate them into a URL, make sure the resulting URL only points to pages you control.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22 — all three branches (if/elif/else) pass via the automated Playwright matrix in `tests/`. Users arriving at `/signup/<your-page>/?src=<value>` have `{{ args.src }}` automatically available in the redirect URL template — no hidden form inputs needed.
