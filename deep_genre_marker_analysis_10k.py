#!/usr/bin/env python3
"""
10,000-Video Deep AI Marker Analysis (2,000 Videos per Genre Cluster)
Harvests 2,000 unique videos per genre across 5 major music/content categories:
1. Techno & Electronic (2,000 videos)
2. Ambient, Piano & Relaxation (2,000 videos)
3. Phonk, Trap & Gym (2,000 videos)
4. Lofi & Chill Beats (2,000 videos)
5. AI Music & Synthetic Media (2,000 videos)

Extracts comprehensive marker profiles for all detected AI content:
- Emoji distribution
- Hashtag usage
- ChatGPT bio/description text patterns
- Title formulas & clickbait markers
- Channel naming styles
- YouTube native disclosure badges vs heuristics vs keywords
"""

import re
import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

# 5 Major Genre Clusters with 50 diverse queries each to reach 2,000 videos per genre
GENRE_CLUSTERS = {
    "Techno & Electronic": [
        "techno mix 2026", "dark techno mix", "industrial techno rave", "peak time techno set",
        "minimal techno mix", "acid techno 303", "melodic techno 2025", "cyberpunk techno session",
        "goth dark techno", "hard techno rave 2026", "underground techno session", "berlin techno mix",
        "hypnotic techno session", "detroit techno classics", "raw industrial techno", "driving techno set",
        "dark forest rave techno", "toxic techno energy", "deep hypnotic techno", "hard acid rave",
        "techno warehouse party", "peak time acid set", "hardstyle rave mix", "rawstyle festival mix",
        "drum and bass 2026", "liquid dnb study", "dubstep bangers 2025", "psytrance festival mix",
        "afro house 2025", "slap house party", "electro house mix", "vocal trance mix", "progressive house set",
        "deep house 2026", "eurodance 90s mix", "hard trance classics", "tech house mix 2025",
        "club dance mix 2026", "edm festival mix", "future bass bangers", "bass house 2025",
        "dark rave session", "underground warehouse techno", "hard club beats", "electro synth mix",
        "peak time rave 2025", "toxic euphoria mix", "hypnotic underground mix", "cyber rave energy"
    ],

    "Ambient, Piano & Relaxation": [
        "relaxing piano music sleep", "528hz sleep music 10 hours", "432hz miracle tone healing",
        "dark ambient 10 hours", "meditation piano zen", "deep sleep rain sounds 10 hours",
        "calm relaxing guitar", "solfeggio frequencies 10 hours", "binaural beats focus", "peaceful piano",
        "ambient space music 10h", "sleep music deep rest", "piano music for studying", "calm piano mix",
        "nature sounds 10 hours", "relaxing piano and rain", "healing frequencies 528", "deep ambient sleep",
        "meditation music 10 hours", "soft piano sleep", "zen spa music", "stress relief ambient", "calm acoustic guitar",
        "relaxing ocean waves 10h", "forest rain sounds 10h", "tibetan singing bowls 10h", "delta waves sleep",
        "theta waves concentration", "alpha waves focus", "deep space ambient 10h", "peaceful guitar acoustic",
        "relaxing piano balcony", "cozy rain piano", "sleep music insomnia", "pure aura healing 432hz",
        "chopin relaxing piano", "beethoven calm piano", "mozart study music", "baroque relaxation",
        "gentle piano lullaby", "soothing piano melody", "calm sleep radio", "tranquil nature piano",
        "spiritual healing 528hz", "reiki healing music 10h", "deep focus binaural", "mindfulness meditation"
    ],

    "Phonk, Trap & Gym": [
        "drift phonk mix 2026", "aggressive phonk gym", "memphis phonk 90s", "phonk remix 2025",
        "trap metal mix", "hard trap beat 2025", "cloud rap mix", "underground phonk session",
        "gym phonk workout", "brazilian phonk 2026", "funk mandelao remix", "aggressive gym beats",
        "hard phonk 2025", "slowed down phonk", "phonk radio 24/7", "cowbell phonk mix",
        "drift phonk car mix", "tokyo drift phonk", "hyperphonk mix", "hardstyle phonk gym",
        "memphis rap underground", "dark phonk workout", "phonk bass boosted", "trap workout mix 2026",
        "gym motivation music", "heavy trap bangers", "phonk metal gym", "hardcore phonk mix",
        "drift phonk bass", "aggressive rage trap", "underground trap mix", "phonk wave 2025",
        "cyberpunk phonk", "demon phonk workout", "night drive phonk", "sigma phonk music",
        "brazilian funk 2026", "phonk gym workout 2025", "ultra bass phonk", "dark trap beat",
        "phonk compilation 2026", "speed up phonk", "phonk remix gaming", "hard drift beats",
        "phonk energy mix", "gym rage mix", "hard phonk bass boosted", "phonk 10 hours mix"
    ],

    "Lofi & Chill Beats": [
        "lofi hip hop study beats", "chillhop radio stream", "lofi beats to relax to", "chill lofi mix",
        "lofi sleep beats", "lo-fi hip hop chill", "study lofi 10 hours", "late night lofi mix",
        "cozy lofi rain", "japanese lofi chill", "lofi anime study", "lofi hip hop radio 24/7",
        "aesthetic lofi mix", "coffee shop lofi", "lofi jazz hip hop", "sad lofi beats",
        "chillhop study beats", "lofi guitar chill", "vintage lofi mix", "soft lofi sleep",
        "lofi hip hop 2026", "gaming lofi beats", "lofi study session", "autumn lofi mix",
        "winter lofi beats", "spring lofi chill", "summer lofi radio", "retro lofi beats",
        "lofi space chill", "lofi city rain", "bedroom lofi mix", "peaceful lofi beats",
        "lofi chillout session", "lofi piano study", "relaxing lofi beats", "lofi beats for work",
        "lofi instrumental hip hop", "lofi nostalgia beats", "nighttime lofi study", "lofi rain 10 hours",
        "cozy room lofi", "lofi homework beats", "lofi coffee house", "chill lofi hip hop stream",
        "lofi beats to sleep", "lofi focus beats", "ambient lofi mix", "lofi study radio"
    ],

    "AI Music & Synthetic Media": [
        "suno ai music bangers", "udio ai song mix", "ai drake cover song", "ai kanye west song",
        "ai singer song 2025", "ai cover song full", "rvc v2 voice clone", "made with suno ai",
        "generated by udio", "ai generated vocal trance", "ai michael jackson song", "ai eminem rap",
        "ai taylor swift song", "ai spongebob cover", "ai trump song", "ai biden rap",
        "suno v3.5 country song", "suno v4 metal mix", "udio v2 rock song", "ai song generator showcase",
        "ai voice clone cover", "ai duet song", "prompted ai music", "ai beat prod by gpt",
        "ai generated rap song", "ai synthwave song", "ai pop music 2025", "ai acoustic song",
        "suno ai radio", "udio ai playlist", "ai voice clone tutorial", "ai song creation demo",
        "ai singer cover 2026", "ai heavy metal song", "ai lo-fi beats", "ai phonk track",
        "ai cover full album", "ai vocal clone generator", "elevenlabs voice clone story", "ai deepfake song",
        "ai character voice song", "ai rap battle", "ai cover viral tiktok", "suno studio showcase",
        "udio v1.5 bangers", "ai generated anime song", "ai music showcase 2026", "ai cover playlist"
    ]
}

