# Monthly upgrade redirect

Route one-time donors (and most other supporters) to a monthly-giving upgrade page with entry-level amounts. Send existing monthly donors straight to a standard thank-you.

## What this recipe does

After any AK action submission, this snippet checks whether the supporter is already a monthly donor. If they're **not** (or you don't know — same outcome), they get redirected to an upgrade page with monthly ask amounts pre-set. If they **are** already giving monthly, they get a standard thank-you instead of being asked to upgrade something they're already doing.

The check uses a custom user field your team maintains. That maintenance burden is the main thing to plan for — see *What you need before you install*.

## Who this is for

Use this when:

- You've decided monthly recurring giving is a strategic priority (and aren't trying to maximize this-week's one-time revenue at the expense of it).
- Your team can keep an `is_monthly_donor` flag up to date — set when someone starts a monthly gift, unset when they cancel.
- Your donation page is a **Payments-enabled** AK page (the `monthly_amounts=` parameter only works there — see top-level README → *Some features are Payments-only*).

Skip this if:

- You can't keep the monthly-donor flag fresh. A stale flag sends current monthly donors back to the upgrade page (annoying) or sends ex-monthly donors past it (missed reactivation).
- You're already running an aggressive monthly conversion path elsewhere — chaining two monthly asks back-to-back trains supporters to ignore them.

## The snippet

```django
{% if user.custom_fields.is_monthly_donor != "true" %}
https://yourorg.actionkit.com/donate/go-monthly/?monthly_amounts=5,10,15,20,25,30
{% else %}
https://yourorg.actionkit.com/donate/thanks/
{% endif %}
```

A clean copy lives in `snippet.txt` next to this README.

## How the snippet works, line by line

If you've never seen Django template syntax before — the bits inside `{% %}` are placeholders that AK evaluates when a supporter submits the form. The rest is the literal URL AK will redirect to.

### Line 1 — the condition

```django
{% if user.custom_fields.is_monthly_donor != "true" %}
```

Read this line as: "If the user's `is_monthly_donor` custom field is **not** the string `"true"`, use the next URL."

- `user.custom_fields.is_monthly_donor` — a custom user field your team adds and maintains. The name is up to you (`is_sustainer`, `monthly_status`, etc.); just keep it consistent.
- `!= "true"` — comparison: the value is anything other than the literal string `"true"`. That includes unset, empty, `"false"`, `"0"`, `"no"`, or any other value. All of those send the supporter to the upgrade branch.

### Why the explicit string comparison

AK stores all custom field values as **strings**, not booleans — even ones that look like numbers or true/false. The pattern that *looks* natural — `{% if not user.custom_fields.is_monthly_donor %}` — fails in a subtle way.

If the field is set to the literal string `"false"`, Django treats any non-empty string as truthy. So `not "false"` evaluates to `False`, and the `{% else %}` branch fires for someone who isn't actually a monthly donor. The upgrade ask never happens.

The explicit equality check (`!= "true"`) sidesteps that. Any value other than the literal string `"true"` routes to the upgrade page. Be consistent with whatever writes the field (your integration, your staff tool, your nightly sync) so a single canonical value — exactly `"true"`, lowercase, no spaces — means "monthly donor."

### Line 2 — the upgrade URL

```django
https://yourorg.actionkit.com/donate/go-monthly/?monthly_amounts=5,10,15,20,25,30
```

The URL AK redirects non-monthly supporters to. The fixed parts:

- `https://yourorg.actionkit.com/donate/go-monthly/` — your monthly-upgrade donation page. Replace `yourorg` and the slug with yours.
- `?monthly_amounts=5,10,15,20,25,30` — sets the buttons on the **Monthly** tab of the donation page. Entry-level amounts; pick numbers appropriate for first-time monthly donors at your org.

See `reference/donation-url-params.md` for the full set of ask-amount parameters.

### Lines 3–4 — the fallback branch

```django
{% else %}
https://yourorg.actionkit.com/donate/thanks/
```

`{% else %}` catches existing monthly donors — anyone whose `is_monthly_donor` field is exactly `"true"`. These supporters already chose to give monthly, so asking them to "upgrade" makes no sense. Send them to a standard thank-you page instead.

### Line 5 — close the conditional

```django
{% endif %}
```

Closes the `{% if %}`. Every `{% if %}` needs a matching `{% endif %}` below it.

## What you need before you install

- A **Payments-enabled** AK donation page. The `monthly_amounts=` parameter is silently ignored on legacy donation pages.
- A **custom user field** called `is_monthly_donor` (or whatever you want to call it). Two things have to write to it:
  - When a supporter starts a monthly gift → write `"true"`. Easiest setup: an after-action user-update on your monthly donation page.
  - When a supporter's monthly gift cancels → write `"false"` (or unset). Source of truth here is your payment processor (NGP, Stripe, etc.) — usually via a webhook or nightly sync into AK.
- A monthly-upgrade donation page distinct from your standard donation page. The upgrade page should lead with a monthly framing, not a one-time ask.
- A standard thank-you page for existing monthly donors. Bonus points if it acknowledges they're already a sustainer ("Thank you — you're already one of our monthly donors.").

