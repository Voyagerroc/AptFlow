"""Public CLI: scaffold, inspect, run synthetic workflow, optionally render locally."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from .config import read_config
from .media import render
from .workflow import plan, run


def main() -> int:
    parser = argparse.ArgumentParser(description="Account-independent specialist-tool workflow starter")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a private user config from the demo template")
    init.add_argument("--config", type=Path, default=Path("aptflow.json"))
    for name in ("plan", "doctor", "run"):
        sub = commands.add_parser(name)
        sub.add_argument("--config", type=Path, default=Path("aptflow.json"))
        if name == "run":
            sub.add_argument("--out", type=Path, required=True)
    media = commands.add_parser("render", help="Render a storyboard locally; requires FFmpeg")
    media.add_argument("bundle", type=Path)
    media.add_argument("--out", type=Path, required=True)
    media.add_argument("--font", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            # Bundled template is included in wheel installs as package data.
            source = Path(__file__).parent / "demo-config.json"
            with args.config.open("x", encoding="utf-8") as destination:
                destination.write(source.read_text(encoding="utf-8"))
            result = {"created": str(args.config), "mode": "demo", "account_required": False}
        elif args.command == "render":
            candidates = [Path("C:/Windows/Fonts/arial.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                          Path("/System/Library/Fonts/Supplemental/Arial.ttf")]
            font = args.font or next((p for p in candidates if p.is_file()), None)
            if font is None:
                raise ValueError("No default font found; supply --font /path/to/font.ttf")
            result = render(args.bundle.resolve(), args.out.resolve(), font.resolve())
        else:
            config = read_config(args.config)
            result = run(config, args.out.resolve()) if args.command == "run" else plan(config)
            if args.command == "doctor":
                result["optional_render_tools"] = {tool: bool(shutil.which(tool)) for tool in ("ffmpeg", "ffprobe")}
                print(json.dumps(result, indent=2))
                return 0 if result["ready"] else 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