KEYWORDS = [
    'suno', 'suno.ai', 'suno ai', 'suno v3', 'suno v3.5', 'suno v4', 'suno v5', 'suno v6', 'suno studio',
    'udio', 'udio.ai', 'udio ai', 'udio v1', 'udio v1.5', 'udio v2',
    'elevenlabs', 'eleven labs', '11labs', 'fakeyou', 'uberduck', 'tortoise tts', 'rvc', 'rvc v2',
    'so-vits-svc', 'sovits', 'bark ai', 'voice clone', 'voice cloning', 'ai voice', 'ai vocals',
    'ai singer', 'ai cover', 'ai covers', 'ai duet', 'ai song', 'ai songs', 'ai rap', 'ai beat', 'ai beats',
    'ai track', 'ai tracks', 'ai audio', 'ai generated music', 'ai generated song', 'prompted music', 'riffusion', 'musicgen',
    'ai drake', 'ai kanye', 'ai trump', 'ai biden', 'ai obama', 'ai spongebob', 'ai plankton',
    'ai michael jackson', 'ai freddie mercury', 'ai the weeknd', 'ai eminem', 'ai taylor swift',
    'sora 2', 'sora openai', 'sora ai', 'runwayml', 'gen-2', 'gen-3', 'gen-3 alpha', 'gen3 alpha',
    'kling ai', 'kling 1.5', 'pika labs', 'pika 1.0', 'pika 2.0', 'luma ai', 'luma dream machine',
    'minimax video', 'minimax ai', 'hailuo ai', 'hailuo 01', 'haiper ai', 'viggle ai', 'google veo', 'veo google',
    'ltx video', 'cogvideo', 'mochi 1', 'wan 2.1', 'wan2.1', 'hunyuan video', 'animatediff',
    'deforum stable diffusion', 'infinite zoom ai',
    'ai animation', 'ai animated video', 'ai film', 'ai movie', 'ai cinema', 'ai trailer', 'ai visualizer',
    'midjourney v5', 'midjourney v6', 'midjourney v7', 'dall-e 3', 'dalle3',
    'stable diffusion', 'sdxl', 'sd1.5', 'sd3', 'flux.1', 'flux dev', 'flux schnell', 'recraft',
    'comfyui', 'leonardo ai', 'ideogram ai', 'magnific ai',
    'ai art generator', 'ai artwork generator', 'ai illustration generator',
    'generative ai music', 'ai generated video', 'ai generated track',
    'generated with ai', 'generated by ai', 'made with ai', 'created with ai', 'created using ai',
    'powered by ai', 'synthesized with ai', 'synthetic media', 'synthetic voice',
    'ai model prompt', 'prompts shared',
    'suno.com', 'udio.com', 'elevenlabs.io', 'midjourney.com', 'replicate.com/spaces',
    'ki generiert', 'generado por ia', 'hecho con ia', 'généré par ia', 'создано ии', 'нейросеть',
    'ai生成', '画像生成ai', '音楽生成ai'
]

