"""Optional local storyboard renderer; no external account or network access."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path


def load_bundle(path: Path) -> dict:
    bundle = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(bundle, dict):
        raise ValueError("Storyboard must be a JSON object")
    scenes = bundle.get("scenes")
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= 12:
        raise ValueError("Provide between 1 and 12 scenes")
    evidence = bundle.get("evidence", [])
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(e, dict) or not isinstance(e.get("url"), str) or not e["url"].startswith("https://")
        for e in evidence
    ):
        raise ValueError("HTTPS evidence references are required")
    ids = [e.get("id") for e in evidence]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Evidence IDs must be unique nonempty strings")
    for scene in scenes:
        if not isinstance(scene, dict):
            raise ValueError("Scenes must be objects")
        for field, maximum in (("title", 48), ("body", 200)):
            if not isinstance(scene.get(field), str) or not scene[field].strip() or len(scene[field]) > maximum:
                raise ValueError(f"Invalid scene {field}")
        seconds = scene.get("seconds")
        if isinstance(seconds, bool) or not isinstance(seconds, int) or not 1 <= seconds <= 15:
            raise ValueError("Scene seconds must be an integer from 1 to 15")
        references = scene.get("evidence_ids")
        if not isinstance(references, list) or not references or any(not isinstance(i, str) or i not in ids for i in references):
            raise ValueError("Every scene must reference known evidence IDs")
    if sum(s["seconds"] for s in scenes) > 120:
        raise ValueError("Maximum demo duration is 120 seconds")
    return bundle


def execute(command: list[str], cwd: Path, timeout: int = 180) -> str:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout)
    if completed.returncode:
        raise RuntimeError(f"{Path(command[0]).name} failed: {completed.stderr[-3000:]}")
    return completed.stdout


def inspect_video(path: Path) -> dict:
    probe = shutil.which("ffprobe")
    if not probe:
        raise RuntimeError("ffprobe is required")
    data = json.loads(execute([probe, "-v", "error", "-show_streams", "-show_format",
                               "-of", "json", str(path.resolve())], path.parent))
    videos = [s for s in data["streams"] if s["codec_type"] == "video"]
    if not videos:
        raise ValueError("No video stream")
    return {"duration_seconds": float(data["format"]["duration"]),
            "width": videos[0]["width"], "height": videos[0]["height"],
            "codec": videos[0]["codec_name"], "size_bytes": path.stat().st_size}


def render(bundle_path: Path, output: Path, font: Path) -> dict:
    bundle = load_bundle(bundle_path)
    encoder = shutil.which("ffmpeg")
    if not encoder or not shutil.which("ffprobe"):
        raise RuntimeError("Install ffmpeg and ffprobe before rendering")
    if not font.is_file():
        raise ValueError("Pass an existing TrueType font with --font")
    # Never overwrite an earlier run, including a failed run's evidence.
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    report = {"status": "running", "mode": "local-title-card-demo",
              "upstream_mode": "provided-storyboard",
              "synthetic": bool(bundle.get("synthetic", False)),
              "started_at": datetime.now(timezone.utc).isoformat(),
              "external_cost_usd": None,
              "limitations": ["No HeyGen avatar, voiceover or Activepieces execution",
                              "Evidence links are provenance; semantic truth needs editorial review",
                              "Rendering uses the supplied storyboard; it does not run web search"]}
    (output / "input.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        shutil.copyfile(font, output / "font.ttf")
        total = 0
        filters = ["drawbox=x=48:y=132:w=6:h=830:color=0x33ddaa:t=fill"]
        for index, scene in enumerate(bundle["scenes"]):
            # Position each line explicitly; font metrics differ across FFmpeg builds.
            lines = [(f"{index+1:02d} / {len(bundle['scenes']):02d}", 28, 200, "0x33ddaa")]
            lines += [(line, 44, 350 + n * 60, "white")
                      for n, line in enumerate(textwrap.wrap(scene["title"], 21))]
            lines += [(line, 32, 600 + n * 48, "0xc4d0dc")
                      for n, line in enumerate(textwrap.wrap(scene["body"], 29))]
            for number, (value, size, ypos, color) in enumerate(lines):
                filename = f"scene{index}line{number}.txt"
                (output / filename).write_text(value, encoding="utf-8")
                end = total + scene["seconds"]
                filters.append(f"drawtext=fontfile=font.ttf:textfile={filename}:expansion=none:"
                               f"fontsize={size}:fontcolor={color}:line_spacing=16:x=84:y={ypos}:"
                               f"enable='gte(t,{total})*lt(t,{end})'")
            total += scene["seconds"]
        (output / "footer.txt").write_text("APTFLOW / LOCAL DEMO", encoding="utf-8")
        filters.append("drawtext=fontfile=font.ttf:textfile=footer.txt:expansion=none:fontsize=22:fontcolor=0x33ddaa:x=84:y=1110")
        execute([encoder, "-hide_banner", "-loglevel", "error", "-n", "-f", "lavfi", "-i",
                 f"color=c=0x0b1523:s=720x1280:r=24:d={total}", "-vf", ",".join(filters),
                 "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
                 "-movflags", "+faststart", "demo.mp4"], output)
        media = inspect_video(output / "demo.mp4")
        checks = {"duration": abs(media["duration_seconds"] - total) <= 0.1,
                  "dimensions": (media["width"], media["height"]) == (720, 1280),
                  "nonempty": media["size_bytes"] > 1000}
        execute([encoder, "-hide_banner", "-loglevel", "error", "-xerror", "-i", "demo.mp4",
                 "-f", "null", "-"], output)
        checks["full_decode"] = True
        report.update(media=media, checks=checks)
        if not all(checks.values()):
            raise ValueError("Media acceptance checks failed")
        report["status"] = "local_demo_completed"
        report["sha256"] = hashlib.sha256((output / "demo.mp4").read_bytes()).hexdigest()
        (output / "sources.md").write_text("# Evidence\n\n" + "\n".join(
            f"- [{e['id']}] {e['url']} — {e.get('finding', '')}" for e in bundle["evidence"]), encoding="utf-8")
    except Exception as error:
        report.update(status="failed", error=str(error))
        raise
    finally:
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
        (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/arial.ttf"))
    args = parser.parse_args()
    try:
        result = render(args.bundle.resolve(), args.out.resolve(), args.font.resolve())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
