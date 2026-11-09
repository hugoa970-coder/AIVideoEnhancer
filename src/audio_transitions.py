"""Acoustic transition and crossfade engine (Patent US 2026/0341309 A1 - Block 260).
Eliminates audio artifacts, pops, clicks, and phase cancellation during speech replacement.
"""

import math
from typing import List, Tuple
from .models import AudioFormatConfig, TransitionMetrics


class AcousticCrossfader:
    """Computes mathematical curves and blends audio buffers seamlessly."""

    @staticmethod
    def calculate_weights(samples_count: int, curve: str = "equal_power") -> List[Tuple[float, float]]:
        """Generates (fade_out_weight, fade_in_weight) pairs for transition region."""
        if samples_count <= 0:
            return []

        weights: List[Tuple[float, float]] = []
        for i in range(samples_count):
            fraction = i / max(1, samples_count - 1)
            
            if curve == "equal_power":
                # Equal power cross-fade: cos(pi/2 * x) and sin(pi/2 * x)
                # Ensures w_out^2 + w_in^2 == 1.0 (constant acoustic power)
                angle = (math.pi / 2.0) * fraction
                w_out = math.cos(angle)
                w_in = math.sin(angle)
            elif curve == "sigmoid":
                # Smooth S-curve transition
                # Sigmoid normalized between 0 and 1
                s = 1.0 / (1.0 + math.exp(-10.0 * (fraction - 0.5)))
                w_in = s
                w_out = 1.0 - s
            else:  # Linear fallback
                w_in = fraction
                w_out = 1.0 - fraction

            weights.append((w_out, w_in))

        return weights

    @classmethod
    def blend_regions(
        cls,
        outgoing_samples: List[int],
        incoming_samples: List[int],
        curve: str = "equal_power"
    ) -> Tuple[List[int], TransitionMetrics]:
        """Blends two sequences of 16-bit PCM samples over their overlapping region."""
        blend_len = min(len(outgoing_samples), len(incoming_samples))
        if blend_len == 0:
            return [], TransitionMetrics(
                crossfade_duration_ms=0,
                samples_blended=0,
                curve_type=curve,
                power_conservation_ratio=1.0
            )

        weights = cls.calculate_weights(blend_len, curve=curve)
        blended: List[int] = []
        power_sum_before = 0.0
        power_sum_after = 0.0

        for idx, (w_out, w_in) in enumerate(weights):
            s_out = outgoing_samples[idx]
            s_in = incoming_samples[idx]

            power_sum_before += (s_out ** 2 + s_in ** 2) / 2.0

            mixed = int((s_out * w_out) + (s_in * w_in))
            # Clamp to 16-bit signed range [-32768, 32767]
            clamped = max(-32768, min(32767, mixed))
            blended.append(clamped)
            power_sum_after += clamped ** 2

        power_ratio = (power_sum_after / max(1e-6, power_sum_before)) if power_sum_before > 0 else 1.0

        metrics = TransitionMetrics(
            crossfade_duration_ms=int((blend_len / 44100.0) * 1000),
            samples_blended=blend_len,
            curve_type=curve,
            power_conservation_ratio=round(power_ratio, 4)
        )

        return blended, metrics
