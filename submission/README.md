# Sentinel Relay event submission archive

This directory keeps the current submission references and production screenshots.

## Current references

- Application: https://sentinel-relay-alpha.vercel.app
- Public repository: https://github.com/Caleb-Todd-commits/sentinel-relay
- Current screenshots: `screenshots/workspace.png`, `screenshots/approval.png`, `screenshots/result.png`, and `screenshots/custom-question.png`

## Historical artifacts

`cover.png` and `Sentinel-Relay-Demo.mp4` are historical artifacts. They may show the retired multi-page interface and should not be used as current product documentation. The repository no longer carries a PowerPoint or voiceover package; use the separately prepared presentation instead.

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
