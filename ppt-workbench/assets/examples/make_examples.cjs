'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {parseArgs} = require('node:util');
const {NativeDeck} = require('../../scripts/native.cjs');
const cases = require('./cases.json');

function buildExample(spec, options) {
  const d = new NativeDeck({...options,theme:spec.theme});
  const s = d.page({title:spec.title,subtitle:spec.subtitle,source:spec.source,
    notes:`Synthetic input. Review: ${spec.review}`});
  const body = {x:0.55,y:2.3,w:d.width-1.1,h:d.height-2.96};
  const chartBox = {...body,h:body.h-0.72};
  switch(spec.kind) {
    case 'kpi': {
      const f=spec.facts,growth=(f.revenue-f.prior)/f.prior*100,gap=f.collectionTarget-f.collectionRate;
      d.kpis(s,[{label:'本期收入',value:`${f.revenue}`,detail:'万元；合成数据'},
        {label:'收入同比',value:`${growth.toFixed(0)}%`,detail:`基期 ${f.prior} 万元`},
        {label:'回款率',value:`${f.collectionRate}%`,detail:`低于目标 ${gap} 个百分点`}],{...body,h:2.75});
      d.text(s,'待核实：回款缺口的账龄分布及成因。',{...body,y:5.65,h:0.8},{fontSize:21,bold:true});
      break;
    }
    case 'trend': {
      d.chart(s,[{name:'收入',labels:spec.labels,values:spec.values}],chartBox,{type:'line',unit:'万元'});
      const delta=spec.values.at(-1)-spec.values[0];
      d.text(s,`${spec.labels.at(-1)}较${spec.labels[0]}${delta>=0?'增加':'减少'}${Math.abs(delta)}万元；序列仅说明观察期内的变化。`,{...body,y:6.3,h:0.55},{fontSize:17});
      break;
    }
    case 'target': case 'style': {
      d.chart(s,[{name:'目标',labels:spec.labels,values:spec.target},{name:'实际',labels:spec.labels,values:spec.values}],chartBox,{unit:'万元'});
      const target=spec.target.reduce((a,b)=>a+b,0),actual=spec.values.reduce((a,b)=>a+b,0);
      const rate=target>0?`合计完成率${(actual/target*100).toFixed(1)}%`:'目标不为正，未计算完成率';
      d.text(s,`${rate}；区域差异需结合各区域口径继续分析。`,{...body,y:6.3,h:0.55},{fontSize:17});
      break;
    }
    case 'multi': {
      d.chart(s,[{name:'线上',labels:spec.labels,values:spec.values},{name:'门店',labels:spec.labels,values:spec.other}],chartBox,{type:'line',unit:'万元'});
      d.text(s,`门店减线上差额：期初${spec.other[0]-spec.values[0]}万元，期末${spec.other.at(-1)-spec.values.at(-1)}万元；尚无原因证据。`,{...body,y:6.3,h:0.55},{fontSize:17});
      break;
    }
    case 'table': case 'dense':
      d.table(s,spec.rows,body,{fontSize:spec.kind==='dense'?16:18});
      break;
    case 'process': case 'structure': d.flow(s,spec.items,body); break;
    case 'matrix': d.matrix(s,spec.items,body); break;
    case 'evidence':
      d.image(s,path.join(__dirname,'evidence-synthetic.png'),{...body,w:7.45},
        {source:spec.source,description:'Synthetic project register slide',width:1600,height:900});
      d.text(s,spec.body,{x:8.35,y:2.5,w:d.width-8.9,h:3.9},{fontSize:20});
      break;
    case 'cover':
      d.rect(s,{...body,w:0.16},{fill:d.theme.primary});
      d.text(s,spec.body,{x:1.1,y:2.65,w:d.width-2.2,h:3.4},{fontSize:24});
      break;
    default: throw new Error('Unknown example kind');
  }
  return d;
}

async function main() {
  const {values} = parseArgs({options:{'output-dir':{type:'string'},'font-path':{type:'string'},
    'font-name':{type:'string'},case:{type:'string'}}});
  if(!values['output-dir'] || !values['font-path']) throw new Error('Use --output-dir and --font-path, plus --font-name for a font collection');
  const selected=values.case?cases.filter(c=>c.id===values.case):cases;
  if(!selected.length) throw new Error('Unknown case');
  const out=path.resolve(values['output-dir']);
  fs.mkdirSync(out,{recursive:true});
  for(const spec of selected) {
    const deck=buildExample(spec,{fontPath:values['font-path'],fontName:values['font-name']});
    console.log(JSON.stringify(await deck.save(path.join(out,`${spec.id}.pptx`))));
  }
}

if(require.main===module) main().catch(e=>{console.error(e.message);process.exitCode=2;});
module.exports={buildExample,cases};
