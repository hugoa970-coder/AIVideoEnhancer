"""Video and Facial Lip-Sync Generator (Patent US 2026/0341309 A1 - Block 265).
Calculates visemes, jaw openness factors, and mouth morphing instructions for replacement words.
"""

from typing import Dict, List, Tuple
from .models import LipSyncFramePlan, ScriptModification


class VisemeMapper:
    """Maps phonemes and vowels to visual mouth shapes (Visemes)."""

    VISEME_MAP: Dict[str, Tuple[float, float, str]] = {
        # char: (jaw_open, lip_width, viseme_code)
        'a': (0.85, 0.60, "VISEME_AH"),
        'e': (0.50, 0.85, "VISEME_EE"),
        'i': (0.35, 0.90, "VISEME_IH"),
        'o': (0.75, 0.40, "VISEME_OH"),
        'u': (0.30, 0.25, "VISEME_OO"),
        'm': (0.05, 0.50, "VISEME_MBP"),
        'b': (0.05, 0.50, "VISEME_MBP"),
        'p': (0.05, 0.50, "VISEME_MBP"),
        'f': (0.15, 0.70, "VISEME_FV"),
        'v': (0.15, 0.70, "VISEME_FV"),
        's': (0.20, 0.75, "VISEME_SS"),
        't': (0.25, 0.65, "VISEME_TD"),
        'r': (0.40, 0.45, "VISEME_RR"),
        'c': (0.35, 0.60, "VISEME_KG"),
        'l': (0.30, 0.65, "VISEME_LL"),
    }

    @classmethod
    def get_viseme(cls, char: str) -> Tuple[float, float, str]:
        return cls.VISEME_MAP.get(char.lower(), (0.20, 0.50, "VISEME_REST"))


class VideoLipSyncGenerator:
    """Generates per-frame facial animation plan for the replacement segments."""

    def __init__(self, fps: float = 30.0):
        self.fps = fps
        self.frame_duration_ms = 1000.0 / fps

    def generate_plan(
        self,
        total_duration_ms: int,
        modifications: List[ScriptModification]
    ) -> List[LipSyncFramePlan]:
        total_frames = int((total_duration_ms / 1000.0) * self.fps)
        frames: List[LipSyncFramePlan] = []

        # Build quick lookup for modification windows
        mod_ranges = [
            (m.original_segment.start_ms, m.original_segment.end_ms, m.replacement_word)
            for m in modifications
        ]

        for frame_idx in range(total_frames):
            ts = frame_idx * self.frame_duration_ms
            
            # Check if this frame falls inside a replacement segment
            active_replacement = None
            for start, end, word in mod_ranges:
                if start <= ts <= end:
                    active_replacement = (start, end, word)
                    break

            if active_replacement:
                start, end, word = active_replacement
                duration = max(1.0, end - start)
                progress = (ts - start) / duration
                
                # Pick character in replacement word corresponding to frame position
                chars = [c for c in word if c.isalpha()] or ['a']
                char_idx = min(len(chars) - 1, int(progress * len(chars)))
                target_char = chars[char_idx]

                jaw_open, lip_width, viseme = VisemeMapper.get_viseme(target_char)
                frames.append(
                    LipSyncFramePlan(
                        frame_index=frame_idx,
                        timestamp_ms=round(ts, 2),
                        viseme=viseme,
                        jaw_open_factor=jaw_open,
                        lip_width_factor=lip_width,
                        is_modified=True
                    )
                )
            else:
                # Default baseline resting frame
                frames.append(
                    LipSyncFramePlan(
                        frame_index=frame_idx,
                        timestamp_ms=round(ts, 2),
                        viseme="VISEME_REST",
                        jaw_open_factor=0.10,
                        lip_width_factor=0.50,
                        is_modified=False
                    )
                )

        return frames