CURATED_AI_CHANNELS = [
    'amoda session', 'astral phonk', 'atus music', 'berlin pulse', 'brahman games',
    'chili ai music', 'chill music lab', 'cinecipher', 'cybermode beats', 'cyberfalco',
    'cyber cyber', 'cyprus rave', 'dark noir techno', 'deep flow techno', 'digital pulse beats',
    'dolopz', 'dreamy darlings', 'echoloop', 'far east echoes', 'fristok', 'goth dark techno',
    'grand sound', 'grandsound', 'hard wind frequencies', 'helio432hz', 'human music',
    'hypertechfury', 'hypnotic night sessions', 'krya dark tech', 'larub techno sessions',
    'magic techno', 'melodic techno space', 'midnight sessions', 'misstiq', 'moebius fm',
    'muzlub', 'neutral phonks', 'nocturnal moon session', 'nocturne echoes',
    'nocturne echoes and nocturne cello', 'obsidian hyper techno',
    'occultus records & black square recordings', 'phonk yt', 'shadow house mixes',
    'studio suno', 'sub pulse', 'suno hits', 'suno music', 'synthwavesz', 'techno b34tz',
    'techno black', 'techno is my life', 'techno king', 'techno-exe', 'this song is ai',
    'the ai music genre dictionary', 'ai mastery', 'traxtorm records', 'wave abyss records',
    'wildcore techno', 'zkxai - topic', 'zulvrendeepminimal'
]

