'use strict';

const fs = require('node:fs');
const path = require('node:path');
const PptxGenJS = require('pptxgenjs');
const fontkit = require('fontkit');

const DEFAULT_THEME = Object.freeze({
  ink: '202728', muted: '556165', primary: '007F78', accent: 'C5485A',
  secondary: '4477AA', surface: 'F1F5F4', line: 'D5DFDC', paper: 'FFFFFF',
});

function check(condition, message) {
  if (!condition) throw new Error(message);
}

class NativeDeck {
  constructor({fontPath, fontName, width = 13.333333, height = 7.5, theme = {}}) {
    check(fontPath && fs.statSync(fontPath).isFile(), 'An installed, readable fontPath is required');
    let font = fontkit.openSync(fontPath);
    if (font.fonts) {
      check(fontName, 'Font collections require an explicit family or PostScript fontName');
      font = font.fonts.find(f => f.postscriptName === fontName || f.familyName === fontName);
    }
    check(font && (!fontName || [font.familyName, font.postscriptName].includes(fontName)),
      'Requested fontName does not match the measured font');
    this.font = font;
    this.fontName = font.familyName;
    check(Number.isFinite(width) && Number.isFinite(height) && width >= 7 && height >= 5,
      'Invalid slide dimensions');
    this.width = width;
    this.height = height;
    this.theme = {...DEFAULT_THEME, ...theme};
    for (const color of Object.values(this.theme)) check(/^[0-9A-F]{6}$/i.test(color), 'Use six-digit HEX colors');
    this.pptx = new PptxGenJS();
    this.pptx.defineLayout({name: 'CUSTOM', width, height});
    this.pptx.layout = 'CUSTOM';
    this.pptx.author = 'ppt-generate';
    this.pptx.subject = 'Native editable PowerPoint';
    this.pptx.lang = 'zh-CN';
    this.pptx.theme = {headFontFace: this.fontName, bodyFontFace: this.fontName, lang: 'zh-CN'};
    this.pages = [];
    this.measureCache = new Map();
  }

  measure(text, size) {
    const key = `${size}:${text}`;
    if (!this.measureCache.has(key)) {
      for (const char of text) {
        check(this.font.hasGlyphForCodePoint(char.codePointAt(0)), `Missing font glyph U+${char.codePointAt(0).toString(16)}`);
      }
      const run = this.font.layout(text);
      this.measureCache.set(key, run.positions.reduce((s, p) => s + p.xAdvance, 0) * size / this.font.unitsPerEm);
    }
    return this.measureCache.get(key);
  }

  wrap(text, width, size, bold = false) {
    check(typeof text === 'string' && text.length <= 20000, 'Text must be a bounded string');
    const max = width * 72 / (bold ? 1.08 : 1.04);
    const lines = [];
    // Shape real glyph runs; retain Chinese punctuation with its preceding clause.
    for (const paragraph of text.split('\n')) {
      let line = '';
      const tokens = paragraph.match(/[A-Za-z0-9][A-Za-z0-9.,%+_/@:-]*|\s+|./gu) || [''];
      for (const token of tokens) {
        if (this.measure(line + token, size) <= max) { line += token; continue; }
        check(this.measure(token, size) <= max, `Unbreakable token exceeds text width: ${token.slice(0, 30)}`);
        if (/^[，。；：！？、）】》]/u.test(token) && line.length > 1) {
          const chars = Array.from(line);
          const tail = chars.pop();
          lines.push(chars.join('').trimEnd());
          line = tail + token;
        } else {
          if (line.trim()) lines.push(line.trimEnd());
          line = token.trimStart();
        }
      }
      lines.push(line.trimEnd());
    }
    return lines;
  }

  bounds(box) {
    const {x, y, w, h} = box;
    check([x,y,w,h].every(Number.isFinite) && x >= 0 && y >= 0 && w > 0 && h > 0 &&
      x + w <= this.width + 0.001 && y + h <= this.height + 0.001, 'Object is outside slide bounds');
  }

  text(slide, value, box, options = {}) {
    this.bounds(box);
    const {fontSize = 18, bold = false, color = this.theme.ink, align = 'left'} = options;
    check(fontSize >= 10, 'Do not shrink below 10pt; restructure the content');
    const lines = this.wrap(String(value), box.w, fontSize, bold);
    const linePt = fontSize * 1.28;
    check(lines.length * linePt <= box.h * 72, `Text capacity exceeded (${lines.length} lines, ${fontSize}pt)`);
    slide.addText(lines.join('\n'), {...box, fontFace: this.fontName, fontSize, bold, color, align,
      margin: 0, breakLine: false, lineSpacingMultiple: 1.15, paraSpaceAfterPt: 0,
      valign: 'top', lang: 'zh-CN', charSpacing: 0, isTextBox: true});
  }

