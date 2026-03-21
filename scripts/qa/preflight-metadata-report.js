#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const repoRoot = path.resolve(__dirname, '../..');
const reportsDir = path.join(repoRoot, 'work', 'publish', 'reports');
const validator = path.join(repoRoot, 'scripts', 'metadata', 'validate-song-metadata.js');
const targetArg = process.argv[2] || 'upload/metadata';
const targetPath = path.resolve(repoRoot, targetArg);

fs.mkdirSync(reportsDir, { recursive: true });

const run = spawnSync(process.execPath, [validator, targetPath], {
  cwd: repoRoot,
  encoding: 'utf8'
});

const timestamp = new Date().toISOString();
const report = {
  type: 'metadata-preflight',
  timestamp,
  target: path.relative(repoRoot, targetPath),
  exitCode: run.status,
  status: run.status === 0 ? 'pass' : 'fail',
  stdout: run.stdout.trimEnd(),
  stderr: run.stderr.trimEnd()
};

const latestPath = path.join(reportsDir, 'metadata-preflight.latest.json');
const stampedPath = path.join(reportsDir, `metadata-preflight.${timestamp.replace(/[:]/g, '-')}.json`);

fs.writeFileSync(latestPath, JSON.stringify(report, null, 2) + '\n');
fs.writeFileSync(stampedPath, JSON.stringify(report, null, 2) + '\n');

console.log(`Report written: ${path.relative(repoRoot, latestPath)}`);
console.log(`Snapshot written: ${path.relative(repoRoot, stampedPath)}`);
if (report.stdout) console.log(report.stdout);
if (report.stderr) console.error(report.stderr);
process.exit(run.status ?? 1);
