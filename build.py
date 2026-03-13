#!/usr/bin/env python3
"""
Multi-source site builder.

Reads from sibling directories in the projects/ folder based on the SOURCES
config below. Only files matching the configured patterns are read — nothing
else leaves these folders. The output is a single _site/index.html.

To add a new source: add an entry to SOURCES and the tab will appear
automatically.
"""

import glob
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.dirname(SCRIPT_DIR)  # ../projects/

# ── Source configuration ─────────────────────────────────────────────
# Each source defines:
#   id       — unique key, used as HTML element id
#   label    — tab name shown on the site
#   type     — "summaries" (multiple .md, most-recent-first)
#              "single"    (one specific .md file rendered as-is)
#   path     — directory relative to PROJECTS_DIR
#   pattern  — glob pattern for "summaries" type
#   exclude  — filenames to skip (for "summaries" type)
#   file     — specific filename for "single" type
#   limit    — max entries for "summaries" type (default 8)

SOURCES = [
    {
        "id": "summaries",
        "label": "Bearcave",
        "type": "summaries",
        "path": "bearcave",
        "pattern": "*.md",
        "exclude": ["casino-master-summary.md", "discord-monitor-instructions.md"],
        "limit": 8,
    },
    {
        "id": "casino-guide",
        "label": "Casino Guide",
        "type": "single",
        "path": "bearcave",
        "file": "casino-master-summary.md",
    },
    {
        "id": "doc-digest",
        "label": "DoC Digest",
        "type": "summaries",
        "path": "doctorofcredit",
        "pattern": "*.md",
        "exclude": [],
        "limit": 8,
    },
    # To add another source, copy this template:
    # {
    #     "id": "ruby",
    #     "label": "Ruby",
    #     "type": "summaries",
    #     "path": "ruby",
    #     "pattern": "*.md",
    #     "exclude": [],
    #     "limit": 8,
    # },
]


def load_summaries(source):
    """Load markdown files matching pattern, sorted newest-first."""
    src_dir = os.path.join(PROJECTS_DIR, source["path"])
    if not os.path.isdir(src_dir):
        return []
    files = sorted(
        [
            f
            for f in glob.glob(os.path.join(src_dir, source["pattern"]))
            if os.path.basename(f) not in source.get("exclude", [])
        ],
        reverse=True,
    )[: source.get("limit", 8)]
    entries = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            entries.append({"filename": os.path.basename(f), "content": fh.read()})
    return entries


def load_single(source):
    """Load a single markdown file."""
    filepath = os.path.join(PROJECTS_DIR, source["path"], source["file"])
    if not os.path.exists(filepath):
        return ""
    with open(filepath, encoding="utf-8") as fh:
        return fh.read()


