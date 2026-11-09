# ARCHITECTURE: AI Video & Audio Enhancement Engine
**Estado:** Aprobado (Fase 2 - Tech Lead / Architecture Review)  
**Ubicación:** `D:\Proyectos\AIVideoEnhancer`

---

## 1. Mapeo Patente -> Módulos de Software

| Bloque Patente | Nombre del Bloque | Componente de Software | Módulo en `src/` |
|---|---|---|---|
| **210** | Access Video & Audio | `MediaLoader` | `src/media_loader.py` |
| **230** | Identify Spoken Words | `SpokenWordDetector` | `src/asr_detector.py` |
| **235** | Modify Script via Profiles | `ScriptEngine` & `Profile` | `src/script_modifier.py` |
| **250** | Replace Spoken Words | `AudioSynthesizer` | `src/audio_synthesizer.py` |
| **260** | Audio Transitions Generator | `AcousticCrossfader` | `src/audio_transitions.py` |
| **265** | Modify Video (Lip Sync) | `VideoLipModifier` | `src/video_lip_sync.py` |
| **275** | Presentation / Output | `EnhancerPipeline` | `src/pipeline.py` |

---

## 2. Contratos de Datos (Data Contracts)

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ProfileType(str, Enum):
    CHILD_SAFE = "CHILD_SAFE"
    BRAND_COMPLIANCE = "BRAND_COMPLIANCE"
    LOCALIZATION = "LOCALIZATION"

@dataclass
class WordSegment:
    word: str
    start_ms: int
    end_ms: int
    confidence: float

@dataclass
class ReplacementRule:
    original_word: str
    replacement_word: str
    profile: ProfileType
    reason: str

@dataclass
class AudioTransitionConfig:
    crossfade_duration_ms: int = 50
    curve_type: str = "sigmoid" # linear, sigmoid, equal_power
    ambient_noise_fill: bool = True
```

---

## 3. Formulación Matemática de Transiciones Acústicas (Bloque 260)
Para evitar el "click" o discontinuidad de fase al empalmar el audio sintetizado con el audio original, se aplica un cross-fade de potencia constante (*Equal Power Crossfade*) o sigmoide:

$$w_{\text{out}}(t) = \cos\left(\frac{\pi}{2} \cdot \frac{t}{T}\right)$$
$$w_{\text{in}}(t) = \sin\left(\frac{\pi}{2} \cdot \frac{t}{T}\right)$$

Donde:
* $T$ es el tiempo total de la ventana de transición en muestras ($T = \text{duration\_ms} \times \frac{f_s}{1000}$).
* $t \in [0, T]$ representa el índice de la muestra en la ventana.
* La potencia combinada satisface $w_{\text{out}}^2(t) + w_{\text{in}}^2(t) = 1$, evitando caídas de volumen perceptibles.

---

## 4. Estrategia de Dependencias y Almacenamiento
* **Disco SSD (C:) Protegido:** Ningún modelo ni entorno pesado se instala en `C:`.
* **Procesamiento de Audio:** Uso de la biblioteca estándar de Python (`wave`, `struct`, `math`) para manipulación matemática de audio PCM a nivel de bytes, garantizando portabilidad sin librerías externas voluminosas.
* **Procesamiento de Video:** Utilización del binario portable de FFmpeg detectado en la unidad `D:\Proyectos\`.
