<!--
id: svg-shape-patterns
category: shape-patterns
read_when: SVG 基础形状、流程节点、指标卡或风险条写法不确定时
page_roles: content, summary
supports: svg_drawingml
outputs: copyable_svg_fragments
depends_on: drawingml-svg-authoring.md
max_use: 只复制需要的片段，颜色必须替换为当前视觉 token
-->

# SVG Shape Patterns

本文件只提供可复制的基础 SVG 片段。业务布局优先读 `layout-*` 文件，颜色必须替换为
当前 deck 的 `background`、`surface`、`title_text`、`body_text`、`accent`、`border`。
常用于“结论-证据-动作”页中的流程节点、指标卡、证据卡组和风险/动作条。

> **片段纪律：所有片段里的字体名与颜色值一律替换为当前 deck 的 token，内联的
> `Microsoft YaHei`、裸 hex（如 `#2563EB`）仅为示意，不得照抄进成稿。** 颜色替换为
> 上面六个 token；字体按 `contract-font-portability.md` 的白名单替换（默认无衬线
> `Microsoft YaHei, Arial`，衬线中文场景 `Noto Serif SC`）。早期片段（流程节点 / 指标卡 /
> 证据卡组 / 风险动作条）仍内联示意值，是历史写法；`{{token}}` 化的片段才是正确写法基准。

## 流程节点

```xml
<g id="step-1">
  <rect x="0" y="0" width="300" height="210" rx="18"
        fill="#FFFFFF" stroke="#D9E2EC"/>
  <circle cx="34" cy="34" r="18" fill="#2563EB"/>
  <text x="34" y="41" text-anchor="middle"
        fill="#FFFFFF" font-family="Microsoft YaHei, Arial" font-size="18"
        font-weight="700">1</text>
  <text x="68" y="42" fill="#0F172A" font-family="Microsoft YaHei, Arial"
        font-size="24" font-weight="700">识别问题</text>
  <text x="24" y="88" fill="#334155" font-family="Microsoft YaHei, Arial"
        font-size="17">锁定阻塞点、责任人和影响范围</text>
  <text x="24" y="126" fill="#475569" font-family="Microsoft YaHei, Arial"
        font-size="15">- 统一数据口径</text>
  <text x="24" y="154" fill="#475569" font-family="Microsoft YaHei, Arial"
        font-size="15">- 标记高风险事项</text>
</g>
```

## 指标卡

```xml
<g id="metric-1" transform="translate(100,300)">
  <rect width="330" height="190" rx="18" fill="#FFFFFF" stroke="#D9E2EC"/>
  <text x="24" y="40" fill="#64748B" font-family="Microsoft YaHei, Arial"
        font-size="15">年度收入</text>
  <text x="24" y="95" fill="#1A3A6B" font-family="Microsoft YaHei, Arial"
        font-size="44" font-weight="800">+20%</text>
  <text x="24" y="132" fill="#334155" font-family="Microsoft YaHei, Arial"
        font-size="17">结构优化带动高质量增长</text>
  <rect x="24" y="150" width="118" height="26" rx="13" fill="#EFF6FF"/>
  <text x="42" y="169" fill="#2563EB" font-family="Microsoft YaHei, Arial"
        font-size="13">同比口径</text>
</g>
```

## 巨数 + 增长徽标

巨数 `<text>` 紧邻一枚小 `<polygon>` 升/降三角 + 增幅百分比：升三角 `points="0,12 7,0 14,12"`、降三角 `points="0,0 7,12 14,0"`。三角与增幅用功能色——增长用 `{{contrast_accent}}`（青/绿）、下滑用 `{{risk_accent}}`（红/橙），巨数用 `{{title_text}}` 或 `{{accent}}`。本节起片段颜色用 `{{token}}` 占位，复制后替换为当前 deck 的对应 token 值。

```xml
<g id="metric-delta-1">
  <text x="0" y="54" fill="{{title_text}}" font-family="Microsoft YaHei, Arial"
        font-size="54" font-weight="800">128</text>
  <polygon points="150,22 157,10 164,22" fill="{{contrast_accent}}"/>
  <text x="170" y="24" fill="{{contrast_accent}}" font-family="Microsoft YaHei, Arial"
        font-size="18" font-weight="700">+12%</text>
  <text x="0" y="82" fill="{{body_text}}" font-family="Microsoft YaHei, Arial"
        font-size="15">同比口径</text>
</g>
```

