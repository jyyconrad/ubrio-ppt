"""Bounded, read-only OOXML checks. Not a visual or PowerPoint editability verdict."""

import argparse
import hashlib
import json
import posixpath
import sys
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def xml(zf, name):
    data = zf.read(name)
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("DTD/entity declarations are not supported")
    return ET.fromstring(data)


def rels_name(part):
    folder, name = posixpath.split(part)
    return posixpath.join(folder, "_rels", name + ".rels")


def targets(zf, part):
    name = rels_name(part)
    if name not in zf.namelist():
        return {}
    return {r.attrib["Id"]: r.attrib for r in xml(zf, name)}


def resolve(part, target):
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), unquote(target))).lstrip("/")


def cache_points(cache, count=None):
    if cache is None:
        return []
    points = {int(p.attrib["idx"]): p.findtext("c:v", namespaces=NS) for p in cache.findall("c:pt", NS)}
    count_node = cache.find("c:ptCount", NS)
    if count is None:
        count = int(count_node.attrib["val"]) if count_node is not None else max(points, default=-1) + 1
    if count < 0 or count > 10000 or any(i < 0 or i >= count for i in points):
        raise ValueError("Chart cache indexes exceed declared or supported bounds")
    return [points.get(i) for i in range(count)]


def series_data(series):
    levels = []
    multi = series.find("c:cat/c:multiLvlStrRef/c:multiLvlStrCache", NS)
    if multi is not None:
        count_node = multi.find("c:ptCount", NS)
        count = int(count_node.attrib["val"]) if count_node is not None else None
        levels = [cache_points(level, count) for level in multi.findall("c:lvl", NS)]
        labels = levels[0] if levels else []
    else:
        labels = []
        for suffix in ("c:strRef/c:strCache", "c:strLit", "c:numRef/c:numCache", "c:numLit"):
            cache = series.find("c:cat/" + suffix, NS)
            if cache is not None:
                labels = cache_points(cache)
                break
    values = []
    for suffix in ("c:numRef/c:numCache", "c:numLit"):
        cache = series.find("c:val/" + suffix, NS)
        if cache is not None:
            values = cache_points(cache)
            break
    name = series.findtext("c:tx/c:strRef/c:strCache/c:pt/c:v", namespaces=NS)
    if name is None:
        name = series.findtext("c:tx/c:v", default="", namespaces=NS)
    return {"name": name, "labels": labels, "category_levels": levels, "values": values}


