"""Media file reader and writer for PCM audio and video tracks (Patent US 2026/0341309 A1 - Block 210).
"""

import struct
import wave
from pathlib import Path
from typing import List, Tuple
from .models import AudioFormatConfig


class MediaLoader:
    """Manages audio file I/O using Python standard library without external dependencies."""

    @staticmethod
    def read_wav(file_path: str) -> Tuple[List[int], AudioFormatConfig]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        with wave.open(str(path), 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            num_frames = wf.getnframes()
            raw_data = wf.readframes(num_frames)

        if sample_width != 2:
            raise ValueError(f"Only 16-bit PCM WAV is supported, got {sample_width * 8}-bit")

        # Unpack 16-bit signed integers
        total_samples = num_frames * channels
        unpacked = struct.unpack(f"<{total_samples}h", raw_data)

        # Convert to mono if stereo
        if channels > 1:
            mono_samples = [
                int(sum(unpacked[i:i + channels]) / channels)
                for i in range(0, len(unpacked), channels)
            ]
        else:
            mono_samples = list(unpacked)

        config = AudioFormatConfig(
            sample_rate=sample_rate,
            channels=1,
            sample_width=sample_width
        )
        return mono_samples, config

    @staticmethod
    def write_wav(file_path: str, samples: List[int], config: AudioFormatConfig) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        packed_data = struct.pack(f"<{len(samples)}h", *samples)

        with wave.open(str(path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(config.sample_width)
            wf.setframerate(config.sample_rate)
            wf.writeframes(packed_data)

    @classmethod
    def generate_synthetic_dialogue_wav(
        cls,
        file_path: str,
        duration_ms: int = 5000,
        sample_rate: int = 44100
    ) -> str:
        """Creates a benchmark WAV file with dialogue carrier tone for zero-dependency testing."""
        import math
        total_samples = int((duration_ms / 1000.0) * sample_rate)
        samples: List[int] = []

        for i in range(total_samples):
            t = i / float(sample_rate)
            # Modulated carrier mimicking human conversational speech
            signal = (
                0.6 * math.sin(2.0 * math.pi * 180.0 * t) +
                0.3 * math.sin(2.0 * math.pi * 360.0 * t) +
                0.1 * math.sin(2.0 * math.pi * 720.0 * t)
            ) * 12000
            samples.append(int(signal))

        config = AudioFormatConfig(sample_rate=sample_rate, channels=1, sample_width=2)
        cls.write_wav(file_path, samples, config)
        return file_path