## 环形单值进度 gauge（甜甜圈弧）

底环 `<circle>` 描边 + 前景进度弧 + 中心巨数 `<text>`。前景弧**优先两段 `path` 扇形闭合** freeform（转换后为可编辑原生形状），或用 `stroke-dasharray` 描边圆近似；弧长按占比算，`rotate(-90)` 从顶端起弧。提取自 `layout-diagonal-duo-panels.md` 的本地画法、升级为共享片段，环形单值需求统一复用此段。

```xml
<g id="gauge-1">
  <circle cx="70" cy="70" r="56" fill="none" stroke="{{border}}" stroke-width="14"/>
  <circle cx="70" cy="70" r="56" fill="none" stroke="{{accent}}" stroke-width="14"
          stroke-linecap="round" stroke-dasharray="264 352"
          transform="rotate(-90 70 70)"/>
  <text x="70" y="82" text-anchor="middle" fill="{{title_text}}"
        font-family="Microsoft YaHei, Arial" font-size="34" font-weight="800">75%</text>
</g>
```

## 折角 / 切角卡片 tab

切角卡：矩形四顶点按水平偏移错位成 `<polygon>`（上下边平行）。折角卡：卡体 `<polygon>` 右上角切掉——顶边到 `(right−f, top)`、斜切到 `(right, top+f)`，再经右下、左下、左上闭合，折出的小三角另叠一枚作折角阴影。KPI 联排的折边比例 `f=卡宽 12%-16%` 与联间距算法见 `layout-kpi-strip.md`。

```xml
<g id="dogear-card-1">
  <polygon points="0,0 176,0 200,24 200,120 0,120"
           fill="{{surface}}" stroke="{{border}}"/>
  <polygon points="176,0 200,24 176,24" fill="{{accent}}" fill-opacity="0.35"/>
  <text x="20" y="58" fill="{{title_text}}" font-family="Microsoft YaHei, Arial"
        font-size="40" font-weight="800">36%</text>
  <text x="20" y="94" fill="{{body_text}}" font-family="Microsoft YaHei, Arial"
        font-size="15">交付提效</text>
</g>
```

## 房形上升 chevron 题头

矩形上边中央顶出向上尖角 = home-plate 房形 `<polygon>`（左下→左上→顶尖→右上→右下闭合），或整条向上折的 chevron 带；标题反白居中，用作分栏期次表头或独立指标带题头。`layout-kpi-strip.md` 的"房形题头"回指此片段。

```xml
<g id="home-plate-header-1">
  <polygon points="0,40 0,14 130,2 260,14 260,40" fill="{{accent}}"/>
  <text x="130" y="30" text-anchor="middle" fill="{{surface}}"
        font-family="Microsoft YaHei, Arial" font-size="16" font-weight="700">第一阶段</text>
</g>
```

## 六边形徽标

正六边形 `<polygon>` 作序号 / 阶段 / 能力徽标。尖顶六边形按中心 `(cx,cy)` 与半径 r 定点：
顶点 `(cx, cy−r)`，其余五点每 60° 递增（水平偏移 `±0.866r`、垂直偏移 `±0.5r`）。徽标内嵌反白
序号或图标，下缀短标签；多枚并列作能力矩阵 / 阶段带时复制本片段改序号与标签，不逐枚重画。
内层再叠一枚缩小同心六边形描边可做双线质感。

```xml
<g id="hex-badge-1">
  <polygon points="60,8 105,34 105,86 60,112 15,86 15,34"
           fill="{{accent}}" stroke="{{border}}"/>
  <polygon points="60,20 94,40 94,80 60,100 26,80 26,40"
           fill="none" stroke="{{surface}}" stroke-opacity="0.35"/>
  <text x="60" y="72" text-anchor="middle" fill="{{surface}}"
        font-family="{{font_cn}}" font-size="34" font-weight="800">01</text>
  <text x="60" y="140" text-anchor="middle" fill="{{title_text}}"
        font-family="{{font_cn}}" font-size="16" font-weight="700">能力标签</text>
</g>
```