def build():
    # Gather data for each source
    tab_data = []
    for src in SOURCES:
        if src["type"] == "summaries":
            entries = load_summaries(src)
            tab_data.append({**src, "entries": entries, "content": ""})
        elif src["type"] == "single":
            content = load_single(src)
            tab_data.append({**src, "entries": [], "content": content})

    # Build tab buttons
    tab_buttons = ""
    for i, tab in enumerate(tab_data):
        active = " active" if i == 0 else ""
        tab_buttons += f'    <button class="tab{active}" data-tab="{tab["id"]}">{tab["label"]}</button>\n'

    # Build tab panels
    tab_panels = ""
    for i, tab in enumerate(tab_data):
        active = " active" if i == 0 else ""
        tab_panels += f'  <div id="{tab["id"]}" class="tab-panel{active}">\n'
        if tab["type"] == "single":
            tab_panels += f'    <div id="{tab["id"]}-content"></div>\n'
        tab_panels += f'  </div>\n'

    # Build JS data
    js_data = ""
    for tab in tab_data:
        var = f'data_{tab["id"].replace("-", "_")}'
        if tab["type"] == "summaries":
            js_data += f'const {var} = {json.dumps(tab["entries"])};\n'
        elif tab["type"] == "single":
            js_data += f'const {var} = {json.dumps(tab["content"])};\n'

    # Build JS render logic
    js_render = ""
    for tab in tab_data:
        var = f'data_{tab["id"].replace("-", "_")}'
        el_id = tab["id"]
        if tab["type"] == "summaries":
            js_render += f"""
(function() {{
  const el = document.getElementById("{el_id}");
  const entries = {var};
  if (entries.length === 0) {{
    el.innerHTML = '<div class="empty">No entries yet.</div>';
  }} else {{
    entries.forEach(e => {{
      const div = document.createElement("div");
      div.className = "summary";
      div.innerHTML = marked.parse(e.content);
      const h1 = div.querySelector('h1');
      if (h1) {{
        const text = h1.textContent;
        const m = text.match(/^#?\\s*(\\S+)\\s+Monitor\\s*[—–-]\\s*(\\d{{4}}-\\d{{2}}-\\d{{2}})\\s+(.+)$/i);
        if (m) {{
          const channel = m[1];
          const dateStr = m[2];
          const rawTime = m[3].trim();
          const timeDisplay = to12h(rawTime);
          const [y, mo, d] = dateStr.split('-');
          const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
          const formatted = months[parseInt(mo)-1] + ' ' + parseInt(d) + ', ' + y + ' · ' + timeDisplay + ' EST';
          const hdr = document.createElement('div');
          hdr.className = 'header';
          hdr.innerHTML = '<div class="channel">' + channel + '</div><div class="datetime">' + formatted + '</div>';
          h1.replaceWith(hdr);
        }}
      }}
      div.querySelectorAll('h3').forEach(h3 => {{
        h3.innerHTML = h3.innerHTML.replace(/\\s*\\(\\d{{1,2}}:\\d{{2}}(\\s*[APap][Mm])?\\)\\s*/g, ' ').trim();
      }});
      el.appendChild(div);
    }});
  }}
}})();
"""
        elif tab["type"] == "single":
            js_render += f"""
(function() {{
  const el = document.getElementById("{el_id}-content");
  const content = {var};
  if (content) {{
    el.innerHTML = marked.parse(content);
    el.querySelectorAll('td').forEach(td => {{
      const m = td.textContent.match(/^(\\d+\\.?\\d?)\\/10$/);
      if (m) {{
        const v = parseFloat(m[1]);
        if (v >= 7) td.classList.add('rating-high');
        else if (v >= 5) td.classList.add('rating-mid');
        else td.classList.add('rating-low');
      }}
    }});
  }} else {{
    el.innerHTML = '<div class="empty">No content found.</div>';
  }}
}})();
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cowork Projects</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #f5f5f5; color: #222; margin: 0; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 0 1rem 1rem; }}

  .tabs {{ display: flex; gap: 0; border-bottom: 2px solid #ddd; margin-bottom: 1rem;
           position: sticky; top: 0; background: #f5f5f5; padding-top: 1rem; z-index: 10;
           flex-wrap: wrap; }}
  .tab {{ padding: .6rem 1.25rem; cursor: pointer; border: none; background: none;
          font-size: .95rem; font-weight: 500; color: #666; border-bottom: 2px solid transparent;
          margin-bottom: -2px; transition: color .15s, border-color .15s; }}
  .tab:hover {{ color: #333; }}
  .tab.active {{ color: #2563eb; border-bottom-color: #2563eb; }}
  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}

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

  .single-content {{ background: #fff; border-radius: 8px; padding: 1.25rem 1.5rem;
             box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
  .single-content h1 {{ font-size: 1.3rem; margin-bottom: .5rem; }}
  .single-content h2 {{ font-size: 1.1rem; margin: 1.5rem 0 .5rem; padding-top: .75rem;
                border-top: 1px solid #eee; color: #1a1a1a; }}
  .single-content h3 {{ font-size: 1rem; margin: 1rem 0 .3rem; color: #2563eb; }}
  .single-content p {{ margin: .4rem 0; line-height: 1.6; }}
  .single-content ul, .single-content ol {{ margin: .3rem 0 .3rem 1.25rem; }}
  .single-content li {{ margin: .2rem 0; line-height: 1.5; }}
  .single-content hr {{ border: none; border-top: 1px solid #eee; margin: 1rem 0; }}
  .single-content table {{ width: 100%; border-collapse: collapse; margin: .75rem 0; font-size: .85rem;
                   display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
  .single-content th {{ background: #f0f4ff; padding: .5rem .6rem; text-align: left; font-weight: 600;
                border-bottom: 2px solid #c7d2fe; white-space: nowrap; position: sticky; top: 0; }}
  .single-content td {{ padding: .45rem .6rem; border-bottom: 1px solid #eee; vertical-align: top; }}
  .single-content tr:hover td {{ background: #f8faff; }}

  .rating-high {{ color: #16a34a; font-weight: 700; }}
  .rating-mid {{ color: #ca8a04; font-weight: 600; }}
  .rating-low {{ color: #dc2626; font-weight: 600; }}

  @media (prefers-color-scheme: dark) {{
    body {{ background: #1a1a1a; color: #ddd; }}
    .tabs {{ background: #1a1a1a; border-bottom-color: #333; }}
    .tab {{ color: #888; }}
    .tab:hover {{ color: #ccc; }}
    .tab.active {{ color: #60a5fa; border-bottom-color: #60a5fa; }}
    .summary, .single-content {{ background: #252525; box-shadow: 0 1px 3px rgba(0,0,0,.4); }}
    .summary .header {{ border-bottom-color: #333; }}
    .summary .header .channel {{ color: #9ca3af; }}
    .summary .header .datetime {{ color: #eee; }}
    .summary h2, .summary strong, .single-content h1, .single-content h2 {{ color: #eee; }}
    .summary h3 {{ color: #d1d5db; }}
    .summary hr {{ border-top-color: #333; }}
    .summary a {{ color: #60a5fa; }}
    .single-content h3 {{ color: #60a5fa; }}
    .single-content th {{ background: #2a2a3a; border-bottom-color: #444; }}
    .single-content td {{ border-bottom-color: #333; }}
    .single-content tr:hover td {{ background: #2a2a2a; }}
    .single-content hr {{ border-top-color: #333; }}
    .single-content h2 {{ border-top-color: #333; }}
  }}

  @media (max-width: 600px) {{
    .single-content table {{ font-size: .75rem; }}
    .single-content th, .single-content td {{ padding: .35rem .4rem; }}
  }}
</style>
</head>
<body>
<div class="container">
  <div class="tabs">
{tab_buttons}  </div>
{tab_panels}</div>
<script>
document.querySelectorAll('.tab').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  }});
}});

function to12h(t) {{
  if (/[ap]m/i.test(t)) return t.toUpperCase().replace(/(\\d)(AM|PM)/, '$1 $2');
  const p = t.match(/^(\\d{{1,2}}):(\\d{{2}})$/);
  if (p) {{
    let h = parseInt(p[1]), mn = p[2];
    const ampm = h >= 12 ? 'PM' : 'AM';
    if (h === 0) h = 12;
    else if (h > 12) h -= 12;
    return h + ':' + mn + ' ' + ampm;
  }}
  return t;
}}

{js_data}
document.querySelectorAll('.tab-panel').forEach(panel => {{
  const contentDiv = panel.querySelector('[id$="-content"]');
  if (contentDiv) contentDiv.classList.add('single-content');
}});

{js_render}
</script>
</body>
</html>"""

    out_dir = os.path.join(SCRIPT_DIR, "_site")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    summary_count = sum(len(t.get("entries", [])) for t in tab_data)
    print(f"Built {out_path} with {len(tab_data)} tabs, {summary_count} total entries")


if __name__ == "__main__":
    build()
