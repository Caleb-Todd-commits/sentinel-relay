#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="$ROOT/outputs/manual-20260618-submission/video"
FINAL="$ROOT/submission/Sentinel-Relay-Demo.mp4"
AUDIO="$ROOT/submission/narration.aiff"

mkdir -p "$WORK/clips"

images=(
  "$ROOT/outputs/manual-20260618-submission/presentations/sentinel-relay-pitch/preview/slide-01.png"
  "$ROOT/submission/screenshots/home.png"
  "$ROOT/submission/screenshots/demo.png"
  "$ROOT/outputs/manual-20260618-submission/presentations/sentinel-relay-pitch/preview/slide-03.png"
  "$ROOT/submission/screenshots/workflow-01-room.png"
  "$ROOT/submission/screenshots/workflow-03-evidence.png"
  "$ROOT/submission/screenshots/workflow-03-evidence.png"
  "$ROOT/submission/screenshots/workflow-06-challenge.png"
  "$ROOT/submission/screenshots/workflow-07-approval-gate.png"
  "$ROOT/submission/screenshots/workflow-08-approved.png"
  "$ROOT/submission/screenshots/workflow-10-report-ready.png"
  "$ROOT/submission/screenshots/workflow-report.png"
  "$ROOT/submission/screenshots/report.png"
  "$ROOT/outputs/manual-20260618-submission/presentations/sentinel-relay-pitch/preview/slide-08.png"
)

durations=(8.0 11.4 12.6 6.9 12.1 12.6 25.7 25.4 11.3 12.2 9.8 10.9 4.1 12.2)

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