  rect(slide, box, {fill = this.theme.surface, line = fill} = {}) {
    this.bounds(box);
    slide.addShape(this.pptx.ShapeType.rect, {...box, fill: {color: fill}, line: {color: line, width: 0.5}});
  }

  page({title, subtitle = '', source = '', notes = ''}) {
    const slide = this.pptx.addSlide();
    slide.background = {color: this.theme.paper};
    this.text(slide, title, {x:0.55,y:0.38,w:this.width-1.1,h:1.08}, {fontSize:28,bold:true});
    if (subtitle) this.text(slide, subtitle, {x:0.55,y:1.54,w:this.width-1.1,h:0.6}, {fontSize:15,color:this.theme.muted});
    if (source) this.text(slide, source, {x:0.55,y:this.height-0.42,w:this.width-1.4,h:0.24}, {fontSize:10,color:this.theme.muted});
    this.text(slide, String(this.pages.length+1), {x:this.width-0.65,y:this.height-0.42,w:0.25,h:0.24}, {fontSize:10,color:this.theme.muted});
    if (notes) slide.addNotes(notes);
    this.pages.push(slide);
    return slide;
  }

  kpis(slide, items, box) {
    check(items.length >= 1 && items.length <= 4, 'KPI component accepts 1-4 items');
    this.bounds(box);
    const gap = 0.28, w = (box.w - gap * (items.length-1)) / items.length;
    items.forEach((item, i) => {
      const x = box.x + i*(w+gap);
      this.rect(slide, {x,y:box.y,w,h:box.h});
      this.text(slide, item.label, {x:x+0.18,y:box.y+0.16,w:w-0.36,h:0.52}, {fontSize:15,color:this.theme.muted});
      this.text(slide, String(item.value), {x:x+0.18,y:box.y+0.76,w:w-0.36,h:0.75}, {fontSize:32,bold:true,color:this.theme.primary});
      if (item.detail) this.text(slide, item.detail, {x:x+0.18,y:box.y+1.64,w:w-0.36,h:box.h-1.8}, {fontSize:15});
    });
  }

  chart(slide, series, box, {type = 'bar', numberFormat = '0', showValue = false, unit = ''} = {}) {
    this.bounds(box);
    check(['bar','line'].includes(type), 'Component validates only 2D bar and line charts');
    check(series.length >= 1 && series.length <= 4, 'Chart accepts 1-4 series');
    const labels = series[0].labels;
    check(labels.length >= 1 && labels.length <= 12, 'Chart accepts 1-12 categories');
    for (const s of series) {
      check(typeof s.name === 'string' && s.name.trim(), 'A series name is required');
      check(JSON.stringify(s.labels) === JSON.stringify(labels) && s.values.length === labels.length,
        'Every series must retain the same categories and numeric length');
      check(s.values.every(v => typeof v === 'number' && Number.isFinite(v)),
        'Chart values must be finite numbers; missing values are not zero');
      this.measure(s.name, 12);
    }
    labels.forEach(label => {
      check(typeof label === 'string' && label.trim(), 'Category labels must be nonempty text');
      check(this.measure(label, 12) <= (box.w - 0.9) * 72 / labels.length,
        'Chart category labels exceed available width; reduce categories or use a table');
    });
    const values = series.flatMap(s=>s.values);
    const min = Math.min(0, ...values), max = Math.max(0, ...values);
    slide.addChart(this.pptx.ChartType[type], structuredClone(series), {...box,
      catAxisLabelFontFace:this.fontName,valAxisLabelFontFace:this.fontName,legendFontFace:this.fontName,
      catAxisLabelFontSize:12,valAxisLabelFontSize:11,legendFontSize:12,
      chartColors:[this.theme.primary,this.theme.accent,this.theme.secondary,'8F7834'],
      showLegend:series.length>1,legendPos:'b',showValue,showCatName:false,
      showTitle:false,showBorder:false,
      showMarker:type==='line',markerSize:5,lineSize:2.5,
      catAxisLabelColor:this.theme.ink,valAxisLabelColor:this.theme.muted,
      valAxisMinVal:min<0?min*1.15:0,valAxisMaxVal:max>0?max*1.15:(min<0?0:1),
      valAxisLabelFormatCode:numberFormat,dataLabelFormatCode:numberFormat,
      showValAxisTitle:Boolean(unit),valAxisTitle:unit,valAxisTitleFontSize:11,
      valAxisTitleFontFace:this.fontName,catAxisLineShow:false,
      valGridLine:{color:this.theme.line,width:0.5},
      catAxisMajorTickMark:'none',valAxisMajorTickMark:'none',showShadow:false,
      gapSizePct:65,showPercent:false,
      chartArea:{fill:{color:this.theme.paper}},plotArea:{fill:{color:this.theme.paper}},
    });
  }

