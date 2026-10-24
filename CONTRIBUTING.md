# Contributing

Use Python 3.11+. No external packages are required for the demo or unit tests.

```console
python -m unittest discover -s tests -v
python aptflow.py init
python aptflow.py run --out outputs/contributor-demo
```

Include a documented adapter contract, synthetic fixtures and meaningful failure tests. Keep live tests opt-in and use your own accounts. See docs/ADAPTERS.md.

Do not include credentials, personal notebook IDs, copied sessions or user-generated media in fixtures. User config, outputs and graphify-out are local-only. Review the staged diff before any push.

Describe working behavior separately from planned integrations. Do not claim autonomous tool selection or live provider workflows until implemented and tested.

The starter is distributed under the MIT license. Contributions must be compatible with it; review third-party assets and provider SDK terms separately.
