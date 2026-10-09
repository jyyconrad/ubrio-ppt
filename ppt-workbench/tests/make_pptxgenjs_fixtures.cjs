#!/usr/bin/env node
"use strict";

const path = require("node:path");
const pptxgen = require("pptxgenjs");

const outDir = process.argv[2];
if (!outDir) throw new Error("output directory is required");

const pixel = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII=";

async function write(name, kind) {
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_WIDE";
  const slide = pptx.addSlide();
  slide.addText(name, { x: 0.6, y: 0.4, w: 5, h: 0.5, fontSize: 24 });
  slide.addNotes(`Synthetic PptxGenJS note: ${name}`);
  if (kind === "chart") {
    slide.addChart(pptx.ChartType.bar, [{ name: "Series", labels: ["A", "B"], values: [2, 3] }], {
      x: 0.8, y: 1.3, w: 5, h: 3,
    });
  } else if (kind === "table") {
    slide.addTable([["Item", "Value"], ["A", "1"]], { x: 0.8, y: 1.3, w: 5, h: 1.5 });
  } else if (kind === "process") {
    slide.addShape(pptx.ShapeType.rect, { x: 0.8, y: 1.5, w: 2, h: 1, fill: { color: "DDEEFF" } });
    slide.addShape(pptx.ShapeType.chevron, { x: 3.1, y: 1.5, w: 2, h: 1, fill: { color: "AACCEE" } });
  } else if (kind === "image") {
    slide.addImage({ data: pixel, x: 0.8, y: 1.3, w: 2, h: 2 });
  }
  await pptx.writeFile({ fileName: path.join(outDir, `${name}.pptx`) });
}

Promise.all([
  write("03-target", "chart"),
  write("05-table", "table"),
  write("06-process", "process"),
  write("09-evidence", "image"),
]).catch((error) => {
  console.error(error);
  process.exitCode = 2;
});
