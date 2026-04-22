# Donation URL parameters reference

ActionKit's NGP VAN Payments-enabled donation pages accept URL parameters that pre-fill the ask-amount buttons. Pair these with the redirect-snippet recipes to build tailored asks per user.

> This reference documents feature #8 (*Vary your ask amount*) from Shannon Turner's 2026 ClientCon talk. Credit to Shannon — see [@shannonturner](https://github.com/shannonturner) / [Supraluminique](https://fasterthanlight.tech).

## Parameters

| Parameter | Frequency tab | Example |
|---|---|---|
| `amounts=` | One-time | `?amounts=10,20,30,40,50,60,70` |
| `weekly_amounts=` | Weekly | `?weekly_amounts=3.50,4.50,5.50,6.50,7.50,8.50,9.50` |
| `monthly_amounts=` | Monthly | `?monthly_amounts=5,10,15,20,25,30,35` |
| `annual_amounts=` | Annually | `?annual_amounts=25,50,75,100,125,150,175` |

Each parameter takes a comma-separated list of numbers. ActionKit renders these as the ask-amount buttons; the user can also enter a custom amount in the last slot.

## Combining parameters

All four can be passed together. When the user selects a frequency tab, AK displays the matching amounts:

```
?amounts=10,20,30,40,50,60,70&weekly_amounts=3.50,4.50,5.50,6.50,7.50,8.50,9.50&monthly_amounts=5,10,15,20,25,30,35&annual_amounts=25,50,75,100,125,150,175
```

## Combining with redirect snippets

The power move: build the URL dynamically in a redirect snippet so each user lands on a donation page calibrated to their giving history.

See [`../recipes/ladder-from-prior-gift/`](../recipes/ladder-from-prior-gift/) for the canonical example.

## Requirements

- Only works on **NGP VAN Payments-enabled** donation pages (AK's newer payments system, not the legacy provider).
- The donation page must be configured to accept every frequency you pass parameters for — otherwise the unconfigured tabs show nothing.