AI_CHANNEL_REGEX = re.compile(
    r'(?:^|\s|#|@|\b)(?:suno\s*ai|udio\s*ai|ai\s*covers?|ai\s*music|ai\s*tracks?|ai\s*beats?|ai\s*generated|generative\s*ai\s*music|aimusic)(?:\b|\s|$)',
    re.I
)

FARM_TITLE_PATTERNS = [
    re.compile(r'(?:[🖤❤️⚫🐍🔥⚡💀🥀🎧✨⭐★]{2,}.*(?:session|rave|mix|set|experience|descent|energy|horizons?))', re.I),
    re.compile(r'\b(?:peak time .* session|deep hypnotic .* experience|hypnotic underground .* (?:mix|set)|industrial warehouse .* (?:session|mix|set)|dark forest rave|toxic euphoria|beyond the (?:dark )?horizon|the rave lives inside you|the dark never forgets|what the darkness left behind|the night pulls you in|underground female dj|female dj drops the beat|cyber rave energy)\b', re.I),
    re.compile(r'\b(?:ai-generated tracks|generated by (?:suno|udio)|made with (?:suno|udio)|suno ai showcase|suno studio|suno v[3-9]|udio v[1-9])\b', re.I)
]

FARM_CHANNEL_PATTERNS = [
    re.compile(r'\b(?:dark tech|cybermode|beats lab|techno-exe)\b', re.I),
    re.compile(r'\b(?:dark techno|deep techno|phonk|lofi|ai music|suno|udio)\s*-\s*topic\b', re.I)
]

CHATGPT_SNIPPET_PATTERNS = [
    re.compile(r'(?:the dark has a memory longer than yours|the walls are silent, but the rhythm is loud|some journeys change you\. this one doesn\'t ask permission|you didn\'t choose to come here\. the night pulled you in|some raves were never meant to be found|this is not just a mix; it\'s a high-voltage descent|dive into a deep hypnotic journey|step into a hypnotic journey|travel beyond the (?:dark )?horizon|welcome to a deep, dark and hypnotic|nocturnal moon session delivers|lose yourself in the (?:dark )?rhythm|let the bass take over|feel the frequency\. heal your mind|crafted with advanced neural soundscapes)', re.I)
]

EMOJI_REGEX = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF🖤❤️⚫🐍🔥⚡💀🥀🎧✨⭐★]')

def compile_keyword_regex():
    escaped = []
    for k in KEYWORDS:
        k = k.strip()
        if not k: continue
        bare = k[1:] if k.startswith('#') else k
        esc = re.escape(bare)
        escaped.append(rf'(?:#|\b){esc}\b')
    pattern = '|'.join(escaped)
    return re.compile(rf'({pattern})', re.I)

keyword_regex = compile_keyword_regex()

def harvest_query(query):
    encoded = quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36', 'Accept-Language': 'en-US,en;q=0.9'})
    vids = []
    try:
        with urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            found = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
            seen = set()
            for v_id in found:
                if v_id not in seen:
                    seen.add(v_id)
                    vids.append(v_id)
    except Exception as e:
        pass
    return query, vids

