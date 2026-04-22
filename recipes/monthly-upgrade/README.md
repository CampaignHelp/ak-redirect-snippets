# Monthly upgrade redirect

Route one-time donors who aren't already monthly supporters to a monthly-upgrade page. Send everyone else to a standard thank-you.

## What it does

Uses a custom user field (e.g. `is_monthly_donor`) to detect whether someone is already giving monthly. If they just took an action and aren't yet a monthly donor, redirect them to an upgrade page with entry-level monthly amounts. Otherwise, redirect to the standard thank-you.

## Variables used

- `user.custom_fields.is_monthly_donor` — a custom user field your team (or an integration) maintains. **Set to the string `"true"` when a user becomes a monthly donor; leave unset (or set to `"false"`/`""`) otherwise.**

## Why the explicit string comparison

AK stores all custom field values as **strings**, not booleans. The seemingly-natural pattern `{% if not user.custom_fields.is_monthly_donor %}` looks right but fails in a subtle way: if the field is set to the string `"false"`, Django treats any non-empty string as truthy — so `not "false"` is `False`, and the `{% else %}` branch fires for someone who isn't actually a monthly donor.

The explicit equality check (`!= "true"`) sidesteps that entirely. Any value other than the literal string `"true"` — unset, empty, `"false"`, `"0"`, anything — routes to the upgrade page. Be consistent with whatever writes the field (integration, staff tool, etc.) so a single canonical value means "monthly donor."

## Snippet

See `snippet.txt`. Substitute your subdomain, custom field name, and page slugs.

## Use cases

- The moment right after a one-time donation is the highest-leverage time to ask for a monthly upgrade.
- Post-action fundraising follow-up: someone signs a petition and isn't a monthly donor — ask them to convert.

## Fallback

The `{% else %}` branch sends existing monthly donors (and anyone for whom the field evaluates truthy) to a safe thank-you page. Keep it.

## Note

This is an *opportunistic* upgrade path. Don't chain it after a declined ask — people who just said no to one-time giving probably shouldn't immediately see another ask.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22. Both branches pass via the automated Playwright matrix in `tests/` — one user with `is_monthly_donor="true"` routed to the else branch, one without the field (or with `"false"`) routed to the upgrade page.
