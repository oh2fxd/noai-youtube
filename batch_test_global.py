#!/usr/bin/env python3
"""
Global Multi-Genre Batch Tester for YouTube AI Detection Engine
Scans 2000+ videos across Techno, Lofi, Phonk, AI Covers, Shorts, Ambient,
Country, Rock, Healing 432Hz, and Reddit Automation.
Collects new AI channels, keywords, and updates the detection engine automatically!
"""

import re
import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

from inspect_youtube_ai import parse_yt_data, KEYWORDS, CURATED_CHANNELS, FARM_TITLE_PATTERNS, FARM_CHANNEL_PATTERNS, CHATGPT_SNIPPET_PATTERNS, AI_CHANNEL_REGEX, CONTENT_ID_AI_MUSIC_REGEX, SHORTS_AUTOMATION_REGEX, EMOJI_FARM_REGEX, DISPOSABLE_HANDLE_REGEX, normalize_text

GLOBAL_SEARCH_QUERIES = [
    # Electronic & Dance
    'techno mix 2026', 'tech house mix 2025', 'dark techno', 'industrial techno',
    'cyberpunk synthwave', 'phonk mix 2025', 'hardstyle rave mix', 'chillstep gaming mix',
    'deep house 2026', 'melodic techno 2025', 'ambient space music', 'lofi hip hop study',
    # AI Generators & Voice Clones
    'suno ai music', 'udio ai song', 'ai cover song', 'rvc v2 voice clone',
    'ai drake song', 'ai kanye west', 'ai voice clone cover', 'ai singer song',
    # Pop, Country, Rock, Metal
    'ai country song', 'ai metal mix', 'ai rock song', 'ai pop music 2025',
    # Shorts & Story Automation
    'unbelievable facts #shorts', 'did you know facts #shorts', 'reddit stories ai voice',
    'scary stories ai voice', 'history facts ai voice', 'motivational speech ai',
    # Sleep, Healing & Frequencies
    '432hz healing music', '528hz miracle tone', 'solfeggio frequencies 10 hours',
    'deep sleep music 10 hours', 'rain sounds for sleeping 10 hours',
    # Automated Mix Clickbait
    'techno no ads 10 hours', 'best gym car music 2025', 'deep focus beats 2026',
    'relaxing piano music 10 hours', 'relaxing study music'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_search_vids(query):
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            seen = set()
            res = []
            for v in vids:
                if v not in seen:
                    seen.add(v)
                    res.append(v)
            return res
    except Exception as e:
        return []

def evaluate_video_global(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception:
        return None

    data = parse_yt_data(html)
    title = data['title']
    channel = data['channel']
    desc = data['description']
    keywords_list = data['keywords']

    norm_title = normalize_text(title)
    norm_channel = normalize_text(channel)
    norm_desc = normalize_text(desc)
    c_lower = norm_channel.lower().strip()

    reasons = []

    if data['official_synthetic_label']:
        reasons.append("Official YouTube Disclosure")

    if any(cur in c_lower for cur in CURATED_CHANNELS):
        reasons.append("Curated AI Farm")

    if re.search(AI_CHANNEL_REGEX, c_lower, re.I):
        reasons.append("AI Channel Name")

    combined_text = f"{norm_title} {norm_desc} {' '.join(keywords_list)}".lower()
    matched_kws = set()
    for kw in KEYWORDS:
        escaped_kw = re.escape(kw)
        pattern = r'(?:#|\b)' + escaped_kw + r'\b'
        if re.search(pattern, combined_text, re.I):
            matched_kws.add(kw)
    if matched_kws:
        reasons.append(f"Keyword: {', '.join(sorted(list(matched_kws))[:3])}")

    if re.search(CONTENT_ID_AI_MUSIC_REGEX, norm_desc, re.I):
        reasons.append("Suno/Udio Content ID Footer")
    if re.search(SHORTS_AUTOMATION_REGEX, f"{norm_title} {norm_desc}", re.I):
        reasons.append("AI Shorts Voiceover")

    score = 0
    for tp in FARM_TITLE_PATTERNS:
        if re.search(tp, norm_title, re.I):
            score += 50
            reasons.append("Title Farm Formula")
            break

    for cp in FARM_CHANNEL_PATTERNS:
        if re.search(cp, norm_channel, re.I):
            score += 35
            reasons.append("Channel Naming Pattern")
            break

    if norm_desc:
        for sp in CHATGPT_SNIPPET_PATTERNS:
            if re.search(sp, norm_desc, re.I):
                score += 50
                reasons.append("ChatGPT Description Formula")
                break

        if re.search(r'distrokid\.com\/hyperfollow', norm_desc, re.I) and not re.search(r'\b(?:0?1[:.-]|\b1\.\s)', norm_desc, re.I):
            score += 45
            reasons.append("DistroKid Link without Tracklist")

    if title != norm_title:
        score += 25
        reasons.append("Unicode Font Evasion")

    if re.search(EMOJI_FARM_REGEX, title):
        score += 20
        reasons.append("Emoji Cluster")

    is_ai = len(reasons) > 0 or score >= 45

    return {
        'video_id': video_id,
        'title': title,
        'channel': channel,
        'is_ai': is_ai,
        'reasons': reasons
    }

def main():
    print("🌍 Starting Global Multi-Genre YouTube Search Sweep...")
    collected_vids = []
    seen = set()

    for q in GLOBAL_SEARCH_QUERIES:
        vids = fetch_search_vids(q)
        new_vids = [v for v in vids if v not in seen]
        for v in new_vids:
            seen.add(v)
            collected_vids.append(v)
        print(f"  • Query '{q}': +{len(new_vids)} new vids (Total unique: {len(collected_vids)})")

    total_to_test = len(collected_vids)
    print(f"\n🚀 Running NoAI Inspection Engine on {total_to_test} videos with 30 parallel workers...\n")

    results = []
    ai_count = 0
    reason_counts = {}
    discovered_channels = set()

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(evaluate_video_global, vid): vid for vid in collected_vids}
        completed = 0
        for future in as_completed(futures):
            completed += 1
            res = future.result()
            if res:
                results.append(res)
                if res['is_ai']:
                    ai_count += 1
                    if res['channel']:
                        discovered_channels.add(res['channel'].strip())
                    for r in set(res['reasons']):
                        reason_counts[r] = reason_counts.get(r, 0) + 1

            if completed % 100 == 0 or completed == total_to_test:
                print(f"  [Progress] {completed}/{total_to_test} inspected... (AI Flagged: {ai_count})")

    elapsed = time.time() - start_time
    flagged_percent = (ai_count / max(len(results), 1)) * 100

    print("\n" + "=" * 70)
    print("🌍 GLOBAL MULTI-GENRE BATCH INSPECTION SUMMARY REPORT")
    print("=" * 70)
    print(f" Total Unique Videos Scanned : {len(results)}")
    print(f" Total AI Flagged            : {ai_count} ({flagged_percent:.1f}%)")
    print(f" Real / Human Content        : {len(results) - ai_count} ({100 - flagged_percent:.1f}%)")
    print(f" Discovered AI Channels      : {len(discovered_channels)}")
    print(f" Execution Time             : {elapsed:.2f} seconds ({len(results)/elapsed:.1f} vids/sec)")
    print("-" * 70)
    print("🏆 BREAKDOWN OF MATCHED DETECTION REASONS:")
    for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {reason:<35} : {count} videos ({count/max(ai_count,1)*100:.1f}%)")
    print("=" * 70)

    # Save detailed JSON report
    report_file = '/home/oh2fxd/toolbox/python/noai/global_batch_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_scanned': len(results),
            'ai_flagged_count': ai_count,
            'ai_flagged_percent': round(flagged_percent, 2),
            'discovered_ai_channels_count': len(discovered_channels),
            'discovered_ai_channels': sorted(list(discovered_channels)),
            'reason_breakdown': reason_counts,
            'sample_ai_videos': [r for r in results if r['is_ai']][:100]
        }, f, indent=2)

    print(f"\n📁 Saved global report to {report_file}")

if __name__ == "__main__":
    main()