def inspect(file, allow_image_slide=False):
    file = Path(file)
    if file.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("PPTX exceeds the 100 MiB input limit")
    errors, warnings, pages = [], [], []
    with ZipFile(file) as zf:
        infos = zf.infolist()
        names = set(zf.namelist())
        if len(infos) > 10000 or sum(i.file_size for i in infos) > 300 * 1024 * 1024:
            raise ValueError("OOXML package exceeds inspection limits")
        if len(infos) != len(names) or any(i.flag_bits & 1 for i in infos):
            raise ValueError("Duplicate or encrypted ZIP members are unsupported")
        if any(n.startswith("/") or ".." in n.split("/") or "\\" in n for n in names):
            raise ValueError("Unsafe ZIP member path")
        if any(i.file_size > 100 * 1024 * 1024 for i in infos):
            raise ValueError("Oversized package member")
        bad = zf.testzip()
        if bad:
            raise ValueError("ZIP CRC mismatch")
        external = []
        for name in sorted(names):
            if not name.endswith(".rels"):
                continue
            folder, relname = posixpath.split(name)
            part = posixpath.join(posixpath.dirname(folder), relname[:-5]) if name != "_rels/.rels" else ""
            for relation in xml(zf, name):
                r = relation.attrib
                if r.get("TargetMode") == "External":
                    external.append({"part": part, "type": r.get("Type", "").rsplit("/", 1)[-1]})
                    if not r.get("Type", "").endswith("/hyperlink"):
                        errors.append(f"External resource in {part}")
                elif resolve(part, r["Target"]) not in names:
                    errors.append(f"Missing relationship target in {part}")
        presentation = xml(zf, "ppt/presentation.xml")
        size = presentation.find("p:sldSz", NS)
        width, height = int(size.attrib["cx"]), int(size.attrib["cy"])
        rels = targets(zf, "ppt/presentation.xml")
        for index, slide_id in enumerate(presentation.findall("p:sldIdLst/p:sldId", NS), 1):
            rel = rels[slide_id.attrib[f"{{{NS['r']}}}id"]]
            part = resolve("ppt/presentation.xml", rel["Target"])
            slide = xml(zf, part)
            texts = [n.text or "" for n in slide.findall(".//a:t", NS)]
            tables = []
            for table in slide.findall(".//a:tbl", NS):
                tables.append([["".join(n.text or "" for n in cell.findall(".//a:t", NS)) for cell in row.findall("a:tc", NS)] for row in table.findall("a:tr", NS)])
            fonts = sorted({n.attrib.get("typeface") for n in slide.iter() if n.tag in {f"{{{NS['a']}}}latin", f"{{{NS['a']}}}ea"} and n.attrib.get("typeface")})
            charts = []
            slide_rels = targets(zf, part)
            for chart_ref in slide.findall(".//c:chart", NS):
                rid = chart_ref.attrib[f"{{{NS['r']}}}id"]
                chart_part = resolve(part, slide_rels[rid]["Target"])
                chart = xml(zf, chart_part)
                series = []
                for s in chart.findall(".//c:ser", NS):
                    data = series_data(s)
                    if data["labels"] and data["values"] and len(data["labels"]) != len(data["values"]):
                        errors.append(f"Page {index}: chart category/value cache lengths differ")
                    if not data["labels"] or not data["values"]:
                        warnings.append(f"Page {index}: chart cache is absent or uses an uninspected data layout")
                    series.append(data)
                chart_rels = targets(zf, chart_part)
                workbook = chart.find("c:externalData", NS)
                if workbook is None:
                    errors.append(f"Page {index}: chart has no embedded editable workbook")
                else:
                    relation = chart_rels.get(workbook.attrib.get(f"{{{NS['r']}}}id"), {})
                    if relation.get("TargetMode") == "External" or not relation.get("Target", "").endswith(".xlsx"):
                        errors.append(f"Page {index}: chart workbook is not a local XLSX")
                charts.append({"part": chart_part, "series": series, "embedded_workbook": workbook is not None})
            native_shapes = len(slide.findall(".//p:sp", NS))
            pictures = slide.findall(".//p:pic", NS)
            for xf in slide.findall("./p:cSld/p:spTree/p:sp/p:spPr/a:xfrm", NS) + slide.findall("./p:cSld/p:spTree/p:pic/p:spPr/a:xfrm", NS) + slide.findall("./p:cSld/p:spTree/p:graphicFrame/p:xfrm", NS):
                off, ext = xf.find("a:off", NS), xf.find("a:ext", NS)
                if off is not None and ext is not None:
                    x,y,w,h = int(off.attrib["x"]),int(off.attrib["y"]),int(ext.attrib["cx"]),int(ext.attrib["cy"])
                    if x < -1000 or y < -1000 or x+w > width+1000 or y+h > height+1000:
                        errors.append(f"Page {index}: object outside slide bounds")
            if pictures and not texts and not tables and not charts:
                message = f"Page {index}: image-only page, no native editable content"
                (warnings if allow_image_slide else errors).append(message)
            notes = []
            for r in slide_rels.values():
                if r.get("Type", "").endswith("/notesSlide"):
                    notes = [n.text for n in xml(zf, resolve(part, r["Target"])).findall(".//a:t", NS)]
            pages.append({"page": index, "part": part, "texts": texts, "tables": tables, "charts": charts,
                          "native_shapes": native_shapes, "pictures": len(pictures), "fonts": fonts, "notes": notes})
        if not pages:
            errors.append("Presentation has no slides")
    return {"file": str(file.resolve()), "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            "page_count": len(pages), "size_inches": [width/914400,height/914400], "pages": pages,
            "external_relationships": external, "errors": errors, "warnings": warnings,
            "structure_passed": not errors, "visual_review": "not_performed", "powerpoint_roundtrip": "not_performed"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--allow-image-slide", action="store_true")
    args = parser.parse_args()
    try:
        result = inspect(args.input, args.allow_image_slide)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["structure_passed"] else 2
    except (OSError, ValueError, KeyError, ET.ParseError, BadZipFile) as exc:
        print(f"Inspection failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
