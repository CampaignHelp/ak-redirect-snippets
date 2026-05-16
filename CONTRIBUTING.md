# Contributing

New recipes welcome. Here's how to submit one.

## Before you submit

Your recipe must:

- [ ] Work on a real ActionKit instance — tested, not theoretical.
- [ ] Include a fallback `{% else %}` branch in the snippet.
- [ ] Live in its own folder under `recipes/`, with a `kebab-case` folder name.
- [ ] Ship both `snippet.txt` (clean copy) and `snippet-tagged.txt` (with UTM measurement tags applied).
- [ ] Include a README that follows the fat structure (see *README style* below).
- [ ] Note any AK-version or feature dependency (e.g., Payments-only).

## Folder layout

Copy `recipes/_TEMPLATE/` to `recipes/your-recipe-name/` and fill in the four files:

- `README.md` — full teaching doc, written for an AK admin who has never seen Django template syntax
- `snippet.txt` — the actual copy-paste content
- `snippet-tagged.txt` — same snippet with UTM measurement tags applied to each branch's destination URL (see [`MEASUREMENT.md`](MEASUREMENT.md) for the convention)

## README style

The bar is "an AK admin reading this can install the recipe without needing to read anything else." Follow the fat structure documented in `recipes/_TEMPLATE/README.md`:

1. **One-sentence summary** at the top — sells the recipe.
2. **Credit** section if adapted from a public talk, blog, or repo.
3. **What this recipe does** — plain language, two to four sentences. Describe the supporter experience, not the syntax.
4. **Who this is for** — *use this when* / *skip this if* bullets. Help the reader self-select.
5. **The snippet** — show it inline, point to `snippet.txt` for the clean copy.
6. **How the snippet works, line by line** — assume zero Django knowledge. Walk through every `{% %}` and `{{ }}` placeholder. Show what each line renders as for a representative user. This is the section that separates a recipe from a code dump.
7. **What you need before you install** — prerequisites: AK version/feature, custom fields, destination pages.
8. **How to install** — numbered steps, including how to find the right field in AK admin.
9. **What can go wrong (specific to this recipe)** — recipe-specific failure modes, not the generic ones in the top-level README. Give each its own `### subheading`.
10. **How to test** — concrete test scenarios with expected destination URLs per branch.
11. **How to know if it's working** — what metric tells you the branching is doing real work, plus the tagged version of the snippet. Reference `MEASUREMENT.md` for the convention.
12. **Tested on** — which instance, which date, which branches pass automatically vs verified by hand. Be honest.

Other style rules:

- Use `yourorg.actionkit.com` as the generic subdomain placeholder.
- Sentence case for all headings.
- Concrete examples beat abstract description. If you say a snippet renders to `$50, $75, $100, $125, $150`, show that.

## Testing checklist

Before you submit, test your recipe as:

- A user who triggers each explicit branch (one per `{% if %}` / `{% elif %}`).
- A user where no explicit branch matches — the `{% else %}` fires.
- A user where the variable being branched on is missing entirely.

If your recipe can be added to the automated matrix in `tests/`, that's preferred — see `tests/README.md` for how. Recipes that can't be automatically tested (e.g., require real donation history) should document why.

## PR process

1. Fork the repo.
2. Add your recipe folder.
3. Open a PR with a short description of the use case it solves.
4. Expect review for correctness, documentation depth, and the tagged-snippet variant.

## Code of conduct

Be kind. This is a community resource for ActionKit users at progressive advocacy orgs.
