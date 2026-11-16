# Security policy

## Supported scope

AptFlow is a pre-1.0 starter. Security fixes target the latest main branch. No long-term support, production suitability or response-time guarantee is promised.

## Report privately

Email **erol@voyagerroctechnologies.com** with the affected revision, a minimal synthetic reproduction and the expected impact. Do not publish credentials, session cookies, personal notebook IDs, user media or exploitable details in a public issue. Do not send real customer data.

## Current boundaries

- The default demo uses synthetic fixtures and makes no provider requests. Its zero external-call count is not a cost or security guarantee for future adapters.
- Live provider adapters are extension stubs. Supplying credentials does not implement them.
- Configuration, environment variables, outputs and credentials belong outside version control. Review fixtures and logs before sharing them.
- Optional FFmpeg rendering runs locally; use media and fonts you have permission to process. Do not treat this starter as a sandbox for hostile input.
- Optional Activepieces/Docker configuration is for evaluation; it has not established production isolation or provider compliance.

For an ordinary reproducible bug without sensitive details, use the public issue tracker and [contribution guide](CONTRIBUTING.md).
