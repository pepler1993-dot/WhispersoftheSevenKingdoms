#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '../..');
const uploadRoot = path.join(repoRoot, 'upload');
const songsDir = path.join(uploadRoot, 'songs');
const thumbsDir = path.join(uploadRoot, 'thumbnails');
const metadataDir = path.join(uploadRoot, 'metadata');
const reportsDir = path.join(repoRoot, 'work', 'publish', 'reports');

const SONG_EXT = new Set(['.mp3', '.wav', '.ogg']);
const THUMB_EXT = new Set(['.jpg', '.png', '.webp']);

function listFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter(name => !name.startsWith('.'))
    .map(name => ({ name, ext: path.extname(name).toLowerCase(), slug: path.basename(name, path.extname(name)) }));
}

function buildIndex(files, allowedExt) {
  const index = new Map();
  for (const file of files) {
    if (!allowedExt.has(file.ext)) continue;
    if (!index.has(file.slug)) index.set(file.slug, []);
    index.get(file.slug).push(file.name);
  }
  return index;
}

function main() {
  const songs = buildIndex(listFiles(songsDir), SONG_EXT);
  const thumbs = buildIndex(listFiles(thumbsDir), THUMB_EXT);
  const metadata = buildIndex(listFiles(metadataDir), new Set(['.json']));

  const slugs = new Set([...songs.keys(), ...thumbs.keys(), ...metadata.keys()]);
  const results = [];

  for (const slug of [...slugs].sort()) {
    const songFiles = songs.get(slug) || [];
    const thumbFiles = thumbs.get(slug) || [];
    const metadataFiles = metadata.get(slug) || [];

    const missing = [];
    if (songFiles.length === 0) missing.push('song');
    if (thumbFiles.length === 0) missing.push('thumbnail');
    if (metadataFiles.length === 0) missing.push('metadata');

    const warnings = [];
    if (songFiles.length > 1) warnings.push('multiple song files');
    if (thumbFiles.length > 1) warnings.push('multiple thumbnail files');
    if (metadataFiles.length > 1) warnings.push('multiple metadata files');

    results.push({
      slug,
      status: missing.length === 0 ? 'complete' : 'incomplete',
      missing,
      warnings,
      files: {
        songs: songFiles,
        thumbnails: thumbFiles,
        metadata: metadataFiles
      }
    });
  }

  const summary = {
    type: 'upload-completeness-check',
    timestamp: new Date().toISOString(),
    status: results.every(r => r.status === 'complete') ? 'pass' : 'fail',
    checkedSlugs: results.length,
    completeSlugs: results.filter(r => r.status === 'complete').length,
    incompleteSlugs: results.filter(r => r.status !== 'complete').length,
    results
  };

  fs.mkdirSync(reportsDir, { recursive: true });
  fs.writeFileSync(path.join(reportsDir, 'upload-completeness.latest.json'), JSON.stringify(summary, null, 2) + '\n');

  for (const result of results) {
    const label = result.status === 'complete' ? 'PASS' : 'FAIL';
    console.log(`${label} ${result.slug}`);
    if (result.missing.length) console.log(`  missing: ${result.missing.join(', ')}`);
    if (result.warnings.length) console.log(`  warnings: ${result.warnings.join(', ')}`);
  }

  console.log('---');
  console.log(`Checked slugs: ${summary.checkedSlugs}`);
  console.log(`Complete: ${summary.completeSlugs}`);
  console.log(`Incomplete: ${summary.incompleteSlugs}`);

  process.exit(summary.status === 'pass' ? 0 : 1);
}

main();
