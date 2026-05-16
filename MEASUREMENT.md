# How to measure whether a redirect snippet is working

Every recipe in this repo branches a supporter to a different destination based on who they are, what they did, or how they got there. The question this doc answers: *how do you know the branching is actually producing better outcomes than a single one-size-fits-all thank-you page?*

The short answer: tag each branch's destination URL with a tracking parameter, then pull branch-level results from AK donation reports, Google Analytics, or your CRM. The rest of this doc is the convention used across every recipe in this repo, and a list of what to actually compare.

## The tagging convention

Every recipe in this repo recommends the same three-part UTM convention on every branch's destination URL:

```
?utm_source=ak-redirect&utm_campaign=<recipe-or-page>&utm_content=<branch-name>
```

What each piece is for:

- `utm_source=ak-redirect` — fixed across every recipe. Lets you isolate "supporters who arrived at a destination page via an AK redirect snippet" from supporters who arrived from email, ads, or organic links.
- `utm_campaign=<recipe-or-page>` — identifies *which* redirect snippet or campaign produced the redirect. Use the recipe name (`ladder-from-prior-gift`, `monthly-upgrade`, etc.) or a more specific campaign tag if you run the same recipe on multiple pages.
- `utm_content=<branch-name>` — identifies *which branch* of the snippet fired. This is the field you'll filter on most.

Each recipe in this repo includes a "tagged version" of its snippet showing the convention applied. The recipe READMEs use predictable `utm_content` values (`ladder` / `entry`, `new` / `returning`, `upgrade-ask` / `already-monthly`, etc.) — keep your own values short and consistent across recipes so reports are easy to read.

## Why this scheme

A few reasons to use UTM parameters (rather than custom tracking parameters) and to attach them at the destination URL (rather than rely on AK action records alone):

- **GA picks them up automatically.** If the destination donation or thank-you page is tagged with Google Analytics, no additional configuration is needed — the `utm_*` parameters flow through to GA sessions and conversions.
- **AK preserves them in action records.** When a supporter submits an action on a page reached via a tagged URL, AK stores the full landing URL on the action record. The `utm_content` value travels with every downstream donation, signature, or submission.
- **CRMs and warehouses inherit them.** Most AK → CRM or AK → data warehouse syncs carry the landing URL through. Branch-level analytics survive the pipeline.

## How to preserve incoming UTMs

If the supporter arrived at the AK action page with their own `?utm_source=facebook&utm_campaign=spring-launch` already attached, those parameters live in `args.*` inside the snippet (see the `utm-routing` recipe). They are *not* automatically preserved when the snippet redirects to a new page — the snippet only outputs whatever URL its branch produces.

Two options if you care about preserving the user's original source through the redirect:

**Option A — append the original source as a separate parameter.** Add the user's incoming UTMs to the destination URL alongside the recipe's own tracking:

```django
{% if user.custom_fields.donation_count_2026 > 3 %}
https://yourorg.actionkit.com/donate/donate/?amounts=…&utm_source=ak-redirect&utm_campaign=ladder-from-prior-gift&utm_content=ladder&original_source={{ args.utm_source|default:"" }}
{% else %}
…
{% endif %}
```

The `original_source` custom parameter rides along to GA and the destination page. The recipe's own `utm_source=ak-redirect` still wins for redirect-attribution; the `original_source` parameter is purely informational.

**Option B — accept the loss.** For most analyses the AK action record already knows the user's original source (it stored the landing URL on the *previous* action — the one whose redirect snippet you're now firing). Joining the original-action record to the donation downstream usually recovers the source. Don't over-engineer the snippet if you don't need to.

## What to actually measure

Branch-level UTMs give you the data; you still have to ask the right question. The questions worth asking, in priority order:

### 1. Did the branching produce a different outcome than no branching?

The baseline question. Compare branch-level conversion (donation rate, average gift, share rate, second-action rate — whatever your campaign is optimizing for) against a control campaign that sent every supporter to the same single page.

If you don't have a clean baseline, run the snippet for a few weeks, then disable it for a few weeks and run the same campaign with a single destination page. Or run both in parallel by installing the snippet on half your pages and a flat redirect on the other half.

### 2. Are the branches differently sized than expected?

Look at submitter counts per branch. If 95% of supporters hit `{% else %}` and almost no one trips the explicit conditions, your branching logic isn't doing much work — the snippet has the overhead of branching with the impact of a single-page redirect. Either tighten the conditions (lower a threshold, expand a tag set) or simplify back to a single destination.

