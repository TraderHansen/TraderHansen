#!/usr/bin/env python3
"""生成 profile 用的自绘 SVG 状态卡（零依赖，Actions 里直接跑）。

玩法说明：仓库不只是存代码，也可以当「渲染结果」的存储。
CI 每天跑一次，把真实抓到的数据画成 SVG 提交回仓库，README 里 <img> 引用它——
于是主页上就有一张没有任何第三方服务、完全自控的动态卡片。
"""
from __future__ import annotations

import datetime
import json
import re
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "status.svg"
UA = "Mozilla/5.0 (profile-card; +https://github.com/TraderHansen)"


def get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def dmit_stock() -> tuple[int, int]:
    try:
        html = get("https://stock.dmitea.com/")
        return len(re.findall("status-in-stock", html)), len(re.findall("status-out-of-stock", html))
    except Exception:
        return -1, -1


def uv_version() -> str:
    try:
        return json.loads(get("https://api.github.com/repos/astral-sh/uv/releases/latest")).get("tag_name", "—")
    except Exception:
        return "—"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    instock, outstock = dmit_stock()
    uv = uv_version()
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    stamp = now.strftime("%Y-%m-%d %H:%M CST")

    total = instock + outstock if instock >= 0 else 0
    ratio = (instock / total) if total else 0.0
    bar_w = int(240 * ratio)
    hot = instock > 0
    accent = "#3fb950" if hot else "#8b949e"
    instock_txt = "—" if instock < 0 else str(instock)
    outstock_txt = "—" if outstock < 0 else str(outstock)

    svg = f"""<svg width="860" height="270" viewBox="0 0 860 270" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="TraderHansen 自动巡检卡片">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#3fb950"/>
      <stop offset="100%" stop-color="#56d364"/>
    </linearGradient>
  </defs>

  <rect x="0.5" y="0.5" width="859" height="269" rx="14" fill="url(#bg)" stroke="#30363d"/>

  <circle cx="28" cy="34" r="5" fill="{accent}"/>
  <text x="44" y="39" fill="#e6edf3" font-size="16" font-weight="600"
        font-family="'PingFang SC','Microsoft YaHei',system-ui,sans-serif">TraderHansen · 自动巡检</text>
  <text x="832" y="39" fill="#8b949e" font-size="12" text-anchor="end"
        font-family="ui-monospace,SFMono-Regular,Menlo,monospace">{esc(stamp)}</text>

  <line x1="24" y1="58" x2="836" y2="58" stroke="#21262d"/>

  <text x="28" y="92" fill="#8b949e" font-size="12" font-family="'PingFang SC',system-ui,sans-serif">DMIT 限量款在售</text>
  <text x="28" y="146" fill="{accent}" font-size="44" font-weight="700"
        font-family="ui-monospace,SFMono-Regular,Menlo,monospace">{instock_txt}</text>
  <text x="28" y="172" fill="#6e7681" font-size="12" font-family="'PingFang SC',system-ui,sans-serif">共 {total} 款跟踪</text>

  <rect x="28" y="186" width="240" height="6" rx="3" fill="#21262d"/>
  <rect x="28" y="186" width="{bar_w}" height="6" rx="3" fill="url(#bar)"/>

  <line x1="300" y1="76" x2="300" y2="200" stroke="#21262d"/>

  <text x="330" y="92" fill="#8b949e" font-size="12" font-family="'PingFang SC',system-ui,sans-serif">缺货</text>
  <text x="330" y="146" fill="#c9d1d9" font-size="44" font-weight="700"
        font-family="ui-monospace,SFMono-Regular,Menlo,monospace">{outstock_txt}</text>
  <text x="330" y="172" fill="#6e7681" font-size="12" font-family="'PingFang SC',system-ui,sans-serif">补货即推送</text>

  <line x1="470" y1="76" x2="470" y2="200" stroke="#21262d"/>

  <text x="500" y="92" fill="#8b949e" font-size="12" font-family="'PingFang SC',system-ui,sans-serif">uv 最新版本</text>
  <text x="500" y="143" fill="#58a6ff" font-size="34" font-weight="700"
        font-family="ui-monospace,SFMono-Regular,Menlo,monospace">{esc(uv)}</text>
  <text x="500" y="172" fill="#6e7681" font-size="12" font-family="'PingFang SC',system-ui,sans-serif">GitHub Releases API</text>

  <line x1="24" y1="214" x2="836" y2="214" stroke="#21262d"/>
  <text x="28" y="240" fill="#6e7681" font-size="11.5"
        font-family="'PingFang SC',system-ui,sans-serif">本卡片由 GitHub Actions 每日生成并提交回仓库，无第三方图床、无外部统计服务</text>
  <text x="832" y="240" fill="#484f58" font-size="11" text-anchor="end"
        font-family="ui-monospace,SFMono-Regular,Menlo,monospace">github.com/TraderHansen</text>
</svg>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"written {OUT} ({OUT.stat().st_size} bytes) | dmit in={instock} out={outstock} | uv={uv}")


if __name__ == "__main__":
    main()
