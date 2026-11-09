"""Data contracts and model definitions for AI Video Enhancement Pipeline (Patent US 2026/0341309 A1).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ProfileType(str, Enum):
    CHILD_SAFE = "CHILD_SAFE"
    BRAND_COMPLIANCE = "BRAND_COMPLIANCE"
    LOCALIZATION = "LOCALIZATION"


@dataclass(frozen=True)
class WordSegment:
    """Represents an identified word and its time boundaries in milliseconds."""
    word: str
    start_ms: int
    end_ms: int
    confidence: float = 1.0

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms


@dataclass
class ScriptModification:
    """Represents a planned change to the dialogue script based on active profile."""
    original_segment: WordSegment
    replacement_word: str
    profile: ProfileType
    rule_id: str
    justification: str


@dataclass
class AudioFormatConfig:
    sample_rate: int = 44100
    channels: int = 1
    sample_width: int = 2  # 16-bit PCM


@dataclass
class TransitionMetrics:
    crossfade_duration_ms: int
    samples_blended: int
    curve_type: str
    power_conservation_ratio: float


@dataclass
class LipSyncFramePlan:
    frame_index: int
    timestamp_ms: float
    viseme: str
    jaw_open_factor: float
    lip_width_factor: float
    is_modified: bool


@dataclass
class PipelineReport:
    input_file: str
    output_audio: str
    output_video_metadata: str
    profile_used: ProfileType
    detected_words: List[WordSegment] = field(default_factory=list)
    applied_modifications: List[ScriptModification] = field(default_factory=list)
    transitions: List[TransitionMetrics] = field(default_factory=list)
    lip_sync_frames: List[LipSyncFramePlan] = field(default_factory=list)
    success: bool = False
