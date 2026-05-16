# UTM-aware routing

Send supporters who arrived from different campaigns to different follow-up pages. Useful when you want the second ask to match the audience that brought them in — Facebook signers see a share-to-Facebook page, email signers see a donation page, and everyone else sees a sensible default.

## What this recipe does

This snippet reads a URL parameter (`src`, or `utm_source`, or anything you use for campaign tracking) from the page the supporter just submitted, and branches the redirect based on its value. The user's source travels with them through the action, into the redirect template, and out to the destination URL.

Unlike most recipes here, this one doesn't depend on anything stored in AK about the user — it works on the very first action a stranger takes, before they're "known" to your database.

## Who this is for

Use this when:

- You're driving traffic to the same AK page from multiple campaigns (Facebook ads, email blasts, partner links, etc.) and want each campaign's signers to see a tailored next step.
- You already tag inbound links with `?src=`, `?utm_source=`, or similar.
- You want to do this *without* duplicating the AK page for each source.

Skip this if:

- All your traffic comes from one source, or you don't tag inbound links at all. There's nothing for the snippet to branch on.
- Your tagging is inconsistent across teams. Branching on noisy parameters produces noisy results.

## The snippet

```django
{% if args.src == "facebook" %}
https://yourorg.actionkit.com/thanks/share-facebook/
{% elif args.src == "email" %}
https://yourorg.actionkit.com/donate/donate/
{% else %}
https://yourorg.actionkit.com/thanks/default/
{% endif %}
```

A clean copy lives in `snippet.txt` next to this README.

## How the snippet works, line by line

If you've never seen Django template syntax before — the bits inside `{% %}` are placeholders that AK evaluates when a supporter submits the form. The rest is the literal URL AK will redirect to.

### Line 1 — the first condition

```django
{% if args.src == "facebook" %}
```

`{{ args.* }}` exposes URL parameters that were on the action page when the supporter loaded it. If the user arrived at `https://yourorg.actionkit.com/signup/your-petition/?src=facebook`, then `args.src` is the string `"facebook"` for the rest of the template.

- `args.src` — the value of the `src` query parameter. If your tracking convention uses `utm_source` instead, use `args.utm_source`. Whatever the parameter is in the URL, that's what you access.
- `== "facebook"` — string equality. Exact, case-sensitive match. `"Facebook"` and `"FACEBOOK"` would not match.

This branch fires when the supporter came in from a link tagged `?src=facebook`.

### Line 2 — the Facebook-tailored URL

```django
https://yourorg.actionkit.com/thanks/share-facebook/
```

A follow-up page tailored to Facebook-sourced supporters — probably a share-to-Facebook page that closes the loop on where they came from.

### Lines 3–4 — the second condition and URL

```django
{% elif args.src == "email" %}
https://yourorg.actionkit.com/donate/donate/
```

`{% elif %}` ("else if") is a second condition that's only checked if the first one was false. If `args.src` wasn't `"facebook"` but **is** `"email"`, this branch fires. Email-sourced supporters skip the share page and go straight to a donation ask — they're already on your list, already engaged, and the leverage is different.

You can chain as many `{% elif %}` branches as you need. Stack them in priority order; the first one that matches wins.

### Lines 5–6 — the fallback branch

```django
{% else %}
https://yourorg.actionkit.com/thanks/default/
```

`{% else %}` catches everyone whose `args.src` didn't match any of the explicit branches above — including the most common case: the parameter wasn't present at all. Direct traffic, organic shares, links typed manually, and links from email clients that strip query parameters all land here.

This branch will probably get the most traffic of the three. Don't treat it as an afterthought.

### Line 7 — close the conditional

```django
{% endif %}
```

Closes the `{% if %}`. One `{% endif %}` covers the whole `if`/`elif`/`else` block — you don't add extras for the `{% elif %}`.

## What you need before you install

- A working URL-parameter tagging convention across the channels you care about. If your email blasts tag links one way and your Facebook ads tag them another, decide on a single convention before installing the snippet.
- One destination page per branch. All of them have to exist before the snippet goes live (AK silently falls back to a default thank-you if any rendered URL 404s — see top-level README → *Unresolvable paths silently fall back*).
- A real default destination for the `{% else %}` branch. The default catches everyone untagged, which is usually most of your traffic.

## How to install

