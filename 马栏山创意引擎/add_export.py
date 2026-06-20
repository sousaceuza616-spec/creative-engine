import os
APP = r"E:\19563\Documents\ruantong\马栏山创意引擎\app.py"
with open(APP, "r", encoding="utf-8") as f:
    c = f.read()

q = chr(34)
nl = chr(10)

func = nl + "def export_as_markdown(result):" + nl
func += "    lines = []" + nl
func += "    lines.append(" + q + "# \u7b56\u521b\u65b9\u6848" + q + ")" + nl
func += '    lines.append("")' + nl
func += "    lines.append(" + q + "**\u7b56\u5212\u9700\u6c42\uff1a** " + q + " + result.get(" + q + "brief" + q + ", " + q + q + "))" + nl
func += "    lines.append(" + q + "**\u54c1\u724c\u8c03\u6027\uff1a** " + q + " + result.get(" + q + "brand_tone" + q + ", " + q + "\u81ea\u52a8\u63a8\u5bfc" + q + "))" + nl
func += '    lines.append("")' + nl
func += "    analyses = result.get(" + q + "all_analyses" + q + ", [])" + nl
func += "    if analyses:" + nl
func += "        lines.append(" + q + "## \u5e02\u573a\u5206\u6790" + q + ")" + nl
func += "        for a in analyses:" + nl
func += "            src = a.get(" + q + "source" + q + ", " + q + q + ")" + nl
func += "            ang = a.get(" + q + "angle" + q + ", " + q + q + ")" + nl
func += "            lines.append(" + q + "### " + q + " + src + " + q + " (" + q + " + ang + " + q + ")" + q + ")" + nl
func += "            lines.append(a.get(" + q + "analysis" + q + ", " + q + q + "))" + nl
func += '        lines.append("")' + nl
func += "    headlines = result.get(" + q + "all_headlines" + q + ", [])" + nl
func += "    if headlines:" + nl
func += "        lines.append(" + q + "## \u521b\u610f\u6807\u9898" + q + ")" + nl
func += "        for h in headlines:" + nl
func += "            hl = h.get(" + q + "headline" + q + ", " + q + q + ")" + nl
func += "            hang = h.get(" + q + "angle" + q + ", " + q + q + ")" + nl
func += "            lines.append(" + q + "- " + q + " + hl + " + q + " (" + q + " + hang + " + q + ")" + q + ")" + nl
func += '        lines.append("")' + nl
func += "    lines.append(" + q + "## \u65b9\u6848\u5927\u7eb2" + q + ")" + nl
func += "    lines.append(result.get(" + q + "outline" + q + ", " + q + q + "))" + nl
func += "    return chr(10).join(lines)" + nl
func += nl

marker = "if run_button and brief:"
if marker in c:
    c = c.replace(marker, func + marker)
    with open(APP, "w", encoding="utf-8") as f:
        f.write(c)
    compile(c, APP, "exec")
    print("Export function added successfully!")
else:
    print("Marker not found - adding at end of file")
    c = c.rstrip() + nl + func + nl + marker + nl
    with open(APP, "w", encoding="utf-8") as f:
        f.write(c)
    compile(c, APP, "exec")
    print("Export function added at end!")

print("export_as_markdown:", "export_as_markdown" in c)
print("download button:", "download_btn" in c)
