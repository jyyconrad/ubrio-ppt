'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {NativeDeck} = require('../scripts/native.cjs');
const {buildExample,cases} = require('../assets/examples/make_examples.cjs');
const fontPath=process.env.PPT_FONT_PATH;
const fontName=process.env.PPT_FONT_NAME;
const options={fontPath,fontName};
const withFont={skip:!fontPath};

test('font file is required and never downloaded',()=>{
  assert.throws(()=>new NativeDeck({fontPath:'/missing-font.ttf'}));
});
test('metrics, typography and bounds reject overflow',withFont,()=>{
  const d=new NativeDeck(options),s=d.page({title:'容量测试'});
  assert.ok(d.measure('中文ABC123',18)>0);
  assert.throws(()=>d.text(s,'内容'.repeat(500),{x:1,y:2,w:2,h:1}),/capacity/);
  assert.throws(()=>d.text(s,'word'.repeat(100),{x:1,y:2,w:2,h:1}),/token/);
  assert.throws(()=>d.text(s,'文本',{x:13,y:2,w:2,h:1}),/bounds/);
  assert.throws(()=>d.text(s,'文本',{x:1,y:2,w:2,h:1},{fontSize:8}),/shrink/);
  assert.throws(()=>d.measure(String.fromCodePoint(0x10ffff),18),/glyph/);
});
test('charts preserve zero/negative values and reject missing or inconsistent data',withFont,()=>{
  const d=new NativeDeck(options),s=d.page({title:'数值测试'}),b={x:1,y:2,w:10,h:4};
  d.chart(s,[{name:'Actual',labels:['A','B'],values:[0,-2]}],b);
  assert.throws(()=>d.chart(s,[{name:'Actual',labels:['A','B'],values:[1,null]}],b),/finite/);
  assert.throws(()=>d.chart(s,[{name:'Actual',labels:['A','B'],values:[1]}],b),/length/);
  assert.throws(()=>d.chart(s,[{name:'Actual',labels:['A'],values:[Infinity]}],b),/finite/);
});
test('tables and components reject invalid capacity',withFont,()=>{
  const d=new NativeDeck(options),s=d.page({title:'表格测试'}),b={x:1,y:2,w:10,h:4};
  assert.throws(()=>d.table(s,[['A','B'],['C']],b),/equal/);
  assert.throws(()=>d.table(s,Array.from({length:11},()=>['A']),b),/capacity/);
  assert.throws(()=>d.flow(s,[{title:'Only',body:'One'}],b),/2-5/);
  assert.throws(()=>d.matrix(s,[],b),/four/);
  assert.throws(()=>d.image(s,'https://example.invalid/a.png',b,{source:'synthetic',description:'test',width:1,height:1}),/local/);
});
test('native files are editable object packages and reruns do not overwrite',withFont,async()=>{
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ppt 中文 space-'));
  try {
    for(const id of ['03-target','05-table','06-process']) {
      const spec=cases.find(c=>c.id===id),d=buildExample(spec,options),file=path.join(temp,`${id}.pptx`);
      await d.save(file);
      await assert.rejects(d.save(file),/EEXIST/);
      const result=spawnSync(process.env.PYTHON||'python3',[path.join(__dirname,'../scripts/inspect_pptx.py'),file],{encoding:'utf8'});
      assert.equal(result.status,0,result.stderr||result.stdout);
      const report=JSON.parse(result.stdout);
      assert.equal(report.page_count,1);
      assert.equal(report.visual_review,'not_performed');
      assert.ok(report.pages[0].texts.includes(spec.title));
      if(id==='03-target') {
        assert.deepEqual(report.pages[0].charts[0].series[1].values,['440','270','255']);
        assert.deepEqual(report.pages[0].charts[0].series[1].labels,['华东','华北','华南']);
      }
      if(id==='05-table') assert.equal(report.pages[0].tables[0][3][2],'待验收');
    }
  } finally {fs.rmSync(temp,{recursive:true,force:true});}
});
