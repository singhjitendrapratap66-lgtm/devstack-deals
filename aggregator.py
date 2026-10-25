#!/usr/bin/env python3
"""
Aggregator Engine: Fetches feeds, parses XML/RSS, injects tracking links, and saves structured JSON.
Zero external pip dependencies required (runs directly on Python 3 standard library).
"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
import datetime
import html
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 DevDealsBot/1.0"
}

MAX_FEED_BYTES = 2 * 1024 * 1024  # 2MB max payload per feed to prevent memory exhaustion / DoS attacks

def sanitize_url(raw_url: str) -> str:
    """Strictly validates URL scheme to prevent javascript:, data:, and malformed protocol attacks."""
    if not raw_url or not isinstance(raw_url, str):
        return "#"
    clean = raw_url.strip()
    clean = re.sub(r"[\x00-\x1f\x7f]", "", clean)
    try:
        parsed = urllib.parse.urlsplit(clean)
        if parsed.scheme.lower() not in ("http", "https"):
            return "#"
        if not parsed.netloc:
            return "#"
        return urllib.parse.urlunsplit(parsed)
    except Exception:
        return "#"

def clean_html(raw_html: str) -> str:
    """Removes HTML tags and cleans up whitespace."""
    if not raw_html:
        return ""
    # Strip dangerous HTML tags and content
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    clean = html.unescape(clean)
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", clean)
    return " ".join(clean.split())[:280]

def append_affiliate_query(url: str, param_str: str) -> str:
    """Safely appends tracking/affiliate query parameters to a target URL."""
    if not param_str or not url or url == "#":
        return url
    parts = list(urllib.parse.urlsplit(url))
    query = parts[3]
    if query:
        query = f"{query}&{param_str}"
    else:
        query = param_str
    parts[3] = query
    return urllib.parse.urlunsplit(parts)

def fetch_rss_feed(feed_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fetches an RSS/Atom feed and parses items into a unified deal format."""
    feed_url = feed_config.get("url")
    category = feed_config.get("category", "Tech & Software")
    source_name = feed_config.get("name", "Web")
    affiliate_param = feed_config.get("affiliate_param", "")
    
    if not feed_url or not isinstance(feed_url, str) or not feed_url.startswith(("http://", "https://")):
        print(f"[-] Security alert: Ignored invalid or non-HTTP feed URL: {feed_url}")
        return []
        
    items = []
    print(f"[*] Fetching feed: {source_name} ({feed_url})...")
    
    try:
        req = urllib.request.Request(feed_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as response:
            content = response.read(MAX_FEED_BYTES)
            
        root = ET.fromstring(content)
        
        # Handle standard RSS 2.0 channel/item
        channel = root.find("channel")
        entries = channel.findall("item") if channel is not None else []
        
        # Fallback for Atom feeds
        if not entries:
            entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            if not entries:
                entries = root.findall("entry")

        for entry in entries[:15]:
            title_elem = entry.find("title")
            if title_elem is None:
                title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                
            link_elem = entry.find("link")
            if link_elem is None:
                link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
                
            desc_elem = entry.find("description")
            if desc_elem is None:
                desc_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
            if desc_elem is None:
                desc_elem = entry.find("{http://www.w3.org/2005/Atom}content")
                
            pub_date_elem = entry.find("pubDate")
            if pub_date_elem is None:
                pub_date_elem = entry.find("{http://www.w3.org/2005/Atom}published")
            if pub_date_elem is None:
                pub_date_elem = entry.find("{http://www.w3.org/2005/Atom}updated")

            title = title_elem.text if title_elem is not None and title_elem.text else "Untitled Tool / Deal"
            
            raw_link = ""
            if link_elem is not None:
                raw_link = link_elem.get("href") or link_elem.text or ""
            
            raw_desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
            desc = clean_html(raw_desc)
            if not desc:
                desc = "Curated tech resource and developer tool offering special community access and tier limits."

            monetized_link = sanitize_url(append_affiliate_query(raw_link.strip(), affiliate_param))
            if monetized_link == "#":
                continue  # Skip items with dangerous or invalid URL schemes
            pub_date = pub_date_elem.text if pub_date_elem is not None and pub_date_elem.text else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

            items.append({
                "title": title.strip(),
                "description": desc,
                "url": monetized_link,
                "category": category,
                "source": source_name,
                "date": pub_date[:16],
                "badge": "COMMUNITY DEAL",
                "price": "Free / Discounted",
                "is_featured": False
            })

    except Exception as e:
        print(f"[-] Warning: Error fetching {feed_url}: {e}")
        
    return items

def run_aggregation(config_path="config.json", output_path="data/deals.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    all_deals = []
    
    # 1. Load hand-curated high-ticket affiliate deals first
    featured_deals = config.get("featured_deals", [])
    for deal in featured_deals:
        item = dict(deal)
        item["is_featured"] = True
        item["source"] = "Official Partner"
        item["date"] = datetime.datetime.now(datetime.timezone.utc).strftime("%b %d, %Y")
        all_deals.append(item)
        
    # 2. Fetch and aggregate dynamic RSS feeds
    feeds = config.get("feeds", [])
    for feed in feeds:
        feed_items = fetch_rss_feed(feed)
        all_deals.extend(feed_items)
        
    # Deduplicate by URL or title
    seen = set()
    unique_deals = []
    for d in all_deals:
        key = d.get("title", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique_deals.append(d)
            
    print(f"[+] Total verified deals processed: {len(unique_deals)} (Featured: {len(featured_deals)})")
    
    payload = {
        "metadata": {
            "site_name": config.get("site_name"),
            "site_description": config.get("site_description"),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total_items": len(unique_deals)
        },
        "deals": unique_deals
    }
    
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(payload, out, indent=2, ensure_ascii=False)
        
    print(f"[+] Saved structured data to {output_path}")
    return payload

if __name__ == "__main__":
    run_aggregation()
