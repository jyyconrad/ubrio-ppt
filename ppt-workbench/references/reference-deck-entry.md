# 参考构图整册入口

`scripts/svg/build_reference_deck.py` 只负责把已经完成业务判断的整册规格绑定到参考构图。它不生成业务事实、不替代 `page_spec`，也不合并最终整册。

## 输入

传入一个 JSON 对象：

```json
{
  "manifest": {"...": "validate_deck_contract.py 接受的完整 manifest"},
  "pages": [
    {
      "...": "现有完整 page_spec 字段",
      "reference_id": "R10",
      "reference_content": {"...": "R10 的纯业务字段"}
    }
  ]
}
```

先查看入口与指定参考页合同：

```bash
python scripts/svg/build_reference_deck.py --describe
python scripts/svg/build_reference_deck.py --describe-reference R10
```

`--describe-reference` 返回业务字段、容量和结构合同，不输出默认示例事实。授权合成 fixture 也必须作为明确的 `--input` 提供。

## 前置顺序

入口先读取全部实际 `page_spec/reference_content`，用现有 `_business_data/_check_content/_no_unknown/_bind` 还原固定设计，并在内存中生成参考 SVG 与 native data。随后只调用现有合同：

1. `validate_deck_contract.validate_deck` 检查整册。
2. `normalize_page_spec/quality_report` 检查每页 Gold 规格。
3. `validate_svg_drawingml` 检查每页最终参考 SVG/native。
4. 所有页面通过后才允许第一次 `render_svg_drawingml`。

`page_spec.title` 必须等于 `reference_content.title`。来源脚注直接取实际规格的 `evidence_state/period/population/denominator/source_ref/limitation(s)`；缺项必须补齐或明确写“未知”。状态按事实/观察/建议/目标/待验证显示，年份、样本、来源和限制原值仍保留。

脚注固定为 11px、`role=source`，最多两行。renderer schema 可声明受信任的 `source_band={x,y,w,h,max_lines,font_size}`；坐标只属于参考资源，业务输入不能提供或覆盖。入口用实际 SVG bbox 与该矩形逐项求交，复杂可见对象无法求界时也会阻断。未声明时，单行说明使用约 15px 的画布底部安全区；两行要求主体真实预留约 32px。发生碰撞时不会覆盖原内容或整体缩放页面。

R31 与 R10 同时出现时必须共享业务内容和证据元数据。R32 保持参考 renderer 声明的 1080x720，渲染使用 SVG 自身画布。

## 执行与输出

先做无落盘验证：

```bash
python scripts/svg/build_reference_deck.py --input deck.json --validate-only
```

实际生成：

```bash
python scripts/svg/build_reference_deck.py --input deck.json --output-dir build/reference-deck
```

入口按列表顺序写 `page-001/`、`page-002/`，每页保存原始/normalized spec、实际 content、前置报告、Gold 起始 SVG/native、最终参考 SVG/native、适配说明和单页 PPTX。根目录只增加 `reference-deck-manifest.json`，其中记录事件顺序和 SHA-256。视觉审读与 PowerPoint 往返始终标为 `not_performed`，必须由后续真实验收补充。

需要同画布整册时，继续使用 `scripts/merge_export.py` 合并各页 `page.pptx`；不同画布比例应分开交付。