def inspect_and_extract_markers(video_id, cluster_name):
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36', 'Accept-Language': 'en-US,en;q=0.9'})
    try:
        with urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            t_match = re.search(r'<title>(.*?)</title>', html)
            title = t_match.group(1).replace(' - YouTube', '').strip() if t_match else ''
            
            c_match = re.search(r'"author":"([^"]+)"', html) or re.search(r'itemprop="author"[^>]*content="([^"]+)"', html)
            channel = c_match.group(1).strip() if c_match else ''
            
            d_match = re.search(r'"shortDescription":"([^"]+)"', html)
            desc = ''
            if d_match:
                try:
                    desc = d_match.group(1).encode('utf-8').decode('unicode-escape', errors='ignore')
                except Exception:
                    desc = d_match.group(1)
            
            is_official_ai = False
            if any(w in html.lower() for w in ['synthetic', 'altered', 'made with ai', 'ai-generated']):
                is_official_ai = True
                
            is_ai, reason = check_card(title, channel, desc=desc, official_label=is_official_ai)
            
            if not is_ai:
                return {"id": video_id, "cluster": cluster_name, "is_ai": False}
                
            emojis_found = list(set(EMOJI_REGEX.findall(f"{title} {desc}")))
            hashtags_found = list(set(re.findall(r'#\w+', f"{title} {desc}")))
            
            writing_patterns = []
            for sp in CHATGPT_SNIPPET_PATTERNS:
                m = sp.search(desc)
                if m:
                    writing_patterns.append(m.group(0))
                    
            title_features = []
            if re.search(r'\[no ads\]|\(no ads\)', title, re.I):
                title_features.append("[No Ads] Clickbait")
            if re.search(r'202[4-9]', title):
                title_features.append("Year Tag (2024-2029)")
            if any(w in title.lower() for w in ['suno', 'udio', 'rvc', 'ai cover', 'ai song']):
                title_features.append("AI Tool Mention")
                
            channel_style = []
            if re.search(r'\b(?:session|sessions|records|music lab|beats|pulse)\b', channel, re.I):
                channel_style.append("Content Farm Naming Formula")
            if "-topic" in channel.lower():
                channel_style.append("Topic Channel (-Topic)")
                
            return {
                "id": video_id,
                "cluster": cluster_name,
                "title": title,
                "channel": channel,
                "is_ai": True,
                "reason": reason,
                "markers": {
                    "emojis": emojis_found,
                    "hashtags": hashtags_found,
                    "writing_patterns": writing_patterns,
                    "title_features": title_features,
                    "channel_style": channel_style,
                    "official_disclosure": is_official_ai
                }
            }
    except Exception as e:
        return None

def check_card(title, channel, desc='', official_label=False):
    channel_lower = channel.lower()
    for known in CURATED_AI_CHANNELS:
        if known in channel_lower:
            return True, 'Curated AI Farm'
    if AI_CHANNEL_REGEX.search(channel):
        return True, 'AI Channel'
    if official_label:
        return True, 'YouTube AI Disclosure'
    combined = f"{title} {desc}"
    m = keyword_regex.search(combined)
    if m:
        found = m.group(1) or m.group(0)
        return True, f"Keyword: {found.strip().upper()}"
    score = 0
    for tp in FARM_TITLE_PATTERNS:
        if tp.search(title):
            score += 30; break
    for cp in FARM_CHANNEL_PATTERNS:
        if cp.search(channel):
            score += 25; break
    if desc:
        for sp in CHATGPT_SNIPPET_PATTERNS:
            if sp.search(desc):
                score += 40; break
    if score >= 50:
        return True, f'AI Farm Heuristic (score={score})'
    return False, 'Legitimate'

