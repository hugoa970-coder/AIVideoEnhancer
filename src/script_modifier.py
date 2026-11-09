"""Script modification engine based on audience profiles (Patent US 2026/0341309 A1 - Block 235).
"""

from typing import Dict, List, Optional
from .models import ProfileType, ScriptModification, WordSegment


class ProfileRulesRegistry:
    """Stores replacement dictionaries and semantic rules mapped by audience profile."""
    
    RULES: Dict[ProfileType, Dict[str, str]] = {
        ProfileType.CHILD_SAFE: {
            "maldicion": "caracoles",
            "mierda": "rayos",
            "estupido": "tontuelo",
            "matar": "vencer",
            "demonio": "pillo",
            "infierno": "lugar oscuro",
            "violencia": "accion",
        },
        ProfileType.BRAND_COMPLIANCE: {
            "coca-cola": "refresco",
            "pepsi": "soda",
            "iphone": "telefono",
            "google": "buscador",
            "windows": "sistema operativo",
            "netflix": "plataforma de streaming",
        },
        ProfileType.LOCALIZATION: {
            "coche": "auto",
            "ordenador": "computadora",
            "guay": "genial",
            "vale": "de acuerdo",
            "chaval": "muchacho",
            "aparcamiento": "estacionamiento",
        }
    }

    @classmethod
    def get_replacement(cls, word: str, profile: ProfileType) -> Optional[str]:
        cleaned = word.lower().strip(",.?!:;\"'")
        profile_dict = cls.RULES.get(profile, {})
        return profile_dict.get(cleaned)


class ScriptModifier:
    """Evaluates transcription segments against active profile and prepares modifications."""

    def __init__(self, profile: ProfileType):
        self.profile = profile

    def evaluate(self, segments: List[WordSegment]) -> List[ScriptModification]:
        modifications: List[ScriptModification] = []

        for segment in segments:
            replacement = ProfileRulesRegistry.get_replacement(segment.word, self.profile)
            if replacement:
                mod = ScriptModification(
                    original_segment=segment,
                    replacement_word=replacement,
                    profile=self.profile,
                    rule_id=f"{self.profile.value}_{len(modifications)+1:02d}",
                    justification=f"Replaced '{segment.word}' with '{replacement}' for compliance with {self.profile.value}"
                )
                modifications.append(mod)

        return modifications
