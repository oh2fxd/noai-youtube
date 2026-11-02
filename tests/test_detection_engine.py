#!/usr/bin/env python3
"""
Unit Test Suite for NoAI YouTube Detection Engine
Verifies core detection rules, Unicode evasion normalization,
content farm patterns, and false-positive immunity offline.
"""

import unittest
import os
import sys

# Add parent directory to path so inspect_youtube_ai can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inspect_youtube_ai import (
    check_video_metadata,
    normalize_text,
    load_extension_signatures,
    KEYWORDS,
    CURATED_CHANNELS
)

class TestNoAIDetectionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_extension_signatures()

    def test_unicode_normalization(self):
        """Tests unmasking of fullwidth characters, accents, and slashed variants."""
        # Fullwidth ASCII unmasked by NFKD
        self.assertEqual(normalize_text("Ｓｕｎｏ"), "Suno")
        # Accents stripped
        self.assertEqual(normalize_text("Téchno Mîx"), "Techno Mix")
        # Slashed-o and empty set symbols normalized to 'o'
        self.assertEqual(normalize_text("Dølōpz"), "Dolopz")
        self.assertEqual(normalize_text("T∅PIC"), "TOPIC")

    def test_keyword_matching(self):
        """Tests detection of explicit AI tool keywords in titles or descriptions."""
        # Suno AI
        reasons = check_video_metadata(
            title="Epic Cyberpunk Track (Suno v4)",
            channel="SynthWave Creator"
        )
        self.assertTrue(any("KEYWORDS" in r for r in reasons))

        # Udio AI
        reasons = check_video_metadata(
            title="Late Night Chill Beats",
            channel="Beats Lab",
            desc="Generated using Udio v1.5 audio model #udio"
        )
        self.assertTrue(any("KEYWORDS" in r for r in reasons))

        # Sora / Midjourney
        reasons = check_video_metadata(
            title="Cinematic Space Travel [Midjourney v6 + Sora AI]",
            channel="Future Visuals"
        )
        self.assertTrue(any("KEYWORDS" in r for r in reasons))

    def test_curated_ai_channels(self):
        """Tests that known AI content farm channels are accurately caught."""
        ai_channels = [
            "Dark Sound Session",
            "Techno Industria",
            "Cybermode Beats",
            "Obsidian Hyper Techno",
            "Neutral Phonks",
            "Night Reactor Music"
        ]
        for chan in ai_channels:
            reasons = check_video_metadata(
                title="Underground Music Live",
                channel=chan
            )
            self.assertTrue(
                any("CURATED_CHANNEL" in r for r in reasons),
                f"Failed to flag curated AI channel: {chan}"
            )

    def test_topic_dump_channels(self):
        """Tests auto-generated generic topic farm channel flags."""
        reasons = check_video_metadata(
            title="Track 01",
            channel="Dark Techno - Topic"
        )
        self.assertTrue(any("TOPIC_AI_DUMP" in r for r in reasons))

        reasons = check_video_metadata(
            title="Track 02",
            channel="AI Music - Topic"
        )
        self.assertTrue(any("TOPIC_AI_DUMP" in r or "CHANNEL_NAME" in r for r in reasons))

    def test_clickbait_farm_title_formulas(self):
        """Tests regex catching repetitive clickbait title patterns."""
        reasons = check_video_metadata(
            title="🖤🔥 Peak Time Underground Techno Session 2026",
            channel="AnonymousDJ"
        )
        self.assertTrue(any("FARM_TITLE_PATTERN" in r for r in reasons))

        reasons = check_video_metadata(
            title="Dark Techno for Late Night Currents [Dark Club Bass]",
            channel="Underground Sound"
        )
        self.assertTrue(any("FARM_TITLE_PATTERN" in r for r in reasons))

    def test_chatgpt_description_formulas(self):
        """Tests ChatGPT promotional copy formulas."""
        reasons = check_video_metadata(
            title="Deep Minimal Vibes",
            channel="Unknown Producer",
            desc="You didn't choose to come here. The night pulled you in. Stay underground. Stay dark."
        )
        self.assertTrue(any("CHATGPT_DESCRIPTION" in r for r in reasons))

    def test_official_youtube_disclosure(self):
        """Tests YouTube's native altered or synthetic content badge."""
        reasons = check_video_metadata(
            title="Interview with Historical Figure",
            channel="History Channel",
            official_label=True
        )
        self.assertTrue(any("OFFICIAL_LABEL" in r for r in reasons))

    def test_false_positive_immunity(self):
        """Critical: Real human artists, DJs, and legitimate non-AI music must NEVER be flagged."""
        authentic_entries = [
            ("Charlotte de Witte - Live at Tomorrowland 2025", "Charlotte de Witte", "Official live festival set from Belgium."),
            ("Amelie Lens @ Awakenings Festival 2024", "Amelie Lens", "Live techno DJ set recorded at Awakenings."),
            ("Carl Cox Boiler Room Ibiza Villa Takeover", "Boiler Room", "Carl Cox playing classic house and techno vinyl set."),
            ("Boris Brejcha - Space Diver (Official Video)", "Boris Brejcha", "High-tech minimal produced by Boris Brejcha."),
            ("Enrico Sangiuliano - Moon Rocks (Drumcode)", "Drumcode", "Released on Drumcode Records DC160."),
            ("Stephan Bodzin - Singularity (Live)", "Stephan Bodzin", "Live analog synthesizer performance with Moog Sub 37."),
            ("Tale of Us - Afterlife Voyage 028", "Afterlife", "Melodic techno podcast mix series."),
            ("Adam Beyer Live at Printworks London", "Drumcode", "Full 2 hour club set recorded live.")
        ]

        for title, channel, desc in authentic_entries:
            reasons = check_video_metadata(title=title, channel=channel, desc=desc)
            self.assertEqual(
                reasons, [],
                f"FALSE POSITIVE DETECTED on authentic content: {title} by {channel} (reasons: {reasons})"
            )

if __name__ == '__main__':
    unittest.main()

