"""Master Pipeline Orchestrator (Patent US 2026/0341309 A1 - System 200).
Integrates Blocks 210, 230, 235, 250, 260, 265 and 275 into a single cohesive engine.
Includes security and boundary validation.
"""

import json
from pathlib import Path
from typing import List, Optional

from .models import (
    AudioFormatConfig,
    PipelineReport,
    ProfileType,
    ScriptModification,
    WordSegment,
)
from .media_loader import MediaLoader
from .asr_detector import SpokenWordDetector
from .script_modifier import ScriptModifier
from .audio_synthesizer import FormantVocalSynthesizer
from .audio_transitions import AcousticCrossfader
from .video_lip_sync import VideoLipSyncGenerator


class VideoEnhancerPipeline:
    """Executes the full post-production replacement cycle according to Patent Fig. 2."""

    def __init__(self, profile: ProfileType = ProfileType.CHILD_SAFE):
        self.profile = profile
        self.script_modifier = ScriptModifier(profile=self.profile)
        self.synthesizer = FormantVocalSynthesizer()
        self.lip_sync_gen = VideoLipSyncGenerator(fps=30.0)

    def process(
        self,
        input_audio_path: str,
        output_audio_path: str,
        transcript_text: str,
        output_metadata_path: Optional[str] = None
    ) -> PipelineReport:
        # [210] Access Media Files
        samples, config = MediaLoader.read_wav(input_audio_path)
        if not samples:
            raise ValueError("Input audio file contains no samples.")

        total_duration_ms = max(1, int((len(samples) / float(config.sample_rate)) * 1000))

        # [230] Identify Spoken Words and Align Timestamps
        detected_words = SpokenWordDetector.parse_aligned_transcript(
            transcript_text=transcript_text,
            total_audio_duration_ms=total_duration_ms
        )

        # [235] Modify Script Based on Profile
        modifications = self.script_modifier.evaluate(detected_words)

        # Working buffer for modified audio
        modified_samples = list(samples)
        transition_metrics_list = []

        # [250 & 260] Synthesize replacements and apply acoustic crossfading
        for mod in modifications:
            start_ms = max(0, mod.original_segment.start_ms)
            end_ms = min(total_duration_ms, mod.original_segment.end_ms)
            if start_ms >= end_ms:
                continue

            duration_ms = max(50, end_ms - start_ms)

            # Generate synthetic replacement word [250]
            replacement_samples = self.synthesizer.synthesize_word(
                word=mod.replacement_word,
                target_duration_ms=duration_ms
            )

            if not replacement_samples:
                continue

            # Convert ms boundaries to sample indices
            start_sample = max(0, int((start_ms / 1000.0) * config.sample_rate))
            if start_sample >= len(modified_samples):
                continue

            # Apply acoustic crossfade at boundary [260]
            crossfade_len = min(
                int(0.03 * config.sample_rate),
                len(replacement_samples) // 4,
                start_sample
            )
            
            # Blend leading transition
            if crossfade_len > 0 and (start_sample - crossfade_len >= 0):
                out_region = modified_samples[start_sample - crossfade_len:start_sample]
                in_region = replacement_samples[:crossfade_len]
                blended, metrics = AcousticCrossfader.blend_regions(out_region, in_region, curve="equal_power")
                modified_samples[start_sample - crossfade_len:start_sample] = blended
                transition_metrics_list.append(metrics)

            # Insert replacement body safely
            body_end = min(len(modified_samples), start_sample + len(replacement_samples))
            count_to_copy = max(0, body_end - start_sample)
            modified_samples[start_sample:body_end] = replacement_samples[:count_to_copy]

        # [265] Generate Video Lip-Sync and Viseme deformation plan
        lip_frames = self.lip_sync_gen.generate_plan(
            total_duration_ms=total_duration_ms,
            modifications=modifications
        )

        # [275] Write final enhanced audio file and export metadata
        MediaLoader.write_wav(output_audio_path, modified_samples, config)

        if not output_metadata_path:
            output_metadata_path = str(Path(output_audio_path).with_suffix('.metadata.json'))

        metadata_dict = {
            "patent_reference": "US 2026/0341309 A1 - Fig. 2",
            "profile_applied": self.profile.value,
            "total_duration_ms": total_duration_ms,
            "modifications_count": len(modifications),
            "modifications": [
                {
                    "original": m.original_segment.word,
                    "replacement": m.replacement_word,
                    "start_ms": m.original_segment.start_ms,
                    "end_ms": m.original_segment.end_ms,
                    "justification": m.justification
                }
                for m in modifications
            ],
            "total_lip_sync_frames": len(lip_frames),
            "modified_lip_sync_frames": len([f for f in lip_frames if f.is_modified]),
            "viseme_samples": [
                {
                    "frame": f.frame_index,
                    "time_ms": f.timestamp_ms,
                    "viseme": f.viseme,
                    "jaw_open": f.jaw_open_factor,
                    "lip_width": f.lip_width_factor
                }
                for f in lip_frames if f.is_modified][:10]
        }

        with open(output_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)

        return PipelineReport(
            input_file=input_audio_path,
            output_audio=output_audio_path,
            output_video_metadata=output_metadata_path,
            profile_used=self.profile,
            detected_words=detected_words,
            applied_modifications=modifications,
            transitions=transition_metrics_list,
            lip_sync_frames=lip_frames,
            success=True
        )
