# Escalation ladder by prior action

Route supporters to the *next* step in your engagement ladder based on what they've already done. If they've already taken the harder ask, push them to the next one up. Different from `new-vs-returning` — this branches on **specific** prior actions, not just "have we ever heard from you."

## What this recipe does

This snippet uses AK's built-in `actiontaken` template filter to check whether a supporter has previously taken action on a specific page. The classic use is post-petition routing: if a signer has already called their representative, send them straight to the donation page — don't ask them to call again. If they haven't called yet, route them to the call page to escalate.

The check reads from AK's own action history. There's no custom field to maintain, no integration to wire up, no nightly sync. Works on any AK instance out of the box.

## Who this is for

Use this when:

- You run multi-step campaigns where the order of asks matters — petition → call → donate, RSVP → invite-a-friend → host-an-event, etc.
- You want to avoid asking the same supporter to do something they've already done.
- You're willing to look up and hardcode AK page IDs (see *Finding the page ID* below).

Skip this if:

- Your campaign is single-step. Branching on prior actions adds no value.
- You need fine-grained timing (e.g., "called in the last 30 days"). `actiontaken` only tells you whether the user has *ever* taken the action — see *What can go wrong* below.

## The snippet

```django
{% if user|actiontaken:PRIOR_PAGE_ID %}
https://yourorg.actionkit.com/donate/donate/
{% else %}
https://yourorg.actionkit.com/call/call-your-rep/
{% endif %}
```

A clean copy lives in `snippet.txt` next to this README. Replace `PRIOR_PAGE_ID` with the actual numeric page ID you want to check against.

## How the snippet works, line by line

If you've never seen Django template syntax before — the bits inside `{% %}` are placeholders that AK evaluates when a supporter submits the form. The rest is the literal URL AK will redirect to.

### Line 1 — the condition

```django
{% if user|actiontaken:PRIOR_PAGE_ID %}
```

`actiontaken` is an AK-native template filter. Read this line as: "If the user has any prior action recorded on the page with ID `PRIOR_PAGE_ID`, use the next URL."

- `user` — the current supporter.
- `|actiontaken:` — the filter. The pipe character (`|`) applies the filter to `user`; the colon (`:`) introduces the filter's argument.
- `PRIOR_PAGE_ID` — the numeric ID of the page you're checking against. **Not** the slug — see *Finding the page ID* below.

The filter returns `1` (truthy) if the user has any action on that page, `0` (falsy) otherwise. The `{% if %}` fires on `1` and skips on `0`.

### Line 2 — the "already done it" URL

```django
https://yourorg.actionkit.com/donate/donate/
```

Where to send supporters who've already taken the gated action. In the petition → call → donate ladder, this is the donation page — they've already called, escalate them.

### Lines 3–4 — the fallback branch

```django
{% else %}
https://yourorg.actionkit.com/call/call-your-rep/
```

Where to send everyone who hasn't taken the gated action yet. In the same ladder, this is the call page — they signed the petition, push them to the next step.

### Line 5 — close the conditional

```django
{% endif %}
```

Closes the `{% if %}`. Every `{% if %}` needs a matching `{% endif %}` below it.

## Why this is portable

Unlike custom-field patterns (`user.custom_fields.signed_petition_xyz`), `actiontaken` reads directly from the action history AK already tracks. There's nothing for your team to wire up — no after-action user-update, no integration writing a flag, no per-page boilerplate. Drop the recipe in, swap the page ID, ship.

## Finding the page ID

`actiontaken` takes a numeric page ID, not a slug. To find a page's ID in ActionKit:

- **Admin UI.** Open the page in the AK admin. The URL ends in `/admin/cms/signuppage/<id>/` — that number is your page ID.
- **REST API.** `GET /rest/v1/signuppage/?name=<slug>&format=json` returns `objects[0].id`.

The ID is stable across the page's lifetime — safe to hardcode in a redirect URL snippet.

## What you need before you install

- The numeric page ID of the action you're checking against. Look this up before editing the snippet.
- A "next step" page for users who've already done the gated action, and an "escalate to this" page for users who haven't. Both have to exist (AK silently falls back to a default thank-you if either URL 404s — see top-level README → *Unresolvable paths silently fall back*).
- A real understanding of where each branch lands in your ladder. The strongest ask should be the next step *after* the gated action, not the gated action itself.

## How to install