The reverse problem: if a branch you expected to be small (the laddered branch on a donation-history recipe, say) is catching half your traffic, your thresholds may be too generous and the branch is losing its sharpness.

### 3. Are the branches outperforming a generic page individually?

Each branch should beat a generic thank-you on its own merits. The laddered branch should produce higher average gifts than a flat ask. The monthly-upgrade branch should convert non-monthly donors to monthly at a rate above your baseline monthly-acquisition channels. If a branch is underperforming its baseline, the branch's destination page is doing the wrong job — fix the page, not the snippet.

### 4. Is there spillover damage on related metrics?

Watch for cannibalization. Common patterns:

- A monthly-upgrade snippet might cannibalize one-time donation revenue from the same supporters. Trading short-term cash for sustainer revenue is usually a good deal, but measure both sides.
- A "send Facebook supporters to a share page" branch might reduce immediate donation revenue from that segment. If Facebook is your strongest paid-acquisition channel, that's worth knowing — you might want them on a donation page after all.

Always include the displaced metric in the comparison, not just the metric you were optimizing.

## Sample size

The biggest practical mistake in measuring redirect snippets: drawing conclusions too early. A few rules of thumb:

- For one-time donation rate: at least a few hundred signers per branch.
- For monthly conversion rate: at least a thousand signers per branch (monthly conversion is rarer and noisier than one-time).
- For share or share-to-friend rate: at least a few hundred per branch; share rates are wildly variable.
- For a downstream second-action rate (e.g., "did the new user take a second action within 30 days"): at least a few hundred per branch, and a full 30 days of observation before reading the number.

Smaller samples than these can be directionally interesting but shouldn't drive permanent decisions. When in doubt, wait a full campaign cycle.

## Where to look at the data

Three reasonable places to pull branch-level results from, ordered from easiest to most involved:

### AK donation reports

For any branch that ends in a donation, the simplest measurement path. AK donation reports can be filtered or grouped by source, campaign, or landing URL — the `utm_*` parameters you set on the destination URL are stored on each donation record.

In the AK admin, look at donation reports for the destination donation pages and group/filter by `Source` or `Page Source` (depending on your AK version). Each `utm_content` value becomes its own row.

### Google Analytics

For any branch whose destination page is tagged with GA, the `utm_*` parameters flow through automatically. GA shows:

- Sessions per branch (good for confirming branch volumes).
- Bounce rate per branch (good for catching destination pages that are misaligned with the branch's audience).
- Conversion rate per branch, if GA goals are set up.
- Time-on-page per branch.

GA is less useful for revenue questions than AK donation reports (unless you've set up Enhanced Ecommerce on the donation page), but better for engagement and qualitative questions.

### CRM or data warehouse

If you sync AK actions and donations downstream, the destination landing URL — and the `utm_*` parameters on it — usually ride along into the warehouse. Once there, you can run any analysis you want: cohort analysis (do supporters who hit the laddered branch lifetime-give more?), funnel analysis across multiple actions, segmentation against other supporter dimensions.

This is the most powerful but most setup-heavy path. Worth it for organizations running redirect snippets at scale across many campaigns.

## A note on A/B testing

AK redirect snippets don't have native A/B testing support — there's no "send 50% of supporters down branch A, 50% down branch B" primitive. You can approximate it with the `divisibleby` filter on the user ID:

```django
{% if user.id|divisibleby:2 %}
  (branch A)
{% else %}
  (branch B)
{% endif %}
```

Half the supporters (those with even user IDs) hit branch A, half hit branch B. This is good enough for casual experiments but isn't a real randomized split — user IDs aren't random, they correlate with how long someone's been on your list. If you need rigorous A/B testing, look at AK's own A/B testing features on the page side, or run the comparison across distinct campaigns.

## Summary

For each recipe in this repo:

1. Copy the recipe's "tagged version" snippet from its README.
2. Adjust the `utm_campaign` and `utm_content` values if you want them more specific to your campaign.
3. After two to four weeks of campaign traffic, pull branch-level numbers from AK donation reports or GA.
4. Compare each branch's performance to a no-branching baseline (historical conversion from a flat thank-you, or a parallel control campaign).
5. Adjust thresholds, destination pages, or ask amounts based on what you find. Don't change them mid-campaign — let each variant collect at least a few hundred submitters before deciding.

The snippets are tools, not magic. Measuring them honestly is the only way to know whether the branching is paying for the overhead of maintaining it.
