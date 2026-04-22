# Contributing

New recipes welcome. Here's how to submit one.

## Before you submit

Your recipe must:

- [ ] Work on a real ActionKit instance — tested, not theoretical.
- [ ] Document every variable it uses in the `README.md`.
- [ ] Include a fallback `{% else %}` branch in the snippet.
- [ ] Note any AK-version or feature dependency (e.g. Payments-only).
- [ ] Live in its own folder under `recipes/`, with a `kebab-case` folder name.

## Folder layout

Copy `recipes/_TEMPLATE/` to `recipes/your-recipe-name/` and fill in both files:

- `README.md` — explanation, variables, use cases, fallback, gotchas
- `snippet.txt` — the actual copy-paste content

## README style

- Lead with one sentence explaining what the recipe does.
- Describe the logic, not the syntax.
- Use `yourorg.actionkit.com` as the generic subdomain placeholder.
- If you adapted from someone else's public talk, blog post, or repo, credit them in a **Credit** section near the top.

## Testing checklist

Before you submit, test your recipe as:

- A new user the action just created
- A returning user with the relevant variables set
- A user missing the relevant variables (should hit the fallback)

## PR process

1. Fork the repo.
2. Add your recipe folder.
3. Open a PR with a short description of the use case it solves.
4. Expect review for correctness and documentation completeness.

## Code of conduct

Be kind. This is a community resource for ActionKit users at progressive advocacy orgs.
