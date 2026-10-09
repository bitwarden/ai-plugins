# Bitwarden Stripe Tools Plugin

Reads Bitwarden's Stripe test-mode data through a guarded Stripe CLI wrapper.

## Overview

When local testing or debugging needs Stripe data that the web vault and Admin Portal cannot show, such as a subscription's status, its attached test clock, a failed test-mode payment, or coupon and price IDs, this plugin reads it through the `stripe_cli.py` wrapper. The wrapper refuses any key that is not a test key before calling the CLI, builds every command from scratch, and never forwards a caller-supplied flag.

## Skills

| Skill              | What It Does                                                                                                                                                      |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `using-stripe-cli` | Queries read-only Stripe test-mode data, previews a subscription's next invoice, and advances an already-attached test clock through the `stripe_cli.py` wrapper. |

## Read-only contract

The wrapper is read-only apart from one sanctioned write: advancing a test clock that is already attached. The invoice preview is sent as a POST but creates nothing, so it counts as a read. Other plugins rely on this guarantee, so any future write capability ships as a separate script and skill, never as a new wrapper subcommand.

## Prerequisites

- **[Stripe CLI](https://docs.stripe.com/stripe-cli)**, authenticated once with `stripe login`. The wrapper was written against Stripe CLI v1.35.
- **Python 3.11+**, which the wrapper needs to read the CLI's config and verify the key is a test key. If `STRIPE_API_KEY` is set, the wrapper checks that key instead and does not read the config.

## Installation

```bash
/plugin install bitwarden-stripe-tools@bitwarden-marketplace
```

## Usage

The skill activates on natural-language requests:

```
What's the status of test subscription sub_abc123, and is a test clock attached?
```

```
Why did the last test-mode payment for cus_abc123 fail?
```

## References

- [Stripe CLI](https://docs.stripe.com/stripe-cli)
- [Stripe test clocks](https://docs.stripe.com/billing/testing/test-clocks)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