## 证据卡组

```xml
<g id="evidence-1" transform="translate(760,250)">
  <rect width="700" height="130" rx="16" fill="#FFFFFF" stroke="#D9E2EC"/>
  <rect x="0" y="0" width="8" height="130" rx="4" fill="#2563EB"/>
  <text x="34" y="42" fill="#0F172A" font-family="Microsoft YaHei, Arial"
        font-size="22" font-weight="700">证据一：标杆项目已验证</text>
  <text x="34" y="78" fill="#334155" font-family="Microsoft YaHei, Arial"
        font-size="17">A 项目在 6 周内完成上线，关键流程效率提升 18%。</text>
  <text x="34" y="108" fill="#64748B" font-family="Microsoft YaHei, Arial"
        font-size="14">来源：用户素材 / 项目周报</text>
</g>
```

## 风险/动作条

```xml
<g id="actions" transform="translate(90,785)">
  <rect width="1420" height="70" rx="18" fill="#EFF6FF" stroke="#BFDBFE"/>
  <text x="28" y="44" fill="#1A3A6B" font-family="Microsoft YaHei, Arial"
        font-size="21" font-weight="700">下一步：</text>
  <text x="122" y="44" fill="#334155" font-family="Microsoft YaHei, Arial"
        font-size="18">本周锁定责任人，月底完成问题闭环并形成复盘台账。</text>
</g>
```

## 连接箭头

```xml
<defs>
  <marker id="arrow-accent" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="8" markerHeight="8" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563EB"/>
  </marker>
</defs>
<line x1="430" y1="415" x2="540" y2="415" stroke="#2563EB"
      stroke-width="3" marker-end="url(#arrow-accent)"/>
```

## 带页签的分区框

用于一个大分区的“页签 + 薄边框”容器，例如指标体系、案例证据或落地举措区。页签宽度按标题
长度计算，通常占分区宽度 `22%-40%`；它只命名分区，不给每张小卡重复加页签。下面是局部
坐标片段，放入页面前按目标 region 等比缩放或重算，不能照抄为整页坐标。

```xml
<g id="section-tab-frame-1">
  <rect x="0" y="18" width="520" height="182" rx="8"
        fill="{{surface}}" stroke="{{border}}"/>
  <rect x="0" y="0" width="176" height="46" rx="8" fill="{{accent}}"/>
  <text x="20" y="31" fill="{{surface}}" font-family="{{font_cn}}"
        font-size="18" font-weight="700">指标体系</text>
</g>
```

失败检查：页签不得比主标题更大；标题超过 10-12 个汉字时缩短文案而不是继续拉宽；框内必须
有真实内容组，不能把空框当作层次感。

## 语义行栈

用于多个对象共享 `目标/动作/产出/风险`、`现象/根因/方案` 或
`事实/分析/影响` 等固定 schema。左列宽度跨对象稳定，右列弹性；语义 tone 只用于风险、行动
等含义，不逐行随机换色。

```xml
<g id="semantic-row-stack-1">
  <g id="semantic-row-1">
    <rect x="0" y="0" width="142" height="66" fill="{{surface}}" stroke="{{border}}"/>
    <rect x="0" y="0" width="8" height="66" fill="{{accent}}"/>
    <text x="24" y="40" fill="{{title_text}}" font-family="{{font_cn}}"
          font-size="17" font-weight="700">核心目标</text>
    <rect x="142" y="0" width="378" height="66" fill="{{surface}}" stroke="{{border}}"/>
    <text x="164" y="29" fill="{{body_text}}" font-family="{{font_cn}}" font-size="15">
      <tspan x="164" dy="0">统一标准与数据口径，建立可验收基线</tspan>
    </text>
  </g>
  <g id="semantic-row-2" transform="translate(0,66)">
    <rect x="0" y="0" width="142" height="66" fill="{{surface}}" stroke="{{border}}"/>
    <rect x="0" y="0" width="8" height="66" fill="{{contrast_accent}}"/>
    <text x="24" y="40" fill="{{title_text}}" font-family="{{font_cn}}"
          font-size="17" font-weight="700">重点动作</text>
    <rect x="142" y="0" width="378" height="66" fill="{{surface}}" stroke="{{border}}"/>
    <text x="164" y="29" fill="{{body_text}}" font-family="{{font_cn}}" font-size="15">
      <tspan x="164" dy="0">拆分责任、交付物和检查节点</tspan>
    </text>
  </g>
</g>
```

