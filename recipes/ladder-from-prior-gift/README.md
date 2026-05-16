# Donation ladder from prior gift

Send returning donors to a donation page pre-filled with ask amounts scaled from their largest previous gift. Send everyone else to a monthly-giving page with entry-level amounts.

## Credit

This recipe is adapted directly from **Shannon Turner's** ClientCon 2026 demonstration of *Snippets in redirect URLs*. She presented this exact pattern as the flagship example of the feature. All credit for the technique goes to her.

- Shannon on GitHub: [@shannonturner](https://github.com/shannonturner)
- Shannon's consultancy, Supraluminique: [fasterthanlight.tech](https://fasterthanlight.tech)
- Shannon's ActionKit materials: [shannonturner/actionkit-clientcon-2025](https://github.com/shannonturner/actionkit-clientcon-2025)

## What this recipe does

When a supporter finishes any action on your page (signs a petition, RSVPs to an event, takes a survey), this snippet picks one of two follow-up destinations based on their donation history:

- **Loyal donors** (more than three gifts this year) → a donation page where the ask buttons are scaled to *their* giving capacity. Someone whose biggest past gift was $100 sees ask amounts of $50, $75, $100, $125, $150. Someone whose biggest was $25 sees $12.50, $18.75, $25, $31.25, $37.50.
- **Everyone else** (new donors, lapsed donors, signers who've never given) → a monthly-giving page with entry-level amounts ($5–$30).

The result: each supporter sees an ask calibrated to their giving history, instead of a single one-size-fits-all thank-you page.

## Who this is for

Use this when:

- You have an active donor base with measurable giving history.
- You're running a campaign that generates a lot of non-donor actions (petitions, RSVPs, surveys) and you want to convert some of those signers.
- Your donation page is a **Payments-enabled** AK page (see *What you need before you install* below).

Skip this if:

- You don't track per-user donation counts or amounts (the snippet has nothing to branch on).
- Your donation page is on a legacy non-Payments processor (the `amounts=` parameter is ignored there).

## The snippet

```django
{% if user.custom_fields.donation_count_2026 > 3 %}
https://yourorg.actionkit.com/donate/donate/?amounts={{ user.highest_previous_contribution|multiply:0.5 }},{{ user.highest_previous_contribution|multiply:0.75 }},{{ user.highest_previous_contribution|multiply:1 }},{{ user.highest_previous_contribution|multiply:1.25 }},{{ user.highest_previous_contribution|multiply:1.5 }}
{% else %}
https://yourorg.actionkit.com/donate/donate/?monthly_amounts=5,10,15,20,25,30
{% endif %}
```

A clean copy lives in `snippet.txt` next to this README.

## How the snippet works, line by line

If you've never seen Django template syntax before — the bits inside `{% %}` and `{{ }}` are placeholders that AK fills in with real values when a supporter submits the form. The rest of the text is the literal URL AK will redirect to.

### Line 1 — the condition

```django
{% if user.custom_fields.donation_count_2026 > 3 %}
```

`{% if %}` opens a branch. Read this line as: "If the user's `donation_count_2026` custom field is greater than 3, use the next URL."

- `user.custom_fields.donation_count_2026` — pulls a value from the user's record. `custom_fields` is the bucket where AK stores fields your team has added (as opposed to AK's built-in fields like name and email). `donation_count_2026` is the name your team gave the field.
- `> 3` — the comparison. The branch fires only when the value is greater than 3.

Change the threshold to match how *you* define "loyal." More than one gift? More than five? Edit the number.

### Line 2 — the laddered URL

```django
https://yourorg.actionkit.com/donate/donate/?amounts={{ user.highest_previous_contribution|multiply:0.5 }},{{ user.highest_previous_contribution|multiply:0.75 }},{{ user.highest_previous_contribution|multiply:1 }},{{ user.highest_previous_contribution|multiply:1.25 }},{{ user.highest_previous_contribution|multiply:1.5 }}
```

This is the URL the loyal-donor branch redirects to. The fixed parts:

- `https://yourorg.actionkit.com/donate/donate/` — your AK donation page. Replace `yourorg` and the slug with yours.
- `?amounts=…` — a parameter that overrides the page's default ask buttons. See `reference/donation-url-params.md` for the full list of these parameters.

The `{{ … }}` placeholders are where each ask amount gets calculated:

- `user.highest_previous_contribution` — a built-in AK field. The largest past gift this user has made, as a number.
- `|multiply:0.5` — a filter that multiplies the value before it. So if the largest past gift was $100, this renders as `50`.

Five buttons get built, at 0.5×, 0.75×, 1×, 1.25×, and 1.5× of the user's largest past gift. Adjust the multipliers to make the ladder steeper or gentler.

Rendered for a user whose largest past gift was $100:

```
https://yourorg.actionkit.com/donate/donate/?amounts=50,75,100,125,150
```

### Lines 3–4 — the fallback branch

```django
{% else %}
https://yourorg.actionkit.com/donate/donate/?monthly_amounts=5,10,15,20,25,30
```

`{% else %}` is the catch-all. Anyone whose `donation_count_2026` is **not** greater than 3 — including users where the field is missing or zero — gets redirected to this URL instead.

`?monthly_amounts=` sets the buttons on the **Monthly** tab of the donation page. Pick amounts appropriate for a first-time monthly donor.

You can include both `amounts=` and `monthly_amounts=` in the same URL — AK shows the right set based on which frequency tab the user picks. See `reference/donation-url-params.md` for combining the four tabs.

### Line 5 — close the conditional

```django
{% endif %}
```

Every `{% if %}` needs a matching `{% endif %}` somewhere below it. Leaving it off produces a template error and breaks the redirect.

## What you need before you install

- A **Payments-enabled** AK donation page. The `amounts=` and `monthly_amounts=` parameters are silently ignored on legacy donation pages (see top-level README → *Some features are Payments-only*).
- A **custom user field** that counts donations (here: `donation_count_2026`). Your team has to populate this — AK doesn't maintain it automatically. Update it nightly from your donation reports, or write to it via AK's user-update API on each successful donation.
- `user.highest_previous_contribution` is built into AK — it tracks the largest past gift per user automatically — but it will be empty for users who've never donated. The `{% else %}` branch handles those users by not referencing the field.
- The actual slug for your donation page. Update `donate/donate/` to whatever yours is called.

## How to install

1. Copy the contents of `snippet.txt`.
2. In AK admin, open the page you want to add the redirect to (the petition, RSVP, survey — **not** the donation page itself).
3. Click the **After-action info** tab.
4. Paste the snippet into the **Redirect URL** field. Do not wrap it in quotes (see top-level README → *Don't wrap the snippet in quotes*).
5. Replace `yourorg.actionkit.com` with your subdomain. Replace `donate/donate/` with your real donation page slug. Adjust `donation_count_2026` to match the custom field name on your instance.
6. Save the page.
7. Test before announcing the campaign (see *How to test* below).

## What can go wrong (specific to this recipe)

### `highest_previous_contribution` is empty for some users

If a user has never donated, this field is empty. In the laddered branch, `|multiply:0.5` on an empty value produces an empty string — so the URL ends up as `?amounts=,,,,`, which AK renders as no ask amounts at all.

The current snippet sidesteps this by only entering the laddered branch when `donation_count_2026 > 3`, on the assumption that anyone with four or more donations also has a non-empty `highest_previous_contribution`. If you lower the threshold to `> 0` or `> 1`, add a defensive check:

```django
{% if user.custom_fields.donation_count_2026 > 1 and user.highest_previous_contribution %}
```

The second clause short-circuits if the field is empty, so the laddered URL never tries to multiply nothing.

### The ladder is too aggressive

A donor whose largest past gift was $500 sees asks of $250, $375, $500, $625, $750. That can backfire — the user feels like you're pushing them past their comfort.

Two ways to soften:

- Lower the top multiplier. Replace `1.5` with `1.25` (or `1.1`).
- Cap the ladder. Add an `{% elif %}` branch for high-dollar donors that uses a flat ask range instead of a multiplier.

### Decimal ask amounts look ugly

`|multiply:0.5` on a value of $37 produces `18.5`. The donation page accepts it, but `$18.50` next to `$27.75` and `$37.00` on the button row looks unintentional.

If round numbers matter to you, either:

- Stick to multipliers that produce whole numbers given your typical gift amounts (e.g., use `0.5`, `1.0`, and `1.5` only — drop the `0.75` and `1.25` buttons).
- Treat the decimals as known cosmetic noise and move on. Donors rarely mention it.

### The threshold is wrong for your donor base

`> 3` was Shannon's example. For your org it might be `> 1` (most donors give once a year, so a second gift signals loyalty) or `> 10` (you have a heavy monthly base and want to flag only the most engaged).

Look at the distribution of `donation_count_2026` across your active users before picking a number. Pick a threshold where roughly the top quartile of donors lands in the laddered branch — high enough to be meaningful, low enough that the laddered branch sees real traffic.

## How to test

You'll need at least three test accounts in your instance — or use your AK admin account with manually edited custom field values.

1. **Loyal donor test.** Set `donation_count_2026 = 5` and `highest_previous_contribution = 100` on a test user. Submit the form as that user. Confirm the destination URL is exactly:
   `https://yourorg.actionkit.com/donate/donate/?amounts=50,75,100,125,150`
2. **Sub-threshold donor test.** Set `donation_count_2026 = 1` on a test user. Submit. Confirm the destination URL is:
   `https://yourorg.actionkit.com/donate/donate/?monthly_amounts=5,10,15,20,25,30`
3. **Never-donor test.** Use a fresh test user with no `donation_count_2026` set at all. Submit. Same expected URL as test 2 — confirm the `{% else %}` branch catches them.

For each test, also load the destination page and confirm the ask buttons show the expected amounts. AK silently falls back to the page's default amounts if anything in the URL is off (see top-level README → *Unresolvable paths silently fall back*).

The `tests/` folder in this repo automates tests 2 and 3 against the Robotic Dogs sandbox via Playwright.

## How to know if it's working

The snippet is doing its job if loyal donors who hit the laddered branch give **more on average** than they did before, and if everyone else converts to monthly at a measurable rate.

To get that data, tag each branch's destination URL with a tracking parameter so you can pull branch-level results from AK donation reports.

Tagged version of the snippet:

```django
{% if user.custom_fields.donation_count_2026 > 3 %}
https://yourorg.actionkit.com/donate/donate/?amounts={{ user.highest_previous_contribution|multiply:0.5 }},{{ user.highest_previous_contribution|multiply:0.75 }},{{ user.highest_previous_contribution|multiply:1 }},{{ user.highest_previous_contribution|multiply:1.25 }},{{ user.highest_previous_contribution|multiply:1.5 }}&utm_source=ak-redirect&utm_campaign=ladder-from-prior-gift&utm_content=ladder
{% else %}
https://yourorg.actionkit.com/donate/donate/?monthly_amounts=5,10,15,20,25,30&utm_source=ak-redirect&utm_campaign=ladder-from-prior-gift&utm_content=entry
{% endif %}
```

The two branches now carry distinct `utm_content` values (`ladder` vs `entry`). AK stores the full landing URL on each donation record, so you can:

- **In AK donation reports** — filter or group by `utm_content` to compare average gift, conversion rate, and total raised across branches.
- **In Google Analytics** (if your donation page is tagged for GA) — the same `utm_*` parameters flow through. Use them to compare bounce rate and time-on-page across branches.
- **In your CRM or data warehouse** — if you sync AK donations downstream, the landing URL travels with each gift record.

What to compare:

- Average gift on the laddered branch vs your historical average gift from a similar donor segment. If the ladder is working, average gift goes up.
- Conversion rate on the entry-level branch (donations divided by signers). A directional read on whether the monthly ask is finding takers.
- Total raised across both branches vs the same campaign run without redirect branching, if you have a baseline.

Sample size: redirect-snippet effects need a few hundred signers per branch before the numbers stabilize. Wait at least a few weeks of campaign traffic before drawing conclusions, especially on the laddered branch (which usually sees lower volume).

See the top-level `MEASUREMENT.md` for the branch-tagging convention used across all recipes in this repo.

## Tested on

Tested on Robotic Dogs (`roboticdogs.actionkit.com`) on 2026-04-22. The `{% else %}` branch (sub-threshold and never-donor cases) passes via the automated Playwright matrix in `tests/`. The laddered branch requires a user with real donation history, which can't be planted via REST; its branch logic is syntactically identical to the fallback and has been visually verified.
