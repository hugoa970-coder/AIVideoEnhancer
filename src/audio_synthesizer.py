"""Speech replacement and synthesis engine (Patent US 2026/0341309 A1 - Block 250).
Generates formant-modeled acoustic replacements with matching speaker pitch.
"""

import math
from typing import List
from .models import AudioFormatConfig


class FormantVocalSynthesizer:
    """Synthesizes voice-like replacement words using formant-filtered harmonic oscillations."""

    # Approximate Spanish vowel formants [F1, F2] in Hz
    VOWEL_FORMANTS = {
        'a': (800, 1200),
        'e': (500, 1800),
        'i': (300, 2300),
        'o': (500, 900),
        'u': (300, 700),
    }

    def __init__(self, format_config: AudioFormatConfig = AudioFormatConfig()):
        self.config = format_config

    def synthesize_word(
        self,
        word: str,
        target_duration_ms: int,
        base_f0: float = 140.0,
        target_amplitude: int = 14000
    ) -> List[int]:
        """Synthesizes audio samples for the replacement word to fit target duration."""
        total_samples = int((target_duration_ms / 1000.0) * self.config.sample_rate)
        if total_samples <= 0:
            return []

        word_clean = word.lower()
        samples: List[int] = []

        # Analyze letters and map phonemes
        chars = [c for c in word_clean if c.isalpha()] or ['a']
        samples_per_char = max(1, total_samples // len(chars))

        current_sample = 0
        for char_idx, char in enumerate(chars):
            f1, f2 = self.VOWEL_FORMANTS.get(char, (600, 1400))
            is_last = (char_idx == len(chars) - 1)
            char_samples_count = (total_samples - current_sample) if is_last else samples_per_char

            for i in range(char_samples_count):
                t = current_sample / float(self.config.sample_rate)
                
                # Pitch modulation (subtle vibrato for human vocal naturalness)
                f0_mod = base_f0 + 2.5 * math.sin(2.0 * math.pi * 5.0 * t)

                # Glottal pulse train approximation (Harmonics)
                vocal_source = (
                    1.0 * math.sin(2.0 * math.pi * f0_mod * t) +
                    0.5 * math.sin(2.0 * math.pi * 2 * f0_mod * t) +
                    0.25 * math.sin(2.0 * math.pi * 3 * f0_mod * t)
                )

                # Formant resonance simulation
                f1_res = 0.4 * math.sin(2.0 * math.pi * f1 * t)
                f2_res = 0.2 * math.sin(2.0 * math.pi * f2 * t)

                # Global envelope (Attack - Sustain - Release)
                global_progress = current_sample / float(total_samples)
                if global_progress < 0.1:
                    env = global_progress / 0.1
                elif global_progress > 0.85:
                    env = (1.0 - global_progress) / 0.15
                else:
                    env = 1.0

                combined = (vocal_source * 0.5 + f1_res + f2_res) * env * target_amplitude
                clamped = max(-32768, min(32767, int(combined)))
                samples.append(clamped)
                current_sample += 1

        return samples
