"""Static sanity check of the built dashboard HTML."""
import json, re
html = open("reports/anaikadu_preprint.html", encoding="utf-8").read()
assert "__DATA__" not in html, "placeholder not replaced!"
m = re.search(r"const DATA = (\{.*?\});</script>", html, re.S)
assert m, "DATA block not found"
d = json.loads(m.group(1))          # validates inlined JSON
print("DATA parses OK:", list(d.keys()))
assert html.count("<script") == html.count("</script>"), "unbalanced script tags"
for idd in ["#abstract","#sitecards","#losocards","#oversel","#micards","#shadeChart",
            "#cropbars","#senstbl","#fintbl","#cfChart","#mctbl","#mcChart","#recbox"]:
    assert idd.strip("#") in html, "missing id "+idd
print("all section ids present; script tags balanced; size", len(html)//1024, "KB")
print("systems:", [f["system"] for f in d["finance"]])
print("pepper NPV:", [f for f in d["finance"] if "Pepper" in f["system"]][0]["npv"])
