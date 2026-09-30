#!/usr/bin/env python3
"""
Batch Tester for YouTube AI Detection
Fetches 2000 YouTube video URLs under 'techno' search queries
and runs NoAI detection heuristics against all of them in parallel.
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

SEARCH_QUERIES = [
    'techno',
    'techno mix',
    'dark techno',
    'industrial techno',
    'techno 2026',
    'techno 2025',
    'peak time techno',
    'hypnotic techno',
    'acid techno',
    'hard techno mix',
    'melodic techno',
    'underground techno',
    'raw techno',
    'cyberpunk techno',
    'dark techno session',
    'techno rave mix',
    'berlin techno mix',
    'warehouse techno',
    'minimal techno',
    'techno live set',
    'deep tech house',
    'techno no ads'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_search_video_ids(query):
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            # Deduplicate preserving order
            seen = set()
            unique_vids = []
            for v in vids:
                if v not in seen:
                    seen.add(v)
                    unique_vids.append(v)
            return unique_vids
    except Exception as e:
        print(f"⚠️ Warning fetching search query '{query}': {e}")
        return []

def evaluate_video(video_id):
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

    # 1. Official Disclosure
    if data['official_synthetic_label']:
        reasons.append("Official YouTube Disclosure")

    # 2. Curated Channels
    if any(cur in c_lower for cur in CURATED_CHANNELS):
        reasons.append("Curated AI Farm")

    # 3. Channel Name Regex
    if re.search(AI_CHANNEL_REGEX, c_lower, re.I):
        reasons.append("AI Channel Name")

    # 4. Keyword Matches
    text_to_scan = f"{norm_title} {norm_desc} {' '.join(keywords_list)}".lower()
    matched_kws = set()
    for kw in KEYWORDS:
        escaped_kw = re.escape(kw)
        pattern = r'(?:#|\b)' + escaped_kw + r'\b'
        if re.search(pattern, text_to_scan, re.I):
            matched_kws.add(kw)
    if matched_kws:
        reasons.append(f"Keyword: {', '.join(sorted(list(matched_kws))[:3])}")

    # 5. Direct Regexes
    if re.search(CONTENT_ID_AI_MUSIC_REGEX, norm_desc, re.I):
        reasons.append("Suno/Udio Content ID Footer")
    if re.search(SHORTS_AUTOMATION_REGEX, combined_text := f"{norm_title} {norm_desc}", re.I):
        reasons.append("AI Shorts Voiceover")

    # 6. Weighted Score Evaluation
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
    print("🔎 Collecting techno video URLs from YouTube search queries...")
    collected_vids = []
    seen = set()

    for q in SEARCH_QUERIES:
        vids = fetch_search_video_ids(q)
        for v in vids:
            if v not in seen:
                seen.add(v)
                collected_vids.append(v)
        print(f"  • Search '{q}': found {len(vids)} videos (Total unique so far: {len(collected_vids)})")
        if len(collected_vids) >= 2000:
            break

    total_to_test = min(len(collected_vids), 2000)
    target_vids = collected_vids[:total_to_test]
    print(f"\n🚀 Running NoAI inspection suite against {total_to_test} YouTube videos in parallel...\n")

    results = []
    ai_count = 0
    reason_counts = {}

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(evaluate_video, vid): vid for vid in target_vids}
        completed = 0
        for future in as_completed(futures):
            completed += 1
            res = future.result()
            if res:
                results.append(res)
                if res['is_ai']:
                    ai_count += 1
                    for r in set(res['reasons']):
                        reason_counts[r] = reason_counts.get(r, 0) + 1
            
            if completed % 100 == 0 or completed == total_to_test:
                print(f"  [Progress] Inspected {completed}/{total_to_test} videos... (AI Flagged so far: {ai_count})")

    elapsed = time.time() - start_time
    flagged_percent = (ai_count / max(len(results), 1)) * 100

    print("\n" + "=" * 70)
    print("📊 BATCH INSPECTION SUMMARY REPORT (TECHNO DOMAIN)")
    print("=" * 70)
    print(f" Total Videos Scanned : {len(results)}")
    print(f" Total AI Flagged      : {ai_count} ({flagged_percent:.1f}%)")
    print(f" Real / Human Tracks  : {len(results) - ai_count} ({100 - flagged_percent:.1f}%)")
    print(f" Execution Time       : {elapsed:.2f} seconds ({len(results)/elapsed:.1f} vids/sec)")
    print("-" * 70)
    print("🏆 BREAKDOWN OF MATCHED AI DETECTION REASONS:")
    for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {reason:<35} : {count} videos ({count/max(ai_count,1)*100:.1f}%)")
    print("=" * 70)

    # Save summary report to JSON
    report_file = '/home/oh2fxd/toolbox/python/noai/techno_batch_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_scanned': len(results),
            'ai_flagged_count': ai_count,
            'ai_flagged_percent': round(flagged_percent, 2),
            'execution_time_seconds': round(elapsed, 2),
            'reason_breakdown': reason_counts,
            'sample_ai_videos': [r for r in results if r['is_ai']][:50]
        }, f, indent=2)
    print(f"\n📁 Detailed batch report saved to: {report_file}\n")

if __name__ == "__main__":
    main()
