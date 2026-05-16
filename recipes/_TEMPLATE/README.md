# [Recipe name in sentence case]

One sentence (two at most) describing what the recipe does and the audience it serves. This is the line that sells the recipe — make it concrete.

## Credit

*Optional — include only if the recipe is adapted from someone else's public talk, blog post, or repo.*

- Name on GitHub: [@handle](https://github.com/handle)
- Their org / consultancy: [link](https://example.com)
- Source material: [link to talk slides, blog post, or repo]

## What this recipe does

Two to four sentences in plain language explaining the routing logic. Mention which variables drive the decision and what the supporter actually sees on each branch — not the syntax.

## Who this is for

Use this when:

- Concrete condition 1
- Concrete condition 2

Skip this if:

- Reason 1 (the data isn't there, the page type isn't supported, the audience is too small to branch on, etc.)
- Reason 2

## The snippet

```django
{% if condition %}
https://yourorg.actionkit.com/path/to/page-a/
{% else %}
https://yourorg.actionkit.com/path/to/fallback/
{% endif %}
```

A clean copy lives in `snippet.txt` next to this README.

## How the snippet works, line by line

Assume the reader has never seen Django template syntax. Walk through each line: what the placeholder does, where each value comes from (built-in AK field, custom user field, URL parameter), and what the rendered output looks like for a sample user. Use `### Line N — purpose` subheadings for each.

### Line 1 — the condition

Explain the `{% if %}` and the comparison.

### Line 2 — the branch URL

Explain the URL, any filters or template placeholders inside it, and what it renders as for a representative user.

### Line 3 — the fallback

Explain the `{% else %}` and what it catches.

### Line 4 — close the conditional

`{% endif %}` ends the block. Every `{% if %}` needs one.

## What you need before you install

- Any AK page type or version requirement (e.g., Payments-enabled donation page).
- Any custom user field your team has to maintain, plus a one-line description of when each value should be written.
- The actual page slug(s) the snippet will redirect to. Both must exist before installation — AK silently falls back to a default thank-you if a slug doesn't resolve.

## How to install

1. Copy the contents of `snippet.txt`.
2. In AK admin, open the page you want to add the redirect to.
3. Click the **After-action info** tab.
4. Paste the snippet into the **Redirect URL** field. Do not wrap it in quotes.
5. Replace `yourorg.actionkit.com` with your subdomain. Update field names and page slugs to match your instance.
6. Save the page.
7. Test before announcing the campaign (see *How to test* below).

## What can go wrong (specific to this recipe)

List recipe-specific failure modes — the things that will go wrong in practice that the generic warnings in the top-level README don't cover. Examples: a field can be empty for some users, a threshold being wrong for the org's donor base, ask amounts looking ugly when scaled. Give each its own `### subheading` and explain how to fix it.

### Concrete failure mode 1

What it looks like, why it happens, how to fix.

### Concrete failure mode 2

Same.

## How to test

You'll need at least two (preferably three) test scenarios — one per branch, plus the fallback.

1. **Branch-A test.** What state the user needs to be in. Submit. Expected destination URL.
2. **Branch-B test.** Same, for the other explicit branch.
3. **Fallback test.** A user who matches neither explicit branch — the `{% else %}` fires. Expected destination URL.

For each test, also load the destination page and confirm it renders correctly. AK silently falls back to a default thank-you if the rendered URL doesn't resolve.

If the recipe has tests in the `tests/` folder, mention which cases are covered automatically.

## How to know if it's working

State the metric that tells you the branching is doing real work. Donation rate? Average gift? Share rate? Second-action rate? Be specific.

Tagged version of the snippet:

```django
{% if condition %}
https://yourorg.actionkit.com/path/to/page-a/?utm_source=ak-redirect&utm_campaign=recipe-name&utm_content=branch-a
{% else %}
https://yourorg.actionkit.com/path/to/fallback/?utm_source=ak-redirect&utm_campaign=recipe-name&utm_content=branch-b
{% endif %}
```

A clean copy of the tagged snippet lives in `snippet-tagged.txt` next to this README.

What to compare:

- Branch A's metric vs your historical baseline from a single-page thank-you.
- Branch B's metric vs the same baseline.
- Anything that might cannibalize (related metrics that could quietly drop).

Sample size: state a reasonable per-branch floor before drawing conclusions. A few hundred signers for one-time conversion, a thousand for monthly conversion, more for low-rate downstream metrics.

See the top-level `MEASUREMENT.md` for the branch-tagging convention used across all recipes in this repo.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on YYYY-MM-DD. Which branches pass via the automated Playwright matrix in `tests/`, and which (if any) had to be verified by hand. Be honest about what's covered.
