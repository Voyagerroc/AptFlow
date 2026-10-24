"""Run directly after cloning; installation is optional."""
from aptflow_core.cli import main
from aptflow_core.media import load_bundle, render

if __name__ == "__main__":
    raise SystemExit(main())
