# Sentinel Relay event submission archive

This directory preserves the original event deliverables and the current production screenshots.

## Current references

- Application: https://sentinel-relay-alpha.vercel.app
- Public repository: https://github.com/Caleb-Todd-commits/sentinel-relay
- Current screenshots: `screenshots/workspace.png`, `screenshots/approval.png`, `screenshots/result.png`, and `screenshots/custom-question.png`
- Presentation/voiceover script: `demo-narration-script.md`

## Historical artifacts

`cover.png`, `Sentinel-Relay-Pitch-Deck.pptx`, and `Sentinel-Relay-Demo.mp4` are preserved as the original event submission. They may show the retired multi-page interface and should not be used as current product documentation.

## Current status

- [x] Repository is public.
- [x] MIT license is present.
- [x] Production deployment is ready.
- [x] Production and repository links work signed out.
- [x] Current screenshots were captured from production.
- [x] Seeded approval flow and open-ended analysis were smoke-tested.

Regenerate current screenshots with:

```bash
node scripts/submission/capture-demo.mjs https://sentinel-relay-alpha.vercel.app submission/screenshots
```