行数通常 `2-4`，单行正文不超过两行。对象之间 schema 不一致时不要强套行栈，改用非对称
分栏或证据表。

## 单指标变化卡

一个卡只表达一个主指标，顺序固定为“指标名 → baseline/result 或 delta → implication”。
百分比、百分点、金额和时长必须保留单位与口径；目标值必须标为目标，不能装成已完成结果。

```xml
<g id="metric-delta-card-1">
  <rect x="0" y="0" width="260" height="152" rx="8"
        fill="{{surface}}" stroke="{{border}}"/>
  <text x="20" y="34" fill="{{body_text}}" font-family="{{font_cn}}"
        font-size="15">平均交付周期</text>
  <text x="20" y="86" fill="{{source_text}}" font-family="{{font_cn}}"
        font-size="27" font-weight="700">12.5</text>
  <text x="83" y="86" fill="{{body_text}}" font-family="{{font_cn}}"
        font-size="18">个月</text>
  <text x="128" y="84" fill="{{accent}}" font-family="{{font_cn}}"
        font-size="24" font-weight="700">→</text>
  <text x="162" y="86" fill="{{accent}}" font-family="{{font_cn}}"
        font-size="32" font-weight="800">8.3</text>
  <text x="222" y="86" fill="{{body_text}}" font-family="{{font_cn}}"
        font-size="18">个月</text>
  <line x1="20" y1="104" x2="240" y2="104" stroke="{{border}}"/>
  <text x="20" y="132" fill="{{title_text}}" font-family="{{font_cn}}"
        font-size="15" font-weight="700">前置评审减少返工等待</text>
</g>
```

若需要 4 个以上时间点、趋势线、阈值或系列比较，改用 native chart slot，不在卡内手绘假图表。

## 洞察侧栏

洞察侧栏用于把相邻证据翻译成一句管理判断，不承担新证据。宽度通常占所属 group 的
`18%-28%`，正文最多两行；图标可选，若使用必须先检索图标并按最终页面绝对坐标写
`data-icon-box`，不能复制本地坐标猜路径。

```xml
<g id="insight-rail-1">
  <rect x="0" y="0" width="210" height="188" rx="8"
        fill="{{surface}}" stroke="{{border}}"/>
  <rect x="20" y="20" width="72" height="30" rx="15" fill="{{accent}}"/>
  <text x="56" y="41" text-anchor="middle" fill="{{surface}}"
        font-family="{{font_cn}}" font-size="14" font-weight="700">洞察</text>
  <text x="20" y="92" fill="{{title_text}}" font-family="{{font_cn}}"
        font-size="19" font-weight="700">
    <tspan x="20" dy="0">前置定义边界，</tspan>
    <tspan x="20" dy="29">比后期返工更有效</tspan>
  </text>
</g>
```

## 高对比结论带

用于把上方证据收成原则、行动或决策。它必须回指主体，不能凭空新增事实；通常放 1 个判断，
最多 3 个短槽。横条只是收口层，不能用来掩盖主体空洞。

```xml
<g id="conclusion-band-1">
  <rect x="0" y="0" width="760" height="78" rx="8" fill="{{accent}}"/>
  <text x="24" y="48" fill="{{surface}}" font-family="{{font_cn}}"
        font-size="18" font-weight="700">核心结论</text>
  <line x1="142" y1="18" x2="142" y2="60" stroke="{{surface}}" stroke-opacity="0.45"/>
  <text x="168" y="48" fill="{{surface}}" font-family="{{font_cn}}"
        font-size="18" font-weight="700">先统一架构与口径，再推进工具和流程</text>
</g>
```

## 卡片内部填充

卡片内部空白过大时，不要用大面积空卡片保留“干净感”。优先补：

- 1 个指标胶囊：周期、对象、口径、同比/环比。
- 1 条风险或动作标签：高风险、待决策、下周完成。
- 1 行来源或责任：来源、负责人、完成时间。
