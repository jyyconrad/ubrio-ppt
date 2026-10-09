# 可选预览路线

**LibreOffice是支线，不能作为用户使用本技能的安装前提。** 生成与对象检查独立运行，制作成功与视觉验证分别记录。

| 当前环境 | 处理方式 | 可以说明的结果 |
| --- | --- | --- |
| 宿主已有PPTX预览或编辑器控制能力 | 使用该能力打开本次最终PPTX，查看实际页 | 确实查看后，说明本次实际视觉检查结果 |
| 用户已有PowerPoint/WPS/其他编辑器 | 通过宿主已有授权能力打开或导出预览；不擅自安装、操作其他文件 | 仅记录所用编辑器与本次检查；未自动测过的兼容性不泛化 |
| 已安装LibreOffice与Poppler，且本次选择该支线 | 调用包内可选脚本，查看转换结果 | 本文件在该渲染器的效果；不是PowerPoint编辑往返 |
| 无PPTX渲染器但能看图 | 不以HTML/SVG制作稿替代最终PPTX效果；可看中间稿辅助设计但不能称最终渲染 | 可编辑PPTX及对象检查已完成，最终视觉未验证 |
| 没有渲染器或图片查看能力 | 不尝试自动下载类库或反复修环境；交付PPTX并简短注明限制 | “已检查原生对象，未做渲染目检” |

不把源文件私自上传到在线转换器。使用在线服务需要用户明确授权，且需符合资料隐私要求。本包不自建插件、云转换服务或宿主适配。

选择可选LibreOffice分支时，预览目录必须是新目录：

```bash
python3 "$SKILL/scripts/optional/render_with_libreoffice.py" "$PPTX" \
  --output-dir "$PREVIEW_DIR" --soffice "$SOFFICE"
```

该脚本不会从主线自动调用，也不安装依赖。只在已安装的参考环境中验证过LibreOffice 26.2.2.2 + Poppler；其他宿主预览路径是能力选择规则，不是已经编写或验证的适配器。

预览必须来自用户将收到的最终PPTX。任何修改使旧预览失效，重新打开/渲染之后才能确认新版本。正式发行的PowerPoint编辑往返与视觉评测仍属于维护者验收，不是要求每位用户安装PowerPoint或LibreOffice。

中文显示成手写体、缺笔画或字形异常时，先核对 PPTX 的东亚字体与预览 PDF 的实际字体。使用 Poppler 路线可运行 `pdffonts slides.pdf`；系统显示已安装不代表 LibreOffice 已按该字体渲染。选用已获授权且预览器能识别的中文字体（例如 Noto Sans CJK SC），在金标 page spec 或固定页 spec 中设置 `typography.font_family` 后重编译、重渲染并检查字体表。金标原生表格同时继承 `body_px`（转换为 pt）；单槽覆盖使用 `native_table_slots[].style.font_face/font_size`，字号单位为 pt。用户锁定字体时保留原合同，另行处理预览环境并说明替换情况。字体文件不随本技能打包，也不自动下载。
