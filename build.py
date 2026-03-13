#!/usr/bin/env python3
"""Reads all .md summaries and generates a single-page site."""

import glob
import json
import os

def build():
    md_files = sorted(
        [f for f in glob.glob("*.md") if f != "casino-master-summary.md"],
        reverse=True,
    )[:8]

    entries = []
    for f in md_files:
        with open(f, encoding="utf-8") as fh:
            entries.append({"filename": f, "content": fh.read()})

    casino_content = ""
    if os.path.exists("casino-master-summary.md"):
        with open("casino-master-summary.md", encoding="utf-8") as fh:
            casino_content = fh.read()

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
         background: #f5f5f5; color: #222; margin: 0; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 0 1rem 1rem; }}

  /* Tabs */
  .tabs {{ display: flex; gap: 0; border-bottom: 2px solid #ddd; margin-bottom: 1rem;
           position: sticky; top: 0; background: #f5f5f5; padding-top: 1rem; z-index: 10; }}
  .tab {{ padding: .6rem 1.25rem; cursor: pointer; border: none; background: none;
          font-size: .95rem; font-weight: 500; color: #666; border-bottom: 2px solid transparent;
          margin-bottom: -2px; transition: color .15s, border-color .15s; }}
  .tab:hover {{ color: #333; }}
  .tab.active {{ color: #2563eb; border-bottom-color: #2563eb; }}
  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}

  /* Summaries */
  .summary {{ background: #fff; border-radius: 10px; padding: 1.5rem 1.75rem 1.25rem;
              margin-bottom: 1.25rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .summary .header {{ text-align: center; margin-bottom: 1.25rem; padding-bottom: 1rem;
                      border-bottom: 1px solid #eee; }}
  .summary .header .channel {{ font-size: .75rem; font-weight: 600; text-transform: uppercase;
                               letter-spacing: .06em; color: #6b7280; margin-bottom: .25rem; }}
  .summary .header .datetime {{ font-size: 1.1rem; font-weight: 600; color: #1a1a1a; }}
  .summary h2 {{ font-size: 1.05rem; margin: 1.25rem 0 .5rem; color: #1a1a1a; }}
  .summary h3 {{ font-size: .95rem; margin: 1rem 0 .4rem; color: #374151; }}
  .summary p {{ margin: .5rem 0; line-height: 1.6; }}
  .summary ul {{ margin: .4rem 0 .4rem 1.25rem; }}
  .summary li {{ margin: .3rem 0; line-height: 1.55; }}
  .summary strong {{ color: #1a1a1a; }}
  .summary hr {{ border: none; border-top: 1px solid #eee; margin: 1.25rem 0; }}
  .summary a {{ color: #2563eb; text-decoration: none; }}
  .summary a:hover {{ text-decoration: underline; }}
  .empty {{ text-align: center; padding: 3rem; color: #888; }}

  /* Casino guide */
  #casino {{ background: #fff; border-radius: 8px; padding: 1.25rem 1.5rem;
             box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
  #casino h1 {{ font-size: 1.3rem; margin-bottom: .5rem; }}
  #casino h2 {{ font-size: 1.1rem; margin: 1.5rem 0 .5rem; padding-top: .75rem;
                border-top: 1px solid #eee; color: #1a1a1a; }}
  #casino h3 {{ font-size: 1rem; margin: 1rem 0 .3rem; color: #2563eb; }}
  #casino p {{ margin: .4rem 0; line-height: 1.6; }}
  #casino ul, #casino ol {{ margin: .3rem 0 .3rem 1.25rem; }}
  #casino li {{ margin: .2rem 0; line-height: 1.5; }}
  #casino hr {{ border: none; border-top: 1px solid #eee; margin: 1rem 0; }}

  /* Table */
  #casino table {{ width: 100%; border-collapse: collapse; margin: .75rem 0; font-size: .85rem;
                   display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
  #casino th {{ background: #f0f4ff; padding: .5rem .6rem; text-align: left; font-weight: 600;
                border-bottom: 2px solid #c7d2fe; white-space: nowrap; position: sticky; top: 0; }}
  #casino td {{ padding: .45rem .6rem; border-bottom: 1px solid #eee; vertical-align: top; }}
  #casino tr:hover td {{ background: #f8faff; }}

  /* Rating colors */
  .rating-high {{ color: #16a34a; font-weight: 700; }}
  .rating-mid {{ color: #ca8a04; font-weight: 600; }}
  .rating-low {{ color: #dc2626; font-weight: 600; }}

  @media (prefers-color-scheme: dark) {{
    body {{ background: #1a1a1a; color: #ddd; }}
    .tabs {{ background: #1a1a1a; border-bottom-color: #333; }}
    .tab {{ color: #888; }}
    .tab:hover {{ color: #ccc; }}
    .tab.active {{ color: #60a5fa; border-bottom-color: #60a5fa; }}
    .summary, #casino {{ background: #252525; box-shadow: 0 1px 3px rgba(0,0,0,.4); }}
    .summary .header {{ border-bottom-color: #333; }}
    .summary .header .channel {{ color: #9ca3af; }}
    .summary .header .datetime {{ color: #eee; }}
    .summary h2, .summary strong, #casino h1, #casino h2 {{ color: #eee; }}
    .summary h3 {{ color: #d1d5db; }}
    .summary hr {{ border-top-color: #333; }}
    .summary a {{ color: #60a5fa; }}
    #casino h3 {{ color: #60a5fa; }}
    #casino th {{ background: #2a2a3a; border-bottom-color: #444; }}
    #casino td {{ border-bottom-color: #333; }}
    #casino tr:hover td {{ background: #2a2a2a; }}
    #casino hr {{ border-top-color: #333; }}
    #casino h2 {{ border-top-color: #333; }}
  }}

  @media (max-width: 600px) {{
    #casino table {{ font-size: .75rem; }}
    #casino th, #casino td {{ padding: .35rem .4rem; }}
  }}
</style>
</head>
<body>
<div class="container">
  <div class="tabs">
    <button class="tab active" data-tab="summaries">Summaries</button>
    <button class="tab" data-tab="casino-guide">Casino Guide</button>
  </div>
  <div id="summaries" class="tab-panel active"></div>
  <div id="casino-guide" class="tab-panel">
    <div id="casino"></div>
  </div>
</div>
<script>
// Tab switching
document.querySelectorAll('.tab').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  }});
}});

// Summaries tab
const entries = {json.dumps(entries)};
const summariesEl = document.getElementById("summaries");
if (entries.length === 0) {{
  summariesEl.innerHTML = '<div class="empty">No summaries yet.</div>';
}} else {{
  entries.forEach(e => {{
    const div = document.createElement("div");
    div.className = "summary";
    div.innerHTML = marked.parse(e.content);
    // Normalize the h1 header into a styled centered block
    const h1 = div.querySelector('h1');
    if (h1) {{
      const text = h1.textContent;
      // Match patterns like "#bearcave-chat Monitor — 2026-03-13 7:07 AM" or "bearcave-chat Monitor — 2026-03-13 07:37"
      const m = text.match(/^#?\\s*(\\S+)\\s+Monitor\\s*[—–-]\\s*(\\d{{4}}-\\d{{2}}-\\d{{2}})\\s+(.+)$/i);
      if (m) {{
        const channel = m[1];
        const dateStr = m[2];
        const timeStr = m[3].trim();
        // Parse and format the date nicely
        const [y, mo, d] = dateStr.split('-');
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const formatted = months[parseInt(mo)-1] + ' ' + parseInt(d) + ', ' + y + ' · ' + timeStr;
        const hdr = document.createElement('div');
        hdr.className = 'header';
        hdr.innerHTML = '<div class="channel">' + channel + '</div><div class="datetime">' + formatted + '</div>';
        h1.replaceWith(hdr);
      }}
    }}
    summariesEl.appendChild(div);
  }});
}}

// Casino guide tab
const casinoContent = {json.dumps(casino_content)};
const casinoEl = document.getElementById("casino");
if (casinoContent) {{
  casinoEl.innerHTML = marked.parse(casinoContent);
  // Color-code ratings in table cells
  casinoEl.querySelectorAll('td').forEach(td => {{
    const m = td.textContent.match(/^(\\d+\\.?\\d?)\\/10$/);
    if (m) {{
      const v = parseFloat(m[1]);
      if (v >= 7) td.classList.add('rating-high');
      else if (v >= 5) td.classList.add('rating-mid');
      else td.classList.add('rating-low');
    }}
  }});
}} else {{
  casinoEl.innerHTML = '<div class="empty">No casino guide found.</div>';
}}
</script>
</div>
</body>
</html>"""

    os.makedirs("_site", exist_ok=True)
    with open("_site/index.html", "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Built _site/index.html with {len(entries)} summaries")

if __name__ == "__main__":
    build()
