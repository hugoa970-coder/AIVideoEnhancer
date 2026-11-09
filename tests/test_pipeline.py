"""End-to-end Integration tests for Full Pipeline.
"""

import json
import unittest
from pathlib import Path
from src.models import ProfileType
from src.media_loader import MediaLoader
from src.pipeline import VideoEnhancerPipeline


class TestPipelineE2E(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("D:/Proyectos/AIVideoEnhancer/samples/test_run")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.input_wav = str(self.test_dir / "input_e2e.wav")
        self.output_wav = str(self.test_dir / "output_e2e.wav")
        self.metadata_json = str(self.test_dir / "output_e2e.metadata.json")
        MediaLoader.generate_synthetic_dialogue_wav(self.input_wav, duration_ms=3000)

    def test_full_pipeline_execution(self):
        transcript = "el chaval dijo una maldicion en el aparcamiento"
        pipeline = VideoEnhancerPipeline(profile=ProfileType.CHILD_SAFE)
        report = pipeline.process(
            input_audio_path=self.input_wav,
            output_audio_path=self.output_wav,
            transcript_text=transcript,
            output_metadata_path=self.metadata_json
        )

        self.assertTrue(report.success)
        self.assertTrue(Path(self.output_wav).exists())
        self.assertTrue(Path(self.metadata_json).exists())

        # Verify output audio readability and length
        samples, config = MediaLoader.read_wav(self.output_wav)
        self.assertGreater(len(samples), 0)

        # Verify metadata JSON contents
        with open(self.metadata_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data["profile_applied"], "CHILD_SAFE")
        self.assertGreater(data["modifications_count"], 0)


if __name__ == "__main__":
    unittest.main()
