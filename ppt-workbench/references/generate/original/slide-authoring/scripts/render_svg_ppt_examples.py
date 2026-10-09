"""生成并渲染 slide-authoring 的多页 SVG-PPT 示例套件。

核心流程：用内置 deck 蓝图生成 7 套中国式业务场景 SVG 页，再调用 vendored
DrawingML 转换边界，把每个场景合成为一套可编辑 PPTX，并写出 manifest。
边界：此脚本只维护 skill 示例资产，不参与 Runtime，不读取会话 workspace。
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import html
import json
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
SKILL_ROOT = SCRIPT_PATH.parents[1]
BACKEND_ROOT = SCRIPT_PATH.parents[5]
EXAMPLES_DIR = SKILL_ROOT / "assets" / "examples" / "svg-ppt"
DECKS_DIR = EXAMPLES_DIR / "decks"
BENCHMARKS_DIR = EXAMPLES_DIR / "benchmarks"
PPTX_DIR = EXAMPLES_DIR / "pptx"
MANIFEST_PATH = EXAMPLES_DIR / "examples-manifest.json"
FONT = "Microsoft YaHei, Arial"
# 蓝图设计画布是 1600x900，输出前由 _scale_svg_to_ppt169 统一缩放到 1280x720；
# 改动此常量会破坏「重跑脚本可逐字节复现 decks/*.svg」的再生产契约。
W, H = 1600, 900
PPT_W, PPT_H = 1280, 720
SVG_NS = "http://www.w3.org/2000/svg"
SCALE_X = PPT_W / W
SCALE_Y = PPT_H / H
PROJECT_GOLD_PAGE_IDS = {"04-timeline", "08-issue-log"}
GOLD_EXAMPLE_DEFINITIONS = [
    {
        "source_id": "scenario-project-report",
        "id": "scenario-project-report-gold-pages",
        "scenario": "项目阶段汇报截图级两页",
        "pages": [
            ("04-timeline", "04-timeline"),
            ("08-issue-log", "08-issue-log"),
        ],
    },
    {
        "source_id": "scenario-annual-summary",
        "id": "scenario-annual-summary-gold-pages",
        "scenario": "年度经营总结截图级三页",
        "pages": [
            ("04-dashboard", "04-dashboard"),
            ("08-evidence-table", "08-evidence-table"),
            ("09-actions", "09-actions"),
        ],
    },
]
LITERARY_BENCHMARK_ID = "scenario-book-deep-analysis-benchmark"
LITERARY_BENCHMARK_IMAGE_ASSET_KEY = "materials/destiny-upload/extracted-images/cover-like-photo.png"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

THEMES: dict[str, dict[str, str]] = {
    "business_blue": {
        "bg": "#F6F8FB", "surface": "#FFFFFF", "title": "#0F172A",
        "body": "#334155", "muted": "#64748B", "accent": "#2563EB",
        "accent2": "#0EA5E9", "border": "#D9E2EC", "warning": "#B91C1C",
        "footer": "#64748B",
    },
    "project_blue": {
        "bg": "#F4F7FA", "surface": "#FFFFFF", "title": "#003D79",
        "body": "#243447", "muted": "#6B7A90", "accent": "#2F80ED",
        "accent2": "#F59E0B", "border": "#D7DEE8", "warning": "#B91C1C",
        "footer": "#6B7A90",
    },
    "finance_dark": {
        "bg": "#07111F", "surface": "#0F2438", "title": "#FFFFFF",
        "body": "#D8E7FF", "muted": "#8CA3C7", "accent": "#45D1FF",
        "accent2": "#A7F3D0", "border": "#2B4C7E", "warning": "#FCA5A5",
        "footer": "#8CA3C7",
    },
    "product_light": {
        "bg": "#F6F8FB", "surface": "#FFFFFF", "title": "#0F172A",
        "body": "#334155", "muted": "#64748B", "accent": "#1A3A6B",
        "accent2": "#22C55E", "border": "#D9E2EC", "warning": "#B91C1C",
        "footer": "#64748B",
    },
    "academic_light": {
        "bg": "#F8FAFC", "surface": "#FFFFFF", "title": "#1E293B",
        "body": "#334155", "muted": "#64748B", "accent": "#2563EB",
        "accent2": "#7C3AED", "border": "#E2E8F0", "warning": "#B91C1C",
        "footer": "#64748B",
    },
    "government_red": {
        "bg": "#8A1538", "surface": "#FFF7ED", "title": "#FFFFFF",
        "body": "#3B1F1F", "muted": "#F8D98A", "accent": "#F8D98A",
        "accent2": "#D4A843", "border": "#D4A843", "warning": "#7F1D1D",
        "footer": "#F8D98A",
    },
    "training_clean": {
        "bg": "#F8FAFC", "surface": "#FFFFFF", "title": "#1E293B",
        "body": "#334155", "muted": "#64748B", "accent": "#F59E0B",
        "accent2": "#0F766E", "border": "#E2E8F0", "warning": "#9A3412",
        "footer": "#64748B",
    },
}


def item(head: str, body: str, bullets: list[str], tag: str = "") -> dict[str, Any]:
    return {"head": head, "body": body, "bullets": bullets, "tag": tag}


DECKS: list[dict[str, Any]] = [
    {
        "id": "scenario-annual-summary", "theme": "business_blue", "scenario": "年度经营总结",
        "source_materials": [
            {
                "material_id": "finance-monthly-report",
                "kind": "table",
                "display_name": "年度财务月报",
                "summary": "记录收入、毛利、回款、行业结构和月度波动。",
            },
            {
                "material_id": "crm-contract-ledger",
                "kind": "table",
                "display_name": "CRM 商机与合同清单",
                "summary": "记录重点行业客户、合同金额、区域归属和复制线索。",
            },
            {
                "material_id": "delivery-pmo-ledger",
                "kind": "table",
                "display_name": "交付 PMO 台账",
                "summary": "记录项目周期、返工率、验收节点和交付责任人。",
            },
            {
                "material_id": "customer-success-renewal",
                "kind": "table",
                "display_name": "客户成功复购台账",
                "summary": "记录 A/B/C 客户分层、续约金额、复购率和风险客户。",
            },
        ],
        "pages": [
            {"id": "01-cover", "role": "cover", "layout": "cover", "eyebrow": "年度经营复盘 / 中国区业务中心", "title": "全年目标稳步达成，增长质量持续改善", "subtitle": "从规模扩张转向高质量经营，聚焦行业深耕、标杆复制和复购运营。", "metrics": [("结构", "重点行业占比提升"), ("效率", "交付周期持续压缩"), ("风险", "复购运营待闭环")]},
            {"id": "04-dashboard", "role": "content", "layout": "dashboard", "title": "年度结果：收入结构优化，但复购质量仍需补强", "subtitle": "经营复盘页用指标和差距同时证明观点。", "metrics": [("收入达成", "102%", 82), ("重点行业", "58%", 70), ("交付效率", "+18%", 62), ("复购贡献", "待补", 36)], "items": [item("贡献项", "行业深耕带来高毛利项目", ["华东、华南形成标杆打法", "大客户复制效率提升"], "证据"), item("差距项", "复购运营还未责任到人", ["客户分层台账不完整", "需补充复购率口径"], "缺口")]},
            {"id": "05-matrix", "role": "content", "layout": "matrix", "title": "差距诊断：问题集中在效率、协同和客户运营", "subtitle": "用二维矩阵区分立即整改与机制优化。", "items": [item("高影响 / 易推进", "标杆项目复制", ["沉淀模板包", "区域销售复用"], "优先"), item("高影响 / 难推进", "客户分层运营", ["补 CRM 口径", "明确客户经理责任"], "攻坚"), item("低影响 / 易推进", "周报口径统一", ["统一字段", "减少人工汇总"], "快赢"), item("低影响 / 难推进", "跨部门排期", ["建立月度协调会", "升级冲突事项"], "机制")]},
            {"id": "06-cause", "role": "content", "layout": "left_right", "title": "原因分析：增长不是单点动作，而是三类机制共同作用", "subtitle": "左侧给判断，右侧用证据链支撑。", "items": [item("核心判断", "收入增长来自行业选择、交付机制和复购运营的组合改善。", ["不能只归因于销售投入", "需要补齐经营数据来源"], "结论"), item("行业选择", "重点行业需求更确定", ["预算明确、客户集中", "案例可跨区域复用"], "证据一"), item("交付机制", "联合评审降低返工", ["售前、交付、运营同评审", "节点风险进入周会"], "证据二"), item("复购运营", "短板影响长期质量", ["分层策略缺少动作闭环", "老客户价值挖掘不足"], "风险")]},
            {"id": "07-roadmap", "role": "content", "layout": "timeline", "title": "来年抓手：从增长目标拆到四个季度动作", "subtitle": "年度计划页必须给周期、责任和可检查交付物。", "items": [item("Q1", "建立行业打法包", ["完成客户分层", "输出标杆案例库"], "基础"), item("Q2", "复制区域样板", ["华东打法复制到华中", "周度跟踪转化"], "复制"), item("Q3", "提升交付效率", ["标准化里程碑", "异常事项 48h 升级"], "提效"), item("Q4", "复盘与续约", ["复购台账收口", "明确来年预算池"], "闭环")]},
            {"id": "09-actions", "role": "summary", "layout": "action_table", "title": "行动闭环：把经营判断落到责任、指标和复盘节奏", "subtitle": "总结页不只写口号，要形成可追踪台账。", "items": [item("行业打法包", "市场部 + 销售战区", ["2月底完成模板", "覆盖 3 个重点行业"], "Owner"), item("交付效率专项", "交付 PMO", ["月度看板", "周期缩短目标待补"], "KPI"), item("复购运营台账", "客户成功部", ["A/B/C 客户分层", "季度复盘续约机会"], "风险"), item("经营数据口径", "财经 + 运营", ["统一收入、毛利、回款口径", "进入月度经营会"], "口径")]},
        ],
    },
    {
        "id": "scenario-project-report", "theme": "project_blue", "scenario": "项目阶段汇报",
        "source_materials": [
            {
                "material_id": "project-weekly-ledger",
                "kind": "table",
                "display_name": "项目周报台账",
                "summary": "记录总体进度、里程碑、责任人、风险等级和下周动作。",
            },
            {
                "material_id": "integration-issue-list",
                "kind": "table",
                "display_name": "联调问题清单",
                "summary": "记录异常回流、口径差异、关闭截图和技术责任人。",
            },
            {
                "material_id": "pmo-schedule-board",
                "kind": "schedule",
                "display_name": "PMO 验收排期表",
                "summary": "记录区县驻场窗口、供应商资源冲突和验收材料提交节点。",
            },
            {
                "material_id": "acceptance-evidence-pack",
                "kind": "evidence_pack",
                "display_name": "验收证据包目录",
                "summary": "记录部署包、联调截图、培训签到、会议纪要和口径确认单。",
            },
        ],
        "pages": [
            {"id": "01-cover", "role": "cover", "layout": "cover", "eyebrow": "市级数据治理项目 / 阶段汇报", "title": "总体进度可控，两项风险需要本周升级处理", "subtitle": "当前已完成核心系统联调，风险集中在数据口径和资源排期。", "metrics": [("进度", "82% 核心任务完成"), ("风险", "2 项需升级"), ("诉求", "PMO 本周决策")]},
            {"id": "04-timeline", "role": "content", "layout": "timeline", "title": "里程碑：主流程按计划推进，验收准备进入关键窗口", "subtitle": "项目页用进度、证据和阻塞共同表达，不用泛泛写“正常推进”。", "items": [item("立项", "目标和范围确认", ["责任矩阵已归档", "验收口径待业务确认"], "已完成"), item("联调", "市区两级系统打通", ["主流程通过 12/14", "异常回流 3 项待关"], "完成"), item("试点", "两家单位准备验收", ["材料完成 70%", "口径差异待签字"], "进行中"), item("验收", "月底提交总结材料", ["驻场窗口需锁定", "证据包需复核"], "风险")]},
            {"id": "05-risk", "role": "content", "layout": "risk_heatmap", "title": "风险热力图：数据口径和资源排期是主要阻塞", "subtitle": "风险页必须写清影响、触发条件、责任人和升级动作。", "items": [item("数据口径未统一", "影响验收材料一致性", ["三类指标周期不同", "业务处室 A 本周三确认"], "高影响"), item("资源排期冲突", "影响驻场验收窗口", ["供应商与区县时间重叠", "PMO B 需统一协调"], "高概率"), item("异常数据回流", "影响系统稳定性说明", ["技术组 C 日清修复", "关闭截图入证据包"], "中风险"), item("培训覆盖不足", "影响上线后使用率", ["运营组 D 补一轮培训", "签到表和 FAQ 入档"], "可控")]},
            {"id": "06-decision", "role": "content", "layout": "left_right", "title": "本周决策：明确责任边界，避免月底验收被动", "subtitle": "升级页要把判断、证据、诉求和截止时间放在同一页。", "items": [item("项目判断", "目标仍可达成，但风险不能继续在项目组内部消化。", ["月底窗口不可后移", "口径和排期已跨部门"], "需决策"), item("诉求一", "业务处室确认三类指标口径", ["本周三前给结论", "纳入验收材料"], "口径"), item("诉求二", "PMO 统一区县验收排期", ["锁定驻场窗口", "明确供应商责任"], "排期"), item("诉求三", "异常回流问题进入日清单", ["48 小时内响应", "每日同步风险"], "机制")]},
            {"id": "07-gantt", "role": "content", "layout": "roadmap", "title": "资源计划：按验收倒排 4 条工作流", "subtitle": "用泳道式计划展示任务并行关系、责任人、交付物和检查点。", "items": [item("数据口径", "业务处室牵头", ["周一收集差异", "周三确认口径"], "业务"), item("系统修复", "技术组牵头", ["异常回流修复", "发布回归报告"], "技术"), item("验收材料", "PMO 牵头", ["材料模板统一", "区县补充附件"], "材料"), item("培训上线", "运营组牵头", ["组织操作培训", "收集使用反馈"], "运营")]},
            {"id": "09-actions", "role": "summary", "layout": "action_table", "title": "下周行动台账：每项风险必须有责任人和完成时限", "subtitle": "项目总结页必须形成可追踪的责任闭环和复盘节奏。", "items": [item("统一指标口径", "业务处室 A", ["6月10日前确认", "输出口径说明"], "红"), item("协调驻场排期", "PMO B", ["6月11日前锁定", "同步区县联系人"], "黄"), item("异常回流修复", "技术负责人 C", ["每日发布修复清单", "回归截图入库"], "蓝"), item("验收材料复核", "项目经理 D", ["6月14日完成", "形成提交包"], "绿")]},
        ],
    },
    {
        "id": "scenario-financing-roadshow", "theme": "finance_dark", "scenario": "融资路演",
        "pages": [
            {"id": "01-cover", "role": "cover", "layout": "cover", "eyebrow": "融资路演 / 企业智能化升级", "title": "垂直行业智能化进入规模复制期", "subtitle": "以行业数据、交付网络和标杆客户形成壁垒，支撑产品扩展和销售放大。", "metrics": [("窗口", "高价值行业先启动"), ("壁垒", "数据 + 交付网络"), ("用途", "工程化与销售放大")]},
            {"id": "02-market", "role": "content", "layout": "funnel", "title": "市场机会：需求增长但供给仍然碎片化", "subtitle": "BP 市场页用漏斗拆 TAM/SAM/SOM，同时标出待补数据口径。", "items": [item("TAM", "企业智能化升级总需求", ["制造、能源、园区预算明确", "需补第三方市场报告"], "最大市场"), item("SAM", "垂直行业可服务市场", ["先聚焦高频流程", "渠道伙伴可覆盖"], "可服务"), item("SOM", "12-18 个月可获得市场", ["围绕标杆客户复制", "销售线索集中"], "近期目标")]},
            {"id": "03-product-moat", "role": "content", "layout": "architecture", "title": "产品壁垒：行业知识库和交付网络共同形成复制能力", "subtitle": "能力页要展示模块关系，而不是罗列功能名。", "items": [item("行业知识库", "沉淀高频业务场景", ["流程、指标、话术可复用"], "数据"), item("交付网络", "区域伙伴支撑落地", ["本地化实施成本更低"], "网络"), item("智能编排", "把任务识别到执行闭环", ["减少单点工具割裂"], "产品"), item("客户成功", "复购运营形成反馈", ["场景数据反哺模型"], "闭环")]},
            {"id": "04-traction", "role": "content", "layout": "dashboard", "title": "增长验证：标杆客户证明复制方向，但财务指标需补齐", "subtitle": "融资页必须主动标注证据和缺口。", "metrics": [("试点客户", "N 家", 52), ("ARR", "待补", 34), ("留存", "待补", 28), ("回款周期", "待补", 24)], "items": [item("已有证据", "客户痛点和试点价值成立", ["政企会议、督办、项目协同高频", "管理视图减少人工汇总"], "验证"), item("证据缺口", "投资人会追问财务质量", ["需补 ARR、毛利、留存、回款", "需补客户合同截图"], "缺口")]},
            {"id": "05-business-model", "role": "content", "layout": "comparison", "title": "商业模式：从项目制交付转向产品化订阅和服务包", "subtitle": "商业模式页对比当前模式与目标模式。", "items": [item("当前模式", "项目制收入占比高", ["定制交付重", "区域复制慢"], "现状"), item("目标模式", "订阅 + 服务包组合", ["标准产品售卖", "伙伴交付复制"], "目标"), item("关键变化", "提升毛利和可预测收入", ["工程化降低交付成本", "续费和增购形成 LTV"], "影响")]},
            {"id": "06-funding-use", "role": "summary", "layout": "roadmap", "title": "融资用途：12 个月完成产品工程化和重点区域复制", "subtitle": "结尾页给资金用途、里程碑和可验收成果。", "items": [item("45% 产品工程化", "补齐平台能力", ["权限、审计、部署自动化"], "产品"), item("30% 行业数据", "沉淀知识库", ["覆盖三类重点行业"], "数据"), item("25% 销售网络", "扩大区域覆盖", ["伙伴培训和线索转化"], "销售"), item("验收目标", "形成可复制增长模型", ["指标口径待补", "季度复盘给董事会"], "目标")]},
        ],
    },
    {
        "id": "scenario-product-launch", "theme": "product_light", "scenario": "产品发布",
        "pages": [
            {"id": "01-cover", "role": "cover", "layout": "cover", "eyebrow": "产品发布 / 国产智能协同平台", "title": "三项能力重构政企客户协同闭环", "subtitle": "从单点提醒升级为任务识别、过程跟踪和结果复盘的端到端协同。", "metrics": [("对象", "政企协同场景"), ("能力", "识别-跟踪-复盘"), ("行动", "开放试用")]},
            {"id": "02-pain-journey", "role": "content", "layout": "timeline", "title": "用户旅程：断点出现在会议后、执行中和复盘时", "subtitle": "发布页先讲用户痛点，不先堆功能。", "items": [item("会议后", "纪要无法直接变任务", ["责任人和时间易丢失"], "断点一"), item("执行中", "管理者看不到进展", ["多项目状态分散"], "断点二"), item("协同中", "跨部门依赖不透明", ["风险不能及时升级"], "断点三"), item("复盘时", "经验难沉淀为模板", ["下一次仍从零开始"], "断点四")]},
            {"id": "03-capability", "role": "content", "layout": "architecture", "title": "产品能力：围绕任务闭环构建三层架构", "subtitle": "能力页用架构关系解释功能价值。", "items": [item("任务识别", "自动抽取责任事项", ["会议、文档、聊天多源输入"], "识别"), item("过程跟踪", "按项目和责任人归集", ["看板、提醒、风险升级"], "跟踪"), item("结果复盘", "生成复盘建议和模板", ["沉淀有效动作"], "复盘"), item("权限审计", "满足政企安全要求", ["可追踪、可留痕"], "安全")]},
            {"id": "04-comparison", "role": "content", "layout": "comparison", "title": "价值差异：从单点工具升级为组织级协同系统", "subtitle": "功能亮点必须对应用户收益。", "items": [item("传统工具", "提醒、表格和群消息割裂", ["人工维护成本高", "责任链不清晰"], "Before"), item("新平台", "事项自动进入执行闭环", ["责任、进度、结果可追踪", "管理者一屏掌握"], "After"), item("客户收益", "减少人工汇总，提高督办透明度", ["适配会议、专项督办、项目协同"], "Value")]},
            {"id": "05-case", "role": "content", "layout": "case_story", "title": "试点案例：专项督办场景验证闭环价值", "subtitle": "案例页要写对象、动作、结果和待补指标。", "items": [item("对象", "某政企客户专项督办", ["事项多、责任链长"], "客户"), item("动作", "会议纪要转任务清单", ["责任人自动归集", "风险定期提醒"], "动作"), item("结果", "人工汇总成本下降", ["需补具体效率指标", "需补客户证言"], "结果")]},
            {"id": "06-launch-plan", "role": "summary", "layout": "action_table", "title": "发布计划：先试用验证，再行业复制", "subtitle": "发布收口页给渠道、节奏和验收指标。", "items": [item("开放试用", "产品 + 客成", ["首批 20 家目标客户", "2 周完成试用反馈"], "启动"), item("行业样板", "解决方案团队", ["沉淀 3 个场景模板", "形成销售话术"], "复制"), item("伙伴培训", "渠道团队", ["输出演示脚本", "覆盖重点区域"], "放大"), item("指标复盘", "运营团队", ["试用转化、活跃、留存", "月度发布迭代"], "复盘")]},
        ],
    },
    {
        "id": "scenario-academic-defense", "theme": "academic_light", "scenario": "学术答辩",
        "pages": [
            {"id": "01-cover", "role": "cover", "layout": "cover", "eyebrow": "硕士论文答辩 / 智慧城市数据治理", "title": "面向多源数据口径一致性的识别方法研究", "subtitle": "以城市治理数据为对象，构建可解释、可复核的半自动识别流程。", "metrics": [("问题", "口径不一致"), ("方法", "规则 + 语义匹配"), ("验证", "实验指标待补")]},
            {"id": "02-background", "role": "content", "layout": "left_right", "title": "研究背景：多源数据治理面临三类现实冲突", "subtitle": "答辩页用 SCQA 说明为什么这个问题值得研究。", "items": [item("研究问题", "不同部门的数据口径、周期和责任主体存在差异。", ["人工排查成本高", "影响治理决策一致性"], "问题"), item("冲突一", "指标定义不统一", ["同名指标含义不同", "跨部门映射缺失"], "定义"), item("冲突二", "异常发现依赖经验", ["缺少自动排序", "复核压力大"], "方法"), item("冲突三", "责任闭环弱", ["发现问题后难追踪整改", "反馈不能反哺模型"], "闭环")]},
            {"id": "03-method", "role": "content", "layout": "architecture", "title": "方法框架：规则约束、语义匹配和人工复核协同工作", "subtitle": "方法页要展示模块输入输出，不只放框图名词。", "items": [item("口径知识库", "沉淀指标定义和映射", ["字段、周期、责任主体"], "知识"), item("候选识别", "生成异常候选列表", ["规则过滤 + 语义匹配"], "模型"), item("复核流程", "专家确认和标注", ["结果可解释、可追踪"], "复核"), item("反馈迭代", "复核结果反哺规则", ["降低误报和漏报"], "迭代")]},
            {"id": "04-experiment", "role": "content", "layout": "dashboard", "title": "实验结果：关键指标优于规则基线，但泛化仍需验证", "subtitle": "实验页必须写基线、指标和结论。", "metrics": [("准确率", "待补", 48), ("召回率", "待补", 44), ("F1", "待补", 40), ("样本量", "待补", 36)], "items": [item("实验设计", "与规则基线进行对比", ["需补数据集规模", "需补训练/测试划分"], "设计"), item("实验结论", "方法提升方向成立", ["指标数值待补", "跨城市泛化待验证"], "结论")]},
            {"id": "05-contribution", "role": "content", "layout": "pyramid", "title": "创新贡献：从人工排查推进到可解释半自动治理流程", "subtitle": "创新页用金字塔表达理论、方法和应用层贡献。", "items": [item("应用贡献", "支撑城市治理数据口径协同", ["形成可追踪整改闭环"], "应用"), item("方法贡献", "融合规则约束和语义匹配", ["提升候选识别效率"], "方法"), item("理论贡献", "构建口径一致性识别框架", ["明确问题定义和评价口径"], "理论")]},
            {"id": "06-limitations", "role": "summary", "layout": "action_table", "title": "不足与展望：补齐实验指标后扩展跨城市验证", "subtitle": "答辩收口页主动说明局限和后续研究计划。", "items": [item("实验指标补充", "研究者", ["补准确率/召回率/F1", "补显著性说明"], "近期"), item("数据集扩展", "课题组", ["增加跨城市样本", "补充行业差异"], "中期"), item("系统化落地", "合作单位", ["接入治理平台", "记录复核反馈"], "应用"), item("论文完善", "作者", ["图表统一口径", "强化结论边界"], "答辩后")]},
        ],
    },
    {
        "id": "scenario-government-study", "theme": "government_red", "scenario": "党政学习",
        "pages": [
            {"id": "01-cover", "role": "cover", "layout": "cover", "eyebrow": "党政学习 / 国企基层党组织", "title": "将学习成果转化为岗位实践和责任闭环", "subtitle": "围绕精神实质、实践路径和落实机制，推动学习贯彻从“学过”走向“见效”。", "metrics": [("学习", "准确把握精神实质"), ("实践", "联系岗位任务"), ("闭环", "台账督导见效")]},
            {"id": "02-policy", "role": "content", "layout": "cards3", "title": "学习重点：把政策要求拆成认知、行动和机制三层", "subtitle": "党政页要区分政策原文和本单位行动。", "items": [item("精神实质", "原原本本学，统一思想认识", ["抓住核心要求", "结合本单位职责"], "认知"), item("实践路径", "联系岗位学，找准工作切口", ["问题清单", "整改台账"], "行动"), item("落实机制", "闭环跟踪学，确保见效", ["责任、督导、评价", "挂牌督办未闭环事项"], "机制")]},
            {"id": "03-pyramid", "role": "content", "layout": "pyramid", "title": "转化逻辑：从精神内涵到岗位行动再到组织机制", "subtitle": "用层级结构避免只堆口号。", "items": [item("组织机制", "支部月度跟踪和评价反馈", ["纳入重点任务督办"], "机制"), item("岗位行动", "党员责任区牵引重点任务", ["服务群众、提质增效、风险防控"], "行动"), item("精神内涵", "统一思想和行动方向", ["需补政策原文出处"], "内涵")]},
            {"id": "04-mechanism", "role": "content", "layout": "timeline", "title": "落实机制：学习、查摆、整改、复盘形成闭环", "subtitle": "机制页必须有节点和产物。", "items": [item("集中学习", "统一政策理解", ["领学 + 研讨", "形成学习纪要"], "学"), item("问题查摆", "对照岗位找差距", ["列问题清单", "明确责任主体"], "查"), item("整改落实", "把问题转为任务", ["节点、标准、负责人"], "改"), item("复盘评价", "对未闭环事项督办", ["月度通报", "评价反馈"], "评")]},
            {"id": "05-branch-actions", "role": "content", "layout": "action_table", "title": "支部行动台账：每项学习成果都要落到责任主体", "subtitle": "国企/政务汇报要体现责任、时限和检查方式。", "items": [item("服务窗口优化", "第一党小组", ["梳理群众高频问题", "月底提交优化清单"], "服务"), item("安全生产排查", "第二党小组", ["重点岗位风险复核", "形成整改闭环"], "安全"), item("降本增效专项", "第三党小组", ["梳理流程堵点", "提出 3 项优化建议"], "经营"), item("青年党员攻关", "团青小组", ["参与重点项目", "每月交流成果"], "队伍")]},
            {"id": "06-closed-loop", "role": "summary", "layout": "roadmap", "title": "闭环收口：用责任台账推动学习成果转化见效", "subtitle": "总结页强调可检查、可复盘、可问责。", "items": [item("建账", "形成问题和任务双台账", ["来源、责任、时限清楚"], "起点"), item("跟踪", "月度支部会议滚动检查", ["更新状态和风险"], "过程"), item("督办", "未闭环事项挂牌推进", ["明确升级路径"], "保障"), item("复盘", "把有效做法沉淀为制度", ["纳入年度党建总结"], "成果")]},
        ],
    },
    {
        "id": "scenario-training-course", "theme": "training_clean", "scenario": "培训课程",
        "pages": [
            {"id": "01-cover", "role": "cover", "layout": "cover", "eyebrow": "企业培训 / 一线管理者执行闭环训练营", "title": "把日常管理做成可追踪的执行闭环", "subtitle": "从识别问题、拆解动作到复盘改进，帮助班组长完成一次真实闭环。", "metrics": [("目标", "掌握 3 项能力"), ("方法", "问题卡-行动清单-复盘"), ("产出", "课后真实演练")]},
            {"id": "02-objectives", "role": "content", "layout": "cards3", "title": "学习目标：完成从概念理解到行动输出的转化", "subtitle": "培训页要写可观察的学习产出。", "items": [item("识别问题", "把现象转成可描述问题", ["对象、时间、影响范围", "区分现象和原因"], "能力一"), item("拆解动作", "把目标拆到责任和节点", ["完成标准", "风险和依赖"], "能力二"), item("复盘改进", "把结果沉淀为标准动作", ["偏差分析", "有效动作复用"], "能力三")]},
            {"id": "03-sop", "role": "content", "layout": "timeline", "title": "方法步骤：从识别到执行再到复盘", "subtitle": "SOP 页用步骤、产物和检查点降低弱模型发挥空间。", "items": [item("问题卡", "写清问题和影响", ["一句话描述", "列影响对象"], "产物一"), item("行动清单", "拆责任人和节点", ["每项动作有完成标准"], "产物二"), item("风险标记", "提前识别依赖", ["标出阻塞和升级路径"], "产物三"), item("复盘模板", "沉淀有效动作", ["下一轮直接复用"], "产物四")]},
            {"id": "04-case", "role": "content", "layout": "case_story", "title": "案例演练：班组交付延误如何拆成可执行闭环", "subtitle": "案例页要保留场景、问题、动作、结果。", "items": [item("场景", "班组连续两周交付延误", ["影响客户上线窗口", "跨岗位协同不清"], "背景"), item("动作", "建立日清单和风险升级", ["责任人到人", "每日 17 点同步"], "处理"), item("结果", "延误事项逐步收敛", ["需补真实数据", "沉淀排期模板"], "复盘")]},
            {"id": "05-worksheet", "role": "content", "layout": "worksheet", "title": "课堂练习：用真实问题完成一张执行闭环表", "subtitle": "练习页给填写框架，不用只写“请讨论”。", "items": [item("问题描述", "对象 / 时间 / 影响", ["写 1 句话问题", "补充影响范围"], "填空"), item("原因判断", "现象 / 原因 / 后果", ["至少 2 条原因", "标出证据来源"], "分析"), item("行动拆解", "责任人 / 节点 / 标准", ["不少于 3 项动作", "每项有完成标准"], "行动"), item("复盘指标", "结果 / 偏差 / 改进", ["选择 1 个量化指标", "写下一轮优化"], "复盘")]},
            {"id": "06-transfer", "role": "summary", "layout": "action_table", "title": "课后迁移：一周内完成一次真实管理闭环", "subtitle": "培训总结页给作业、验收标准和反馈机制。", "items": [item("选题", "学员本人", ["选择一个真实班组问题", "周一前提交问题卡"], "Day1"), item("执行", "学员 + 主管", ["按行动清单推进", "遇阻升级"], "Day2-5"), item("复盘", "培训组织者", ["收集模板和结果", "给出改进建议"], "Day6"), item("沉淀", "部门负责人", ["优秀案例进入 SOP", "纳入月度分享"], "Day7")]},
        ],
    },
]


EXTRA_PAGES: dict[str, list[dict[str, Any]]] = {
    "scenario-annual-summary": [
        {"id": "02-agenda", "role": "agenda", "layout": "agenda", "title": "汇报目录：年度结果、差距诊断、来年抓手和行动闭环", "subtitle": "目录页让弱模型学习整套汇报的章节组织。", "items": [item("01", "年度经营结果", ["收入结构、重点行业、交付效率"], "结果"), item("02", "差距与原因诊断", ["效率、协同、复购运营"], "诊断"), item("03", "来年重点抓手", ["行业打法、区域复制、复购台账"], "计划"), item("04", "责任闭环", ["Owner、KPI、风险和口径"], "闭环")]},
        {"id": "03-section-results", "role": "section_divider", "layout": "section", "title": "第一部分：年度经营结果", "subtitle": "先用指标证明“做成了什么”，再讲原因和差距。", "items": [item("主问题", "全年目标是否达成？", ["收入、结构、效率、复购"], "Q1"), item("回答方式", "用数据和缺口共同证明", ["不只写成绩，也写风险"], "Method")]},
        {"id": "08-evidence-table", "role": "content", "layout": "evidence_table", "title": "证据表：经营结论必须对应来源、口径和缺口", "subtitle": "用于训练模型不要只写泛化判断。", "items": [item("收入达成", "经营月报 / 财务口径", ["需补按行业收入", "需补毛利贡献"], "数据"), item("重点行业", "CRM 商机池 / 合同清单", ["需补客户名单", "需补区域对比"], "来源"), item("交付效率", "PMO 项目台账", ["需补平均周期", "需补返工率"], "效率"), item("复购贡献", "客户成功台账", ["需补复购率", "需补续约金额"], "缺口")]},
        {"id": "10-appendix", "role": "appendix", "layout": "appendix", "title": "附录：经营数据口径与待补素材清单", "subtitle": "附录页用于说明真实生成时还需要哪些证据。", "items": [item("财务口径", "收入、毛利、回款", ["按月、按行业、按区域"], "口径"), item("客户口径", "新增、续约、流失", ["分层客户台账", "复购金额"], "客户"), item("项目口径", "周期、返工、验收", ["PMO 台账", "交付问题清单"], "项目"), item("责任口径", "Owner、时限、复盘", ["月度经营会模板"], "责任")]},
    ],
    "scenario-project-report": [
        {"id": "02-agenda", "role": "agenda", "layout": "agenda", "title": "汇报目录：进度、风险、决策诉求和下周闭环", "subtitle": "项目 deck 必须让领导快速看到是否需要决策。", "items": [item("01", "总体进度", ["里程碑、完成率、验收窗口"], "进度"), item("02", "风险阻塞", ["口径、排期、异常回流"], "风险"), item("03", "决策诉求", ["责任边界、资源协调"], "诉求"), item("04", "行动台账", ["负责人、时限、验收材料"], "闭环")]},
        {"id": "03-section-progress", "role": "section_divider", "layout": "section", "title": "第一部分：项目进度与验收窗口", "subtitle": "用进度和验收倒排解释为什么本周必须处理风险。", "items": [item("关键窗口", "月底验收不可后移", ["资源排期需要提前锁定"], "窗口"), item("表达方式", "里程碑 + 风险 + 诉求", ["避免只写项目正常推进"], "结构")]},
        {"id": "08-issue-log", "role": "content", "layout": "evidence_table", "title": "问题清单：每项阻塞都要有来源、影响和下一步", "subtitle": "真实项目汇报需要可追踪 issue log。", "items": [item("指标口径差异", "业务处室反馈", ["影响验收材料一致性", "周三前确认"], "高"), item("驻场排期冲突", "PMO 排期表", ["影响区县验收窗口", "需统一协调"], "高"), item("异常回流失败", "联调问题单", ["影响稳定性说明", "技术组日清"], "中"), item("培训未覆盖", "运营计划", ["影响上线使用率", "补一轮培训"], "低")]},
        {"id": "10-appendix", "role": "appendix", "layout": "appendix", "title": "附录：项目交付材料与验收口径", "subtitle": "附录页覆盖交付物、验收证据和责任人。", "items": [item("交付物", "系统部署包 / 操作文档", ["版本号、部署记录"], "材料"), item("验收证据", "联调清单 / 截图", ["问题关闭记录"], "证据"), item("培训材料", "课件 / 签到表", ["覆盖单位清单"], "培训"), item("责任清单", "PMO / 业务 / 技术", ["本周确认责任边界"], "责任")]},
    ],
    "scenario-financing-roadshow": [
        {"id": "02-agenda", "role": "agenda", "layout": "agenda", "title": "路演目录：机会、产品、验证、模式和融资用途", "subtitle": "BP deck 需要用投资人视角组织证据链。", "items": [item("01", "市场窗口", ["TAM/SAM/SOM 与供给缺口"], "机会"), item("02", "产品壁垒", ["行业知识库、交付网络"], "壁垒"), item("03", "增长验证", ["客户、ARR、留存、回款"], "验证"), item("04", "融资用途", ["产品、数据、销售网络"], "资金")]},
        {"id": "03-section-market", "role": "section_divider", "layout": "section", "title": "第一部分：市场机会与切入窗口", "subtitle": "先说明为什么是现在，再说明为什么是我们。", "items": [item("投资人问题", "市场是否足够大？", ["预算、刚需、替代方案"], "Q1"), item("回答方式", "漏斗 + 数据缺口 + 切入场景", ["不讲纯愿景"], "Method")]},
        {"id": "08-financial-table", "role": "content", "layout": "evidence_table", "title": "财务证据表：增长叙事必须补齐关键经营指标", "subtitle": "用于提醒模型主动标注待补数据。", "items": [item("ARR", "财务模型", ["当前值待补", "同比增速待补"], "收入"), item("毛利率", "财务报表", ["项目制 vs 订阅制", "交付成本拆分"], "质量"), item("留存率", "客户成功台账", ["续费、增购、流失"], "留存"), item("获客成本", "销售费用表", ["线索、转化、回款周期"], "效率")]},
        {"id": "10-appendix", "role": "appendix", "layout": "appendix", "title": "附录：投资人尽调材料清单", "subtitle": "路演附录页要覆盖可被追问的底层材料。", "items": [item("市场材料", "第三方报告 / 行业预算", ["TAM/SAM/SOM 口径"], "市场"), item("客户材料", "合同 / 案例 / 证言", ["标杆客户可披露范围"], "客户"), item("财务材料", "收入 / 毛利 / 回款", ["模型假设说明"], "财务"), item("产品材料", "Demo / Roadmap", ["安全合规与部署能力"], "产品")]},
    ],
    "scenario-product-launch": [
        {"id": "02-agenda", "role": "agenda", "layout": "agenda", "title": "发布目录：痛点、能力、价值验证和发布计划", "subtitle": "产品发布 deck 应从用户问题展开，而不是从功能清单展开。", "items": [item("01", "用户痛点", ["旅程断点与协同成本"], "痛点"), item("02", "产品能力", ["任务识别、跟踪、复盘"], "能力"), item("03", "价值验证", ["试点案例、前后对比"], "证据"), item("04", "发布行动", ["试用、样板、伙伴培训"], "行动")]},
        {"id": "03-section-user", "role": "section_divider", "layout": "section", "title": "第一部分：用户问题与场景断点", "subtitle": "先讲用户为什么需要，再讲产品怎么解决。", "items": [item("核心问题", "协同事项跨系统、跨部门、跨周期", ["责任链和结果链断裂"], "问题"), item("表达方式", "旅程图 + 前后对比 + 案例", ["功能必须映射收益"], "方法")]},
        {"id": "08-release-metrics", "role": "content", "layout": "evidence_table", "title": "发布指标：试用、转化、活跃和留存必须可追踪", "subtitle": "发布计划页不能只写市场动作。", "items": [item("试用客户", "CRM 目标名单", ["首批 20 家", "行业分布待补"], "试用"), item("转化率", "销售漏斗", ["试用到签约", "周期待补"], "转化"), item("活跃度", "产品埋点", ["任务创建、闭环率", "周活待补"], "活跃"), item("客户反馈", "访谈记录", ["证言、问题、需求池"], "反馈")]},
        {"id": "10-appendix", "role": "appendix", "layout": "appendix", "title": "附录：发布素材与演示资产清单", "subtitle": "弱模型参考时要知道发布 deck 还需要哪些素材。", "items": [item("Demo 素材", "场景脚本 / 截图", ["会议转任务", "督办看板"], "演示"), item("销售素材", "一页纸 / FAQ", ["行业话术", "竞品回应"], "销售"), item("客户素材", "试点案例 / 证言", ["授权范围", "指标口径"], "客户"), item("运营素材", "试用流程 / 反馈表", ["上线节奏", "回访机制"], "运营")]},
    ],
    "scenario-academic-defense": [
        {"id": "02-agenda", "role": "agenda", "layout": "agenda", "title": "答辩目录：问题、方法、实验、贡献和展望", "subtitle": "学术 deck 需要遵循答辩委员会的审查路径。", "items": [item("01", "研究背景与问题", ["现有方法不足、研究问题"], "问题"), item("02", "方法与框架", ["模型、流程、输入输出"], "方法"), item("03", "实验与结果", ["基线、指标、消融"], "实验"), item("04", "创新与不足", ["贡献、局限、展望"], "结论")]},
        {"id": "03-section-question", "role": "section_divider", "layout": "section", "title": "第一部分：研究问题与理论价值", "subtitle": "先证明问题存在，再进入方法设计。", "items": [item("答辩问题", "为什么这个问题重要？", ["治理数据的一致性影响决策"], "Q1"), item("回答方式", "背景冲突 + 现有不足 + 研究目标", ["避免直接讲模型"], "Method")]},
        {"id": "08-related-work", "role": "content", "layout": "evidence_table", "title": "相关工作对比：明确本文方法解决了什么不足", "subtitle": "学术页要有对比对象和评价维度。", "items": [item("规则方法", "可解释但覆盖不足", ["维护成本高", "难处理语义差异"], "Baseline"), item("统计方法", "可发现异常但解释弱", ["依赖样本规模", "跨域泛化不稳"], "Baseline"), item("语义匹配", "能处理文本差异", ["需要领域知识约束"], "Related"), item("本文方法", "规则 + 语义 + 复核闭环", ["兼顾解释与效率"], "Ours")]},
        {"id": "10-appendix", "role": "appendix", "layout": "appendix", "title": "附录：实验设置与论文补充材料", "subtitle": "答辩附录用于准备老师追问。", "items": [item("数据集", "样本来源 / 标注规则", ["规模、字段、脱敏说明"], "数据"), item("评价指标", "准确率 / 召回率 / F1", ["定义和计算公式"], "指标"), item("基线模型", "规则、统计、语义匹配", ["参数和实现说明"], "基线"), item("消融实验", "去除规则 / 去除复核", ["验证模块贡献"], "消融")]},
    ],
    "scenario-government-study": [
        {"id": "02-agenda", "role": "agenda", "layout": "agenda", "title": "学习目录：精神内涵、转化路径、落实机制和责任台账", "subtitle": "党政 deck 必须把学习和落实分层呈现。", "items": [item("01", "精神实质", ["政策原文、核心要求"], "学习"), item("02", "转化路径", ["岗位职责、问题清单"], "实践"), item("03", "落实机制", ["查摆、整改、复盘"], "机制"), item("04", "行动台账", ["责任、时限、检查"], "闭环")]},
        {"id": "03-section-study", "role": "section_divider", "layout": "section", "title": "第一部分：准确把握精神实质", "subtitle": "学习页要先引用要求，再落到本单位任务。", "items": [item("学习问题", "政策要求如何转化为岗位行动？", ["不能停留在口号和标语"], "问题"), item("回答方式", "原文要求 + 岗位切口 + 责任机制", ["区分层级"], "方法")]},
        {"id": "08-policy-table", "role": "content", "layout": "evidence_table", "title": "政策-行动对照表：每条要求都要有本单位落实动作", "subtitle": "这是中国式党政学习页的核心证据结构。", "items": [item("提高政治站位", "集中学习 + 专题研讨", ["形成学习纪要", "党员撰写体会"], "学习"), item("服务发展大局", "党员责任区攻关", ["围绕重点项目", "每月复盘"], "发展"), item("强化风险防控", "安全生产排查", ["风险清单", "整改闭环"], "安全"), item("改进工作作风", "窗口服务优化", ["群众问题清单", "满意度回访"], "作风")]},
        {"id": "10-appendix", "role": "appendix", "layout": "appendix", "title": "附录：学习材料与落实台账清单", "subtitle": "党政附录页用于沉淀引用来源和执行证据。", "items": [item("政策原文", "会议精神 / 文件摘录", ["标明出处和日期"], "来源"), item("学习记录", "签到 / 照片 / 纪要", ["支部留档"], "记录"), item("问题台账", "查摆问题 / 整改措施", ["责任人和时限"], "台账"), item("成果材料", "案例 / 制度 / 通报", ["纳入年度总结"], "成果")]},
    ],
    "scenario-training-course": [
        {"id": "02-agenda", "role": "agenda", "layout": "agenda", "title": "课程目录：目标、方法、案例、练习和迁移", "subtitle": "培训 deck 要把学习路径和产出物讲清楚。", "items": [item("01", "学习目标", ["三项执行闭环能力"], "目标"), item("02", "方法 SOP", ["问题卡、行动清单、复盘"], "方法"), item("03", "案例演练", ["真实管理问题拆解"], "练习"), item("04", "课后迁移", ["一周内完成闭环"], "迁移")]},
        {"id": "03-section-method", "role": "section_divider", "layout": "section", "title": "第一部分：从知道概念到写出产物", "subtitle": "培训页要降低行动门槛，让学员知道下一步做什么。", "items": [item("学习问题", "为什么知道概念但不会落地？", ["缺模板、缺检查点、缺复盘"], "问题"), item("回答方式", "步骤 + 表单 + 案例 + 作业", ["每页都有产物"], "方法")]},
        {"id": "08-checklist", "role": "content", "layout": "evidence_table", "title": "检查清单：一张执行闭环表必须包含四类信息", "subtitle": "检查表页让弱模型学会做可填的培训材料。", "items": [item("问题", "对象、时间、影响", ["一句话描述", "证据来源"], "输入"), item("动作", "责任人、节点、标准", ["不少于 3 项动作", "标出依赖"], "执行"), item("风险", "阻塞、升级、预案", ["触发条件", "升级路径"], "风险"), item("复盘", "结果、偏差、改进", ["量化指标", "下一轮标准"], "复盘")]},
        {"id": "10-appendix", "role": "appendix", "layout": "appendix", "title": "附录：培训讲师准备材料清单", "subtitle": "培训附录覆盖课前、课中、课后的交付物。", "items": [item("课前", "学员问题收集表", ["按部门和岗位分类"], "准备"), item("课中", "案例卡 / 练习表", ["分组讨论材料"], "课堂"), item("课后", "迁移任务模板", ["一周反馈机制"], "作业"), item("评估", "满意度 / 行动完成率", ["纳入培训复盘"], "评估")]},
    ],
}


def _expanded_decks() -> list[dict[str, Any]]:
    decks: list[dict[str, Any]] = []
    for deck in DECKS:
        extras = EXTRA_PAGES[deck["id"]]
        pages = [deck["pages"][0], extras[0], extras[1], *deck["pages"][1:5], extras[2], deck["pages"][5], extras[3]]
        decks.append({**deck, "pages": pages})
    return decks



def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(SKILL_ROOT).as_posix()


def _text(x: int, y: int, value: str, size: int, fill: str, weight: int = 400, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>'
    )


def _lines(x: int, y: int, lines: list[str], size: int, fill: str, gap: int = 30, weight: int = 400) -> list[str]:
    return [_text(x, y + i * gap, line, size, fill, weight) for i, line in enumerate(lines)]


def _rect(x: int, y: int, w: int, h: int, fill: str, stroke: str, rx: int = 18) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'


def _format_number(value: float) -> str:
    rounded = round(value, 3)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.3f}".rstrip("0").rstrip(".")


def _scale_svg_to_ppt169(svg: str) -> str:
    """把示例设计坐标（1600x900 蓝图画布）缩放到 vendored converter 的 1280x720 ppt169 画布。"""
    ET.register_namespace("", SVG_NS)
    root = ET.fromstring(svg)

    x_attrs = {"x", "x1", "x2", "cx", "width", "rx"}
    y_attrs = {"y", "y1", "y2", "cy", "height", "ry"}
    for elem in root.iter():
        for attr, value in list(elem.attrib.items()):
            if attr in x_attrs:
                elem.set(attr, _format_number(float(value) * SCALE_X))
            elif attr in y_attrs:
                elem.set(attr, _format_number(float(value) * SCALE_Y))
            elif attr in {"r", "stroke-width", "font-size"}:
                elem.set(attr, _format_number(float(value) * SCALE_X))
    root.set("viewBox", f"0 0 {PPT_W} {PPT_H}")
    root.set("width", str(PPT_W))
    root.set("height", str(PPT_H))
    return ET.tostring(root, encoding="unicode")


def _page_base(theme: dict[str, str], page: dict[str, Any], deck: dict[str, Any]) -> list[str]:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{theme["bg"]}"/>')
    if page["layout"] not in {"cover", "section"}:
        parts.append(_text(90, 88, f'{deck["scenario"]} / {page["role"]}', 18, theme["muted"], 500))
        parts.append(_text(90, 142, page["title"], 42, theme["title"], 800))
        parts.append(_text(90, 194, page["subtitle"], 20, theme["body"], 400))
    return parts


def _footer(parts: list[str], theme: dict[str, str], deck: dict[str, Any], page: dict[str, Any]) -> None:
    parts.append(_text(90, 856, f'示例：{deck["scenario"]} / {page["id"]} / 来源：模拟业务素材，真实生成时需替换为用户证据', 12, theme["footer"]))
    parts.append("</svg>")


def _project_line(parts: list[str], x1: int, y1: int, x2: int, y2: int, color: str, width: int = 1) -> None:
    parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')


def _project_badge(parts: list[str], x: int, y: int, text: str, theme: dict[str, str], tone: str = "blue") -> None:
    fill = {"blue": "#EAF3FF", "red": "#FEF2F2", "amber": "#FFF7ED", "green": "#ECFDF5"}[tone]
    color = {"blue": theme["accent"], "red": theme["warning"], "amber": "#B45309", "green": "#15803D"}[tone]
    parts.append(_rect(x, y, 118, 34, fill, color, 17))
    parts.append(_text(x + 18, y + 23, text, 14, color, 800))


def _project_metric(parts: list[str], x: int, label: str, value: str, note: str, pct: int, theme: dict[str, str]) -> None:
    parts.append(_rect(x, 240, 300, 108, theme["surface"], theme["border"], 16))
    parts.append(_text(x + 24, 278, label, 16, theme["muted"], 600))
    parts.append(_text(x + 24, 320, value, 30, theme["title"], 900))
    parts.append(_text(x + 146, 302, note, 13, theme["body"], 500))
    parts.append(f'<rect x="{x + 146}" y="318" width="126" height="10" rx="5" fill="{theme["border"]}"/>')
    parts.append(f'<rect x="{x + 146}" y="318" width="{max(18, int(pct * 1.25))}" height="10" rx="5" fill="{theme["accent"]}"/>')


def _project_page_base(theme: dict[str, str], page: dict[str, Any]) -> list[str]:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{theme["bg"]}"/>')
    parts.append(_text(88, 24, "市级数据治理项目 / 阶段汇报 / SVG-PPT 高密度示例", 15, theme["muted"], 600))
    parts.append(_text(88, 118, page["title"], 38, theme["title"], 900))
    parts.append(_text(88, 162, page["subtitle"], 18, theme["body"], 500))
    parts.append(_rect(88, 188, 1424, 42, "#EAF3FF", "#B8D8FF", 18))
    parts.append(_text(116, 215, "页面合同：观点 + 证据 + 解释 + 影响 + 行动/风险，所有正文页必须有责任人、时限或来源。", 15, theme["title"], 700))
    return parts


def _project_footer(parts: list[str], theme: dict[str, str], deck: dict[str, Any], page: dict[str, Any]) -> None:
    parts.append(_text(88, 846, "素材：项目周报台账 / 联调问题清单 / PMO 验收排期表 / 验收证据包目录", 12, theme["footer"], 500))
    parts.append(_text(1240, 846, f'{deck["scenario"]} / {page["id"]}', 12, theme["footer"], 500))
    parts.append("</svg>")


def _render_project_section(parts: list[str], theme: dict[str, str]) -> None:
    parts.append(_rect(88, 250, 520, 390, "#003D79", "#003D79", 28))
    parts.append(_text(128, 318, "本章节回答什么", 22, "#FFFFFF", 900))
    parts.extend(_lines(128, 372, [
        "1. 进度是否真实可控？",
        "2. 哪些风险会影响月底验收？",
        "3. 需要领导本周拍板什么？",
        "4. 下周闭环如何追踪？",
    ], 18, "#EAF3FF", 42, 700))
    parts.append(_rect(128, 572, 380, 42, "#F59E0B", "#F59E0B", 21))
    parts.append(_text(154, 600, "结论先行：可控但必须升级两项风险", 16, "#FFFFFF", 900))

    cards = [
        ("进度证据", "核心任务完成 82%，主流程通过 12/14", "来源：项目周报台账；缺口：异常回流截图"),
        ("风险证据", "口径差异、驻场排期两项为红色风险", "来源：联调问题清单、PMO 排期表"),
        ("决策证据", "月底验收窗口不可后移，跨部门事项需授权", "输出：本周三口径确认 + 周五排期锁定"),
    ]
    for idx, (head, body, note) in enumerate(cards):
        y = 258 + idx * 128
        parts.append(_rect(660, y, 850, 102, theme["surface"], theme["border"], 18))
        parts.append(_text(696, y + 38, head, 20, theme["accent"], 900))
        parts.append(_text(696, y + 70, body, 17, theme["title"], 800))
        parts.append(_text(1040, y + 70, note, 14, theme["body"], 500))
    parts.append(_rect(660, 664, 850, 88, "#FFF7ED", "#F59E0B", 18))
    parts.append(_text(696, 700, "章节输出", 18, "#B45309", 900))
    parts.append(_text(820, 700, "形成“里程碑-风险-决策-行动”闭环，避免只汇报动作、不暴露阻塞。", 17, theme["title"], 800))


def _render_project_timeline(parts: list[str], theme: dict[str, str]) -> None:
    metrics = [
        ("总体进度", "82%", "核心任务完成", 82),
        ("主流程", "12/14", "联调用例通过", 86),
        ("验收材料", "70%", "附件待补齐", 70),
        ("问题关闭率", "78%", "已关闭十一项", 78),
    ]
    for idx, metric in enumerate(metrics):
        _project_metric(parts, 88 + idx * 350, *metric, theme)

    parts.append(_rect(88, 374, 430, 328, "#003D79", "#003D79", 18))
    parts.append(_text(120, 416, "领导先看结论", 22, "#FFFFFF", 900))
    parts.extend(_lines(120, 462, [
        "总体可控：核心链路已进入验收准备。",
        "主要缺口：口径确认、驻场排期、截图证据。",
        "本周动作：两项红色风险必须升级。",
        "验收判断：6月14日前完成提交包复核。",
    ], 16, "#EAF3FF", 36, 700))
    parts.append(_rect(120, 632, 344, 44, "#F59E0B", "#F59E0B", 20))
    parts.append(_text(144, 660, "本页输出：进度 + 证据 + 风险 + 行动", 15, "#FFFFFF", 900))

    x0, y0 = 552, 374
    parts.append(_rect(x0, y0, 584, 328, theme["surface"], theme["border"], 16))
    parts.append(_text(x0 + 24, y0 + 38, "验收倒排里程碑", 22, theme["title"], 900))
    headers = [("节点", 586), ("完成标准", 720), ("证据材料", 910), ("状态", 1080)]
    for head, hx in headers:
        parts.append(_text(hx, y0 + 78, head, 13, theme["accent"], 900))
    milestones = [
        ("立项", "范围/责任矩阵已归档", "会议纪要、RACI表", "绿"),
        ("联调", "主流程 12/14 通过", "联调清单、截图", "绿"),
        ("试点", "2家单位验收材料70%", "材料包、签收表", "黄"),
        ("验收", "月底提交总结材料", "口径说明、排期表", "红"),
    ]
    for idx, (node, standard, evidence, status) in enumerate(milestones):
        row_y = y0 + 116 + idx * 48
        _project_line(parts, x0 + 20, row_y - 28, x0 + 558, row_y - 28, theme["border"], 1)
        parts.append(_text(586, row_y, node, 15, theme["title"], 900))
        parts.append(_text(720, row_y, standard, 13, theme["body"], 600))
        parts.append(_text(910, row_y, evidence, 13, theme["body"], 500))
        tone = {"绿": "green", "黄": "amber", "红": "red"}[status]
        _project_badge(parts, 1060, row_y - 25, status, theme, tone)

    parts.append(_rect(1170, 374, 342, 328, theme["surface"], theme["border"], 16))
    parts.append(_text(1198, 416, "进度趋势与阻塞", 22, theme["title"], 900))
    chart_x, chart_y = 1202, 472
    chart_vals = [48, 58, 67, 76, 82]
    chart_labels = ["5/13", "5/20", "5/27", "6/03", "6/06"]
    for idx, val in enumerate(chart_vals):
        bx = chart_x + idx * 54
        bh = int(val * 1.35)
        parts.append(f'<rect x="{bx}" y="{chart_y + 126 - bh}" width="30" height="{bh}" rx="8" fill="{theme["accent"]}"/>')
        parts.append(_text(bx - 4, chart_y + 154, chart_labels[idx], 10, theme["muted"], 600))
        parts.append(_text(bx - 1, chart_y + 112 - bh, f"{val}%", 10, theme["title"], 800))
    parts.append(_rect(1202, 650, 278, 34, "#FEF2F2", theme["warning"], 14))
    parts.append(_text(1222, 672, "红色阻塞：口径差异、驻场排期", 13, theme["warning"], 900))

    evidence = [
        ("项目周报台账", "完成率、主流程、问题关闭率", "来源"),
        ("联调问题清单", "异常回流、关闭截图、Owner", "证据"),
        ("PMO排期表", "区县窗口、供应商冲突", "排期"),
        ("验收证据包", "部署包、培训签到、会议纪要", "归档"),
    ]
    for idx, (head, body, tag) in enumerate(evidence):
        x = 88 + idx * 356
        parts.append(_rect(x, 724, 320, 62, "#EAF3FF", "#B8D8FF", 14))
        parts.append(_text(x + 18, 750, f"{tag}｜{head}", 13, theme["accent"], 900))
        parts.append(_text(x + 18, 774, body, 12, theme["title"], 700))
    parts.append(_rect(88, 800, 1424, 34, "#003D79", "#003D79", 14))
    parts.append(_text(118, 823, "倒排判断：若 6月11日前未锁定口径和驻场排期，月底验收材料将无法一次性提交；本页不是时间轴装饰，而是验收可行性证明。", 13, "#FFFFFF", 900))


def _render_project_risk(parts: list[str], theme: dict[str, str]) -> None:
    parts.append(_text(102, 278, "影响高", 15, theme["warning"], 800))
    parts.append(_text(102, 746, "影响低", 15, theme["muted"], 700))
    parts.append(_text(340, 778, "概率低", 15, theme["muted"], 700))
    parts.append(_text(1190, 778, "概率高", 15, theme["warning"], 800))
    _project_line(parts, 190, 730, 1420, 730, theme["border"], 2)
    _project_line(parts, 190, 270, 190, 730, theme["border"], 2)
    _project_line(parts, 805, 300, 805, 730, theme["border"], 1)
    _project_line(parts, 190, 515, 1420, 515, theme["border"], 1)
    risks = [
        (228, 322, "数据口径未统一", "触发：三类指标周期不同", "影响：验收材料口径冲突", "Owner：业务处室A / 截止：6月10日", "升级：周三前书面确认", "red"),
        (858, 322, "资源排期冲突", "触发：供应商与区县窗口重叠", "影响：驻场验收无法展开", "Owner：PMO B / 截止：6月11日", "升级：PMO统一排期", "red"),
        (228, 560, "异常数据回流", "触发：3项问题关闭截图缺失", "影响：稳定性说明不完整", "Owner：技术C / 截止：每日18点", "动作：日清单+回归截图", "amber"),
        (858, 560, "培训覆盖不足", "触发：两家单位未完成操作演练", "影响：上线使用率波动", "Owner：运营D / 截止：6月13日", "动作：补课+FAQ归档", "green"),
    ]
    for x, y, head, trigger, impact, owner, action, tone in risks:
        color = theme["warning"] if tone == "red" else "#B45309" if tone == "amber" else "#15803D"
        fill = "#FEF2F2" if tone == "red" else "#FFF7ED" if tone == "amber" else "#ECFDF5"
        parts.append(_rect(x, y, 530, 154, fill, color, 18))
        parts.append(_text(x + 26, y + 38, head, 22, color, 900))
        parts.append(_text(x + 26, y + 70, trigger, 15, theme["title"], 700))
        parts.append(_text(x + 26, y + 96, impact, 15, theme["body"], 600))
        parts.append(_text(x + 26, y + 122, owner, 14, theme["body"], 600))
        parts.append(_text(x + 316, y + 122, action, 14, color, 800))


def _render_project_decision(parts: list[str], theme: dict[str, str]) -> None:
    parts.append(_rect(88, 250, 500, 430, "#003D79", "#003D79", 24))
    parts.append(_text(126, 314, "项目判断", 24, "#FFFFFF", 900))
    parts.extend(_lines(126, 370, [
        "目标仍可达成，但不能继续由项目组内部消化风险。",
        "月底验收窗口不可后移，口径和排期已跨部门。",
        "若本周没有明确责任边界，下周只能被动补材料。",
    ], 17, "#EAF3FF", 40, 700))
    parts.append(_rect(126, 548, 390, 76, "#F59E0B", "#F59E0B", 18))
    parts.append(_text(152, 580, "本周需拍板", 18, "#FFFFFF", 900))
    parts.append(_text(152, 608, "口径确认 / 驻场排期 / 日清机制", 15, "#FFFFFF", 700))
    asks = [
        ("诉求一：确认指标口径", "业务处室A 本周三前给书面结论", "输出：口径说明 + 验收材料引用页"),
        ("诉求二：统一区县排期", "PMO B 本周五前锁定驻场窗口", "输出：排期表 + 供应商责任边界"),
        ("诉求三：建立日清机制", "技术C 每日18点同步异常关闭情况", "输出：问题单 + 回归截图 + 风险日报"),
    ]
    for idx, (head, body, out) in enumerate(asks):
        y = 250 + idx * 142
        # 汇报类卡片禁装饰性左缘色条（contract-svg-self-qa），层级靠字重与留白表达。
        parts.append(_rect(650, y, 862, 108, theme["surface"], theme["border"], 18))
        parts.append(_text(684, y + 38, head, 22, theme["title"], 900))
        parts.append(_text(684, y + 70, body, 16, theme["body"], 700))
        parts.append(_text(684, y + 96, out, 14, theme["muted"], 500))
    parts.append(_rect(650, 704, 862, 58, "#EAF3FF", "#B8D8FF", 16))
    parts.append(_text(684, 740, "决策后验收影响：材料口径统一、驻场窗口锁定、异常关闭可追踪，验收包可在6月14日复核。", 16, theme["title"], 800))


def _render_project_gantt(parts: list[str], theme: dict[str, str]) -> None:
    x0, y0 = 92, 270
    lane_w, lane_h = 1028, 72
    parts.append(_rect(x0, y0, lane_w, 430, theme["surface"], theme["border"], 18))
    dates = ["6/7", "6/8", "6/9", "6/10", "6/11", "6/12", "6/13", "6/14"]
    for idx, date in enumerate(dates):
        x = x0 + 164 + idx * 96
        _project_line(parts, x, y0 + 46, x, y0 + 398, "#E5EDF7", 1)
        parts.append(_text(x + 16, y0 + 28, date, 14, theme["muted"], 700))
    lanes = [
        ("数据口径", "业务处室A", 1, 3, "#2F80ED", "差异收集 -> 书面确认"),
        ("系统修复", "技术组C", 0, 5, "#15803D", "异常回流修复 -> 回归截图"),
        ("验收材料", "PMO+区县", 2, 6, "#F59E0B", "模板统一 -> 附件补齐"),
        ("培训上线", "运营组D", 4, 7, "#7C3AED", "操作培训 -> 使用反馈"),
    ]
    for idx, (lane, owner, start, end, color, note) in enumerate(lanes):
        y = y0 + 62 + idx * lane_h
        parts.append(_text(x0 + 26, y + 26, lane, 18, theme["title"], 900))
        parts.append(_text(x0 + 26, y + 52, owner, 13, theme["muted"], 600))
        bar_x = x0 + 178 + start * 96
        bar_w = (end - start + 1) * 78
        parts.append(f'<rect x="{bar_x}" y="{y + 12}" width="{bar_w}" height="30" rx="15" fill="{color}"/>')
        parts.append(_text(bar_x + 18, y + 34, note, 13, "#FFFFFF", 800))
        _project_line(parts, x0 + 20, y + lane_h - 4, x0 + lane_w - 20, y + lane_h - 4, theme["border"], 1)
    parts.append(_rect(1156, 270, 356, 430, "#FFF7ED", "#F59E0B", 18))
    parts.append(_text(1184, 318, "资源与依赖", 21, "#B45309", 900))
    parts.extend(_lines(1184, 370, [
        "PMO：锁定区县联系人",
        "业务：确认三类指标口径",
        "技术：每日关闭截图入库",
        "运营：补齐培训签到表",
        "项目经理：6/14 形成提交包",
    ], 15, theme["body"], 40, 700))
    parts.append(_rect(88, 724, 1424, 50, "#EAF3FF", "#B8D8FF", 16))
    parts.append(_text(118, 756, "计划表达要点：时间轴不是装饰，必须能看出并行关系、责任人、交付物和检查点。", 16, theme["title"], 800))


def _render_project_issue_log(parts: list[str], theme: dict[str, str]) -> None:
    for idx, (label, value, note, tone) in enumerate([
        ("红色阻塞", "2", "必须升级", "red"),
        ("待关闭问题", "3", "日清跟踪", "amber"),
        ("需补证据", "4", "入证据包", "blue"),
        ("本周动作", "6", "责任到人", "green"),
    ]):
        x = 88 + idx * 244
        color = theme["warning"] if tone == "red" else "#B45309" if tone == "amber" else theme["accent"] if tone == "blue" else "#15803D"
        parts.append(_rect(x, 244, 218, 82, theme["surface"], theme["border"], 14))
        parts.append(_text(x + 20, 274, label, 13, theme["muted"], 600))
        parts.append(_text(x + 20, 308, value, 25, color, 900))
        parts.append(_text(x + 78, 307, note, 12, theme["body"], 700))

    parts.append(_rect(1110, 244, 402, 82, "#003D79", "#003D79", 14))
    parts.append(_text(1138, 276, "本页结论", 14, "#EAF3FF", 800))
    parts.append(_text(1138, 306, "问题不是罗列事项，而是推动跨部门闭环的证据台账。", 13, "#FFFFFF", 900))

    x, y = 88, 350
    parts.append(_rect(x, y, 970, 366, theme["surface"], theme["border"], 16))
    headers = [("编号", 116), ("问题", 184), ("来源/证据", 336), ("影响", 536), ("Owner", 704), ("时限", 812), ("状态", 906)]
    for head, hx in headers:
        parts.append(_text(hx, y + 42, head, 13, theme["accent"], 900))
    rows = [
        ("R1", "指标口径差异", "业务处室反馈单", "验收材料一致性", "业务A", "6/10", "红"),
        ("R2", "驻场排期冲突", "PMO排期表", "区县验收窗口", "PMO B", "6/11", "红"),
        ("I3", "异常回流失败", "联调问题单#27", "稳定性说明", "技术C", "每日", "黄"),
        ("I4", "培训未覆盖", "运营计划", "上线使用率", "运营D", "6/13", "蓝"),
        ("E5", "验收截图缺失", "证据包目录", "提交包完整性", "项目D", "6/14", "蓝"),
        ("A6", "责任边界不清", "会议纪要待补", "跨部门扯皮", "PMO B", "6/12", "黄"),
    ]
    for idx, row in enumerate(rows):
        row_y = y + 82 + idx * 46
        _project_line(parts, x + 18, row_y - 26, x + 946, row_y - 26, theme["border"], 1)
        for value, hx in zip(row, [116, 184, 336, 536, 704, 812, 906], strict=True):
            color = theme["warning"] if value == "红" else "#B45309" if value == "黄" else theme["accent"] if value == "蓝" else theme["body"]
            parts.append(_text(hx, row_y, value, 12, color, 800 if hx in {116, 184, 906} else 500))

    right_x = 1090
    parts.append(_rect(right_x, 350, 422, 366, "#FFF7ED", "#F59E0B", 16))
    parts.append(_text(right_x + 26, 390, "证据链与闭环动作", 20, "#B45309", 900))
    evidence = [
        ("1 来源", "问题单#27 / 业务反馈单 / PMO排期表", "每项阻塞必须能追到文件或截图"),
        ("2 判断", "影响验收材料、驻场窗口、稳定性说明", "写清为什么需要升级，不写泛风险"),
        ("3 动作", "口径确认、排期协调、日清回归、补证据", "动作必须绑定Owner和时限"),
        ("4 验收", "关闭截图入库、口径说明签字、提交包复核", "用验收标准替代“持续跟进”"),
    ]
    for idx, (head, body, note) in enumerate(evidence):
        ey = 420 + idx * 68
        parts.append(_rect(right_x + 24, ey, 374, 50, "#FFFFFF", "#F6C77A", 12))
        parts.append(_text(right_x + 42, ey + 20, head, 13, "#B45309", 900))
        parts.append(_text(right_x + 118, ey + 20, body, 12, theme["title"], 800))
        parts.append(_text(right_x + 42, ey + 40, note, 11, theme["body"], 600))

    actions = [
        ("红色阻塞", "业务A", "周三", "三类指标口径说明签字", "red"),
        ("红色阻塞", "PMO B", "周四", "区县驻场排期锁定", "red"),
        ("黄色跟踪", "技术C", "日清", "18点截图入证据包", "amber"),
        ("蓝色归档", "项目D", "周五", "提交包完成二次复核", "blue"),
    ]
    for idx, (level, owner, due, action, tone) in enumerate(actions):
        ax = 88 + idx * 356
        parts.append(_rect(ax, 736, 320, 52, "#EAF3FF", "#B8D8FF", 14))
        color = theme["warning"] if tone == "red" else "#B45309" if tone == "amber" else theme["accent"]
        parts.append(f'<circle cx="{ax + 24}" cy="753" r="7" fill="{color}"/>')
        parts.append(_text(ax + 40, 758, level, 13, color, 900))
        parts.append(_text(ax + 138, 758, f"{owner}｜{due}", 12, theme["accent"], 900))
        parts.append(_text(ax + 18, 778, action, 12, theme["title"], 700))
    parts.append(_rect(88, 800, 1424, 34, "#003D79", "#003D79", 14))
    parts.append(_text(118, 823, "Issue log 合同：每项阻塞必须有来源、影响、Owner、时限、状态、验收标准；缺来源时标“需补证据”，不能删掉问题。", 13, "#FFFFFF", 900))


def _render_project_actions(parts: list[str], theme: dict[str, str]) -> None:
    x, y = 88, 256
    parts.append(_rect(x, y, 1424, 450, theme["surface"], theme["border"], 16))
    headers = [("事项", 120), ("负责人", 360), ("完成时限", 550), ("交付物", 760), ("验收标准", 1045), ("状态", 1350)]
    for head, hx in headers:
        parts.append(_text(hx, y + 44, head, 15, theme["accent"], 900))
    rows = [
        ("统一指标口径", "业务处室A", "6月10日", "口径说明", "三类指标可直接引用", "红"),
        ("协调驻场排期", "PMO B", "6月11日", "驻场排期表", "区县联系人和供应商责任明确", "黄"),
        ("异常回流修复", "技术负责人C", "每日18点", "修复清单", "关闭截图入证据包", "蓝"),
        ("验收材料复核", "项目经理D", "6月14日", "提交包", "版本号/截图/纪要齐全", "蓝"),
        ("上线培训补课", "运营负责人D", "6月13日", "签到+FAQ", "两家单位完成演练", "绿"),
    ]
    for idx, row in enumerate(rows):
        row_y = y + 92 + idx * 62
        _project_line(parts, x + 22, row_y - 34, x + 1390, row_y - 34, theme["border"], 1)
        tone = {"红": "red", "黄": "amber", "蓝": "blue", "绿": "green"}[row[-1]]
        for value, hx in zip(row[:-1], [120, 360, 550, 760, 1045], strict=True):
            parts.append(_text(hx, row_y, value, 14, theme["title"] if hx == 120 else theme["body"], 800 if hx == 120 else 500))
        _project_badge(parts, 1330, row_y - 26, row[-1], theme, tone)
    parts.append(_rect(88, 728, 1424, 54, "#EAF3FF", "#B8D8FF", 16))
    parts.append(_text(118, 762, "收口规则：行动页不能只写“推进/协调/跟进”，必须写交付物和验收标准，便于下一轮复盘。", 16, theme["title"], 800))


def _render_project_appendix(parts: list[str], theme: dict[str, str], deck: dict[str, Any]) -> None:
    materials = deck.get("source_materials", [])
    for idx, material in enumerate(materials):
        x = 88 + (idx % 2) * 716
        y = 250 + (idx // 2) * 214
        parts.append(_rect(x, y, 666, 168, theme["surface"], theme["border"], 18))
        _project_badge(parts, x + 26, y + 22, material["kind"], theme, "blue")
        parts.append(_text(x + 26, y + 76, material["display_name"], 22, theme["title"], 900))
        parts.append(_text(x + 26, y + 108, material["material_id"], 13, theme["muted"], 600))
        parts.append(_text(x + 26, y + 138, material["summary"], 14, theme["body"], 600))
    parts.append(_rect(88, 706, 1424, 76, "#FFF7ED", "#F59E0B", 16))
    parts.append(_text(118, 738, "附录使用方式", 16, "#B45309", 900))
    parts.append(_text(260, 738, "真实生成时先读文件树和素材 metadata，再把当前页引用的表格、截图、口径说明写入正文页证据槽。", 15, theme["title"], 800))
    parts.append(_text(260, 764, "示例路径：materials/index.md -> issue-list.xlsx -> pmo-schedule.xlsx -> acceptance-evidence-pack/", 14, theme["body"], 600))


def _render_project_report_svg(deck: dict[str, Any], page: dict[str, Any]) -> str:
    theme = THEMES[deck["theme"]]
    if page["layout"] in {"cover", "agenda"}:
        parts = _page_base(theme, page, deck)
        if page["layout"] == "cover":
            _render_cover(parts, theme, page)
        else:
            _render_agenda(parts, theme, page)
        _footer(parts, theme, deck, page)
        return "\n  ".join(parts) + "\n"

    parts = _project_page_base(theme, page)
    page_id = page["id"]
    if page_id == "03-section-progress":
        _render_project_section(parts, theme)
    elif page_id == "04-timeline":
        _render_project_timeline(parts, theme)
    elif page_id == "05-risk":
        _render_project_risk(parts, theme)
    elif page_id == "06-decision":
        _render_project_decision(parts, theme)
    elif page_id == "07-gantt":
        _render_project_gantt(parts, theme)
    elif page_id == "08-issue-log":
        _render_project_issue_log(parts, theme)
    elif page_id == "09-actions":
        _render_project_actions(parts, theme)
    elif page_id == "10-appendix":
        _render_project_appendix(parts, theme, deck)
    else:
        raise ValueError(f"未知项目汇报页: {page_id}")
    _project_footer(parts, theme, deck, page)
    return "\n  ".join(parts) + "\n"


def _annual_page_base(theme: dict[str, str], page: dict[str, Any]) -> list[str]:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{theme["bg"]}"/>')
    parts.append(_text(88, 24, "年度经营总结 / 经营复盘 / SVG-PPT 高密度示例", 15, theme["muted"], 600))
    parts.append(_text(88, 116, page["title"], 38, theme["title"], 900))
    parts.append(_text(88, 160, page["subtitle"], 18, theme["body"], 500))
    parts.append(_rect(88, 186, 1424, 42, "#EFF6FF", "#B8D8FF", 18))
    parts.append(_text(116, 213, "页面合同：年度总结必须同时写结果、差距、原因、证据口径和来年动作；缺数据时标缺口，不删问题。", 15, theme["title"], 700))
    return parts


def _annual_footer(parts: list[str], theme: dict[str, str], deck: dict[str, Any], page: dict[str, Any]) -> None:
    parts.append(_text(88, 846, "素材：年度财务月报 / CRM 商机与合同清单 / 交付 PMO 台账 / 客户成功复购台账", 12, theme["footer"], 500))
    parts.append(_text(1240, 846, f'{deck["scenario"]} / {page["id"]}', 12, theme["footer"], 500))
    parts.append("</svg>")


def _annual_metric(
    parts: list[str],
    x: int,
    label: str,
    value: str,
    note: str,
    source: str,
    tone: str,
    pct: int,
    theme: dict[str, str],
) -> None:
    color = theme["warning"] if tone == "red" else "#B45309" if tone == "amber" else theme["accent"]
    fill = "#FEF2F2" if tone == "red" else "#FFF7ED" if tone == "amber" else theme["surface"]
    parts.append(_rect(x, 248, 328, 122, fill, color if tone in {"red", "amber"} else theme["border"], 16))
    parts.append(_text(x + 24, 284, label, 15, theme["muted"], 700))
    parts.append(_text(x + 24, 326, value, 31, color if tone in {"red", "amber"} else theme["title"], 900))
    parts.append(_text(x + 148, 308, note, 13, theme["body"], 700))
    parts.append(_text(x + 148, 334, source, 11, theme["muted"], 500))
    parts.append(f'<rect x="{x + 148}" y="348" width="142" height="10" rx="5" fill="{theme["border"]}"/>')
    parts.append(f'<rect x="{x + 148}" y="348" width="{max(20, int(pct * 1.35))}" height="10" rx="5" fill="{color}"/>')


def _annual_compact_tiles(
    parts: list[str],
    theme: dict[str, str],
    y: int,
    entries: list[tuple[str, str, str]],
    *,
    fill: str = "#EFF6FF",
    stroke: str = "#B8D8FF",
) -> None:
    """年度总结示例反复使用的证据/动作承载条，避免退回空卡模板。"""
    for idx, (tag, head, note) in enumerate(entries):
        x = 88 + idx * 356
        parts.append(_rect(x, y, 320, 58, fill, stroke, 14))
        parts.append(_text(x + 18, y + 23, tag, 12, theme["accent"], 900))
        parts.append(_text(x + 76, y + 23, head, 12, theme["title"], 800))
        parts.append(_text(x + 18, y + 46, note, 11, theme["body"], 600))


def _annual_mini_badge(parts: list[str], x: int, y: int, text: str, color: str) -> None:
    parts.append(_rect(x, y, 104, 24, "#FFFFFF", color, 12))
    parts.append(_text(x + 14, y + 17, text, 10, color, 900))


def _render_annual_cover(deck: dict[str, Any], page: dict[str, Any]) -> str:
    theme = THEMES[deck["theme"]]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']
    parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{theme["bg"]}"/>')
    parts.append(_text(88, 36, "年度经营总结 / 中国区业务中心 / SVG-PPT 高密度示例", 15, theme["muted"], 600))
    parts.append(_text(88, 126, page["title"], 46, theme["title"], 900))
    parts.append(_text(88, 184, page["subtitle"], 20, theme["body"], 500))
    parts.append(_rect(88, 230, 610, 364, "#0F3B73", "#0F3B73", 22))
    parts.append(_text(126, 286, "汇报主判断", 24, "#FFFFFF", 900))
    parts.extend(_lines(126, 342, [
        "全年目标稳步达成，但增长质量仍需继续补强。",
        "重点行业和交付效率是主要贡献来源。",
        "复购贡献、毛利口径和客户分层仍是短板。",
        "来年重点不是继续喊增长，而是建立可复盘经营台账。",
    ], 17, "#EAF3FF", 42, 800))
    parts.append(_rect(126, 520, 430, 44, "#F59E0B", "#F59E0B", 22))
    parts.append(_text(154, 549, "年度结论：增长质量优于规模增速", 15, "#FFFFFF", 900))

    metrics = [
        ("结构", "重点行业", "收入占比提升", "来源：CRM合同清单"),
        ("效率", "交付周期", "持续压缩", "来源：PMO项目台账"),
        ("风险", "复购运营", "待闭环", "来源：客户成功台账"),
        ("口径", "经营数据", "需统一", "来源：财务月报"),
    ]
    for idx, (tag, head, body, source) in enumerate(metrics):
        x = 748 + (idx % 2) * 374
        y = 230 + (idx // 2) * 182
        tone = theme["warning"] if tag == "风险" else theme["accent"]
        fill = "#FEF2F2" if tag == "风险" else theme["surface"]
        parts.append(_rect(x, y, 330, 136, fill, tone if tag == "风险" else theme["border"], 18))
        parts.append(_text(x + 24, y + 38, tag, 15, tone, 900))
        parts.append(_text(x + 24, y + 76, head, 24, theme["title"], 900))
        parts.append(_text(x + 24, y + 106, body, 16, theme["body"], 700))
        parts.append(_text(x + 24, y + 128, source, 11, theme["muted"], 600))

    parts.append(_rect(88, 636, 1424, 76, "#EFF6FF", "#B8D8FF", 16))
    parts.append(_text(118, 666, "本 deck 写法", 16, theme["accent"], 900))
    parts.append(_text(260, 666, "封面即给经营判断，后续每页都必须回到结果、差距、原因、证据口径和行动闭环。", 15, theme["title"], 800))
    parts.append(_text(260, 694, "不要把年度总结写成荣誉清单；缺数据时标“待补口径 + Owner”，不能删除风险。", 14, theme["body"], 700))
    _annual_compact_tiles(
        parts,
        theme,
        736,
        [
            ("证据", "年度财务月报", "收入/毛利/回款先入页"),
            ("来源", "CRM合同清单", "行业/区域/客户可追溯"),
            ("Owner", "交付PMO+客成", "周期/复购缺口责任到人"),
            ("复盘", "月度经营会", "下月继续检查同一口径"),
        ],
    )
    _annual_footer(parts, theme, deck, page)
    return "\n  ".join(parts) + "\n"


def _render_annual_agenda(deck: dict[str, Any], page: dict[str, Any]) -> str:
    theme = THEMES[deck["theme"]]
    parts = _annual_page_base(theme, page)
    parts.append('<g id="annual-agenda-path">')
    chapters = [
        ("01", "年度经营结果", "收入达成、结构贡献、交付效率、复购缺口", "回答：全年做成了什么"),
        ("02", "差距与原因诊断", "效率、协同、客户运营、数据口径", "回答：问题卡在哪里"),
        ("03", "来年重点抓手", "行业打法、区域复制、复购台账、经营口径", "回答：下年度抓什么"),
        ("04", "责任闭环", "Owner、KPI、风险、复盘节奏", "回答：谁负责、怎么验收"),
    ]
    for idx, (num, head, body, answer) in enumerate(chapters):
        y = 258 + idx * 110
        parts.append(_rect(88, y, 1000, 82, theme["surface"], theme["border"], 16))
        parts.append(_text(122, y + 52, num, 26, theme["accent"], 900))
        parts.append(_text(216, y + 34, head, 21, theme["title"], 900))
        parts.append(_text(216, y + 64, body, 13, theme["body"], 600))
        parts.append(_rect(744, y + 24, 214, 34, "#EFF6FF", "#B8D8FF", 17))
        parts.append(_text(760, y + 47, answer, 12, theme["accent"], 900))
        parts.append(_text(986, y + 47, "输出到后续页", 11, theme["muted"], 700))
    parts.append("</g>")

    parts.append('<g id="annual-agenda-readout">')
    parts.append(_rect(1130, 258, 382, 412, "#0F3B73", "#0F3B73", 18))
    parts.append(_text(1160, 302, "领导阅读路径", 22, "#FFFFFF", 900))
    parts.extend(_lines(1160, 354, [
        "先看结论：是否达成、质量如何。",
        "再看证据：哪些表证明该判断。",
        "追问缺口：复购、毛利、客户分层。",
        "落到行动：Owner、时限、验收标准。",
        "进入节奏：月度经营会持续追踪。",
    ], 15, "#EAF3FF", 42, 800))
    for idx, (tag, body) in enumerate([
        ("财务", "收入/毛利/回款"),
        ("CRM", "行业/客户/合同"),
        ("PMO", "周期/返工/验收"),
    ]):
        y = 522 + idx * 30
        parts.append(_rect(1160, y, 302, 24, "#FFFFFF", "#B8D8FF", 10))
        parts.append(_text(1174, y + 17, tag, 11, theme["accent"], 900))
        parts.append(_text(1234, y + 17, body, 10, theme["title"], 700))
    parts.append(_rect(1160, 604, 302, 42, "#F59E0B", "#F59E0B", 20))
    parts.append(_text(1182, 632, "目录不是导航，而是经营问题链", 13, "#FFFFFF", 900))
    parts.append("</g>")
    _annual_compact_tiles(
        parts,
        theme,
        716,
        [
            ("结果页", "输出指标判断", "财务+CRM证据"),
            ("诊断页", "输出差距矩阵", "Owner+影响等级"),
            ("计划页", "输出季度抓手", "交付物+验收口径"),
            ("闭环页", "输出行动台账", "月度复盘节奏"),
        ],
    )
    _annual_footer(parts, theme, deck, page)
    return "\n  ".join(parts) + "\n"


def _render_annual_section(parts: list[str], theme: dict[str, str]) -> None:
    parts.append('<g id="annual-section-question">')
    parts.append(_rect(88, 250, 520, 420, "#0F3B73", "#0F3B73", 24))
    parts.append(_text(126, 306, "本章节回答什么", 24, "#FFFFFF", 900))
    parts.extend(_lines(126, 362, [
        "1. 年度目标是否真实达成？",
        "2. 增长质量是否可持续？",
        "3. 哪些短板会影响来年经营？",
        "4. 哪些口径还必须补证据？",
    ], 18, "#EAF3FF", 44, 800))
    parts.append(_rect(126, 586, 390, 44, "#F59E0B", "#F59E0B", 22))
    parts.append(_text(150, 614, "章节结论：达成目标，但质量仍需补强", 15, "#FFFFFF", 900))
    _annual_mini_badge(parts, 126, 642, "财务口径", theme["accent"])
    _annual_mini_badge(parts, 244, 642, "CRM来源", theme["accent"])
    _annual_mini_badge(parts, 362, 642, "PMO证据", theme["accent"])
    _annual_mini_badge(parts, 480, 642, "复购缺口", theme["warning"])
    parts.append("</g>")

    cards = [
        ("指标证据", "收入达成 102，重点行业占比 58", "来源：年度财务月报、CRM合同清单", "Owner：财经+销售", "动作：按行业拆毛利"),
        ("质量证据", "交付周期改善，但复购贡献仍待补", "来源：PMO台账、客户成功台账", "Owner：PMO+客成", "动作：补返工和续约"),
        ("缺口证据", "毛利、复购率、续约金额仍需统一口径", "动作：财经+运营进入月度经营会", "Owner：运营负责人", "动作：统一月会字段"),
    ]
    parts.append('<g id="annual-section-evidence">')
    for idx, (head, body, note, owner, action) in enumerate(cards):
        y = 258 + idx * 126
        parts.append(_rect(660, y, 852, 98, theme["surface"], theme["border"], 16))
        parts.append(_text(694, y + 36, head, 20, theme["accent"], 900))
        parts.append(_text(694, y + 68, body, 16, theme["title"], 800))
        parts.append(_text(1050, y + 68, note, 13, theme["body"], 600))
        parts.append(_text(694, y + 90, "字段：观点 / 证据 / 解释 / 缺口 / 行动", 11, theme["muted"], 600))
        parts.append(_text(964, y + 90, owner, 11, theme["accent"], 800))
        parts.append(_text(1190, y + 90, action, 11, theme["warning"] if idx == 2 else theme["body"], 800))
    parts.append(_rect(660, 664, 852, 58, "#EFF6FF", "#B8D8FF", 16))
    parts.append(_text(694, 700, "章节输出：后续页必须从“指标结果”进入“差距诊断”，不能只展示成绩。", 15, theme["title"], 800))
    parts.append("</g>")
    parts.append('<g id="annual-section-source-strip">')
    _annual_compact_tiles(
        parts,
        theme,
        738,
        [
            ("结果", "财务月报", "收入达成/毛利/回款"),
            ("结构", "CRM合同清单", "行业贡献/客户名单"),
            ("效率", "PMO项目台账", "周期/返工/验收"),
            ("复购", "客户成功台账", "复购口径仍待补"),
        ],
    )
    parts.append("</g>")


def _render_annual_gap_matrix(parts: list[str], theme: dict[str, str]) -> None:
    parts.append('<g id="annual-gap-metrics">')
    metrics = [
        ("优先整改", "2", "标杆复制/客户分层"),
        ("机制优化", "2", "周报口径/跨部门排期"),
        ("关键Owner", "4", "销售/客成/运营/PMO"),
        ("复盘频率", "月度", "进入经营会"),
    ]
    for idx, (label, value, note) in enumerate(metrics):
        x = 88 + idx * 356
        parts.append(_rect(x, 248, 320, 74, theme["surface"], theme["border"], 14))
        parts.append(_text(x + 20, 276, label, 13, theme["muted"], 700))
        parts.append(_text(x + 20, 306, value, 23, theme["accent"], 900))
        parts.append(_text(x + 110, 304, note, 12, theme["body"], 700))
    parts.append("</g>")

    positions = [
        (88, 352, "高影响/易推进", "标杆项目复制", "沉淀行业打法包", "来源：CRM合同清单", "销售战区", "blue"),
        (612, 352, "高影响/难推进", "客户分层运营", "补A/B/C客户台账", "来源：客户成功台账", "客户成功", "red"),
        (88, 564, "低影响/易推进", "周报口径统一", "统一收入/毛利/回款字段", "来源：经营会纪要", "运营", "blue"),
        (612, 564, "低影响/难推进", "跨部门排期", "建立月度经营协调会", "来源：PMO项目台账", "PMO", "amber"),
    ]
    parts.append('<g id="annual-gap-matrix">')
    for x, y, tag, head, action, source, owner, tone in positions:
        color = theme["warning"] if tone == "red" else "#B45309" if tone == "amber" else theme["accent"]
        fill = "#FEF2F2" if tone == "red" else "#FFF7ED" if tone == "amber" else theme["surface"]
        parts.append(_rect(x, y, 470, 162, fill, color if tone != "blue" else theme["border"], 16))
        parts.append(_text(x + 26, y + 34, tag, 13, color, 900))
        parts.append(_text(x + 26, y + 72, head, 22, theme["title"], 900))
        parts.append(_text(x + 26, y + 104, action, 14, theme["body"], 700))
        parts.append(_text(x + 26, y + 132, source, 12, theme["muted"], 600))
        parts.append(_text(x + 344, y + 132, owner, 12, color, 900))
        parts.append(_text(x + 26, y + 152, "检查口径：影响等级 + 推进难度 + 复盘节奏", 11, theme["body"], 600))
        _annual_mini_badge(parts, x + 248, y + 20, "Owner", color)
        _annual_mini_badge(parts, x + 360, y + 20, "验收", color)
    parts.append("</g>")

    parts.append('<g id="annual-gap-principle">')
    parts.append(_rect(1130, 352, 382, 374, "#0F3B73", "#0F3B73", 18))
    parts.append(_text(1160, 394, "诊断页写法", 21, "#FFFFFF", 900))
    parts.extend(_lines(1160, 444, [
        "1. 每个问题必须有影响等级。",
        "2. 每个差距必须写来源或口径。",
        "3. 每个动作必须绑定Owner。",
        "4. 不写“继续加强、持续推进”。",
        "5. 低优先问题也要说明复盘节奏。",
    ], 14, "#EAF3FF", 38, 800))
    parts.append(_rect(1160, 660, 302, 40, "#F59E0B", "#F59E0B", 18))
    parts.append(_text(1184, 686, "矩阵不是装饰，是整改优先级", 13, "#FFFFFF", 900))
    for idx, (label, value) in enumerate([
        ("本周输出", "整改台账"),
        ("月度检查", "经营会"),
        ("失败信号", "口径缺失"),
    ]):
        y = 706 + idx * 26
        parts.append(_text(1160, y, label, 10, "#EAF3FF", 800))
        parts.append(_text(1254, y, value, 10, "#FFFFFF", 900))
    parts.append("</g>")
    parts.append('<g id="annual-gap-ledger">')
    ledger = [
        ("整改项", "Owner", "本月动作", "验收标准"),
        ("客户分层", "客成", "补A/B/C台账", "续约金额入表"),
        ("标杆复制", "销售", "三类打法包", "区域可复用"),
        ("数据口径", "运营", "字段统一", "月会同表"),
    ]
    parts.append(_rect(88, 742, 1010, 78, "#EFF6FF", "#B8D8FF", 14))
    for row_idx, row in enumerate(ledger):
        y = 762 + row_idx * 18
        for value, x in zip(row, [116, 300, 520, 780], strict=True):
            parts.append(_text(x, y, value, 10 if row_idx else 11, theme["accent"] if row_idx == 0 else theme["title"], 900 if row_idx == 0 else 700))
    parts.append(_rect(1130, 742, 382, 78, "#FFF7ED", "#F59E0B", 14))
    parts.append(_text(1156, 770, "复盘节奏", 13, "#B45309", 900))
    parts.append(_text(1250, 770, "月度经营会 / 季度专题复盘", 11, theme["title"], 800))
    parts.append(_text(1156, 798, "缺口处理", 13, "#B45309", 900))
    parts.append(_text(1250, 798, "待补数据必须写Owner，不许删", 11, theme["title"], 800))
    parts.append(_rect(1160, 812, 148, 20, "#FFFFFF", "#F59E0B", 10))
    parts.append(_text(1172, 826, "检查标准入台账", 9, "#B45309", 900))
    parts.append(_rect(1320, 812, 148, 20, "#FFFFFF", "#F59E0B", 10))
    parts.append(_text(1332, 826, "下月复盘同口径", 9, "#B45309", 900))
    parts.append("</g>")


def _render_annual_cause(parts: list[str], theme: dict[str, str]) -> None:
    parts.append('<g id="annual-cause-claim">')
    parts.append(_rect(88, 250, 500, 340, "#0F3B73", "#0F3B73", 22))
    parts.append(_text(126, 306, "核心判断", 24, "#FFFFFF", 900))
    parts.extend(_lines(126, 362, [
        "收入增长不是销售单点冲刺，",
        "而是行业选择、交付机制、",
        "复购运营三类机制共同作用。",
        "短板也来自这三类机制没有闭环。",
    ], 17, "#EAF3FF", 38, 800))
    parts.append(_rect(126, 528, 348, 38, "#F59E0B", "#F59E0B", 19))
    parts.append(_text(150, 553, "结论：机制解释优先于功劳罗列", 14, "#FFFFFF", 900))
    parts.append(_text(150, 582, "素材口径：CRM + PMO + 客成三表共同解释", 11, "#EAF3FF", 800))
    parts.append("</g>")

    reasons = [
        ("行业选择", "重点行业需求更确定", "预算明确、客户集中、案例可复制", "证据：CRM合同清单", "销售战区", "解释：结构优化来自行业深耕"),
        ("交付机制", "联合评审降低返工", "售前/交付/运营同评审，风险进周会", "证据：PMO项目台账", "交付PMO", "动作：把里程碑看板固化"),
        ("复购运营", "客户价值挖掘不足", "分层策略缺动作闭环，续约金额待补", "证据：客户成功台账", "客户成功", "风险：复购口径仍待补"),
    ]
    parts.append('<g id="annual-cause-evidence">')
    for idx, (head, body, explain, source, owner, closure) in enumerate(reasons):
        y = 250 + idx * 132
        color = theme["warning"] if idx == 2 else theme["accent"]
        # 汇报类卡片禁装饰性左缘色条（contract-svg-self-qa），语义色由标题/Owner 文字承担。
        parts.append(_rect(650, y, 862, 102, theme["surface"], theme["border"], 16))
        parts.append(_text(684, y + 34, head, 20, color, 900))
        parts.append(_text(840, y + 34, body, 17, theme["title"], 900))
        parts.append(_text(684, y + 66, explain, 13, theme["body"], 700))
        parts.append(_text(684, y + 90, source, 12, theme["muted"], 600))
        parts.append(_text(1260, y + 90, owner, 12, color, 900))
        parts.append(_text(1038, y + 66, closure, 12, color, 800))
        _annual_mini_badge(parts, 1378, y + 18, "Owner", color)
        _annual_mini_badge(parts, 1378, y + 52, "证据", color)
    parts.append("</g>")

    parts.append('<g id="annual-cause-closure">')
    _annual_compact_tiles(
        parts,
        theme,
        610,
        [
            ("原因", "行业选择", "用CRM合同清单证明"),
            ("原因", "交付机制", "用PMO台账解释效率"),
            ("风险", "复购运营", "用客户成功台账补口径"),
            ("承接", "来年抓手", "转成季度动作和Owner"),
        ],
    )
    for idx, label in enumerate(["解释结果", "解释差距", "转成动作", "进入复盘"]):
        parts.append(_text(148 + idx * 356, 690, label, 10, theme["accent"], 900))
    parts.append(_rect(88, 704, 1424, 58, "#EFF6FF", "#B8D8FF", 16))
    parts.append(_text(118, 738, "原因页合同：原因必须能解释结果和差距，并且能转成来年抓手；不能写“市场环境、团队努力”这类不可执行归因。", 15, theme["title"], 800))
    parts.append(_rect(88, 792, 1424, 34, "#0F3B73", "#0F3B73", 14))
    parts.append(_text(118, 815, "下一页承接：把三类机制拆成 Q1-Q4 行动和验收口径。", 13, "#FFFFFF", 900))
    parts.append("</g>")


def _render_annual_roadmap(parts: list[str], theme: dict[str, str]) -> None:
    parts.append('<g id="annual-roadmap-lanes">')
    quarters = [
        ("Q1", "建立行业打法包", "完成客户分层；输出标杆案例库", "市场+销售", "打法包可复用"),
        ("Q2", "复制区域样板", "华东打法复制到华中；周度跟踪转化", "销售战区", "三地样板复用"),
        ("Q3", "提升交付效率", "标准化里程碑；异常事项48h升级", "交付PMO", "周期/返工率入表"),
        ("Q4", "复盘与续约", "复购台账收口；明确来年预算池", "客户成功", "续约金额入表"),
    ]
    for idx, (q, head, action, owner, standard) in enumerate(quarters):
        x = 88 + idx * 356
        parts.append(_rect(x, 270, 320, 392, theme["surface"], theme["border"], 18))
        parts.append(_rect(x + 20, 294, 82, 38, theme["accent"], theme["accent"], 19))
        parts.append(_text(x + 61, 320, q, 16, "#FFFFFF", 900, "middle"))
        parts.append(_text(x + 24, 372, head, 21, theme["title"], 900))
        parts.append(_text(x + 24, 416, "关键动作", 13, theme["accent"], 900))
        parts.extend(_lines(x + 24, 448, action.split("；"), 13, theme["body"], 28, 700))
        parts.append(_text(x + 24, 542, "Owner", 13, theme["accent"], 900))
        parts.append(_text(x + 94, 542, owner, 13, theme["title"], 800))
        parts.append(_text(x + 24, 586, "验收口径", 13, theme["accent"], 900))
        parts.append(_text(x + 104, 586, standard, 12, theme["body"], 700))
        parts.append(_rect(x + 24, 612, 236, 28, "#EFF6FF", "#B8D8FF", 14))
        parts.append(_text(x + 42, 631, "进入月度经营会复盘", 11, theme["accent"], 900))
        parts.append(_text(x + 24, 658, "风险缺口", 11, theme["warning"], 900))
        parts.append(_text(x + 94, 658, "数据/责任/预算需补齐", 10, theme["body"], 700))
        _annual_mini_badge(parts, x + 184, 294, "来源", theme["accent"])
        _annual_mini_badge(parts, x + 184, 324, "Owner", theme["accent"])
    parts.append("</g>")
    parts.append(_rect(88, 704, 1424, 58, "#FFF7ED", "#F59E0B", 16))
    parts.append(_text(118, 738, "路线图合同：每个季度必须写动作、Owner、交付物和验收口径；时间轴不是装饰，必须能被下次复盘检查。", 15, theme["title"], 800))
    for idx, (tag, head, note) in enumerate([
        ("输入", "上一年差距矩阵", "客户分层/交付/口径"),
        ("输出", "季度交付物", "打法包/看板/续约池"),
        ("Owner", "部门责任", "市场/销售/PMO/客成"),
        ("检查", "经营会复盘", "同一口径持续追踪"),
    ]):
        x = 166 + idx * 324
        parts.append(_text(x, 760, tag, 10, "#B45309", 900))
        parts.append(_text(x + 48, 760, head, 10, theme["title"], 800))
        parts.append(_text(x + 48, 778, note, 9, theme["body"], 600))
    parts.append(_rect(88, 792, 1424, 34, "#0F3B73", "#0F3B73", 14))
    parts.append(_text(118, 815, "来年抓手必须承接前页原因：行业选择、交付机制、复购运营、经营数据口径。", 13, "#FFFFFF", 900))


def _render_annual_dashboard(parts: list[str], theme: dict[str, str]) -> None:
    parts.append('<g id="annual-metrics-panel">')
    metrics = [
        ("收入达成", "102", "达成率", "年度财务月报", "blue", 82),
        ("重点行业", "58", "收入占比", "CRM合同清单", "blue", 70),
        ("交付效率", "+18", "周期改善", "PMO项目台账", "blue", 62),
        ("复购贡献", "待补", "口径缺口", "客户成功台账", "red", 36),
    ]
    for idx, metric in enumerate(metrics):
        _annual_metric(parts, 88 + idx * 356, *metric, theme)
    parts.append("</g>")

    parts.append('<g id="annual-leader-claim">')
    parts.append(_rect(88, 402, 438, 286, "#0F3B73", "#0F3B73", 18))
    parts.append(_text(120, 444, "先给经营判断", 22, "#FFFFFF", 900))
    parts.extend(_lines(120, 492, [
        "全年目标稳步达成，但增长质量仍有结构性短板。",
        "重点行业贡献提升，说明打法复制有效。",
        "复购贡献缺口暴露客户成功台账不足。",
        "来年必须把复购从口号变成经营责任。",
    ], 16, "#EAF3FF", 36, 700))
    parts.append(_rect(120, 638, 340, 36, "#F59E0B", "#F59E0B", 18))
    parts.append(_text(146, 662, "一句话收口：增长质量优于规模增速", 14, "#FFFFFF", 900))
    parts.append("</g>")

    parts.append('<g id="annual-trend-chart">')
    parts.append(_rect(558, 402, 478, 286, theme["surface"], theme["border"], 16))
    parts.append(_text(586, 440, "月度收入与质量趋势", 22, theme["title"], 900))
    values = [68, 72, 75, 81, 86, 89]
    labels = ["7月", "8月", "9月", "10月", "11月", "12月"]
    for idx, val in enumerate(values):
        bx = 600 + idx * 66
        bh = int(val * 1.35)
        parts.append(f'<rect x="{bx}" y="{618 - bh}" width="34" height="{bh}" rx="8" fill="{theme["accent"]}"/>')
        parts.append(_text(bx - 2, 642, labels[idx], 11, theme["muted"], 600))
        parts.append(_text(bx - 2, 602 - bh, str(val), 11, theme["title"], 800))
    parts.append(_rect(850, 480, 154, 42, "#EFF6FF", "#B8D8FF", 14))
    parts.append(_text(868, 507, "结构改善>短期冲量", 12, theme["accent"], 900))
    parts.append(_rect(850, 544, 154, 42, "#FEF2F2", "#FCA5A5", 14))
    parts.append(_text(868, 571, "复购口径仍待补", 12, theme["warning"], 900))
    parts.append("</g>")

    parts.append('<g id="annual-gap-and-actions">')
    parts.append(_rect(1068, 402, 444, 286, "#FFF7ED", "#F59E0B", 16))
    parts.append(_text(1096, 440, "差距转行动", 22, "#B45309", 900))
    actions = [
        ("贡献", "行业深耕带来高毛利项目", "沉淀三类行业打法包"),
        ("差距", "复购运营还未责任到人", "补 A/B/C 客户分层台账"),
        ("原因", "数据口径跨部门不统一", "收入/毛利/回款进入月会"),
        ("风险", "续约金额和复购率待补", "客户成功部周度拉通"),
    ]
    for idx, (tag, body, action) in enumerate(actions):
        y = 464 + idx * 48
        parts.append(_text(1096, y, tag, 13, "#B45309", 900))
        parts.append(_text(1160, y, body, 12, theme["title"], 800))
        parts.append(_text(1160, y + 20, action, 11, theme["body"], 600))
    parts.append("</g>")

    parts.append('<g id="annual-source-bar">')
    sources = [
        ("财务", "年度财务月报", "收入/毛利/回款"),
        ("客户", "CRM合同清单", "重点行业/客户名单"),
        ("交付", "PMO项目台账", "周期/返工/验收"),
        ("复购", "客户成功台账", "续约/复购/风险"),
    ]
    for idx, (tag, head, body) in enumerate(sources):
        x = 88 + idx * 356
        parts.append(_rect(x, 720, 320, 58, "#EFF6FF", "#B8D8FF", 14))
        parts.append(_text(x + 18, 744, f"{tag}｜{head}", 13, theme["accent"], 900))
        parts.append(_text(x + 18, 766, body, 12, theme["title"], 700))
    parts.append(_rect(88, 792, 1424, 36, "#0F3B73", "#0F3B73", 14))
    parts.append(_text(118, 816, "年度驾驶舱合同：不能只放指标卡，必须同时出现结论、趋势、差距、来源和下一步动作。", 13, "#FFFFFF", 900))
    parts.append("</g>")


def _render_annual_evidence_table(parts: list[str], theme: dict[str, str]) -> None:
    parts.append('<g id="annual-evidence-metrics">')
    summary = [
        ("已验证结论", "3", "收入、行业、效率"),
        ("待补口径", "4", "毛利、复购、返工、续约"),
        ("责任部门", "5", "财经/销售/交付/客成/运营"),
        ("复盘频率", "月度", "进入经营会"),
    ]
    for idx, (label, value, note) in enumerate(summary):
        x = 88 + idx * 356
        parts.append(_rect(x, 248, 320, 74, theme["surface"], theme["border"], 14))
        parts.append(_text(x + 20, 276, label, 13, theme["muted"], 700))
        parts.append(_text(x + 20, 306, value, 23, theme["accent"], 900))
        parts.append(_text(x + 116, 304, note, 12, theme["body"], 700))
    parts.append("</g>")

    x, y = 88, 352
    parts.append('<g id="annual-evidence-table">')
    parts.append(_rect(x, y, 1018, 354, theme["surface"], theme["border"], 16))
    headers = [("经营结论", 118), ("证据/口径", 306), ("解释", 568), ("缺口", 782), ("Owner", 958)]
    for head, hx in headers:
        parts.append(_text(hx, y + 40, head, 13, theme["accent"], 900))
    rows = [
        ("收入达成", "财务月报", "全年目标完成但结构需分解", "按行业收入/毛利", "财经"),
        ("重点行业提升", "CRM合同清单", "标杆复制开始形成贡献", "客户名单/区域对比", "销售"),
        ("交付效率改善", "PMO项目台账", "联合评审压缩返工周期", "平均周期/返工率", "交付"),
        ("复购贡献待补", "客户成功台账", "老客户价值挖掘不足", "复购率/续约金额", "客成"),
        ("数据口径不一", "经营会纪要", "跨部门复盘无法闭环", "统一字段和日期", "运营"),
    ]
    for idx, row in enumerate(rows):
        row_y = y + 84 + idx * 50
        _project_line(parts, x + 18, row_y - 28, x + 994, row_y - 28, theme["border"], 1)
        for value, hx in zip(row, [118, 306, 568, 782, 958], strict=True):
            color = theme["warning"] if value in {"复购率/续约金额", "统一字段和日期"} else theme["title"] if hx == 118 else theme["body"]
            parts.append(_text(hx, row_y, value, 12, color, 800 if hx in {118, 958} else 500))
    parts.append("</g>")

    parts.append('<g id="annual-proof-chain">')
    right_x = 1140
    parts.append(_rect(right_x, 352, 372, 354, "#FFF7ED", "#F59E0B", 16))
    parts.append(_text(right_x + 24, 392, "证据链写法", 20, "#B45309", 900))
    chain = [
        ("1 观点", "先写经营判断，不写名词标签"),
        ("2 证据", "每条结论绑定表格、截图或会议纪要"),
        ("3 解释", "说明数据为什么支撑该判断"),
        ("4 缺口", "缺数据时标待补口径和责任人"),
        ("5 动作", "进入来年计划或月度经营会"),
    ]
    for idx, (head, body) in enumerate(chain):
        cy = 430 + idx * 50
        parts.append(_rect(right_x + 22, cy, 326, 36, "#FFFFFF", "#F6C77A", 12))
        parts.append(_text(right_x + 38, cy + 23, head, 12, "#B45309", 900))
        parts.append(_text(right_x + 108, cy + 23, body, 11, theme["title"], 700))
    parts.append("</g>")

    parts.append('<g id="annual-evidence-closure">')
    closures = [
        ("数据", "按月/行业/区域补齐收入和毛利", "财经负责人"),
        ("客户", "输出 A/B/C 客户分层和续约池", "客户成功"),
        ("交付", "补平均周期和返工率趋势", "交付 PMO"),
        ("经营", "统一收入、毛利、回款口径", "运营负责人"),
    ]
    for idx, (tag, action, owner) in enumerate(closures):
        ax = 88 + idx * 356
        parts.append(_rect(ax, 730, 320, 54, "#EFF6FF", "#B8D8FF", 14))
        parts.append(_text(ax + 18, 752, tag, 13, theme["accent"], 900))
        parts.append(_text(ax + 70, 752, action, 11, theme["title"], 800))
        parts.append(_text(ax + 70, 774, owner, 11, theme["muted"], 600))
    parts.append(_rect(88, 800, 1424, 34, "#0F3B73", "#0F3B73", 14))
    parts.append(_text(118, 823, "证据表合同：每个经营结论必须有来源、解释、缺口和Owner；不能用“持续优化、加强管理”替代表格证据。", 13, "#FFFFFF", 900))
    parts.append("</g>")


def _render_annual_actions(parts: list[str], theme: dict[str, str]) -> None:
    parts.append('<g id="annual-action-metrics">')
    metrics = [
        ("来年抓手", "4", "行业/交付/复购/口径"),
        ("责任部门", "5", "跨部门闭环"),
        ("复盘节奏", "月度", "经营会跟踪"),
        ("风险缺口", "2", "复购和毛利口径"),
    ]
    for idx, (label, value, note) in enumerate(metrics):
        x = 88 + idx * 356
        parts.append(_rect(x, 248, 320, 74, theme["surface"], theme["border"], 14))
        parts.append(_text(x + 20, 276, label, 13, theme["muted"], 700))
        parts.append(_text(x + 20, 306, value, 23, theme["accent"], 900))
        parts.append(_text(x + 108, 304, note, 12, theme["body"], 700))
    parts.append("</g>")

    x, y = 88, 350
    parts.append('<g id="annual-action-ledger">')
    parts.append(_rect(x, y, 1020, 360, theme["surface"], theme["border"], 16))
    headers = [("事项", 118), ("责任人", 318), ("关键动作", 500), ("检查标准", 790), ("节奏", 990)]
    for head, hx in headers:
        parts.append(_text(hx, y + 42, head, 13, theme["accent"], 900))
    rows = [
        ("行业打法包", "市场+销售战区", "2月底完成模板，覆盖3个重点行业", "案例库可被区域复用", "月度"),
        ("交付效率专项", "交付PMO", "建立周期看板，异常48小时升级", "周期和返工率可追踪", "双周"),
        ("复购运营台账", "客户成功部", "完成A/B/C分层，季度复盘续约池", "复购率和续约金额入表", "季度"),
        ("经营数据口径", "财务运营", "统一收入、毛利、回款字段", "月会引用同一张表", "月度"),
        ("风险客户处理", "客成+销售", "TOP10风险客户挽回", "Owner和截止日明确", "周度"),
    ]
    for idx, row in enumerate(rows):
        row_y = y + 84 + idx * 50
        _project_line(parts, x + 18, row_y - 28, x + 996, row_y - 28, theme["border"], 1)
        for value, hx in zip(row, [118, 318, 500, 790, 990], strict=True):
            parts.append(_text(hx, row_y, value, 12, theme["title"] if hx == 118 else theme["body"], 800 if hx in {118, 990} else 500))
    parts.append("</g>")

    parts.append('<g id="annual-review-loop">')
    right_x = 1140
    parts.append(_rect(right_x, 350, 372, 360, "#0F3B73", "#0F3B73", 16))
    parts.append(_text(right_x + 24, 392, "复盘闭环", 20, "#FFFFFF", 900))
    loops = [
        ("输入", "财务/CRM/PMO/客成四张表"),
        ("判断", "收入质量、结构贡献、效率短板"),
        ("行动", "打法包、效率专项、复购台账"),
        ("验证", "下月经营会复盘指标和Owner"),
    ]
    for idx, (head, body) in enumerate(loops):
        ly = 434 + idx * 58
        parts.append(_rect(right_x + 24, ly, 324, 42, "#FFFFFF", "#B8D8FF", 12))
        parts.append(_text(right_x + 42, ly + 27, head, 13, theme["accent"], 900))
        parts.append(_text(right_x + 106, ly + 27, body, 12, theme["title"], 700))
    parts.append(_rect(right_x + 24, 674, 324, 38, "#F59E0B", "#F59E0B", 14))
    parts.append(_text(right_x + 44, 699, "禁止只写：持续推进、加强协同、重点关注", 12, "#FFFFFF", 900))
    parts.append("</g>")

    parts.append('<g id="annual-action-closure">')
    parts.append(_rect(88, 734, 1424, 50, "#EFF6FF", "#B8D8FF", 16))
    parts.append(_text(118, 766, "行动页收口：每项行动必须有责任人、交付物、检查标准和复盘节奏；缺指标时写“待补口径+Owner”，不能删掉风险。", 15, theme["title"], 800))
    parts.append(_rect(88, 800, 1424, 34, "#0F3B73", "#0F3B73", 14))
    parts.append(_text(118, 823, "年度总结不是荣誉清单，最后必须形成来年经营台账，让下一次复盘可追踪。", 13, "#FFFFFF", 900))
    parts.append("</g>")


def _render_annual_appendix(parts: list[str], theme: dict[str, str], deck: dict[str, Any]) -> None:
    materials = deck.get("source_materials", [])
    parts.append('<g id="annual-appendix-material-index">')
    parts.append(_rect(88, 250, 1424, 356, theme["surface"], theme["border"], 16))
    headers = [("素材", 118), ("material_id", 394), ("用于页面", 662), ("关键字段", 856), ("待补口径", 1126), ("Owner", 1384)]
    for head, hx in headers:
        parts.append(_text(hx, 292, head, 13, theme["accent"], 900))
    uses = [
        ("04驾驶舱/08证据表", "收入、毛利、回款、行业结构", "按行业毛利/回款周期", "财经"),
        ("04驾驶舱/05矩阵", "客户、合同金额、区域、行业", "客户名单/区域对比", "销售"),
        ("04驾驶舱/06原因/07计划", "周期、返工率、验收节点", "平均周期/返工率趋势", "PMO"),
        ("04驾驶舱/08证据表/09行动", "分层、续约、复购、风险客户", "复购率/续约金额", "客成"),
    ]
    for idx, material in enumerate(materials):
        row_y = 334 + idx * 64
        _project_line(parts, 106, row_y - 34, 1490, row_y - 34, theme["border"], 1)
        parts.append(_text(118, row_y, material["display_name"], 13, theme["title"], 900))
        parts.append(_text(394, row_y, material["material_id"], 12, theme["muted"], 700))
        parts.append(_text(662, row_y, uses[idx][0], 12, theme["body"], 700))
        parts.append(_text(856, row_y, uses[idx][1], 12, theme["body"], 600))
        color = theme["warning"] if idx in {0, 3} else theme["accent"]
        parts.append(_text(1126, row_y, uses[idx][2], 12, color, 800))
        parts.append(_text(1384, row_y, uses[idx][3], 12, theme["title"], 900))
        parts.append(_text(118, row_y + 22, material["summary"], 10, theme["body"], 500))
    parts.append("</g>")

    parts.append('<g id="annual-appendix-usage-contract">')
    rules = [
        ("读取顺序", "materials/index.md -> 当前页引用素材 -> 原始表格/截图", "避免反复全盘检索"),
        ("入页方式", "先写经营判断，再把来源塞进证据槽", "不要只在附录堆清单"),
        ("缺口标注", "缺数据写待补口径、Owner、截止日", "不能删除不利信息"),
        ("复盘追踪", "同一字段进入月度经营会", "保证下次复盘可比较"),
    ]
    for idx, (head, body, note) in enumerate(rules):
        x = 88 + idx * 356
        parts.append(_rect(x, 632, 320, 78, "#EFF6FF", "#B8D8FF", 14))
        parts.append(_text(x + 18, 660, head, 13, theme["accent"], 900))
        parts.append(_text(x + 18, 684, body, 11, theme["title"], 800))
        parts.append(_text(x + 18, 704, note, 10, theme["body"], 600))
    parts.append("</g>")

    parts.append(_rect(88, 736, 1424, 54, "#FFF7ED", "#F59E0B", 16))
    parts.append(_text(118, 770, "附录使用方式", 16, "#B45309", 900))
    parts.append(_text(260, 770, "附录不是素材坟场，而是告诉模型哪些页面引用哪些素材、缺什么口径、由谁补齐。", 14, theme["title"], 800))
    parts.append(_rect(88, 804, 1424, 28, "#0F3B73", "#0F3B73", 14))
    parts.append(_text(118, 824, "示例路径：materials/index.md -> finance-monthly-report.xlsx -> crm-contract-ledger.xlsx -> delivery-pmo-ledger.xlsx -> customer-success-renewal.xlsx", 11, "#FFFFFF", 800))


def _render_annual_summary_svg(deck: dict[str, Any], page: dict[str, Any]) -> str:
    theme = THEMES[deck["theme"]]
    if page["layout"] == "cover":
        return _render_annual_cover(deck, page)
    if page["layout"] == "agenda":
        return _render_annual_agenda(deck, page)

    parts = _annual_page_base(theme, page)
    page_id = page["id"]
    if page_id == "03-section-results":
        _render_annual_section(parts, theme)
    elif page_id == "04-dashboard":
        _render_annual_dashboard(parts, theme)
    elif page_id == "05-matrix":
        _render_annual_gap_matrix(parts, theme)
    elif page_id == "06-cause":
        _render_annual_cause(parts, theme)
    elif page_id == "07-roadmap":
        _render_annual_roadmap(parts, theme)
    elif page_id == "08-evidence-table":
        _render_annual_evidence_table(parts, theme)
    elif page_id == "09-actions":
        _render_annual_actions(parts, theme)
    elif page_id == "10-appendix":
        _render_annual_appendix(parts, theme, deck)
    else:
        raise ValueError(f"未知年度总结页: {page_id}")
    _annual_footer(parts, theme, deck, page)
    return "\n  ".join(parts) + "\n"


def _render_cover(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    parts.append(_text(90, 120, page["eyebrow"], 20, theme["muted"], 600))
    parts.append(_text(90, 218, page["title"], 54, theme["title"], 900))
    parts.append(_text(90, 286, page["subtitle"], 24, theme["body"], 400))
    for idx, (label, value) in enumerate(page["metrics"]):
        x = 90 + idx * 470
        parts.append(_rect(x, 510, 420, 150, theme["surface"], theme["border"], 24))
        parts.append(_text(x + 34, 570, label, 22, theme["accent"], 800))
        parts.append(_text(x + 34, 625, value, 25, theme["title"] if theme["bg"] != "#8A1538" else theme["body"], 800))
    parts.append(_rect(90, 720, 1420, 72, theme["surface"], theme["border"], 20))
    parts.append(_text(124, 765, "示例重点：这是一套多页 deck 的封面，不作为内容页结构复用。", 19, theme["body"], 700))


def _render_agenda(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    for idx, it in enumerate(page["items"]):
        y = 275 + idx * 118
        parts.append(_rect(120, y, 1360, 88, theme["surface"], theme["border"], 18))
        parts.append(_text(160, y + 56, it["head"], 30, theme["accent"], 900))
        parts.append(_text(260, y + 42, it["body"], 22, theme["title"], 800))
        parts.append(_text(260, y + 72, " / ".join(it["bullets"]), 15, theme["body"], 500))
        parts.append(_text(1360, y + 56, it["tag"], 16, theme["muted"], 700))


def _render_section(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    parts.append(_text(90, 150, page["title"], 50, theme["title"], 900))
    parts.append(_text(90, 212, page["subtitle"], 23, theme["body"], 500))
    parts.append(f'<line x1="90" y1="270" x2="1510" y2="270" stroke="{theme["accent"]}" stroke-width="6"/>')
    for idx, it in enumerate(page["items"]):
        x = 150 + idx * 650
        parts.append(_rect(x, 380, 560, 210, theme["surface"], theme["border"], 24))
        parts.append(_text(x + 36, 442, it["tag"], 20, theme["accent"], 900))
        parts.append(_text(x + 36, 500, it["head"], 26, theme["title"], 900))
        parts.append(_text(x + 36, 548, it["body"], 18, theme["body"], 500))
        parts.extend(_lines(x + 36, 592, [f'- {b}' for b in it["bullets"][:2]], 15, theme["body"], 30))


def _render_cards(parts: list[str], theme: dict[str, str], page: dict[str, Any], cols: int) -> None:
    card_w = 420 if cols == 3 else 335
    gap = 80 if cols == 3 else 28
    start_x = 90
    for idx, it in enumerate(page["items"]):
        x = start_x + idx * (card_w + gap)
        y = 285
        parts.append(_rect(x, y, card_w, 350, theme["surface"], theme["border"], 22))
        parts.append(f'<circle cx="{x + 42}" cy="{y + 48}" r="22" fill="{theme["accent"]}"/>')
        parts.append(_text(x + 42, y + 56, str(idx + 1), 20, "#FFFFFF", 800, "middle"))
        parts.append(_text(x + 82, y + 58, it["head"], 24, theme["title"], 800))
        parts.append(_text(x + 32, y + 116, it["body"], 17, theme["body"], 500))
        parts.extend(_lines(x + 32, y + 168, [f'- {b}' for b in it["bullets"]], 16, theme["body"], 34))
        if it["tag"]:
            parts.append(_rect(x + 32, y + 290, 155, 34, "#EFF6FF" if theme["bg"] != "#07111F" else "#102A43", theme["border"], 17))
            parts.append(_text(x + 58, y + 313, it["tag"], 15, theme["accent"], 700))


def _render_dashboard(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    for idx, metric in enumerate(page["metrics"]):
        label, value, pct = metric
        x = 90 + idx * 355
        parts.append(_rect(x, 260, 315, 130, theme["surface"], theme["border"], 18))
        parts.append(_text(x + 28, 312, label, 18, theme["muted"], 600))
        parts.append(_text(x + 28, 360, value, 34, theme["title"], 900))
        parts.append(f'<rect x="{x + 170}" y="340" width="105" height="12" rx="6" fill="{theme["border"]}"/>')
        parts.append(f'<rect x="{x + 170}" y="340" width="{max(24, int(pct))}" height="12" rx="6" fill="{theme["accent"]}"/>')
    for idx, it in enumerate(page["items"]):
        x = 90 + idx * 720
        parts.append(_rect(x, 460, 670, 210, theme["surface"], theme["border"], 20))
        parts.append(_text(x + 34, 520, it["head"], 25, theme["accent"], 800))
        parts.append(_text(x + 34, 568, it["body"], 18, theme["body"], 500))
        parts.extend(_lines(x + 34, 616, [f'- {b}' for b in it["bullets"]], 16, theme["body"], 32))


def _render_left_right(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    claim, evidence = page["items"][0], page["items"][1:]
    parts.append(_rect(90, 255, 590, 500, theme["surface"], theme["border"], 22))
    parts.append(_text(130, 320, claim["head"], 29, theme["accent"], 900))
    parts.append(_text(130, 382, claim["body"], 20, theme["body"], 600))
    parts.extend(_lines(130, 450, [f'- {b}' for b in claim["bullets"]], 17, theme["body"], 38))
    parts.append(_rect(130, 650, 220, 40, "#FEF2F2" if theme["bg"] != "#07111F" else "#3B1D2A", theme["border"], 20))
    parts.append(_text(162, 677, claim["tag"], 16, theme["warning"], 800))
    for idx, it in enumerate(evidence):
        y = 255 + idx * 165
        # 汇报类卡片禁装饰性左缘色条（contract-svg-self-qa），层级靠字重与留白表达。
        parts.append(_rect(760, y, 750, 132, theme["surface"], theme["border"], 18))
        parts.append(_text(800, y + 48, it["head"], 23, theme["title"], 800))
        parts.append(_text(800, y + 86, it["body"], 17, theme["body"], 500))
        parts.append(_text(800, y + 114, " / ".join(it["bullets"]), 13, theme["muted"], 500))


def _render_timeline(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    parts.append(f'<line x1="150" y1="470" x2="1450" y2="470" stroke="{theme["border"]}" stroke-width="6"/>')
    for idx, it in enumerate(page["items"]):
        x = 130 + idx * 335
        parts.append(f'<circle cx="{x + 42}" cy="470" r="26" fill="{theme["accent"]}"/>')
        parts.append(_text(x + 42, 479, str(idx + 1), 20, "#FFFFFF", 800, "middle"))
        parts.append(_rect(x, 540 if idx % 2 else 285, 300, 185, theme["surface"], theme["border"], 18))
        y = 540 if idx % 2 else 285
        parts.append(_text(x + 24, y + 46, it["head"], 23, theme["title"], 800))
        parts.append(_text(x + 24, y + 85, it["body"], 16, theme["body"], 500))
        parts.extend(_lines(x + 24, y + 123, [f'- {b}' for b in it["bullets"][:2]], 14, theme["body"], 28))


def _render_matrix(parts: list[str], theme: dict[str, str], page: dict[str, Any], risk: bool = False) -> None:
    positions = [(90, 270), (820, 270), (90, 520), (820, 520)]
    for idx, it in enumerate(page["items"]):
        x, y = positions[idx]
        color = theme["warning"] if risk and idx < 2 else theme["accent"]
        parts.append(_rect(x, y, 690, 190, theme["surface"], theme["border"], 18))
        parts.append(_text(x + 32, y + 50, it["head"], 24, color, 800))
        parts.append(_text(x + 32, y + 92, it["body"], 17, theme["body"], 500))
        parts.extend(_lines(x + 32, y + 130, [f'- {b}' for b in it["bullets"][:2]], 15, theme["body"], 28))
        parts.append(_text(x + 560, y + 50, it["tag"], 16, color, 800))


def _render_action_table(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    x, y = 90, 270
    parts.append(_rect(x, y, 1420, 500, theme["surface"], theme["border"], 18))
    headers = ["事项", "责任/判断", "关键动作", "标签"]
    xs = [130, 470, 800, 1320]
    for i, h_text in enumerate(headers):
        parts.append(_text(xs[i], y + 54, h_text, 18, theme["accent"], 800))
    for idx, it in enumerate(page["items"]):
        row_y = y + 105 + idx * 88
        parts.append(f'<line x1="120" y1="{row_y - 36}" x2="1480" y2="{row_y - 36}" stroke="{theme["border"]}" stroke-width="1"/>')
        parts.append(_text(xs[0], row_y, it["head"], 19, theme["title"], 800))
        parts.append(_text(xs[1], row_y, it["body"], 16, theme["body"], 500))
        parts.append(_text(xs[2], row_y, "；".join(it["bullets"][:2]), 15, theme["body"], 500))
        parts.append(_text(xs[3], row_y, it["tag"], 16, theme["accent"], 800))


def _render_evidence_table(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    x, y = 90, 265
    parts.append(_rect(x, y, 1420, 510, theme["surface"], theme["border"], 18))
    headers = ["证据项", "来源/口径", "必须补齐的信息", "类型"]
    xs = [130, 455, 780, 1335]
    for i, h_text in enumerate(headers):
        parts.append(_text(xs[i], y + 55, h_text, 18, theme["accent"], 900))
    for idx, it in enumerate(page["items"]):
        row_y = y + 112 + idx * 92
        parts.append(f'<line x1="120" y1="{row_y - 38}" x2="1480" y2="{row_y - 38}" stroke="{theme["border"]}" stroke-width="1"/>')
        parts.append(_text(xs[0], row_y, it["head"], 19, theme["title"], 800))
        parts.append(_text(xs[1], row_y, it["body"], 16, theme["body"], 500))
        parts.append(_text(xs[2], row_y, "；".join(it["bullets"][:2]), 15, theme["body"], 500))
        parts.append(_text(xs[3], row_y, it["tag"], 16, theme["accent"], 800))


def _render_appendix(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    for idx, it in enumerate(page["items"]):
        x = 110 + (idx % 2) * 700
        y = 290 + (idx // 2) * 230
        parts.append(_rect(x, y, 620, 175, theme["surface"], theme["border"], 20))
        parts.append(_text(x + 32, y + 48, it["tag"], 17, theme["accent"], 800))
        parts.append(_text(x + 32, y + 88, it["head"], 23, theme["title"], 900))
        parts.append(_text(x + 32, y + 124, it["body"], 16, theme["body"], 500))
        parts.append(_text(x + 32, y + 152, " / ".join(it["bullets"][:2]), 14, theme["muted"], 500))


def _render_funnel(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    widths = [900, 700, 500]
    for idx, it in enumerate(page["items"]):
        w = widths[idx]
        x = 170 + (900 - w) // 2
        y = 285 + idx * 145
        parts.append(_rect(x, y, w, 105, theme["accent"] if idx == 0 else theme["surface"], theme["border"], 18))
        color = "#FFFFFF" if idx == 0 else theme["title"]
        parts.append(_text(x + 34, y + 44, it["head"], 25, color, 900))
        parts.append(_text(x + 34, y + 78, it["body"], 17, color if idx == 0 else theme["body"], 500))
    for idx, it in enumerate(page["items"]):
        y = 285 + idx * 145
        parts.append(_rect(1120, y, 390, 105, theme["surface"], theme["border"], 18))
        parts.append(_text(1150, y + 42, it["tag"], 20, theme["accent"], 800))
        parts.append(_text(1150, y + 76, " / ".join(it["bullets"][:2]), 15, theme["body"], 500))


def _render_architecture(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    parts.append(_rect(590, 365, 420, 140, theme["accent"], theme["border"], 24))
    parts.append(_text(800, 425, "核心平台", 30, "#FFFFFF", 900, "middle"))
    parts.append(_text(800, 465, "数据 / 流程 / 权限 / 反馈", 18, "#FFFFFF", 500, "middle"))
    positions = [(110, 285), (1070, 285), (110, 560), (1070, 560)]
    for idx, it in enumerate(page["items"]):
        x, y = positions[idx]
        parts.append(_rect(x, y, 390, 170, theme["surface"], theme["border"], 20))
        parts.append(_text(x + 30, y + 48, it["head"], 23, theme["title"], 800))
        parts.append(_text(x + 30, y + 88, it["body"], 16, theme["body"], 500))
        parts.append(_text(x + 30, y + 126, " / ".join(it["bullets"][:2]), 14, theme["muted"], 500))
        parts.append(f'<line x1="{x + (390 if x < 800 else 0)}" y1="{y + 85}" x2="{800}" y2="435" stroke="{theme["border"]}" stroke-width="3"/>')


def _render_comparison(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    left, right, bridge = page["items"]
    for idx, it in enumerate([left, right]):
        x = 90 + idx * 740
        parts.append(_rect(x, 280, 680, 330, theme["surface"], theme["border"], 22))
        parts.append(_text(x + 36, 345, it["tag"], 20, theme["accent"], 800))
        parts.append(_text(x + 36, 398, it["head"], 28, theme["title"], 900))
        parts.append(_text(x + 36, 452, it["body"], 18, theme["body"], 500))
        parts.extend(_lines(x + 36, 508, [f'- {b}' for b in it["bullets"]], 16, theme["body"], 34))
    parts.append(_rect(90, 700, 1420, 78, theme["surface"], theme["border"], 20))
    parts.append(_text(124, 748, f'{bridge["tag"]}：{bridge["body"]}', 20, theme["accent"], 800))
    parts.append(_text(520, 748, " / ".join(bridge["bullets"]), 17, theme["body"], 500))


def _render_pyramid(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    widths = [520, 760, 1000]
    for idx, it in enumerate(page["items"]):
        w = widths[idx]
        x = 300 + (1000 - w) // 2
        y = 285 + idx * 145
        fill = theme["accent"] if idx == 0 else theme["surface"]
        color = "#FFFFFF" if idx == 0 else theme["title"]
        parts.append(_rect(x, y, w, 112, fill, theme["border"], 18))
        parts.append(_text(x + 36, y + 46, it["head"], 24, color, 900))
        parts.append(_text(x + 36, y + 82, it["body"], 17, color if idx == 0 else theme["body"], 500))
    parts.append(_rect(1130, 320, 330, 300, theme["surface"], theme["border"], 18))
    parts.append(_text(1160, 372, "使用提示", 24, theme["accent"], 800))
    parts.extend(_lines(1160, 424, ["- 层级要有递进关系", "- 不把口号当证据", "- 底层必须可执行"], 16, theme["body"], 38))


def _render_roadmap(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    for idx, it in enumerate(page["items"]):
        x = 100 + idx * 355
        parts.append(_rect(x, 305, 310, 380, theme["surface"], theme["border"], 20))
        parts.append(_text(x + 28, 362, it["head"], 24, theme["accent"], 900))
        parts.append(_text(x + 28, 420, it["body"], 17, theme["body"], 500))
        parts.extend(_lines(x + 28, 475, [f'- {b}' for b in it["bullets"][:2]], 15, theme["body"], 34))
        parts.append(_text(x + 28, 625, it["tag"], 17, theme["title"], 800))


def _render_case_story(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    for idx, it in enumerate(page["items"]):
        x = 90 + idx * 485
        parts.append(_rect(x, 300, 430, 310, theme["surface"], theme["border"], 22))
        parts.append(_text(x + 38, 360, it["tag"], 20, theme["accent"], 800))
        parts.append(_text(x + 38, 412, it["head"], 25, theme["title"], 900))
        parts.append(_text(x + 38, 465, it["body"], 17, theme["body"], 500))
        parts.extend(_lines(x + 38, 520, [f'- {b}' for b in it["bullets"]], 15, theme["body"], 34))
    parts.append(_rect(90, 695, 1420, 82, theme["surface"], theme["border"], 20))
    parts.append(_text(124, 746, "示例重点：案例页必须有对象、动作、结果和待补证据。", 20, theme["accent"], 800))


def _render_worksheet(parts: list[str], theme: dict[str, str], page: dict[str, Any]) -> None:
    for idx, it in enumerate(page["items"]):
        x = 90 + (idx % 2) * 730
        y = 270 + (idx // 2) * 245
        parts.append(_rect(x, y, 680, 190, theme["surface"], theme["border"], 18))
        parts.append(_text(x + 32, y + 48, it["head"], 23, theme["title"], 800))
        parts.append(_text(x + 32, y + 88, it["body"], 17, theme["body"], 500))
        parts.extend(_lines(x + 32, y + 128, [f'□ {b}' for b in it["bullets"][:2]], 15, theme["body"], 30))


def render_svg(deck: dict[str, Any], page: dict[str, Any]) -> str:
    if deck["id"] == "scenario-annual-summary":
        return _render_annual_summary_svg(deck, page)
    if deck["id"] == "scenario-project-report":
        return _render_project_report_svg(deck, page)

    theme = THEMES[deck["theme"]]
    parts = _page_base(theme, page, deck)
    layout = page["layout"]
    if layout == "cover":
        _render_cover(parts, theme, page)
    elif layout == "agenda":
        _render_agenda(parts, theme, page)
    elif layout == "section":
        _render_section(parts, theme, page)
    elif layout in {"cards3", "cards4"}:
        _render_cards(parts, theme, page, 3 if layout == "cards3" else 4)
    elif layout == "dashboard":
        _render_dashboard(parts, theme, page)
    elif layout == "left_right":
        _render_left_right(parts, theme, page)
    elif layout == "timeline":
        _render_timeline(parts, theme, page)
    elif layout == "matrix":
        _render_matrix(parts, theme, page)
    elif layout == "risk_heatmap":
        _render_matrix(parts, theme, page, risk=True)
    elif layout == "action_table":
        _render_action_table(parts, theme, page)
    elif layout == "evidence_table":
        _render_evidence_table(parts, theme, page)
    elif layout == "appendix":
        _render_appendix(parts, theme, page)
    elif layout == "funnel":
        _render_funnel(parts, theme, page)
    elif layout == "architecture":
        _render_architecture(parts, theme, page)
    elif layout == "comparison":
        _render_comparison(parts, theme, page)
    elif layout == "pyramid":
        _render_pyramid(parts, theme, page)
    elif layout == "roadmap":
        _render_roadmap(parts, theme, page)
    elif layout == "case_story":
        _render_case_story(parts, theme, page)
    elif layout == "worksheet":
        _render_worksheet(parts, theme, page)
    else:
        raise ValueError(f"未知 layout: {layout}")
    _footer(parts, theme, deck, page)
    return "\n  ".join(parts) + "\n"


def generate_svg_decks(*, decks_dir: Path = DECKS_DIR, clean: bool = True) -> dict[str, list[Path]]:
    """把 7 套蓝图 deck 的 SVG 生成到 ``decks_dir``（可注入，CLI 默认仍写资产目录）。

    清理边界（安全约束）：``clean=True`` 只逐个重建蓝图 deck 自己的子目录
    ``decks_dir/<blueprint_deck_id>``，**绝不 rmtree 整个 decks_dir**——该目录还存放
    不由本脚本生成的手作金标 deck（chart-type / report-structure /
    composite-structure / effects-structure 等 ``*-gold-pages``），整目录删除会把
    它们连带清掉且无法由脚本再生。
    """
    decks_dir.mkdir(parents=True, exist_ok=True)
    generated: dict[str, list[Path]] = {}
    for deck in _expanded_decks():
        deck_dir = decks_dir / deck["id"]
        if clean and deck_dir.exists():
            shutil.rmtree(deck_dir)
        deck_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        for index, page in enumerate(deck["pages"], start=1):
            slug = page["id"].split("-", 1)[1] if "-" in page["id"] else page["id"]
            path = deck_dir / f"{index:02d}-{slug}.svg"
            path.write_text(_scale_svg_to_ppt169(render_svg(deck, page)), encoding="utf-8")
            paths.append(path)
        generated[deck["id"]] = paths
    return generated


def _write_gold_svgs(
    generated: dict[str, list[Path]],
    definition: dict[str, Any],
    *,
    decks_dir: Path = DECKS_DIR,
) -> tuple[dict[str, Any], list[Path]]:
    source_deck = next(deck for deck in _expanded_decks() if deck["id"] == definition["source_id"])
    source_pages = {
        page["id"]: page
        for page in source_deck["pages"]
    }
    source_paths = {
        page["id"]: path
        for page, path in zip(source_deck["pages"], generated[source_deck["id"]], strict=True)
    }
    pages = [source_pages[page_id] for page_id, _slug in definition["pages"]]
    gold_deck = {
        **source_deck,
        "id": definition["id"],
        "scenario": definition["scenario"],
        "pages": pages,
    }
    gold_dir = decks_dir / gold_deck["id"]
    if gold_dir.exists():
        shutil.rmtree(gold_dir)
    gold_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, (page_id, slug) in enumerate(definition["pages"], start=1):
        target = gold_dir / f"{index:02d}-{slug}.svg"
        shutil.copyfile(source_paths[page_id], target)
        paths.append(target)
    return gold_deck, paths


def _trace_summary(trace_path: Path) -> dict[str, int]:
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    slides = trace.get("slides") if isinstance(trace, dict) else []
    native_count = 0
    unsupported_count = 0
    for slide in slides if isinstance(slides, list) else []:
        for event in slide.get("events", []) if isinstance(slide, dict) else []:
            if event.get("decision") == "native":
                native_count += 1
            elif event.get("decision") in {"unsupported", "error"}:
                unsupported_count += 1
    return {"slide_count": len(slides), "native_count": native_count, "unsupported_count": unsupported_count}


class _BenchmarkAssetStorage:
    """只为离线 benchmark smoke 提供 ``asset_key`` 到本地图片的受控映射。"""

    def __init__(self, mapping: dict[str, Path]) -> None:
        self._mapping = {key.strip().lstrip("/"): path for key, path in mapping.items()}

    async def read(self, _namespace: str, key: str) -> bytes:
        clean_key = key.strip().lstrip("/")
        source = self._mapping.get(clean_key)
        if source is None:
            raise FileNotFoundError(f"benchmark smoke image asset not found: {clean_key}")
        return source.read_bytes()


async def _render_deck(deck: dict[str, Any], svg_paths: list[Path], *, output_dir: Path) -> dict[str, Any]:
    from app.contexts.rendering.adapters.ppt_master_compat.adapter import (
        create_native_pptx_from_svg_files,
        svg_contains_data_icon_placeholders,
    )
    from app.contexts.rendering.formats.svg_drawingml.input_gate import validate_svg_input

    pages: list[dict[str, Any]] = []
    for page, svg_path in zip(deck["pages"], svg_paths, strict=True):
        svg_text = svg_path.read_text(encoding="utf-8")
        # 离线示例是完整独立成品 deck (自带整页背景/外框), 没有单独的框架层,
        # 因此按 allow_framework_chrome 校验; 安全/转换规则仍全部执行。
        gate = validate_svg_input(svg_text, allow_framework_chrome=True)
        if not gate.ok:
            raise RuntimeError(f"{svg_path} 未通过 SVG input gate: {gate.blocking_issues}")
        if svg_contains_data_icon_placeholders(svg_path):
            raise RuntimeError(f"{svg_path} 包含 P0 不支持的 data-icon 占位")
        pages.append({
            "id": page["id"], "role": page["role"], "layout": page["layout"],
            "svg": _relative(svg_path), "svg_bytes": len(svg_text.encode("utf-8")),
            "text_node_count": gate.summary.get("text_node_count"),
            "shape_count": gate.summary.get("shape_count"),
        })

    output_path = output_dir / f'{deck["id"]}.pptx'
    with tempfile.TemporaryDirectory(prefix=f'{deck["id"]}-') as tmp:
        trace_path = Path(tmp) / f'{deck["id"]}.trace.json'
        ok = create_native_pptx_from_svg_files(
            svg_paths,
            output_path,
            canvas_format="ppt169",
            verbose=False,
            merge_paragraphs=False,
            conversion_trace_path=trace_path,
        )
        if not ok:
            raise RuntimeError(f'{deck["id"]} 转换失败')
        trace_summary = _trace_summary(trace_path)

    return {
        "id": deck["id"],
        "scenario": deck["scenario"],
        "theme": deck["theme"],
        "page_count": len(svg_paths),
        "pages": pages,
        "pptx": _relative(output_path),
        "pptx_bytes": output_path.stat().st_size,
        "pptx_sha256": _sha256(output_path),
        "trace_summary": trace_summary,
    }


def _literary_benchmark_page_specs() -> list[dict[str, Any]]:
    shared_image_slot = {
        "slot_id": "destiny-cover-like-photo",
        "asset_id": "destiny-upload:embedded:cover-like-photo",
        "asset_key": LITERARY_BENCHMARK_IMAGE_ASSET_KEY,
        "material_id": "destiny-upload",
        "fit": "cover",
        "corner_radius": 18,
        "caption": "用户上传《命运》样本中抽取的深色影像素材",
        "alt_text": "暗色森林/人物意象背景图，用于文学纪录片式页面",
    }
    return [
        {
            "id": "01-cover",
            "filename": "01-cover.svg",
            "role": "cover",
            "layout": "photo_dark_serif",
            "builder": "fixed",
            "spec": {
                "schema_version": "fixed_svg_page/v1",
                "kind": "cover",
                "variant": "photo_dark_serif",
                "theme_id": "literary_documentary_cn",
                "kicker": "《命运》深度解析",
                "title": "我们终将生下自己的命运",
                "subtitle": "从文本、身体与时代里，读懂一个人如何被塑造，也如何反过来塑造自己。",
                "meta": "文学纪录片式读书分享 / SVG route benchmark",
                "title_align": "center",
            },
        },
        {
            "id": "02-theme-panel",
            "filename": "02-theme-panel.svg",
            "native_filename": "02-theme-panel.native-data.json",
            "role": "content",
            "layout": "editorial_image_panel",
            "builder": "editorial",
            "spec": {
                "schema_version": "editorial_svg_page/v1",
                "page_id": "02-theme-panel",
                "layout_family": "editorial_image_panel",
                "theme_id": "literary_documentary_cn",
                "native_data_ref": "02-theme-panel.native-data.json",
                "title": "命运不是一条线，而是一张不断收紧的网",
                "lead": "这类页面用一张可追溯图片承担情绪，用右侧论述块承接讲述密度。",
                "image_slot": shared_image_slot,
                "narrative_blocks": [
                    {
                        "heading": "从出生处境进入主题",
                        "body": "先解释人物为什么被抛入某种秩序，而不是急着给出价值判断。",
                    },
                    {
                        "heading": "从身体经验进入文本",
                        "body": "把疼痛、恐惧、亲密关系等具体经验转成可讲述的证据链。",
                    },
                    {
                        "heading": "从文本回到读者",
                        "body": "最后把作品中的命运感翻译成听众能理解的现实回声。",
                    },
                ],
                "quote": "不是命运先完成我们，而是我们在回应中继续生成命运。",
                "sources": ["用户上传样本 PPT", "slide-authoring literary benchmark"],
            },
        },
        {
            "id": "03-three-questions",
            "filename": "03-three-questions.svg",
            "role": "content",
            "layout": "story_cards_3up",
            "builder": "editorial",
            "spec": {
                "schema_version": "editorial_svg_page/v1",
                "page_id": "03-three-questions",
                "layout_family": "story_cards_3up",
                "theme_id": "literary_documentary_cn",
                "title": "三次追问，把故事从情节推向主题",
                "lead": "弱模型只需填写叙事卡内容，坐标与容量由 builder 兜底。",
                "cards": [
                    {
                        "micro_label": "追问一",
                        "heading": "命运从哪里开始",
                        "body": "不要抽象谈苦难，先讲家庭、时代和身体如何共同塑造人物起点。",
                        "anchor": "起点 / 处境",
                    },
                    {
                        "micro_label": "追问二",
                        "heading": "人如何回应命运",
                        "body": "把抵抗、妥协、沉默和选择拆成可讲述动作，避免空泛抒情。",
                        "anchor": "动作 / 选择",
                    },
                    {
                        "micro_label": "追问三",
                        "heading": "读者为何被击中",
                        "body": "收束到现代人的共鸣：我们也在关系、制度和自我叙事中生成自己。",
                        "anchor": "共鸣 / 回声",
                    },
                ],
                "bottom_close": "文学纪录片式 PPT 的正文页不是海报，而是用卡片组织可复述的观点推进。",
                "sources": ["scenario-book-deep-analysis.md"],
            },
        },
        {
            "id": "04-two-life-stages",
            "filename": "04-two-life-stages.svg",
            "role": "content",
            "layout": "story_cards_2up",
            "builder": "editorial",
            "spec": {
                "schema_version": "editorial_svg_page/v1",
                "page_id": "04-two-life-stages",
                "layout_family": "story_cards_2up",
                "theme_id": "literary_documentary_cn",
                "title": "两个阶段，解释命运如何从外部压力变成内部叙事",
                "lead": "2up 页面用来承载大段对照判断：一边讲处境，一边讲回应。",
                "cards": [
                    {
                        "micro_label": "阶段一",
                        "heading": "被处境命名",
                        "body": "人物先被家庭、时代、性别和身体经验命名；讲述时要把这些外部约束说清楚。",
                        "anchor": "外部结构",
                    },
                    {
                        "micro_label": "阶段二",
                        "heading": "重新命名自己",
                        "body": "当人物开始解释自己的痛苦、欲望和选择，命运就从压迫转成一种可被重写的叙事。",
                        "anchor": "内部回应",
                    },
                ],
                "bottom_close": "这一页验证 story_cards_2up：大段文字必须仍然可读，不能退化成低密度海报。",
                "sources": ["content-literary-documentary-narrative.md"],
            },
        },
        {
            "id": "05-text-reality-compare",
            "filename": "05-text-reality-compare.svg",
            "native_filename": "05-text-reality-compare.native-data.json",
            "role": "content",
            "layout": "book_compare_quote_panel",
            "builder": "editorial",
            "spec": {
                "schema_version": "editorial_svg_page/v1",
                "page_id": "05-text-reality-compare",
                "layout_family": "book_compare_quote_panel",
                "theme_id": "literary_documentary_cn",
                "native_data_ref": "05-text-reality-compare.native-data.json",
                "title": "文本里的命运，与现实中的自我选择彼此照亮",
                "lead": "对照页把书中判断、现实经验和讲者观点放在同一页完成互证。",
                "image_slot": shared_image_slot,
                "compare_blocks": [
                    {
                        "heading": "文本",
                        "body": "作品提供人物如何被环境塑造的细节，承担叙事证据。",
                    },
                    {
                        "heading": "现实",
                        "body": "现实经验提供听众理解入口，避免文学解读变成自说自话。",
                    },
                    {
                        "heading": "观点",
                        "body": "讲者需要给出判断：所谓命运，是处境与回应互相塑形的结果。",
                    },
                ],
                "quote": "好的读书分享不是复述情节，而是让一本书解释我们正在经历的生活。",
                "sources": ["用户上传样本 PPT", "style-literary-documentary-cn.md"],
            },
        },
        {
            "id": "06-section-echo",
            "filename": "06-section-echo.svg",
            "role": "section_divider",
            "layout": "photo_dark_serif",
            "builder": "fixed",
            "spec": {
                "schema_version": "fixed_svg_page/v1",
                "kind": "section_divider",
                "variant": "photo_dark_serif",
                "theme_id": "literary_documentary_cn",
                "kicker": "第三部分",
                "title": "当命运回到我们身上",
                "subtitle": "章节过渡页不堆信息，只把下一段讲述的情绪和问题推到台前。",
                "title_align": "center",
            },
        },
        {
            "id": "07-closing",
            "filename": "07-closing.svg",
            "role": "closing",
            "layout": "photo_dark_serif",
            "builder": "fixed",
            "spec": {
                "schema_version": "fixed_svg_page/v1",
                "kind": "closing",
                "variant": "photo_dark_serif",
                "theme_id": "literary_documentary_cn",
                "kicker": "尾声",
                "title": "命运不是答案，是我们不断生下自己的过程",
                "subtitle": "把问题还给听众：当我们说命运时，究竟是在讲限制，还是在讲回应限制的方式？",
                "quote_text": "不是逃离命运，而是在命运中形成自己。",
                "title_align": "center",
            },
        },
    ]


def _write_literary_benchmark_svgs(
    *,
    benchmarks_dir: Path = BENCHMARKS_DIR,
) -> dict[str, Any]:
    from app.contexts.rendering.formats.svg_drawingml.input_gate import validate_svg_input

    scripts_dir = SCRIPT_PATH.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from build_editorial_svg_page import build_editorial_svg_page, build_native_data
    from build_fixed_svg_page import build_fixed_svg_page

    benchmark_dir = benchmarks_dir / LITERARY_BENCHMARK_ID
    if benchmark_dir.exists():
        shutil.rmtree(benchmark_dir)
    benchmark_dir.mkdir(parents=True, exist_ok=True)

    pages: list[dict[str, Any]] = []
    for page_def in _literary_benchmark_page_specs():
        spec = page_def["spec"]
        if page_def["builder"] == "fixed":
            svg = build_fixed_svg_page(spec)
            native_data = {"version": 1, "images": []}
        else:
            svg = build_editorial_svg_page(spec)
            native_data = build_native_data(spec)
        svg_path = benchmark_dir / page_def["filename"]
        svg_path.write_text(svg, encoding="utf-8")
        gate = validate_svg_input(svg, page_archetype=page_def["role"])
        if not gate.ok:
            raise RuntimeError(f"{svg_path} 未通过 SVG input gate: {gate.blocking_issues}")

        page_entry: dict[str, Any] = {
            "id": page_def["id"],
            "role": page_def["role"],
            "layout": page_def["layout"],
            "svg": _relative(svg_path),
            "svg_bytes": len(svg.encode("utf-8")),
            "text_node_count": gate.summary.get("text_node_count"),
            "shape_count": gate.summary.get("shape_count"),
        }
        image_count = len(native_data.get("images", []))
        native_filename = page_def.get("native_filename")
        if image_count and native_filename:
            native_path = benchmark_dir / str(native_filename)
            native_path.write_text(
                json.dumps(native_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            page_entry["native_data"] = _relative(native_path)
            page_entry["native_image_slot_count"] = image_count
        pages.append(page_entry)

    return {
        "id": LITERARY_BENCHMARK_ID,
        "scenario": "《命运》深度解析 7 页专题基准",
        "style_family": "literary_documentary_cn",
        "purpose": "覆盖 photo_dark_serif、section_divider、editorial SVG 内容层、2/3up narrative cards 与 native image slot 的专题级 smoke；不纳入主 7 套 PPTX 转换 hash 口径。",
        "requires_pptx_render": False,
        "page_count": len(pages),
        "coverage": {
            "routes": [
                "fixed_page_photo_dark",
                "editorial_svg",
                "native_image_slot",
            ],
            "layouts": sorted({page["layout"] for page in pages}),
            "roles": sorted({page["role"] for page in pages}),
        },
        "pages": pages,
    }


def _write_literary_benchmark_smoke_image(benchmark_dir: Path) -> Path:
    """写入一张确定性的本地图片，用于模拟用户上传材料解析出的可商用图片资产。"""

    from PIL import Image, ImageDraw

    assets_dir = benchmark_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    output_path = assets_dir / "destiny-cover-like-photo.png"
    width, height = 900, 1100
    image = Image.new("RGB", (width, height), "#111410")
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(15 + 32 * ratio)
        g = int(18 + 18 * ratio)
        b = int(15 + 8 * ratio)
        draw.line((0, y, width, y), fill=(r, g, b))

    draw.ellipse((610, 82, 742, 214), fill="#D9C7A3")
    draw.ellipse((638, 78, 770, 210), fill="#171A15")
    for index, x in enumerate(range(-60, width + 80, 46)):
        trunk_w = 11 + index % 5
        tone = 33 + (index * 7) % 26
        draw.rectangle((x, 150, x + trunk_w, height), fill=(tone, max(22, tone - 9), 18))
        draw.line((x + trunk_w, 260, x + 90, 80 + (index * 31) % 260), fill=(tone + 15, tone + 2, 24), width=5)
        draw.line((x, 330, x - 80, 130 + (index * 43) % 260), fill=(tone + 8, tone, 22), width=4)

    draw.rectangle((0, 820, width, height), fill="#0B0D0B")
    draw.ellipse((388, 680, 512, 805), fill="#0A0B0A")
    draw.rectangle((418, 790, 482, 1004), fill="#080A08")
    draw.polygon([(322, 1012), (450, 872), (596, 1012)], fill="#070807")
    draw.text((48, height - 84), "benchmark image asset / destiny", fill="#A89269")
    image.save(output_path, "PNG", optimize=True)
    return output_path


def _literary_benchmark_smoke_framework() -> dict[str, Any]:
    return {
        "framework_id": "literary-benchmark-smoke-framework",
        # benchmark SVG 由 1280 原生 builder 生成，画布固定用 PPT 尺寸，
        # 不跟随蓝图设计画布 W/H（1600x900）。
        "canvas": {"width": PPT_W, "height": PPT_H},
        "theme": {
            "background": "#FFFCF6",
            "muted": "#7C6F64",
            "font_family": FONT,
        },
        "chrome": {
            "header": {"enabled": False},
            "footer": {"enabled": False},
            "page_number": {"enabled": False},
        },
    }


def _literary_benchmark_workspace(page: dict[str, Any]) -> dict[str, Any]:
    return {
        "sections": [
            {
                "slides": [
                    {
                        "page_id": page["id"],
                        "slide_no": 1,
                        "page_archetype": page["role"],
                    }
                ]
            }
        ]
    }


def _literary_benchmark_resolved_background(
    *,
    page: dict[str, Any],
    image_asset_path: Path,
) -> dict[str, Any]:
    if page["layout"] == "photo_dark_serif":
        return {
            "source": "benchmark_smoke",
            "page_role": page["role"],
            "type": "photo_dark",
            "base_color": "#0B0F14",
            "_materialized_path": str(image_asset_path),
            "_materialized_by_renderer": True,
            "_materialized_source": "benchmark_smoke_asset",
            "fit": "cover",
            "overlay_color": "#0B0F14",
            "overlay_opacity": 0.52,
            "crop": {"focal_x": 0.52, "focal_y": 0.52},
        }
    return {
        "source": "benchmark_smoke",
        "page_role": page["role"],
        "type": "paper_light",
        "base_color": "#FFFCF6",
        "texture_color": "#FFFFFF",
        "texture_opacity": 0.08,
    }


async def _render_literary_benchmark_single_page_smoke(
    *,
    page: dict[str, Any],
    smoke_dir: Path,
    thumbnail_dir: Path,
    storage: _BenchmarkAssetStorage,
    image_asset_path: Path,
) -> dict[str, Any]:
    from app.tools.pptx._renderer import render_pptx_to_pngs
    from app.contexts.rendering.adapters.ppt_master_compat.adapter import create_native_pptx_from_svg_files
    from app.contexts.rendering.formats.svg_drawingml.deck_framework import apply_svg_deck_framework_to_pptx
    from app.contexts.rendering.formats.svg_native_image_overlay import overlay_native_images_from_svg

    svg_path = SKILL_ROOT / page["svg"]
    svg_text = svg_path.read_text(encoding="utf-8")
    pptx_path = smoke_dir / f"{page['id']}.pptx"
    trace_path = smoke_dir / f"{page['id']}.trace.json"
    workdir = smoke_dir / "work" / page["id"]
    workdir.mkdir(parents=True, exist_ok=True)

    ok = create_native_pptx_from_svg_files(
        [svg_path],
        pptx_path,
        canvas_format="ppt169",
        verbose=False,
        merge_paragraphs=False,
        conversion_trace_path=trace_path,
    )
    if not ok:
        raise RuntimeError(f"{page['id']} benchmark 单页 PPTX 转换失败")

    deck_framework_report = apply_svg_deck_framework_to_pptx(
        pptx_path=pptx_path,
        framework=_literary_benchmark_smoke_framework(),
        workspace=_literary_benchmark_workspace(page),
        slide_id=page["id"],
        resolved_background=_literary_benchmark_resolved_background(
            page=page,
            image_asset_path=image_asset_path,
        ),
        materialized_root=image_asset_path.parents[1],
    )
    if not deck_framework_report.get("applied"):
        raise RuntimeError(f"{page['id']} deck framework 背景未写入: {deck_framework_report}")

    overlay_report: dict[str, Any] = {"applied": False, "image_count": 0, "slots": []}
    native_data_ref = page.get("native_data")
    if isinstance(native_data_ref, str) and native_data_ref:
        native_path = SKILL_ROOT / native_data_ref
        native_payload = json.loads(native_path.read_text(encoding="utf-8"))
        overlay_report = await overlay_native_images_from_svg(
            pptx_path=pptx_path,
            svg_content=svg_text,
            slide_id=page["id"],
            native_data=native_payload,
            workdir=workdir,
            storage=storage,
        )
        if overlay_report.get("error"):
            raise RuntimeError(f"{page['id']} native image overlay 失败: {overlay_report}")
        if native_payload.get("images") and not overlay_report.get("applied"):
            raise RuntimeError(f"{page['id']} native image overlay 未实际写入图片: {overlay_report}")

    thumbnail_work_dir = smoke_dir / "thumbnail-work" / page["id"]
    if thumbnail_work_dir.exists():
        shutil.rmtree(thumbnail_work_dir)
    thumbnail_work_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_paths = await render_pptx_to_pngs(
        str(pptx_path),
        str(thumbnail_work_dir),
        slide_indices=[1],
        dpi=110,
    )
    if len(thumbnail_paths) != 1:
        raise RuntimeError(f"{page['id']} 缩略图渲染数量异常: {thumbnail_paths}")
    final_thumbnail_path = thumbnail_dir / f"{page['id']}.png"
    shutil.copyfile(thumbnail_paths[0], final_thumbnail_path)
    shutil.rmtree(thumbnail_work_dir, ignore_errors=True)

    return {
        "id": page["id"],
        "pptx": _relative(pptx_path),
        "pptx_bytes": pptx_path.stat().st_size,
        "pptx_sha256": _sha256(pptx_path),
        "thumbnail": _relative(final_thumbnail_path),
        "thumbnail_bytes": final_thumbnail_path.stat().st_size,
        "thumbnail_sha256": _sha256(final_thumbnail_path),
        "trace": _relative(trace_path),
        "trace_summary": _trace_summary(trace_path),
        "deck_framework": deck_framework_report,
        "native_image_overlay": overlay_report,
    }


def _compose_literary_benchmark_contact_sheet(
    *,
    page_thumbnails: list[tuple[str, Path]],
    output_path: Path,
    columns: int = 3,
) -> None:
    """将真实 PPTX 渲染出的页缩略图拼成离线 contact sheet。"""

    if not page_thumbnails:
        raise RuntimeError("没有可用于 benchmark contact sheet 的缩略图")

    from PIL import Image, ImageDraw

    tile_w = 360
    tile_h = 203
    label_h = 34
    gap = 22
    padding = 28
    header_h = 52
    rows = (len(page_thumbnails) + columns - 1) // columns
    width = padding * 2 + columns * tile_w + (columns - 1) * gap
    height = padding * 2 + header_h + rows * (tile_h + label_h) + (rows - 1) * gap
    canvas = Image.new("RGB", (width, height), "#F7F0E5")
    draw = ImageDraw.Draw(canvas)
    draw.text((padding, padding), "scenario-book-deep-analysis-benchmark / PPTX smoke", fill="#4B3A2B")
    draw.text((padding, padding + 24), "single-page PPTX renders with native image overlay", fill="#7C6F64")

    for index, (page_id, thumb_path) in enumerate(page_thumbnails):
        row = index // columns
        col = index % columns
        x = padding + col * (tile_w + gap)
        y = padding + header_h + row * (tile_h + label_h + gap)
        with Image.open(thumb_path) as thumb:
            image = thumb.convert("RGB")
            image.thumbnail((tile_w, tile_h))
            offset_x = x + (tile_w - image.width) // 2
            offset_y = y + (tile_h - image.height) // 2
            canvas.paste(image, (offset_x, offset_y))
        draw.rectangle((x, y, x + tile_w, y + tile_h), outline="#D6C8B8", width=2)
        draw.text((x, y + tile_h + 9), page_id, fill="#5B4636")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG", optimize=True)


async def _render_literary_benchmark_smoke(
    entry: dict[str, Any],
    *,
    benchmark_dir: Path,
) -> dict[str, Any]:
    smoke_dir = benchmark_dir / "pptx-smoke"
    if smoke_dir.exists():
        shutil.rmtree(smoke_dir)
    smoke_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_dir = smoke_dir / "thumbnails"
    thumbnail_dir.mkdir(parents=True, exist_ok=True)

    image_asset_path = _write_literary_benchmark_smoke_image(benchmark_dir)
    storage = _BenchmarkAssetStorage({LITERARY_BENCHMARK_IMAGE_ASSET_KEY: image_asset_path})
    smoke_pages = []
    page_thumbnails: list[tuple[str, Path]] = []
    for page in entry["pages"]:
        smoke_page = await _render_literary_benchmark_single_page_smoke(
            page=page,
            smoke_dir=smoke_dir,
            thumbnail_dir=thumbnail_dir,
            storage=storage,
            image_asset_path=image_asset_path,
        )
        smoke_pages.append(smoke_page)
        page_thumbnails.append((page["id"], SKILL_ROOT / smoke_page["thumbnail"]))

    contact_sheet_path = smoke_dir / "contact-sheet.png"
    _compose_literary_benchmark_contact_sheet(
        page_thumbnails=page_thumbnails,
        output_path=contact_sheet_path,
    )
    entry = dict(entry)
    entry["requires_pptx_render"] = True
    entry["pptx_smoke"] = {
        "mode": "single_page_pptx_with_contact_sheet",
        "page_count": len(smoke_pages),
        "image_asset": {
            "asset_key": LITERARY_BENCHMARK_IMAGE_ASSET_KEY,
            "path": _relative(image_asset_path),
            "bytes": image_asset_path.stat().st_size,
            "sha256": _sha256(image_asset_path),
        },
        "contact_sheet": _relative(contact_sheet_path),
        "contact_sheet_bytes": contact_sheet_path.stat().st_size,
        "contact_sheet_sha256": _sha256(contact_sheet_path),
        "pages": smoke_pages,
    }
    return entry


def _replace_literary_benchmark_entry(manifest: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    benchmark_examples = manifest.get("benchmark_examples")
    if not isinstance(benchmark_examples, list):
        benchmark_examples = []
    replaced = False
    next_examples: list[dict[str, Any]] = []
    for item in benchmark_examples:
        if isinstance(item, dict) and item.get("id") == LITERARY_BENCHMARK_ID:
            next_examples.append(entry)
            replaced = True
        else:
            next_examples.append(item)
    if not replaced:
        next_examples.append(entry)
    manifest["benchmark_examples"] = next_examples
    return manifest


async def render_examples(
    *,
    decks_dir: Path = DECKS_DIR,
    output_dir: Path = PPTX_DIR,
    benchmarks_dir: Path = BENCHMARKS_DIR,
    manifest_path: Path = MANIFEST_PATH,
    generate_svg: bool = True,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for legacy in EXAMPLES_DIR.glob("scenario-*.svg"):
        legacy.unlink()
    if generate_svg:
        generated = generate_svg_decks(decks_dir=decks_dir, clean=True)
    else:
        generated = {
            deck["id"]: sorted((decks_dir / deck["id"]).glob("*.svg"))
            for deck in _expanded_decks()
        }
    decks = _expanded_decks()
    entries = [
        await _render_deck(deck, generated[deck["id"]], output_dir=output_dir)
        for deck in decks
    ]
    gold_entries = []
    for definition in GOLD_EXAMPLE_DEFINITIONS:
        gold_deck, gold_paths = _write_gold_svgs(generated, definition, decks_dir=decks_dir)
        gold_entries.append(await _render_deck(gold_deck, gold_paths, output_dir=output_dir))
    literary_benchmark = _write_literary_benchmark_svgs(benchmarks_dir=benchmarks_dir)
    literary_benchmark = await _render_literary_benchmark_smoke(
        literary_benchmark,
        benchmark_dir=benchmarks_dir / LITERARY_BENCHMARK_ID,
    )
    benchmark_entries = [literary_benchmark]
    manifest = {
        "schema_version": 2,
        "description": "slide-authoring 中国式场景多页 SVG deck 示例及已转换 PPTX。",
        "conversion": "app.contexts.rendering.adapters.ppt_master_compat.adapter.create_native_pptx_from_svg_files",
        "coverage": {
            "deck_count": len(entries),
            "total_pages": sum(entry["page_count"] for entry in entries),
            "layouts": sorted({page["layout"] for entry in entries for page in entry["pages"]}),
            "roles": sorted({page["role"] for entry in entries for page in entry["pages"]}),
        },
        "decks": entries,
        "gold_examples": gold_entries,
        "benchmark_examples": benchmark_entries,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


async def render_literary_benchmark_only(
    *,
    benchmarks_dir: Path = BENCHMARKS_DIR,
    manifest_path: Path = MANIFEST_PATH,
) -> dict[str, Any]:
    entry = _write_literary_benchmark_svgs(benchmarks_dir=benchmarks_dir)
    entry = await _render_literary_benchmark_smoke(
        entry,
        benchmark_dir=benchmarks_dir / LITERARY_BENCHMARK_ID,
    )
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "schema_version": 2,
            "description": "slide-authoring 中国式场景多页 SVG deck 示例及已转换 PPTX。",
            "conversion": "app.contexts.rendering.adapters.ppt_master_compat.adapter.create_native_pptx_from_svg_files",
            "coverage": {"deck_count": 0, "total_pages": 0, "layouts": [], "roles": []},
            "decks": [],
            "gold_examples": [],
        }
    manifest = _replace_literary_benchmark_entry(manifest, entry)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render slide-authoring scenario SVG decks to PPTX.")
    parser.add_argument("--decks-dir", type=Path, default=DECKS_DIR)
    parser.add_argument("--output-dir", type=Path, default=PPTX_DIR)
    parser.add_argument("--benchmarks-dir", type=Path, default=BENCHMARKS_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--no-generate-svg", action="store_true")
    parser.add_argument(
        "--benchmark-only",
        action="store_true",
        help="只刷新《命运》benchmark SVG/PPTX smoke，不重渲染主 7 套示例。",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.benchmark_only:
        manifest = asyncio.run(
            render_literary_benchmark_only(
                benchmarks_dir=args.benchmarks_dir,
                manifest_path=args.manifest,
            )
        )
    else:
        manifest = asyncio.run(
            render_examples(
                decks_dir=args.decks_dir,
                output_dir=args.output_dir,
                benchmarks_dir=args.benchmarks_dir,
                manifest_path=args.manifest,
                generate_svg=not args.no_generate_svg,
            )
        )
    print(json.dumps({
        "ok": True,
        "decks": manifest["coverage"]["deck_count"],
        "pages": manifest["coverage"]["total_pages"],
        "manifest": str(args.manifest),
        "output_dir": str(args.output_dir),
        "benchmark_only": args.benchmark_only,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
