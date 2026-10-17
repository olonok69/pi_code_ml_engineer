#!/usr/bin/env python3
"""
Capture the ticket knowledge graph (docs/knowledge-graph/output/graph.html, an
interactive vis-network page) as a PNG for the Part 3 slide.

    uv run --with playwright python presentation/capture_kg_graph.py   # -> kg_graph.png

Uses an installed Chromium/Chrome (PW_CHANNEL=chrome by default; set PW_CHANNEL="" for
playwright's bundled chromium). Waits for the vis-network physics to settle before
shooting. Needs network for the vis-network CDN (unpkg) the first time.
"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "..", "docs", "knowledge-graph", "output", "graph.html")
OUT = os.path.join(HERE, "kg_graph.png")

with sync_playwright() as p:
    channel = os.environ.get("PW_CHANNEL", "chrome") or None
    browser = p.chromium.launch(channel=channel)
    page = browser.new_page(viewport={"width": 1760, "height": 990}, device_scale_factor=2)
    page.goto("file://" + os.path.abspath(HTML))
    page.wait_for_function("typeof vis !== 'undefined'", timeout=30000)
    # let the physics settle and the initial fit() happen
    page.wait_for_timeout(25000)
    page.screenshot(path=OUT)
    browser.close()
print(f"OK -> {OUT}")
