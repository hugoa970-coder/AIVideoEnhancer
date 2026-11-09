"""Unit tests for Audience Profiles and Script Modification.
"""

import unittest
from src.models import ProfileType, WordSegment
from src.script_modifier import ScriptModifier, ProfileRulesRegistry


class TestProfilesAndScript(unittest.TestCase):

    def test_child_safe_profile_replacement(self):
        modifier = ScriptModifier(ProfileType.CHILD_SAFE)
        segments = [
            WordSegment("hola", 0, 500),
            WordSegment("maldicion", 500, 1000),
            WordSegment("amigo", 1000, 1500),
            WordSegment("violencia", 1500, 2000),
        ]
        mods = modifier.evaluate(segments)
        self.assertEqual(len(mods), 2)
        self.assertEqual(mods[0].replacement_word, "caracoles")
        self.assertEqual(mods[1].replacement_word, "accion")

    def test_brand_compliance_profile(self):
        modifier = ScriptModifier(ProfileType.BRAND_COMPLIANCE)
        segments = [
            WordSegment("bebo", 0, 400),
            WordSegment("coca-cola", 400, 900),
            WordSegment("usando", 900, 1200),
            WordSegment("iphone", 1200, 1700),
        ]
        mods = modifier.evaluate(segments)
        self.assertEqual(len(mods), 2)
        self.assertEqual(mods[0].replacement_word, "refresco")
        self.assertEqual(mods[1].replacement_word, "telefono")

    def test_localization_profile(self):
        modifier = ScriptModifier(ProfileType.LOCALIZATION)
        segments = [
            WordSegment("mi", 0, 200),
            WordSegment("coche", 200, 700),
            WordSegment("y", 700, 900),
            WordSegment("ordenador", 900, 1500),
        ]
        mods = modifier.evaluate(segments)
        self.assertEqual(len(mods), 2)
        self.assertEqual(mods[0].replacement_word, "auto")
        self.assertEqual(mods[1].replacement_word, "computadora")


if __name__ == "__main__":
    unittest.main()
