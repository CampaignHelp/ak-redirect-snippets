# ak-redirect-snippets

> A recipe book of tested Django-template snippets for ActionKit's after-action redirect URLs. Route signers to the right follow-up page based on who they are, what they did, and how they got there.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Platform: ActionKit](https://img.shields.io/badge/platform-ActionKit-orange.svg)](https://actionkit.com)

## What this is

ActionKit lets you embed Django-style template logic inside a page's **After-action info → Redirect URL** field. Instead of sending every signer to the same thank-you page, you can conditionally route them based on their properties, the action they took, or the URL parameters they arrived with.

The syntax works well. Most AK admins don't know it exists — and when they do, it's hard to find tested examples. This repo fixes that.

## Credit

The feature and this repo's flagship example come from **Shannon Turner**, who demoed *Snippets in redirect URLs* at ActionKit ClientCon 2026 (feature #9 of her *10 Features Every Client Should Use* talk).

- Shannon on GitHub: [@shannonturner](https://github.com/shannonturner)
- Shannon's consultancy, **Supraluminique**: [fasterthanlight.tech](https://fasterthanlight.tech)

This repo exists to spread what Shannon taught to a wider audience. Every recipe is tested and documented so AK admins who missed her talk can still use the feature with confidence. The donation-ladder recipe is her original demonstration — see that recipe for its direct attribution.

## How to use a recipe

1. Open the recipe folder you want (e.g. `recipes/ladder-from-prior-gift/`).
2. Read the `README.md`. It explains what the recipe does, what variables it needs, and any gotchas.
3. Copy the contents of `snippet.txt`.
4. In ActionKit: open the page you want to customize → **After-action info** tab → paste into **Redirect URL**.
5. Replace `yourorg.actionkit.com` with your actual AK subdomain. Replace the example page slugs with yours.
6. **Test it.** AK has no page-preview mode for redirect URLs — the only way to verify branching is to actually submit the page as different users. Create (or reuse) at least three test accounts: one that triggers the `{% if %}` branch, one for any `{% elif %}`, and one where no branch matches so the `{% else %}` fallback fires. For each, submit the form and confirm the landing URL is what you expect. The `tests/` folder in this repo shows one way to automate this against a test instance.

## Syntax reference

Available inside the Redirect URL field:

| Syntax | Purpose |
|---|---|
| `{% if … %}{% elif … %}{% else %}{% endif %}` | Conditional logic |
| `{{ user.* }}` | Built-in user properties (e.g. `user.highest_previous_contribution`, `user.state`) |
| `{{ user.custom_fields.* }}` | Any custom user field (e.g. `user.custom_fields.donation_count_2026`) |
| `{{ action.* }}` | Properties of the current action (e.g. `action.created_user` → `True`/`False`) |
| `{{ args.* }}` | URL parameters the user arrived with (e.g. `args.utm_campaign`, `args.src`) |
| `{{ value&#124;filter:arg }}` | Django template filters — e.g. `{{ user.highest_previous_contribution&#124;multiply:0.5 }}`, `{{ user.custom_fields.foo&#124;default:"0" }}` |
| `{{ user&#124;actiontaken:PAGE_ID }}` | Returns `1` if the user has any prior action on the given page id, `0` otherwise. Native AK filter — works without custom-field setup. |
| `{{ user&#124;tagged:"tag-name" }}` | Returns `1` if the user has taken action on any page carrying that tag, `0` otherwise. |

For the full filter list supported in your instance, see ActionKit's Custom Tags documentation.

## Recipes

| Folder | What it does |
|---|---|
| [`recipes/new-vs-returning`](recipes/new-vs-returning) | Route first-time supporters and returning users to different follow-up pages. |
| [`recipes/ladder-from-prior-gift`](recipes/ladder-from-prior-gift) | Build a donation ladder from a user's highest previous contribution. *(Shannon's flagship example.)* |
| [`recipes/monthly-upgrade`](recipes/monthly-upgrade) | Send one-time donors to a monthly-giving upgrade page. |
| [`recipes/utm-routing`](recipes/utm-routing) | Send users arriving from different campaigns to different follow-up pages. |
| [`recipes/escalation-ladder`](recipes/escalation-ladder) | Route signers to the next step based on whether they've already taken a specific prior action — e.g. petition signers who haven't called yet → call page, signers who already called → donate page. |

## Reference

- [`MEASUREMENT.md`](MEASUREMENT.md) — how to tell whether a redirect snippet is actually working: branch-tagging convention, what to compare, where to pull the data, and sample-size rules of thumb. Every recipe's README has a "How to know if it's working" section that follows this convention.
- [`reference/donation-url-params.md`](reference/donation-url-params.md) — URL parameters AK Payments donation pages accept (`amounts=`, `weekly_amounts=`, `monthly_amounts=`, `annual_amounts=`). Pairs naturally with the donation-ladder recipe.

## Warnings

These are the failure modes you'll actually hit. Read them before publishing a snippet.

### Always provide a fallback

Every conditional needs an `{% else %}` branch with a safe default URL. If the `{% if %}` (and any `{% elif %}`) doesn't match and there's no `{% else %}`, AK renders the Redirect URL field as **empty** — the user falls through to the page's default thank-you URL, or in some edge cases gets a broken redirect.

Wrong — no fallback:

```django
{% if user.custom_fields.donation_count_2026 > 3 %}
https://yourorg.actionkit.com/upgrade/
{% endif %}
```