1. Copy the contents of `snippet.txt`.
2. In AK admin, open the page you want to add the redirect to (the petition, the new action — **not** the gated prior action).
3. Click the **After-action info** tab.
4. Paste the snippet into the **Redirect URL** field. Do not wrap it in quotes (see top-level README → *Don't wrap the snippet in quotes*).
5. Replace `yourorg.actionkit.com` with your subdomain. Replace `PRIOR_PAGE_ID` with the actual numeric page ID. Update both destination slugs.
6. Save the page.
7. Test before announcing the campaign (see *How to test* below).

## Going further — three-step ladder

The basic recipe is binary. For a longer ladder, chain `actiontaken` checks with `{% elif %}`, ordered from highest commitment down:

```django
{% if user|actiontaken:DONATE_PAGE_ID %}
https://yourorg.actionkit.com/share/thanks-and-share/
{% elif user|actiontaken:CALL_PAGE_ID %}
https://yourorg.actionkit.com/donate/donate/
{% else %}
https://yourorg.actionkit.com/call/call-your-rep/
{% endif %}
```

Read top-to-bottom: "If they've already donated → send to share. Else if they've already called → escalate to donate. Else → escalate to call." Put your strongest ask at the top so supporters who've done it skip past; weaker asks fall through to it.

This pattern extends to four or more steps as long as you can rank the actions in commitment order.

## Tag-based variation

If your "prior action" is really a *set* of pages (e.g., "any of our 2026 climate petitions"), tag those pages in the AK admin and use `tagged` instead:

```django
{% if user|tagged:"climate-petition" %}
https://yourorg.actionkit.com/call/call-on-climate/
{% else %}
https://yourorg.actionkit.com/petition/sign-climate-petition/
{% endif %}
```

`{{ user|tagged:"name" }}` returns `1` if the user has taken action on *any* page tagged with that name. Useful when you care about the campaign, not the specific page. Maintain the tag in AK; the snippet picks up new pages automatically.

## What can go wrong (specific to this recipe)

### The current submission usually counts

When the user submits page X, by the time the redirect URL template evaluates, AK has already created the action on X. So `user|actiontaken:X_ID` returns `1` from the *first* submission of page X onward.

For cross-page laddering this is fine — the common case is "did they call before submitting this petition?" and the check is against a different page. Where it bites is checking `actiontaken` against the *same* page the snippet is installed on. Every signer of that page will look like a returning user, and the branch logic inverts unexpectedly.

If you need "has the user ever previously taken an action on the page they just submitted" semantics, use a custom field set by an after-action instead — `actiontaken` can't help you there.

### Page IDs are numeric, not slugs

`user|actiontaken:"climate-petition"` does not work. Pass the integer ID, not the slug. If you write a string by accident, the filter returns `0` for everyone and the `{% if %}` never fires — the snippet silently behaves as if no one has ever taken the prior action.

### Page IDs are not portable across instances

Page ID 42 on your staging instance is a different page on production. If you sync content between instances and copy snippets across, the recipe needs different IDs on each side. Easy to miss during deploys.

If you have a staging-to-prod workflow, document the per-environment IDs alongside the snippet, or use the `tagged` variant above (tags are matched by name, not ID, so they cross environments cleanly).

### No per-action filtering

`actiontaken` only tells you *whether* the user has ever taken action on the page — not when, not how many times, not from which source. If you need "called in the last 30 days" granularity, you're back to either a custom field (set by a workflow or integration that knows the timing) or a query-driven email send instead of a redirect.

### The "next step" doesn't actually exist for some supporters

If the gated action was unusual (e.g., a closed event RSVP) and you escalate to a step that no longer makes sense (e.g., asking them to invite friends to an event that already happened), supporters land confused. Audit the ladder when campaigns wind down.

## How to test

You'll need two test users — or use one test user across two campaign cycles.

1. **No-prior-action test.** A fresh user who's never taken action on `PRIOR_PAGE_ID`. Submit the form on the page where you installed the snippet. Confirm the destination URL is the *escalation* page (`call-your-rep/` in the basic recipe).
2. **Already-acted test.** A user who *has* a recorded action on `PRIOR_PAGE_ID` (you can plant one via the AK admin or via a previous submission). Submit the snippet page. Confirm the destination URL is the *already-done* page (`donate/donate/` in the basic recipe).

For each, confirm the destination page actually loads.

The `tests/` folder in this repo automates both cases against the Robotic Dogs sandbox via Playwright.

## How to know if it's working

The snippet is doing its job if supporters routed to the **call page** (escalation branch) actually call at a comparable rate to a non-branched campaign, and supporters routed to the **donate page** (already-called branch) convert better than they would have if you'd asked them to call again.

Tagged version of the snippet:

```django
{% if user|actiontaken:PRIOR_PAGE_ID %}
https://yourorg.actionkit.com/donate/donate/?utm_source=ak-redirect&utm_campaign=escalation-ladder&utm_content=escalate-to-donate
{% else %}
https://yourorg.actionkit.com/call/call-your-rep/?utm_source=ak-redirect&utm_campaign=escalation-ladder&utm_content=escalate-to-call
{% endif %}
```

A clean copy of the tagged snippet lives in `snippet-tagged.txt` next to this README.

What to compare:

- **Call-completion rate** on the `escalate-to-call` branch (actions recorded on the call page / supporters sent there). Compare to a control campaign that sends *every* signer to the call page without escalation. If escalated supporters complete the call at a similar or higher rate, the ladder is doing real work — you're not just filtering for the people who were already going to call.
- **Donation rate** on the `escalate-to-donate` branch. Supporters who've already called are higher-commitment than a typical petition signer; their donation conversion should be noticeably higher than a flat ask to the same campaign.
- **Branch distribution.** What share of submitters land on each branch? If 95% hit the `{% else %}` (no one's called yet), the recipe is functioning as a normal one-step ask and you're not getting much from the escalation. If the share is more balanced, the ladder is genuinely segmenting your supporters.

Sample size: escalation effects need at least a few hundred submitters per branch before the numbers stabilize. Wait through a full campaign cycle (a few weeks) before drawing conclusions, especially on the smaller branch.

See the top-level `MEASUREMENT.md` for the branch-tagging convention used across all recipes in this repo.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-05-15 and 2026-05-16. Both branches pass via the automated Playwright matrix in `tests/`:

- A fresh user submitting against an unrelated page ID → `{% else %}` branch (no prior action).
- A returning user submitting again, with the snippet checking the page they previously submitted → `{% if %}` branch (prior action recorded).
