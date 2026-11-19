# Troubleshooting

Moved from the README. A Turkish version of the common cases is in [QUICKSTART.tr.md](QUICKSTART.tr.md).

| Symptom | What to do |
|---|---|
| Config file does not exist | Run `python aptflow.py init` first, or pass `--config PATH` |
| Config already exists | Edit it or initialize a different path; init will not replace it |
| Output directory already exists | Choose a new `--out` path; previous work is preserved |
| Live doctor reports not ready | Expected: implement/register the provider adapters before live use |
| An API key appears to have no effect | The starter does not implement live APIs or load .env automatically |
| FFmpeg/ffprobe is missing | Install both for render, or use the storyboard-only demo |
| Font is missing | Pass `--font` pointing to your own existing TrueType font |
| FFmpeg reports drawtext or libx264 missing | Use a build with those features; the core demo does not need FFmpeg |
| Video has no voice/avatar | Expected for local title-card rendering; no avatar service is called |

See the [command reference](CLI.md) for the commands and exit codes.