  table(slide, rows, box, {fontSize = 16, colWidths} = {}) {
    this.bounds(box);
    check(rows.length >= 2 && rows.length <= 10 && rows[0].length <= 6, 'Table capacity: 2-10 rows, 1-6 columns');
    const cols = rows[0].length;
    check(cols > 0 && rows.every(r=>r.length===cols), 'Table rows must have equal column count');
    const widths = colWidths || Array(cols).fill(box.w/cols);
    check(widths.length===cols && widths.every(w=>w>0) && Math.abs(widths.reduce((a,b)=>a+b,0)-box.w)<0.01,
      'Column widths must add up to the table width');
    const heights = rows.map((r,i)=>Math.max(...r.map((v,j)=>this.wrap(String(v), widths[j]-0.18,fontSize,i===0).length))*fontSize*1.35/72+0.18);
    check(heights.reduce((a,b)=>a+b,0)<=box.h, 'Table capacity exceeded; reduce or regroup rows');
    const data = rows.map((r,i)=>r.map(v=>({text:String(v),options:{bold:i===0,
      color:i===0?this.theme.paper:this.theme.ink,fill:i===0?this.theme.primary:(i%2?this.theme.surface:this.theme.paper)}})));
    slide.addTable(data, {...box,colW:widths,rowH:heights,fontFace:this.fontName,fontSize,
      autoPage:false,margin:6,border:{type:'solid',pt:0.5,color:this.theme.line},
      valign:'mid',paraSpaceAfterPt:0});
  }

  flow(slide, items, box) {
    this.bounds(box);
    check(items.length>=2 && items.length<=5, 'Flow accepts 2-5 stages');
    const gap=0.38, w=(box.w-gap*(items.length-1))/items.length;
    items.forEach((item,i)=>{
      const x=box.x+i*(w+gap);
      this.rect(slide,{x,y:box.y,w,h:box.h});
      this.text(slide,String(i+1).padStart(2,'0'),{x:x+0.16,y:box.y+0.2,w:w-0.32,h:0.7},{fontSize:26,bold:true,color:this.theme.primary});
      this.text(slide,item.title,{x:x+0.16,y:box.y+1.02,w:w-0.32,h:0.82},{fontSize:20,bold:true});
      this.text(slide,item.body,{x:x+0.16,y:box.y+2,w:w-0.32,h:box.h-2.15},{fontSize:16});
      if(i<items.length-1) slide.addShape(this.pptx.ShapeType.chevron,{x:x+w+0.06,y:box.y+box.h/2-0.16,w:gap-0.12,h:0.32,
        fill:{color:this.theme.primary},line:{color:this.theme.primary}});
    });
  }

  matrix(slide, items, box) {
    this.bounds(box);
    check(items.length===4, 'Matrix requires four explicit quadrants');
    const gap=0.28,w=(box.w-gap)/2,h=(box.h-gap)/2;
    items.forEach((item,i)=>{
      const x=box.x+(i%2)*(w+gap),y=box.y+Math.floor(i/2)*(h+gap);
      this.rect(slide,{x,y,w,h});
      this.text(slide,item.title,{x:x+0.18,y:y+0.18,w:w-0.36,h:0.65},{fontSize:20,bold:true,color:i%2?this.theme.accent:this.theme.primary});
      this.text(slide,item.body,{x:x+0.18,y:y+0.96,w:w-0.36,h:h-1.13},{fontSize:16});
    });
  }

  image(slide, localPath, box, {source, description, width, height}) {
    this.bounds(box);
    check(source && description, 'Images require a source and description');
    check(!/^https?:/i.test(localPath) && fs.statSync(localPath).isFile(), 'Use a prepared local image');
    check(/\.(png|jpe?g)$/i.test(localPath), 'Native component accepts raster PNG/JPEG only');
    check(Number.isFinite(width) && Number.isFinite(height) && width>0 && height>0,'Provide actual image pixel dimensions');
    const scale=Math.min(box.w/width,box.h/height),w=width*scale,h=height*scale;
    slide.addImage({path:localPath,x:box.x+(box.w-w)/2,y:box.y+(box.h-h)/2,w,h,altText:`${description}; source: ${source}`});
  }

  async save(output, {overwrite = false} = {}) {
    check(this.pages.length>0, 'Cannot save an empty deck');
    check(path.extname(output).toLowerCase()==='.pptx', 'Output must have .pptx extension');
    const bytes=await this.pptx.write({outputType:'nodebuffer'});
    // Exclusive publication keeps accidental reruns from replacing user files.
    const fd=fs.openSync(output,overwrite?'w':'wx');
    try { fs.writeFileSync(fd,bytes); } finally { fs.closeSync(fd); }
    return {path:path.resolve(output),pages:this.pages.length,font:this.fontName};
  }
}

module.exports = {NativeDeck, DEFAULT_THEME};
