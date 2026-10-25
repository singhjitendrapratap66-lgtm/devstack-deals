#!/usr/bin/env python3
"""
Static Site Builder:
Takes aggregated data/deals.json and compiles it into a high-performance,
SEO-ready, single-page web application in dist/index.html.
"""
import json
import html
import urllib.parse
import re
from typing import Dict, Any

def validate_safe_url(raw_url: str) -> str:
    """Ensures URL strictly uses http or https protocol to prevent XSS / javascript: execution."""
    if not raw_url or not isinstance(raw_url, str):
        return "#"
    clean = raw_url.strip()
    clean = re.sub(r"[\x00-\x1f\x7f]", "", clean)
    try:
        parsed = urllib.parse.urlsplit(clean)
        if parsed.scheme.lower() not in ("http", "https"):
            return "#"
        return clean
    except Exception:
        return "#"

def render_deal_card(deal: Dict[str, Any]) -> str:
    title = html.escape(str(deal.get("title", "")), quote=True)
    desc = html.escape(str(deal.get("description", "")), quote=True)
    raw_url = validate_safe_url(deal.get("url", "#"))
    url = html.escape(raw_url, quote=True)
    category = html.escape(str(deal.get("category", "General")), quote=True)
    badge = html.escape(str(deal.get("badge", "DEAL")), quote=True)
    price = html.escape(str(deal.get("price", "Free / Discounted")), quote=True)
    orig_price = deal.get("original_price")
    is_featured = bool(deal.get("is_featured", False))
    source = html.escape(str(deal.get("source", "Web")), quote=True)
    
    featured_class = "is-featured" if is_featured else ""
    badge_class = "badge-partner" if is_featured else "badge-community"
    
    orig_price_html = f'<span class="original-price">{html.escape(str(orig_price), quote=True)}</span>' if orig_price else ""
    
    # Generate clean affiliate card HTML
    return f"""
      <article class="deal-card {featured_class}" data-title="{title}" data-desc="{desc}" data-category="{category}">
        <div class="card-top">
          <span class="deal-badge {badge_class}">{badge}</span>
          <span class="deal-category">{category}</span>
        </div>
        <h2 class="deal-title">{title}</h2>
        <p class="deal-desc">{desc}</p>
        <div class="pricing-box">
          <div>
            <span class="price-value">{price}</span>
            {orig_price_html}
          </div>
          <span style="font-size:0.75rem; color:#64748b;">Source: {source}</span>
        </div>
        <a href="{url}" target="_blank" rel="noopener noreferrer sponsored" class="deal-btn">
          Claim Deal / View Tool &rarr;
        </a>
      </article>
    """

def build_site(data_path="data/deals.json", template_path="templates/index.html", output_path="dist/index.html"):
    print("[*] Compiling static site...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    metadata = data.get("metadata", {})
    deals = data.get("deals", [])
    
    cards_html = "\n".join([render_deal_card(d) for d in deals])
    
    rendered = template.replace("{{site_name}}", html.escape(str(metadata.get("site_name", "Dev Deals")), quote=True))
    rendered = rendered.replace("{{site_description}}", html.escape(str(metadata.get("site_description", "")), quote=True))
    rendered = rendered.replace("{{updated_at}}", html.escape(str(metadata.get("updated_at", "")), quote=True))
    rendered = rendered.replace("{{total_items}}", str(len(deals)))
    rendered = rendered.replace("{{deals_html}}", cards_html)
    
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(rendered)
        
    print(f"[+] Static website generated successfully at {output_path} ({len(deals)} items)")

if __name__ == "__main__":
    build_site()
