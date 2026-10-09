"""Regression checks for the Chinese reporting contracts added after sessions 884/915."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ReportingContractTests(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_entry_declares_deck_and_page_contract(self) -> None:
        text = self.read("SKILL.md")
        for marker in (
            "audience_decision", "evidence_ladder", "claim_type", "example_refs",
            "content_logic_passed", "density_passed", "visual_review",
        ):
            self.assertIn(marker, text, marker)

    def test_quality_gates_cover_states_decisions_and_density(self) -> None:
        text = self.read("references/content-visual-quality-gates.md")
        for marker in (
            "FACT", "OBSERVED", "PROPOSAL", "TARGET", "TO_VALIDATE",
            "baseline", "exception_policy", "决策项", "unique_factual_atoms",
            "structure_passed=true",
        ):
            self.assertIn(marker, text, marker)

    def test_research_path_is_shown_by_example(self) -> None:
        narrative = self.read("references/outline/narrative-shape.md")
        skill = self.read("SKILL.md")
        example = narrative.split("## 调研和规范怎么写", 1)[1].split("## 四格", 1)[0]
        for marker in (
            "本次不拍板",
            "单次写码用时",
            "不可比证据",
            "左右对照",
            "流程断点",
            "公开实验只覆盖单次写码",
            "权限和数据",
        ):
            self.assertIn(marker, example, marker)
        self.assertIn("调研和规范怎么写", skill)
        self.assertIn("一个分句", narrative)

    def test_narrative_shape_requires_deck_to_page_chain(self) -> None:
        text = self.read("references/outline/narrative-shape.md")
        for marker in (
            "audience_decision", "evidence_ladder", "claim→evidence→action→validation→decision",
            "primary_claim", "proves", "dominant", "attached",
        ):
            self.assertIn(marker, text, marker)

    def test_example_routing_records_adaptation(self) -> None:
        text = self.read("references/generate/methods/skill-graph.md")
        for marker in ("example_id", "reuse_reason", "adaptations", "not_reused_reason", "reference_dna"):
            self.assertIn(marker, text, marker)

    def test_table_route_and_visual_boundary_remain_explicit(self) -> None:
        text = "\n".join(
            self.read(path)
            for path in (
                "SKILL.md",
                "references/content-visual-quality-gates.md",
                "references/generate/methods/native-components.md",
            )
        )
        self.assertIn("native-table-slot", text)
        self.assertIn("伪表格", text)
        self.assertIn("未完成视觉验收", text)

if __name__ == "__main__":
    unittest.main()
