"""Unit tests for Acoustic Cross-fader and Synthesis Mathematics.
"""

import unittest
from src.audio_transitions import AcousticCrossfader
from src.audio_synthesizer import FormantVocalSynthesizer


class TestAudioTransitions(unittest.TestCase):

    def test_equal_power_weights_conservation(self):
        # Equal power says: w_out^2 + w_in^2 == 1.0 at every point
        weights = AcousticCrossfader.calculate_weights(100, curve="equal_power")
        self.assertEqual(len(weights), 100)
        for w_out, w_in in weights:
            power_sum = (w_out ** 2) + (w_in ** 2)
            self.assertAlmostEqual(power_sum, 1.0, places=4)

    def test_blend_regions_no_clipping(self):
        # Even with max amplitude signals, clamping should prevent overflow
        sig_out = [32000] * 200
        sig_in = [32000] * 200
        blended, metrics = AcousticCrossfader.blend_regions(sig_out, sig_in, curve="equal_power")
        self.assertEqual(len(blended), 200)
        for s in blended:
            self.assertGreaterEqual(s, -32768)
            self.assertLessEqual(s, 32767)

    def test_synthesizer_duration_accuracy(self):
        synth = FormantVocalSynthesizer()
        samples = synth.synthesize_word("caracoles", target_duration_ms=500)
        # At 44100 Hz, 500 ms = 22050 samples
        expected_samples = int(0.5 * 44100)
        self.assertEqual(len(samples), expected_samples)


if __name__ == "__main__":
    unittest.main()
