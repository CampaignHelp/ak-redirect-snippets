# Donation ladder from prior gift

Route returning donors to a donation page pre-filled with ask amounts scaled from their highest previous contribution. Route new donors (with no giving history) to a monthly-giving page with entry-level amounts.

## Credit

This recipe is adapted directly from **Shannon Turner's** ClientCon 2026 demonstration of *Snippets in redirect URLs*. She presented this exact pattern as the flagship example of the feature. All credit for the technique goes to her.

- Shannon on GitHub: [@shannonturner](https://github.com/shannonturner)
- Shannon's consultancy, Supraluminique: [fasterthanlight.tech](https://fasterthanlight.tech)
- Shannon's ActionKit materials: [shannonturner/actionkit-clientcon-2025](https://github.com/shannonturner/actionkit-clientcon-2025)

## What it does

If the user has donated more than three times this year, build a donation URL with ask amounts scaled to their highest previous contribution — `0.5×`, `0.75×`, `1×`, `1.25×`, and `1.5×` that value. Otherwise, send them to a monthly-giving page with entry-level amounts.

## Variables used

- `user.custom_fields.donation_count_2026` — a custom user field your team maintains. Swap the field name / year as needed.
- `user.highest_previous_contribution` — built-in AK field; the user's largest prior gift.
- `|multiply:N` — Django template filter for arithmetic.

## Snippet

See `snippet.txt`. Replace `yourorg.actionkit.com` with your subdomain, adjust the custom field name (`donation_count_2026`) to match your instance, and update the page slug (`donate/donate/`).

## Pairs with

See [`../../reference/donation-url-params.md`](../../reference/donation-url-params.md) for the `amounts=` and `monthly_amounts=` URL parameters used here. Only works on NGP VAN Payments-enabled donation pages.

## Use cases

- **Laddering** — gently push a mid-tier donor toward a higher gift based on what they've given before.
- **Monthly-first** — send users with no giving history directly to a monthly page instead of a one-time page.

## Fallback

If `user.highest_previous_contribution` is null (user has never donated), the `|multiply` filters may produce unusable values. A safer variant adds a defensive guard:

```django
{% if user.highest_previous_contribution and user.custom_fields.donation_count_2026 > 3 %}
  (ladder URL)
{% else %}
  (entry-level URL)
{% endif %}
```

The `{% else %}` branch is the fallback — it catches both new donors and anyone with a broken custom field. Keep it.

## Testing

Test as at least three users before going live:

1. A donor with `donation_count_2026 > 3` and a real `highest_previous_contribution` value.
2. A donor with `donation_count_2026 ≤ 3`.
3. A user who's never donated (no `highest_previous_contribution`) — confirm the fallback fires.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22. The `{% else %}` branch (cases 2 and 3 above) passes via the automated Playwright matrix in `tests/`. Case 1 (populated ladder URL) requires a user with real donation history, which can't be planted via REST; its branch logic is syntactically identical to the fallback and has been visually verified.
