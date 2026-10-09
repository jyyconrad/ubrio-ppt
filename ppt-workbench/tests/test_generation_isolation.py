"""Native authoring/revision tests with no Office, repository or writable skill directory."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT
FONT = os.environ.get("PPT_FONT_PATH")
FONT_NAME = os.environ.get("PPT_FONT_NAME")
NODE = shutil.which("node")


def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}


@unittest.skipUnless(FONT and NODE, "Set PPT_FONT_PATH, optional PPT_FONT_NAME, and install Node dependencies")
class NativeIsolationTests(unittest.TestCase):
    def test_single_readonly_package_without_office(self):
        with tempfile.TemporaryDirectory(prefix="独立技能 space-") as temp:
            root = Path(temp)
            package = root / "只读安装 ppt-generate"
            shutil.copytree(
                SOURCE,
                package,
                ignore=shutil.ignore_patterns("node_modules", ".venv", "tests", "__pycache__"),
            )
            shutil.copytree(SOURCE / "node_modules", package / "node_modules", symlinks=True)
            before = snapshot(package)
            for p in package.rglob("*"):
                p.chmod(0o555 if p.is_dir() else 0o444)
            package.chmod(0o555)
            try:
                env = {"PATH":"/no-office-or-python-here", "HOME":str(root), "LANG":"en_US.UTF-8"}
                for repeat in range(3):
                    output = root / f"生成 输出 {repeat}"
                    command = [NODE,str(package / "assets/examples/make_examples.cjs"),"--font-path",FONT,"--output-dir",str(output)]
                    if FONT_NAME:
                        command += ["--font-name", FONT_NAME]
                    result = subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=90)
                    self.assertEqual(result.returncode,0,result.stderr)
                    files = sorted(output.glob("*.pptx"))
                    self.assertEqual(len(files),12)
                    for pptx in files:
                        checked = subprocess.run([sys.executable,str(package / "scripts/inspect_pptx.py"),str(pptx)],
                                                 cwd=root,env=env,capture_output=True,text=True,timeout=30)
                        self.assertEqual(checked.returncode,0,checked.stderr)
                        report = json.loads(checked.stdout)
                        self.assertEqual(report["visual_review"],"not_performed")
                        self.assertEqual(report["page_count"],1)
                self.assertEqual(before,snapshot(package),"Generation wrote to the read-only installation")
            finally:
                package.chmod(0o755)
                for p in package.rglob("*"):
                    p.chmod(0o755 if p.is_dir() else 0o644)

    def test_revision_updates_chart_and_native_table(self):
        with tempfile.TemporaryDirectory(prefix="ppt-revision-") as temp:
            script = """
const {buildExample,cases}=require(process.argv[1]);
const fs=require('node:fs');const path=require('node:path');
const spec=structuredClone(cases.find(c=>c.id==='03-target'));
spec.title='三地实际值更新后，合计完成率为100%';
spec.source='合成修订数据；目标1000、实际1000';spec.values=[450,280,270];
const options={fontPath:process.argv[2],fontName:process.argv[3]||undefined};
const table=structuredClone(cases.find(c=>c.id==='05-table'));
table.title='台账新增第四项，状态待核实';
table.rows.push(['西部项目','9月20日','待核实','确认范围']);
(async()=>{await buildExample(spec,options).save(path.join(process.argv[4],'revised-chart.pptx'));
await buildExample(table,options).save(path.join(process.argv[4],'revised-table.pptx'));})();
"""
            result = subprocess.run([NODE,"-e",script,str(SOURCE / "assets/examples/make_examples.cjs"),FONT,FONT_NAME or "",temp],
                                    capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            reports = []
            for name in ("revised-chart", "revised-table"):
                checked = subprocess.run([sys.executable,str(SOURCE / "scripts/inspect_pptx.py"),str(Path(temp)/(name+".pptx"))],
                                         capture_output=True,text=True,timeout=30)
                self.assertEqual(checked.returncode,0,checked.stderr)
                reports.append(json.loads(checked.stdout))
            page = reports[0]["pages"][0]
            self.assertEqual(page["charts"][0]["series"][1]["values"],["450","280","270"])
            self.assertIn("100.0%","".join(page["texts"]))
            self.assertNotIn("96.5%","".join(page["texts"]))
            self.assertEqual(reports[1]["pages"][0]["tables"][0][-1],["西部项目","9月20日","待核实","确认范围"])


if __name__ == "__main__":
    unittest.main()
