"""Evidence/claim quality gate from session-884 C-01/C-02/C-03/C-06/C-13/C-14/V-04/V-06."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/svg"))

from gates.evidence import check  # noqa: E402


def _metric(**overrides) -> dict:
    metric = {
        "label": "单任务完成率",
        "value": "55.8%",
        "note": "受控实验",
        "evidence_type": "experiment",
        "claim_type": "fact",
        "population": "实验室开发者 N=48",
        "period": "2024",
        "denominator": "完成的基准任务数",
        "source_ref": "lab-study-2024 §3.2",
        "limitation": "单任务实验室，不可外推到全流程",
        "on_metric_label": "实验 · N=48 · 2024",
    }
    metric.update(overrides)
    return metric


def _content_spec(**overrides) -> dict:
    spec = {
        "page_role": "content",
        "title": "受控实验显示单任务完成率变化",
        "key_message": "实验室样本上的完成率与基线对比",
        "metrics": [
            _metric(),
            _metric(
                label="缺陷逃逸率",
                value="12%",
                population="同一实验室队列 N=48",
                denominator="发布后缺陷 / 完成任务",
                source_ref="lab-study-2024 §4.1",
                limitation="未覆盖生产事故",
                on_metric_label="实验 · N=48 · 2024",
            ),
            _metric(
                label="返工耗时",
                value="3.2h",
                population="同一实验室队列 N=48",
                denominator="每完成任务的返工小时",
                source_ref="lab-study-2024 §4.2",
                limitation="计时不含等待评审",
                on_metric_label="实验 · N=48 · 2024",
            ),
        ],
        "sources": ["https://example.com/lab-study-2024"],
    }
    spec.update(overrides)
    return spec


class EvidenceGateTests(unittest.TestCase):
    def test_kpi_missing_evidence_fields(self) -> None:
        result = check(
            _content_spec(
                metrics=[{"label": "完成率", "value": "55.8%", "note": "实验"}],
            )
        )
        for code in (
            "metrics[0].evidence_type",
            "metrics[0].population",
            "metrics[0].period",
            "metrics[0].denominator",
            "metrics[0].limitation",
        ):
            self.assertIn(code, result.missing)

    def test_mixed_evidence_types_without_on_metric_labels(self) -> None:
        result = check(
            _content_spec(
                metrics=[
                    _metric(on_metric_label=""),
                    _metric(
                        label="调查采用率",
                        value="90%",
                        evidence_type="survey",
                        claim_type="inference",
                        population="问卷应答者 N=1200",
                        period="2024",
                        denominator="自称已采用的应答者",
                        source_ref="dora-2024 p.12",
                        limitation="自报采用率，非产出",
                        on_metric_label="",
                    ),
                ]
            )
        )
        self.assertIn("heterogeneous_kpi_strip", result.missing)

    def test_structure_count_mixed_with_outcome_metrics(self) -> None:
        result = check(
            _content_spec(
                metrics=[
                    _metric(),
                    _metric(
                        label="章节数",
                        value="4",
                        evidence_type="structure_count",
                        claim_type="fact",
                        population="本册目录",
                        period="本册",
                        denominator="章",
                        source_ref="outline",
                        limitation="结构计数，非成效",
                        on_metric_label="结构 · 本册",
                    ),
                ]
            )
        )
        self.assertIn("structure_count_in_kpi_strip", result.missing)

    def test_causal_verbs_with_only_survey_correlation_category_evidence(self) -> None:
        result = check(
            _content_spec(
                title="局部提速被下游系统反噬",
                key_message="调查相关会沿链路衰减，导致返工；市场已升级，端到端必须必达 L4",
                metrics=[
                    _metric(
                        label="调查采用率",
                        value="90%",
                        evidence_type="survey",
                        claim_type="inference",
                        population="问卷应答者 N=1200",
                        period="2024",
                        denominator="自称已采用的应答者",
                        source_ref="dora-2024 p.12",
                        limitation="相关关系，非因果",
                        on_metric_label="调查 · N=1200 · 2024",
                    ),
                    _metric(
                        label="信任缺口",
                        value="30%",
                        evidence_type="correlation",
                        claim_type="inference",
                        population="同一调查",
                        period="2024",
                        denominator="不信任生成代码的应答者",
                        source_ref="dora-2024 p.18",
                        limitation="自报态度",
                        on_metric_label="相关 · 调查 · 2024",
                    ),
                    _metric(
                        label="Agent 品类",
                        value="已出现",
                        evidence_type="category",
                        claim_type="fact",
                        population="公开产品名录",
                        period="2025",
                        denominator="品类条目",
                        source_ref="gartner-summary",
                        limitation="品类存在性，非市场整体升级",
                        on_metric_label="品类 · 公开名录",
                    ),
                ],
            )
        )
        self.assertIn("causal_verb_without_evidence_grade", result.missing)

    def test_chart_with_endpoints_no_data_not_mechanism(self) -> None:
        result = check(
            _content_spec(
                native_chart_slots=[
                    {
                        "chart_type": "line",
                        "chart_kind": "empirical",
                        "has_endpoints": True,
                        "coords": [{"x": 0, "y": 1}, {"x": 1, "y": 2}],
                        "title": "有门禁 vs 无门禁 · 收益走势",
                        "data": [],
                    }
                ]
            )
        )
        self.assertIn("pseudo_empirical_chart", result.missing)

    def test_common_sense_cannot_be_strong_evidence(self) -> None:
        result = check(
            _content_spec(
                metrics=[
                    _metric(source_ref="工程治理常识"),
                    _metric(
                        label="缺陷逃逸率",
                        value="12%",
                        source_ref="常识",
                        on_metric_label="实验 · N=48 · 2024",
                    ),
                ]
            )
        )
        self.assertIn("common_sense_as_strong_evidence", result.missing)

    def test_cover_page_bad_metrics_are_warnings_only(self) -> None:
        result = check(
            {
                "page_role": "cover",
                "title": "AI 全流程提效",
                "key_message": "局部提速被下游反噬，必须已升级到 L4",
                "metrics": [{"label": "完成率", "value": "55.8%", "note": "实验"}],
            }
        )
        self.assertEqual(result.missing, [])
        self.assertTrue(result.warnings)
        self.assertIn("metrics[0].evidence_type", result.warnings)

    def test_valid_experiment_kpis_are_ready(self) -> None:
        result = check(_content_spec())
        self.assertEqual(result.missing, [])

    def test_missing_sources_is_not_common_sense(self) -> None:
        spec = _content_spec()
        spec.pop("sources")
        result = check(spec)
        self.assertNotIn("common_sense_as_strong_evidence", result.missing)

    def test_year_alias_satisfies_period(self) -> None:
        metric = _metric()
        metric.pop("period")
        metric["year"] = "2024"
        result = check(_content_spec(metrics=[metric, _metric(label="对照完成率", value="41%")]))
        self.assertNotIn("metrics[0].period", result.missing)

    def test_mixed_types_with_on_metric_labels_allowed(self) -> None:
        result = check(
            _content_spec(
                metrics=[
                    _metric(),
                    _metric(
                        label="调查采用率",
                        value="90%",
                        evidence_type="survey",
                        claim_type="inference",
                        population="问卷应答者 N=1200",
                        period="2024",
                        denominator="自称已采用的应答者",
                        source_ref="dora-2024 p.12",
                        limitation="自报采用率，非产出",
                        on_metric_label="调查 · N=1200 · 2024",
                    ),
                ]
            )
        )
        self.assertNotIn("heterogeneous_kpi_strip", result.missing)

    def test_mechanism_chart_without_data_is_allowed_when_labeled(self) -> None:
        result = check(
            _content_spec(
                native_chart_slots=[
                    {
                        "chart_type": "line",
                        "chart_kind": "mechanism",
                        "has_endpoints": True,
                        "title": "假设链：写得更快到返工",
                        "insight": "待内部验证",
                        "data": [],
                    }
                ]
            )
        )
        self.assertNotIn("pseudo_empirical_chart", result.missing)
        self.assertNotIn("mechanism_diagram_unlabeled", result.missing)

    def test_section_divider_and_closing_are_warnings_only(self) -> None:
        bad = {
            "title": "目录",
            "key_message": "四章结构",
            "metrics": [{"label": "章", "value": "4"}],
        }
        for role in ("section_divider", "closing", "end"):
            with self.subTest(role=role):
                result = check({**bad, "page_role": role})
                self.assertEqual(result.missing, [])
                self.assertIn("metrics[0].evidence_type", result.warnings)

    def test_does_not_import_gold_builder(self) -> None:
        import gates.evidence as evidence_mod

        self.assertNotIn("build_gold_svg_page", getattr(evidence_mod, "__dict__", {}))
        source = Path(evidence_mod.__file__).read_text(encoding="utf-8")
        self.assertNotIn("build_gold_svg_page", source)


if __name__ == "__main__":
    unittest.main()
