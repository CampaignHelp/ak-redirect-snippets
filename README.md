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
| `|filter:arg` | Django template filters — e.g. `|multiply:0.5`, `|default:"0"` |

For the full filter list supported in your instance, see ActionKit's Custom Tags documentation.

## Recipes

| Folder | What it does |
|---|---|
| [`recipes/new-vs-returning`](recipes/new-vs-returning) | Route first-time supporters and returning users to different follow-up pages. |
| [`recipes/ladder-from-prior-gift`](recipes/ladder-from-prior-gift) | Build a donation ladder from a user's highest previous contribution. *(Shannon's flagship example.)* |
| [`recipes/monthly-upgrade`](recipes/monthly-upgrade) | Send one-time donors to a monthly-giving upgrade page. |
| [`recipes/utm-routing`](recipes/utm-routing) | Send users arriving from different campaigns to different follow-up pages. |

## Reference

- [`reference/donation-url-params.md`](reference/donation-url-params.md) — URL parameters AK Payments donation pages accept (`amounts=`, `weekly_amounts=`, `monthly_amounts=`, `annual_amounts=`). Pairs naturally with the donation-ladder recipe.

## Warnings

- **Always provide a fallback.** Every conditional needs an `{% else %}` branch with a safe default URL. A missing redirect breaks the user's experience.
- **Test by actually submitting.** AK evaluates the redirect URL template at action-submission time, and there's no preview for it — the only way to verify a branch fires is to submit the form as a user in that state. See step 6 in "How to use a recipe" above.
- **Unresolvable paths silently fall back.** If the rendered redirect URL points to a path that 404s on your AK subdomain, AK quietly routes the user to the page's default thank-you URL instead. Make sure every URL a branch might produce actually exists before going live.
- **Mind the quote escaping.** The Redirect URL field accepts the snippet as plain text — don't wrap it in extra quotes.
- **Guard custom field references.** If a custom field is missing on some users, use `|default:"0"` or an explicit `{% if user.custom_fields.foo %}` check before comparing it.
- **Some features are Payments-only.** The donation URL parameters (`amounts=`, etc.) only work on NGP VAN Payments-enabled donation pages.

## Contributing

New recipes welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Bar for inclusion: the recipe works on a real AK instance, documents its variables, and includes a fallback branch.

## License

[MIT](LICENSE). Use these recipes in any instance, commercial or nonprofit. Attribution appreciated but not required.

---

Maintained by [CampaignHelp](https://campaign.help). Inspired by [Shannon Turner](https://github.com/shannonturner) / [Supraluminique](https://fasterthanlight.tech).
