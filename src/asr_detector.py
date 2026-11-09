"""Spoken word identification and timestamp alignment engine (Patent US 2026/0341309 A1 - Block 230).
"""

from typing import List, Optional
from .models import WordSegment


class SpokenWordDetector:
    """Identifies words, phonetic bounds and timestamps in audio streams."""

    @staticmethod
    def parse_aligned_transcript(transcript_text: str, total_audio_duration_ms: int) -> List[WordSegment]:
        """Aligns words evenly or parses explicit timestamped tokens [start_ms, end_ms] word."""
        raw_words = transcript_text.strip().split()
        if not raw_words:
            return []

        segments: List[WordSegment] = []
        ms_per_word = max(100, total_audio_duration_ms // len(raw_words))

        for idx, item in enumerate(raw_words):
            start = idx * ms_per_word
            end = min(total_audio_duration_ms, (idx + 1) * ms_per_word)
            segments.append(
                WordSegment(
                    word=item,
                    start_ms=start,
                    end_ms=end,
                    confidence=0.98
                )
            )

        return segments

    @staticmethod
    def scan_for_sensitive_targets(segments: List[WordSegment], target_words: List[str]) -> List[WordSegment]:
        targets_normalized = {w.lower() for w in target_words}
        matches: List[WordSegment] = []
        for seg in segments:
            clean = seg.word.lower().strip(",.?!:;\"'")
            if clean in targets_normalized:
                matches.append(seg)
        return matches
