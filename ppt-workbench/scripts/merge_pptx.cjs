#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { Automizer } = require("pptx-automizer");

async function main() {
  const jobPath = process.argv[2];
  if (!jobPath) throw new Error("job JSON path is required");
  const job = JSON.parse(fs.readFileSync(jobPath, "utf8"));
  if (!Array.isArray(job.pages) || job.pages.length === 0) {
    throw new Error("job contains no pages");
  }

  const rootPath = job.root || job.pages[0].path;
  const templateDir = path.dirname(rootPath);
  const outputDir = path.dirname(job.output);
  const automizer = new Automizer({
    templateDir,
    outputDir,
    removeExistingSlides: true,
    autoImportSlideMasters: true,
    // Automizer cleanup can remove root slide/chart parts while leaving their
    // relationship sidecars. Keep the root package internally complete; the
    // Python wrapper performs bounded broken-notes cleanup and full rel checks.
    cleanup: false,
    continueOnError: false,
    verbosity: 0,
  });

  let presentation = automizer.loadRoot(path.basename(rootPath));
  const labels = new Map();
  for (const page of job.pages) {
    if (!labels.has(page.path)) {
      const label = `source-${labels.size}`;
      labels.set(page.path, label);
      presentation = presentation.load(page.path, label);
    }
  }
  for (const page of job.pages) {
    presentation.addSlide(labels.get(page.path), page.source_page);
  }
  const summary = await presentation.write(path.basename(job.output));
  process.stdout.write(JSON.stringify({ ok: true, summary }));
}

main().catch((error) => {
  process.stderr.write(`${error && error.stack ? error.stack : error}\n`);
  process.exitCode = 2;
});
