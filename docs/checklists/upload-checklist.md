# Upload Checklist — Whispers of the Seven Kingdoms

Use this checklist before each YouTube upload to ensure quality and consistency.

---

## Preflight Check (Automated)

- [ ] All required files present:
  - [ ] `video.mp4` (YouTube-ready, correct resolution/bitrate)
  - [ ] `thumbnail.jpg` (1280x720 minimum, high quality)
  - [ ] `metadata.json` (valid, all required fields)
  - [ ] `description.txt` (generated from template)
  - [ ] `tags.txt` (line-separated, no duplicates)

- [ ] File integrity:
  - [ ] Video plays without errors
  - [ ] Thumbnail opens and is clear
  - [ ] No zero-byte files

- [ ] Metadata validation:
  - [ ] `slug` matches all filenames
  - [ ] `title` ≤ 100 characters
  - [ ] `description` ≤ 5000 characters
  - [ ] `tags` ≤ 500 characters total, ≤ 15 tags

---

## Manual Review

- [ ] Title is engaging and GoT-themed?
- [ ] Description matches tone (atmospheric, immersive)?
- [ ] Thumbnail is visually striking and legible at small size?
- [ ] Tags are relevant and not spammy?
- [ ] Video has no unintended watermark/logo (unless intentional)?
- [ ] Audio levels consistent (no clipping, good volume)?

---

## Upload Preparation

- [ ] YouTube channel selected
- [ ] Video visibility set correctly (Private → Public schedule)
- [ ] Category: Entertainment (or Music)
- [ ] Audience: Made for Kids? (likely NO)
- [ ] Age restriction appropriate (likely NO)
- [ ] Location tags? (optional)
- [ ] Scheduled publish time? (if applicable)

---

## Post-Upload

- [ ] Upload succeeded (no errors)
- [ ] Video URL recorded in `upload/log.csv`
- [ ] Source files moved to `upload/done/<slug>/`
- [ ] Log entry created in `upload/upload.log`
- [ ] Notification sent (if auto-notify enabled)

---

## Troubleshooting

| Issue                        | Likely Cause               | Fix                                  |
|------------------------------|----------------------------|--------------------------------------|
| "Upload failed: format"      | Video codec/profile wrong  | Re-encode with YouTube recommended   |
| "Thumbnail blurry"           | Resolution too low         | Use 1280x720 or higher               |
| "Description too long"       | Exceeds 5000 chars         | Trim or summarize                    |
| "Tags too many"              | > 500 characters total     | Remove less relevant tags            |
| "File not found"             | Wrong slug/typom           | Check filenames vs metadata          |

---

*Keep this checklist updated as the pipeline evolves.*
