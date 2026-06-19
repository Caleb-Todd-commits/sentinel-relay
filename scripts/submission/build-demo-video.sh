#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="$ROOT/outputs/manual-20260618-submission/video"
FINAL="$ROOT/submission/Sentinel-Relay-Demo.mp4"
AUDIO="$ROOT/submission/narration.aiff"

mkdir -p "$WORK/clips"

images=(
  "$ROOT/submission/cover.png"
  "$ROOT/submission/screenshots/workspace.png"
  "$ROOT/submission/screenshots/approval.png"
  "$ROOT/submission/screenshots/result.png"
  "$ROOT/submission/screenshots/custom-question.png"
  "$ROOT/submission/cover.png"
)

durations=(18.0 38.0 38.0 38.0 38.0 10.0)

: > "$WORK/concat.txt"

for index in "${!images[@]}"; do
  number=$(printf "%02d" "$((index + 1))")
  clip="$WORK/clips/clip-$number.mp4"
  duration="${durations[$index]}"
  fade_out=$(awk -v d="$duration" 'BEGIN { printf "%.3f", d - 0.35 }')

  ffmpeg -hide_banner -loglevel error -y \
    -loop 1 -i "${images[$index]}" -t "$duration" \
    -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(max(zoom,pzoom)+0.00018,1.035)':d=1:s=1920x1080:fps=30,fade=t=in:st=0:d=0.35,fade=t=out:st=$fade_out:d=0.35,format=yuv420p" \
    -an -c:v libx264 -preset medium -crf 18 -r 30 "$clip"

  printf "file '%s'\n" "$clip" >> "$WORK/concat.txt"
done

ffmpeg -hide_banner -loglevel error -y \
  -f concat -safe 0 -i "$WORK/concat.txt" \
  -i "$AUDIO" \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$FINAL"

echo "$FINAL"