Anyone who hasn't donated more than three times this year gets no redirect at all.

Right — explicit fallback for everyone else:

```django
{% if user.custom_fields.donation_count_2026 > 3 %}
https://yourorg.actionkit.com/upgrade/
{% else %}
https://yourorg.actionkit.com/thank-you/
{% endif %}
```

The first branch fires for laddering candidates; everyone else lands on a generic thank-you. Nobody falls through.

Rule of thumb: if you can imagine a user the `{% if %}` doesn't match, you need an `{% else %}` for them.

### Test by actually submitting

AK only evaluates the redirect URL at action-submission time. There is no preview button, no dry-run mode, no admin-side "what would this resolve to for user X" tool. The first time you'll see your branches fire is when a real user submits the form.

What you have to do:

- Create (or reuse) test accounts that exercise each branch — including the `{% else %}` fallback.
- For each test account: log in, submit the page, watch the destination URL in your browser bar.
- Confirm the destination URL is exactly what you expect, query parameters included.

Example — for a snippet that branches on prior donation count, you need at least:

- An account with `donation_count_2026 = 0` (fires the `{% else %}`)
- An account with `donation_count_2026 = 5` (fires the `{% if %}`)

If you only test the populated branch, you'll ship a snippet whose fallback is broken — and you won't find out until a never-donor submits the form.

The `tests/` folder in this repo shows one way to automate this with Playwright against a test instance.

### Unresolvable paths silently fall back

If your rendered redirect URL points to a slug that doesn't exist on your AK subdomain, AK does not return a 404 — it quietly substitutes the page's own default thank-you URL. This is the most common reason a snippet "doesn't work" when the syntax is fine.

```django
{% if action.created_user %}
https://yourorg.actionkit.com/welcome-new/      ← page doesn't exist
{% else %}
https://yourorg.actionkit.com/welcome-back/
{% endif %}
```

A first-time user submits, the `{% if %}` fires, the rendered URL is `…/welcome-new/`, AK looks it up, can't find it, and sends them to the default thank-you. To the admin, it looks like the snippet didn't run. To the user, nothing seems wrong — they just landed somewhere different than you intended.

How to catch it before going live:

- Paste each possible rendered URL into a browser and confirm the page loads.
- Walk every branch (not just the happy path) and check its destination exists.
- Trailing slashes matter — `/welcome-back` and `/welcome-back/` are different URLs to AK.

### Don't wrap the snippet in quotes

The Redirect URL field takes the snippet as plain text. If you copy a snippet out of a code block somewhere, it's easy to accidentally include surrounding quotes — they will break the template.

Wrong — surrounding quotes get treated as part of the URL:

```
"{% if user.custom_fields.donation_count_2026 > 3 %}https://yourorg.actionkit.com/upgrade/{% else %}https://yourorg.actionkit.com/thank-you/{% endif %}"
```

Right — no outer quotes; the template starts with `{%` and ends with `%}`:

```
{% if user.custom_fields.donation_count_2026 > 3 %}https://yourorg.actionkit.com/upgrade/{% else %}https://yourorg.actionkit.com/thank-you/{% endif %}
```

Common slip: copying from Slack, Google Docs, or email can introduce smart quotes (`"` `"` instead of `"`). If your snippet behaves weirdly, retype any quotes inside it from a plain-text editor.

### Guard custom field references

Custom user fields may be empty, missing, or zero for some users — especially newly created accounts or imported users. Comparing an empty field to a number is a common silent-failure pattern in AK templates.

Fragile — assumes the field exists and is a number:

```django
{% if user.custom_fields.donation_count_2026 > 3 %}
…
{% endif %}
```

If `donation_count_2026` is missing on the user (not just empty — actually never set), the comparison can throw or evaluate in surprising ways.

Defensive — option A, coerce missing values to `0`:

```django
{% if user.custom_fields.donation_count_2026|default:"0"|add:0 > 3 %}
…
{% endif %}
```

Defensive — option B, explicit existence check:

```django
{% if user.custom_fields.donation_count_2026 and user.custom_fields.donation_count_2026 > 3 %}
…
{% endif %}
```

The first clause short-circuits if the field is missing or empty, so the second clause never runs against a broken value.

Either pattern is fine. Pick one and use it consistently across your snippets.

### Some features are Payments-only

The donation URL parameters (`amounts=`, `weekly_amounts=`, `monthly_amounts=`, `annual_amounts=`) only work on donation pages wired to NGP VAN **Payments**. They are silently ignored on legacy donation pages.

How to tell which kind you have:

- Open the donation page in the AK admin.
- Payments-enabled pages show payment-method selectors and route through NGP's processor.
- If you're not sure, ask your AK admin or NGP rep before relying on these parameters.

Failure mode if you don't check: the parameters are appended to the URL, the user lands on the donation page, and the page shows its default ask amounts instead of yours. No error message — just no effect.

## Contributing

New recipes welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Bar for inclusion: the recipe works on a real AK instance, documents its variables, and includes a fallback branch.

## License

[MIT](LICENSE). Use these recipes in any instance, commercial or nonprofit. Attribution appreciated but not required.

---

Maintained by [CampaignHelp](https://campaign.help). Inspired by [Shannon Turner](https://github.com/shannonturner) / [Supraluminique](https://fasterthanlight.tech).
