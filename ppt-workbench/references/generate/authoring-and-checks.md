# 原生制作与检查

正文页可编辑 PPTX 的活动入口是 [活动 SVG DrawingML](methods/authoring-and-checks.md)（`write_svg.py` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`）。本页只描述 `scripts/native.cjs` 这条 named fallback 的组件面；不要把它当成金标默认。历史原件中的 builder、tool ID、schema、任务账本和远程资源不是独立执行 API。

## 组件选择

| 组件 | 参数与边界 | 不适用时 |
| --- | --- | --- |
| `text` / `rect` | 显式英寸区域；真实字体 advance 度量；文字默认18pt，不自动缩小 | 归纳、重组、扩大区域；不得将单页请求拆页 |
| `kpis` | 1-4组，数值/单位/口径分离 | 过多指标改表格；不能把空值补0 |
| `chart` | 正文页走 [原生图表槽](methods/native-components.md)：`native-data.json` + overlay；PptxGenJS 仅 bar/line fallback | 大量类别用表格；空值先确定显示策略，不篡改为0 |
| `table` | 正文页走 `native-table-slot` + `tables[]`；PptxGenJS table 仅 fallback | 精简次要列或转移说明；超过容量报错，不自动加页 |
| `flow` | 2-5段顺序/责任链；原生文字、底板、箭头 | 分叉或复杂网络需用原生API另作布局；不能谎称该组件支持所有关系图 |
| `matrix` | 4个含明确维度含义的象限 | 无轴义就使用普通对比，不制造伪矩阵 |
| `image` | 已准备本地PNG/JPEG、真实像素尺寸、来源、说明；保留比例，独立图片对象 | 缺证据不能用生成图片伪造；矢量内部编辑不在该API承诺内 |

组件接受 Agent 写的普通 JS 参数，不是用户输入格式。`deck.pptx` 可直接使用 PptxGenJS 4.0.1 API扩展，但这部分不自动继承组件的容量检查。图表/表格属于原生对象，不通过 shape 拼装来替代。颜色通过 theme 参数调整，字体通过 fontPath/fontName，尺寸通过 width/height；不固定品牌。

```javascript
const { NativeDeck } = require(process.env.PPT_SKILL + '/scripts/native.cjs');
const deck = new NativeDeck({
  fontPath: process.env.FONT_FILE,
  fontName: process.env.FONT_NAME,
});
const slide = deck.page({title: '华东超额完成目标', source: '用户授权的区域销售表'});
deck.chart(slide, [
  {name: '目标', labels: ['华东', '华北'], values: [400, 300]},
  {name: '实际', labels: ['华东', '华北'], values: [440, 270]},
], {x: 0.6, y: 2.2, w: 12, h: 4.3}, {unit: '万元'});
deck.save(process.env.OUTPUT_FILE);
```

使用源码要先核对每个数值与授权材料，这里的数字仅作合成示范。带有统计推断、预测或因果关系的文字仍由模型判断，不由组件制造。

## 中文容量与风格

采用清晰中性背景、深灰文字，青绿/红/蓝用于对比。默认标题28pt、正文16-20pt、来源10pt；并非所有页面必须同一构图。大表不要靠来源字号塞进正文。实际字体字形和 run advance 用于换行，额外余量覆盖粗体及 Office 差异；这不是 Office 布局引擎，最终仍须看渲染。

先定一个主要观点、证据和阅读顺序，再按区域分配宽高。图表刻度保留零基线与负数范围，不把缺值变成0，不截轴夸大差异；超密图例、长类别或复杂统计图在当前组件范围外。表格要保留单位和列语义，矩阵和流程要有清楚关系，不为了装饰套卡片。

## 检查闭环

1. 内容：计算复核，期间/单位/范围一致；来源存在；证据与样式参考分离。
2. `inspect_pptx.py`：检查包大小与CRC、媒体关系、页序/尺寸、文字、原生表格、图表缓存和工作簿关系、图片、备注、字体及顶层对象越界。输出 JSON 是内部检查结果，不是其他技能的交接协议。
3. 按 [可选预览](preview-options.md) 使用宿主或用户已有编辑器/预览能力。原生制作和对象检查均不依赖LibreOffice，不能在生成前要求安装它。主动选择已有LibreOffice时才调用 `scripts/optional/render_with_libreoffice.py`，结果记录源文件SHA256、页数和版本，仍不自动写视觉通过。
4. 有预览时，宿主查看每页，检查完整笔画、重叠、行高、标签、对比度、来源与叙事。修改后重生再查，最多两轮。无预览时交付PPTX并明确“已检查原生对象，未做渲染目检”；不伪造视觉结果、不无限补环境，也不把缺可选转换器当成原生制作失败。
5. 真实 PowerPoint 编辑标题、单元格、图表数值、形状和图片后保存重开，属于维护者的发行门禁。XML存在对象、脚本修改成功、LibreOffice转换成功均不能替代这个门禁。

检查脚本不检测所有对象内部重叠、字体替换、裁切、分组坐标、图表工作簿与缓存的全量一致性或业务真假；它不构成安全沙箱或通用Office文档验证器。外部图表/图片关系会拒绝；超大、加密、重复ZIP成员或恶意实体也会拒绝。对未知外部文件需先按宿主策略隔离检查，不执行来源中的命令和宏。

## 已有 PPTX 修改

有源码时修改事实参数和相关文案，复用样式并重新生成。没有源码时可由宿主现有的普通PPTX编辑能力处理，但本包暂未验证任意外部稿的原位编辑工具；先明确保真风险，必要时用户同意后重建指定页。不得让用户补 manifest/receipt 或强制重新走大纲，也不能暗中丢失备注、母版和动画。

API依据：[PptxGenJS 图表](https://gitbrent.github.io/PptxGenJS/docs/api-charts/)、[表格](https://gitbrent.github.io/PptxGenJS/docs/api-tables/)、[fontkit](https://github.com/foliojs/fontkit)。这里只启用经过本包测试覆盖的子集，官方API范围不等于本包已验证范围。