def main():
    start_time = time.time()
    print("🚀 Starting 10,000-Video Deep AI Marker Analysis (2,000 per genre target)...")
    
    # Step 1: Harvest URLs per cluster
    cluster_vids = {c: set() for c in GENRE_CLUSTERS}
    all_harvest_tasks = []
    for c_name, queries in GENRE_CLUSTERS.items():
        for q in queries:
            all_harvest_tasks.append((c_name, q))
            
    print(f"\n--- Harvesting across {len(all_harvest_tasks)} search queries ---")
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(harvest_query, q) for c_name, q in all_harvest_tasks]
        for f in as_completed(futures):
            q, vids = f.result()
            for c_name, q_list in GENRE_CLUSTERS.items():
                if q in q_list:
                    cluster_vids[c_name].update(vids)
                    
    total_unique = sum(len(v) for v in cluster_vids.values())
    print("\nHarvesting Complete:")
    for c_name, vids in cluster_vids.items():
        print(f"  • {c_name:30s}: {len(vids)} unique videos harvested")
    print(f"Total Unique Videos Across Clusters: {total_unique}")
    
    # Step 2: Deep Inspection & Marker Extraction
    print("\n--- Deep Inspection & Marker Extraction ---")
    inspection_tasks = []
    for c_name, vids in cluster_vids.items():
        for vid in vids:
            inspection_tasks.append((vid, c_name))
            
    results = []
    ai_results = []
    completed = 0
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(inspect_and_extract_markers, vid, c_name) for vid, c_name in inspection_tasks]
        for f in as_completed(futures):
            res = f.result()
            completed += 1
            if completed % 250 == 0 or completed == len(inspection_tasks):
                print(f"  Inspected {completed}/{len(inspection_tasks)} videos ({(completed/len(inspection_tasks))*100:.1f}%)...")
            if res:
                results.append(res)
                if res.get("is_ai"):
                    ai_results.append(res)

    # Step 3: Aggregate Marker Statistics
    emoji_freq = {}
    hashtag_freq = {}
    writing_freq = {}
    title_feature_freq = {}
    channel_style_freq = {}
    disclosure_source_freq = {}
    cluster_stats = {c: {"total": 0, "ai_count": 0, "ai_pct": 0.0} for c in GENRE_CLUSTERS}
    
    for r in results:
        c = r["cluster"]
        cluster_stats[c]["total"] += 1
        if r["is_ai"]:
            cluster_stats[c]["ai_count"] += 1
            
    for c in GENRE_CLUSTERS:
        t = cluster_stats[c]["total"]
        a = cluster_stats[c]["ai_count"]
        cluster_stats[c]["ai_pct"] = round((a / t * 100), 2) if t > 0 else 0.0

    for item in ai_results:
        m = item["markers"]
        for e in m["emojis"]:
            emoji_freq[e] = emoji_freq.get(e, 0) + 1
        for h in m["hashtags"]:
            hashtag_freq[h] = hashtag_freq.get(h, 0) + 1
        for w in m["writing_patterns"]:
            writing_freq[w] = writing_freq.get(w, 0) + 1
        for tf in m["title_features"]:
            title_feature_freq[tf] = title_feature_freq.get(tf, 0) + 1
        for cs in m["channel_style"]:
            channel_style_freq[cs] = channel_style_freq.get(cs, 0) + 1
        reason = item["reason"]
        disclosure_source_freq[reason] = disclosure_source_freq.get(reason, 0) + 1
        
    elapsed = round(time.time() - start_time, 2)
    
    report = {
        "total_inspected": len(results),
        "total_ai_flagged": len(ai_results),
        "ai_flagged_pct": round((len(ai_results) / len(results) * 100), 2) if results else 0.0,
        "elapsed_seconds": elapsed,
        "cluster_stats": cluster_stats,
        "marker_aggregates": {
            "top_emojis": sorted(emoji_freq.items(), key=lambda x: x[1], reverse=True)[:25],
            "top_hashtags": sorted(hashtag_freq.items(), key=lambda x: x[1], reverse=True)[:25],
            "writing_patterns": sorted(writing_freq.items(), key=lambda x: x[1], reverse=True),
            "title_features": sorted(title_feature_freq.items(), key=lambda x: x[1], reverse=True),
            "channel_styles": sorted(channel_style_freq.items(), key=lambda x: x[1], reverse=True),
            "disclosure_sources": sorted(disclosure_source_freq.items(), key=lambda x: x[1], reverse=True)
        },
        "flagged_videos_detail": ai_results
    }
    
    out_file = "/home/oh2fxd/toolbox/python/noai/deep_marker_report_10k.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"\n==================================================")
    print(f"DEEP 10,000 MARKER ANALYSIS COMPLETE in {elapsed}s!")
    print(f"Total Inspected: {len(results)}")
    print(f"Total AI Flagged: {len(ai_results)} ({report['ai_flagged_pct']}%)")
    print(f"Report saved to: {out_file}")

if __name__ == "__main__":
    main()