1. Copy the contents of `snippet.txt`.
2. In AK admin, open the page you want to add the redirect to.
3. Click the **After-action info** tab.
4. Paste the snippet into the **Redirect URL** field. Do not wrap it in quotes (see top-level README → *Don't wrap the snippet in quotes*).
5. Replace `yourorg.actionkit.com` with your subdomain. Change `args.src` to `args.utm_source` (or whatever parameter you use) if needed. Adjust the branch values and destination URLs to match your campaigns.
6. Save the page.
7. Test before driving real traffic (see *How to test* below).

## What can go wrong (specific to this recipe)

### Email clients strip query parameters

Outlook (especially the desktop client) and some corporate email security filters rewrite links to route through a tracking proxy — and the rewrite can drop your query parameters or replace them with the filter's own. Supporters who click an email link tagged `?src=email` may arrive at the page with no `src` at all. They fall into the `{% else %}` branch instead of the `email` branch.

Mitigations:

- Use a redirect link in your email (a short link from a service you control) that adds the `?src=email` parameter on the way through, after the email client has stopped meddling.
- If your email platform supports it, test what your tagged links actually look like when delivered to a few common clients before relying on the branching.

### Shared links carry the original source

If a supporter shares the action URL with a friend, the `?src=facebook` parameter often goes along for the ride. The friend, who came in from Twitter or directly from a text message, gets routed by their friend's source instead of their own.

This is usually a low-volume effect, but if shares are a major part of your traffic, design the destination pages so each one still works for an audience that didn't really come from the channel name.

### Inconsistent tagging across teams

Three teams tagging the same campaign as `src=facebook`, `src=fb`, and `utm_source=facebook` will scatter their supporters across three different branches — or, worse, two branches and the fallback. Pick a single canonical parameter and value per channel, document it, and audit links before launch.

### Don't trust `args.*` for security

URL parameters are user-controllable. Anyone can paste `?src=premium` into the URL bar and arrive at whatever branch matches that. Don't use `{{ args.* }}` values in security-sensitive logic, and don't concatenate them into URLs that point to pages you don't control (the latter could enable an open-redirect issue).

For redirect-snippet routing — where the worst case is a curious user landing on the wrong follow-up page — this is fine. Just don't extend the pattern to anything that matters for security.

## How to test

You'll need to load the action page yourself, with different URL parameters, and submit each version.

1. **Facebook test.** Load `https://yourorg.actionkit.com/signup/your-page/?src=facebook` (or whatever your action page slug is). Submit the form. Confirm the destination is your Facebook-tailored page.
2. **Email test.** Load the same page with `?src=email`. Submit. Confirm the destination is your email follow-up page.
3. **Untagged test.** Load the page with no parameters at all. Submit. Confirm the destination is your default page.

The `tests/` folder in this repo automates all three cases against the Robotic Dogs sandbox via Playwright.

## How to know if it's working

The snippet itself **is** your measurement infrastructure here — each branch's destination URL carries built-in information about where the supporter came from. The question for measurement isn't "did the branching fire?" — it's "did the tailored follow-up perform better than a one-size-fits-all thank-you?"

Tagged version of the snippet (preserves the inbound source as a `utm_content`):

```django
{% if args.src == "facebook" %}
https://yourorg.actionkit.com/thanks/share-facebook/?utm_source=ak-redirect&utm_campaign=utm-routing&utm_content=facebook
{% elif args.src == "email" %}
https://yourorg.actionkit.com/donate/donate/?utm_source=ak-redirect&utm_campaign=utm-routing&utm_content=email
{% else %}
https://yourorg.actionkit.com/thanks/default/?utm_source=ak-redirect&utm_campaign=utm-routing&utm_content=untagged
{% endif %}
```

What to compare:

- **Engagement on the tailored branches vs. a control.** If you've previously sent everyone to the default thank-you, your historical conversion from that page is the baseline. Tailored branches should match or beat it.
- **`{% else %}` branch volume.** If it's catching more than half your traffic, you have a tagging gap. Find which channel isn't being tagged and fix the link templates there.
- **Conversion rates per source.** Facebook-sourced and email-sourced supporters usually convert differently — knowing the gap helps you set realistic targets and decide where to invest more acquisition spend.

Sample size: per-branch volume depends entirely on how much each source drives. The smallest branch sets your floor — wait until it has a few hundred signers before reading too much into the numbers.

See the top-level `MEASUREMENT.md` for the branch-tagging convention used across all recipes in this repo.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22 — all three branches (`if`/`elif`/`else`) pass via the automated Playwright matrix in `tests/`. Users arriving at `/signup/<your-page>/?src=<value>` have `{{ args.src }}` automatically available in the redirect URL template — no hidden form inputs needed.
