# New vs. returning user redirect

Route first-time supporters to a welcome page. Route returning supporters to a follow-up ask. The simplest branching recipe in this repo — good first one to install if you've never used redirect snippets before.

## What this recipe does

When a supporter submits any AK action page, this snippet checks whether the action **created a new user record** in your AK database. If yes, they're new to you — send them somewhere designed to orient and welcome. If no, they were already in your system — skip the welcome and go straight to a second ask (donation, share, second petition, etc.).

The check happens automatically. There's no custom field to maintain, no integration to wire up. AK tracks user creation itself.

## Who this is for

Use this when:

- You have a meaningful difference between what you want new and returning supporters to see right after an action.
- You're running campaigns that mix list-acquisition (lots of new signers) with list-cultivation (returning supporters being asked again).
- You want the post-action page to feel less generic without building heavy logic.

Skip this if:

- Your post-action experience is already the same for everyone and that's working fine. Don't add branching for branching's sake.
- Most of your traffic is one or the other (almost all new, or almost all returning). The branching adds maintenance overhead for little segmentation benefit.

## The snippet

```django
{% if action.created_user %}
https://yourorg.actionkit.com/welcome/welcome-new-supporter/
{% else %}
https://yourorg.actionkit.com/donate/thanks-and-donate/
{% endif %}
```

A clean copy lives in `snippet.txt` next to this README.

## How the snippet works, line by line

If you've never seen Django template syntax before — the bits inside `{% %}` are placeholders that AK evaluates when a supporter submits the form. The rest is the literal URL AK will redirect to.

### Line 1 — the condition

```django
{% if action.created_user %}
```

`action.created_user` is a built-in AK value. It's `True` when this specific action just created a brand-new user record in your AK database, and `False` when the email the user entered was already on file.

Important: "new" here means **new to your AK database**, not new to the campaign or new to advocacy in general. A donor who's been on your list for ten years counts as `False` (returning). Someone who's been signing up under their work email for a decade and uses their personal email today counts as `True` (new), because AK doesn't recognize the new email.

### Line 2 — the welcome URL

```django
https://yourorg.actionkit.com/welcome/welcome-new-supporter/
```

The URL AK redirects new users to. Replace `yourorg` and the slug with yours.

This page should orient and welcome — explain who you are, what you do, what to expect from being on the list. Don't lead with a heavy ask. The user is brand new; they just gave you their email; the relationship is still forming.

### Lines 3–4 — the fallback branch

```django
{% else %}
https://yourorg.actionkit.com/donate/thanks-and-donate/
```

`{% else %}` catches everyone whose `action.created_user` is `False` — returning users who were already in your database. These supporters know you already, so the second ask can come faster. A donation ask, a share-with-a-friend page, or a second petition all fit here.

### Line 5 — close the conditional

```django
{% endif %}
```

Closes the `{% if %}`. Every `{% if %}` needs a matching `{% endif %}` below it.

## What you need before you install

- The actual slugs for your welcome page and your follow-up page. Both pages need to exist in AK before you install the snippet — AK silently falls back to a default thank-you URL if either slug doesn't resolve (see top-level README → *Unresolvable paths silently fall back*).
- A welcome page that's genuinely welcoming. Don't reuse a generic thank-you. The whole point of branching is to give new supporters something different.
- A follow-up page that makes sense as the *next* step. Returning supporters expect you to know them — don't ask them to introduce themselves again.

## How to install

1. Copy the contents of `snippet.txt`.
2. In AK admin, open the page you want to add the redirect to (the petition, RSVP, survey, etc.).
3. Click the **After-action info** tab.
4. Paste the snippet into the **Redirect URL** field. Do not wrap it in quotes (see top-level README → *Don't wrap the snippet in quotes*).
5. Replace `yourorg.actionkit.com` with your subdomain. Replace `welcome/welcome-new-supporter/` and `donate/thanks-and-donate/` with your real page slugs.
6. Save the page.
7. Test before announcing the campaign (see *How to test* below).

## What can go wrong (specific to this recipe)

### "New" doesn't always mean "first time engaging with your cause"

`action.created_user` only checks whether the email was new to AK. Common ways this gets noisy:

- A long-time supporter signs up with a different email (work vs personal, old vs new ISP) — they look new.
- A staff member who's been in your CRM but never as a user-submitted action — first time submitting a form, they look new.
- A list import that went into a different database, then later got merged — depends on how the merge ran.

For most campaigns this noise is acceptable. If precision matters, layer in a custom field check (e.g., `user.custom_fields.first_seen_year`) instead of relying on `action.created_user` alone.

### The welcome page asks for too much, too soon

A common failure mode: the welcome page is a donation page in disguise, or asks the new user to take a second action before they've even read your About page. Conversion on this branch craters and you mistake it for the snippet not working.

If your welcome page has more than one ask, simplify it. Lead with orientation. The fundraising can come on the next email.

### The follow-up page assumes too much familiarity

The mirror failure: the returning-user branch sends them to a page that says "as you know, our work focuses on…" — and the returning user is a one-time signer from two years ago who doesn't remember signing up. Make the follow-up page warm-but-self-contained, not insidery.

### Both URLs point to the same place

If you copy this recipe and forget to differentiate the two URLs, the snippet still works syntactically but does nothing useful. Spot-check before going live.

## How to test

You'll need two test scenarios:

1. **New-user test.** Submit the form with an email that's never been used on your AK instance. Confirm the destination URL is your welcome page.
2. **Returning-user test.** Submit the form a *second* time with the same email (or use any email already on your AK instance). Confirm the destination URL is your follow-up page.

For each test, confirm the destination page actually loads — AK silently falls back to a default thank-you URL if the slug is wrong (see top-level README → *Unresolvable paths silently fall back*).

The `tests/` folder in this repo automates both cases against the Robotic Dogs sandbox via Playwright.

## How to know if it's working

The snippet is doing its job if new supporters who land on the welcome page **stick around** (low bounce, second action within a few weeks) and returning supporters on the follow-up page **convert** (donation, share, second action) at a rate at least as good as your old single-page setup.

Tag each branch's destination URL so you can pull branch-level results:

```django
{% if action.created_user %}
https://yourorg.actionkit.com/welcome/welcome-new-supporter/?utm_source=ak-redirect&utm_campaign=new-vs-returning&utm_content=new
{% else %}
https://yourorg.actionkit.com/donate/thanks-and-donate/?utm_source=ak-redirect&utm_campaign=new-vs-returning&utm_content=returning
{% endif %}
```

A clean copy of the tagged snippet lives in `snippet-tagged.txt` next to this README.

What to compare:

- **Bounce rate on the welcome page** (via Google Analytics if it's tagged). Welcome pages with too much ask or too little orientation bounce hard. Aim for bounce well below your site-wide average.
- **Second-action rate** for the `utm_content=new` segment over the next 30 days. Did the welcome experience earn enough trust for a second engagement? Pull this from AK by filtering recent actions to users whose first action came via this redirect path.
- **Conversion rate on the returning-user branch** (donations or actions divided by signers). Compare to your historical conversion from a single-page thank-you.

Sample size: this branch tends to skew heavily one way (most campaigns are mostly new or mostly returning). Wait until each branch has at least a few hundred signers before drawing conclusions.

See the top-level `MEASUREMENT.md` for the branch-tagging convention used across all recipes in this repo.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22, 2026-05-15, and 2026-05-16. Both branches pass via the automated Playwright matrix in `tests/`. When piloting this on your own instance, make sure the welcome URL actually resolves to a real page — AK silently falls back to a default thank-you URL if the rendered redirect points to a path that 404s on your subdomain.
