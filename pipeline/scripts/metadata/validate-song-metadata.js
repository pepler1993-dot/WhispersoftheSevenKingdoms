#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '../..');
const schemaPath = path.join(repoRoot, 'schemas', 'song.schema.json');
const defaultTargetDir = path.join(repoRoot, 'upload', 'metadata');

const args = process.argv.slice(2);
const targetArg = args[0] ? path.resolve(process.cwd(), args[0]) : defaultTargetDir;

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function validateSong(data, schema) {
  const errors = [];
  const allowedTopLevel = new Set(Object.keys(schema.properties || {}));

  for (const field of schema.required || []) {
    if (!(field in data)) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  for (const key of Object.keys(data)) {
    if (!allowedTopLevel.has(key)) {
      errors.push(`Unexpected top-level field: ${key}`);
    }
  }

  if ('slug' in data && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(data.slug)) {
    errors.push('Field slug must match ^[a-z0-9]+(?:-[a-z0-9]+)*$');
  }

  if ('title' in data && (typeof data.title !== 'string' || data.title.trim().length === 0)) {
    errors.push('Field title must be a non-empty string');
  }

  if ('platform' in data) {
    const allowedPlatforms = ['youtube', 'spotify', 'soundcloud'];
    if (typeof data.platform !== 'string' || !allowedPlatforms.includes(data.platform)) {
      errors.push(`Field platform must be one of: ${allowedPlatforms.join(', ')}`);
    }
  }

  if ('theme' in data && (typeof data.theme !== 'string' || data.theme.trim().length === 0)) {
    errors.push('Field theme must be a non-empty string');
  }

  if ('mood' in data) {
    if (!Array.isArray(data.mood) || data.mood.length === 0) {
      errors.push('Field mood must be a non-empty array');
    } else {
      data.mood.forEach((item, index) => {
        if (typeof item !== 'string' || item.trim().length === 0) {
          errors.push(`Field mood[${index}] must be a non-empty string`);
        }
      });
    }
  }

  for (const field of ['notes', 'duration_hint']) {
    if (field in data && typeof data[field] !== 'string') {
      errors.push(`Field ${field} must be a string`);
    }
  }

  validateBriefObject(data.music_brief, 'music_brief', errors);
  validateBriefObject(data.thumbnail_brief, 'thumbnail_brief', errors);

  return errors;
}

function validateBriefObject(value, fieldName, errors) {
  if (value === undefined) return;
  if (!isObject(value)) {
    errors.push(`Field ${fieldName} must be an object`);
    return;
  }

  const allowed = fieldName === 'music_brief'
    ? ['style', 'influences', 'tempo', 'energy', 'avoid']
    : ['scene', 'elements', 'text', 'style', 'avoid'];

  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) {
      errors.push(`Unexpected field ${fieldName}.${key}`);
    }
  }

  for (const key of Object.keys(value)) {
    const val = value[key];
    if (['influences', 'avoid', 'elements'].includes(key)) {
      if (!Array.isArray(val)) {
        errors.push(`Field ${fieldName}.${key} must be an array`);
      } else {
        val.forEach((item, index) => {
          if (typeof item !== 'string' || item.trim().length === 0) {
            errors.push(`Field ${fieldName}.${key}[${index}] must be a non-empty string`);
          }
        });
      }
    } else if (typeof val !== 'string') {
      errors.push(`Field ${fieldName}.${key} must be a string`);
    }
  }
}

function listJsonFiles(targetPath) {
  const stat = fs.statSync(targetPath);
  if (stat.isFile()) return [targetPath];
  return fs.readdirSync(targetPath)
    .filter(name => name.endsWith('.json'))
    .map(name => path.join(targetPath, name))
    .sort();
}

function main() {
  const schema = loadJson(schemaPath);
  const files = listJsonFiles(targetArg);
  if (files.length === 0) {
    console.log('No JSON metadata files found.');
    process.exit(1);
  }

  let failed = 0;
  for (const file of files) {
    try {
      const data = loadJson(file);
      const errors = validateSong(data, schema);
      const rel = path.relative(repoRoot, file);
      if (errors.length === 0) {
        console.log(`PASS ${rel}`);
      } else {
        failed += 1;
        console.log(`FAIL ${rel}`);
        for (const error of errors) {
          console.log(`  - ${error}`);
        }
      }
    } catch (error) {
      failed += 1;
      const rel = path.relative(repoRoot, file);
      console.log(`FAIL ${rel}`);
      console.log(`  - Invalid JSON or unreadable file: ${error.message}`);
    }
  }

  console.log('---');
  console.log(`Checked files: ${files.length}`);
  console.log(`Failures: ${failed}`);
  process.exit(failed > 0 ? 1 : 0);
}

main();