## How to install

1. Copy the contents of `snippet.txt`.
2. In AK admin, open the page you want to add the redirect to.
3. Click the **After-action info** tab.
4. Paste the snippet into the **Redirect URL** field. Do not wrap it in quotes (see top-level README → *Don't wrap the snippet in quotes*).
5. Replace `yourorg.actionkit.com` with your subdomain. Update the custom field name if yours differs from `is_monthly_donor`. Update both page slugs.
6. Save the page.
7. Test before announcing the campaign (see *How to test* below).

## What can go wrong (specific to this recipe)

### The flag isn't actually maintained

The most common failure: someone sets up the snippet, writes `"true"` to the field when monthly donations come in, and never wires up the cancellation side. Six months later, a third of the supporters tagged as `is_monthly_donor=true` aren't actually giving monthly anymore. They see the standard thank-you and you miss the chance to reactivate.

Check your churn against the flag quarterly. If you can't trust the data, the snippet is doing the wrong thing for the people whose data is stale.

### Capitalization mismatch

`"true"`, `"True"`, and `"TRUE"` are three different strings to Django. The recipe expects exactly `"true"` (lowercase). If your integration writes `"True"`, every monthly donor hits the upgrade branch and gets asked to upgrade something they're already doing.

Pick one canonical value, document it next to the field definition, and audit anything that writes to the field.

### Chained after a declined ask

Don't put this snippet on a page someone just landed on *after* declining a different fundraising ask. A supporter who just clicked "no thanks" on a one-time donation page is the worst possible audience for an immediate monthly upgrade. The redirect snippet doesn't know they declined — it just sees the action submission.

Place this snippet on petitions, surveys, RSVPs, share pages — actions where the supporter expressed support without having just refused to give money.

### Entry-level amounts are too high (or too low)

`$5–$30/month` is a reasonable default for a national progressive list, but your audience might be different. If you have a heavily blue-collar or student base, $5/month might still feel like a stretch — consider starting at $3. If your typical one-time donor is mid-four-figures, starting monthly asks at $5 looks insulting — push the floor up.

Look at the distribution of your existing monthly donor pledges and pick amounts that span the 25th–75th percentile.

## How to test

You'll need at least two test scenarios:

1. **Non-monthly donor test.** Use a test user where `is_monthly_donor` is unset, empty, `"false"`, or anything other than exactly `"true"`. Submit the form. Confirm the destination URL is your upgrade page with the `?monthly_amounts=…` parameter.
2. **Monthly donor test.** Set `is_monthly_donor = "true"` on a test user. Submit. Confirm the destination URL is your standard thank-you.

For both, load the destination page and confirm it renders correctly. For test 1, confirm the monthly tab on the upgrade page shows your specified amounts — if it shows the page's defaults instead, the page is probably not Payments-enabled or the parameter is being stripped.

The `tests/` folder in this repo automates both cases against the Robotic Dogs sandbox via Playwright.

## How to know if it's working

The snippet is doing its job if non-monthly supporters who hit the upgrade page **convert to monthly at a measurable rate** without tanking your one-time donation revenue.

Tagged version of the snippet:

```django
{% if user.custom_fields.is_monthly_donor != "true" %}
https://yourorg.actionkit.com/donate/go-monthly/?monthly_amounts=5,10,15,20,25,30&utm_source=ak-redirect&utm_campaign=monthly-upgrade&utm_content=upgrade-ask
{% else %}
https://yourorg.actionkit.com/donate/thanks/?utm_source=ak-redirect&utm_campaign=monthly-upgrade&utm_content=already-monthly
{% endif %}
```

A clean copy of the tagged snippet lives in `snippet-tagged.txt` next to this README.

What to compare:

- **Monthly conversion rate on the `upgrade-ask` branch.** New monthly donors divided by signers/actions sent to the upgrade page. Anything above 0.5% is meaningful traffic; above 1.5% is strong.
- **Average pledge amount of new monthly donors from this path.** If everyone picks the bottom button, your ask floor is probably too low. If almost nobody picks the top, your ceiling is too high.
- **One-time donation volume across your list.** If you previously sent these supporters to a one-time donation page, watch whether your one-time revenue dips. Trading short-term one-time cash for long-term monthly revenue is usually a good deal — but measure both sides, not just the gain.
- **Cancellation rate** for monthly donors acquired via this path, 90 days out. Monthly donors recruited via a soft post-action ask sometimes churn faster than ones who came in via a dedicated monthly campaign. Watch the 30/60/90-day churn separately.

Sample size: monthly conversion rates are lower than one-time conversion rates. Wait until the upgrade branch has at least a thousand signers before drawing conclusions.

See the top-level `MEASUREMENT.md` for the branch-tagging convention used across all recipes in this repo.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22, 2026-05-15, and 2026-05-16. Both branches pass via the automated Playwright matrix in `tests/` — one user with `is_monthly_donor="true"` routed to the else branch, one without the field (or with `"false"`) routed to the upgrade page.
