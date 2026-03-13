#!/usr/bin/env python3
"""Reads all .md summaries and generates a single-page site."""

import glob
import json
import os

def build():
    md_files = sorted(glob.glob("*.md"), reverse=True)

    entries = []
    for f in md_files:
        with open(f, encoding="utf-8") as fh:
            entries.append({"filename": f, "content": fh.read()})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bearcave Summaries</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #f5f5f5; color: #222; padding: 1rem; max-width: 720px; margin: 0 auto; }}
  .summary {{ background: #fff; border-radius: 8px; padding: 1.25rem 1.5rem;
              margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
  .summary h1 {{ font-size: 1.15rem; margin-bottom: .75rem; color: #1a1a1a; }}
  .summary h2 {{ font-size: 1rem; margin: .75rem 0 .4rem; color: #444; }}
  .summary p {{ margin: .4rem 0; line-height: 1.55; }}
  .summary ul {{ margin: .3rem 0 .3rem 1.25rem; }}
  .summary li {{ margin: .2rem 0; line-height: 1.5; }}
  .summary strong {{ color: #1a1a1a; }}
  .empty {{ text-align: center; padding: 3rem; color: #888; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #1a1a1a; color: #ddd; }}
    .summary {{ background: #252525; box-shadow: 0 1px 3px rgba(0,0,0,.4); }}
    .summary h1 {{ color: #eee; }}
    .summary h2 {{ color: #bbb; }}
    .summary strong {{ color: #eee; }}
  }}
</style>
</head>
<body>
<div id="app"></div>
<script>
const entries = {json.dumps(entries)};
const app = document.getElementById("app");
if (entries.length === 0) {{
  app.innerHTML = '<div class="empty">No summaries yet.</div>';
}} else {{
  entries.forEach(e => {{
    const div = document.createElement("div");
    div.className = "summary";
    div.innerHTML = marked.parse(e.content);
    app.appendChild(div);
  }});
}}
</script>
</body>
</html>"""

    os.makedirs("_site", exist_ok=True)
    with open("_site/index.html", "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Built _site/index.html with {len(entries)} summaries")

if __name__ == "__main__":
    build()
