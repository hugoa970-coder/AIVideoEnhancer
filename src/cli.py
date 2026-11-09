"""High-contrast Interactive Terminal Interface for AI Video Enhancer.
Safe cross-platform encoding for Windows terminals with Interactive Menu and Argument parsing.
"""

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 output if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .models import ProfileType
from .pipeline import VideoEnhancerPipeline
from .media_loader import MediaLoader


class TerminalColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def process_audio_pipeline(transcript: str, profile: ProfileType, custom_audio: str = None):
    C = TerminalColors
    samples_dir = Path("D:/Proyectos/AIVideoEnhancer/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)

    if custom_audio and Path(custom_audio).exists():
        input_wav = Path(custom_audio)
    else:
        input_wav = samples_dir / "sample_dialogue.wav"
        if not input_wav.exists():
            MediaLoader.generate_synthetic_dialogue_wav(str(input_wav), duration_ms=4500)

    output_wav = samples_dir / f"enhanced_{profile.value.lower()}.wav"
    metadata_json = samples_dir / f"enhanced_{profile.value.lower()}.metadata.json"

    print(f"\n{C.CYAN}{'='*80}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}     AI POST-PRODUCTION ENHANCER  |  Patent US 2026/0341309 A1 (Fig. 2){C.RESET}")
    print(f"{C.CYAN}{'='*80}{C.RESET}")
    print(f" {C.BOLD}[Configuracion Inicial]:{C.RESET}")
    print(f"   * Archivo Fuente: {C.WHITE}{input_wav}{C.RESET}")
    print(f"   * Perfil Activo:  {C.YELLOW}{profile.value}{C.RESET}")
    print(f"   * Dialogo Fuente: {C.WHITE}\"{transcript}\"{C.RESET}")
    print(f"{C.CYAN}{'-'*80}{C.RESET}")

    pipeline = VideoEnhancerPipeline(profile=profile)
    report = pipeline.process(
        input_audio_path=str(input_wav),
        output_audio_path=str(output_wav),
        transcript_text=transcript,
        output_metadata_path=str(metadata_json)
    )

    print(f" {C.GREEN}[210] Acceso a Archivo Multimedia:{C.RESET}       OK ({len(report.detected_words)} palabras procesadas)")
    print(f" {C.YELLOW}[230] Escaneo ASR de Terminos Sensibles:{C.RESET}  {len(report.applied_modifications)} detectados para modificacion")

    if not report.applied_modifications:
        print(f"       * {C.CYAN}No se encontraron palabras que requieran modificacion para este perfil.{C.RESET}")
    else:
        for mod in report.applied_modifications:
            print(f"       |-- [{mod.original_segment.start_ms:04d}ms - {mod.original_segment.end_ms:04d}ms] {C.RED}[DETECTADO] \"{mod.original_segment.word}\"{C.RESET}")
            print(f"       |   +-- [235 Guion Modificado]: {C.GREEN}[REEMPLAZO] \"{mod.replacement_word}\"{C.RESET} ({mod.justification})")

    print(f" {C.CYAN}[250] Sintesis Vocal Parametrica:{C.RESET}        {len(report.applied_modifications)} palabras sintetizadas")
    print(f" {C.BLUE}[260] Transiciones Acusticas Cross-Fade:{C.RESET} {len(report.transitions)} empalmes calculados")

    mod_frames = len([f for f in report.lip_sync_frames if f.is_modified])
    print(f" {C.GREEN}[265] Sincronizacion Visual & Lip-Sync:{C.RESET}  {mod_frames} cuadros faciales adaptados")
    print(f" {C.WHITE}[275] Renderizado & Exportacion Final:{C.RESET}   {C.GREEN}[COMPLETADO EXITOSAMENTE]{C.RESET}")

    print(f"{C.CYAN}{'='*80}{C.RESET}")
    print(f" {C.BOLD}Archivos Generados en Disco D:{C.RESET}")
    print(f"   * Audio Modificado: {C.WHITE}{output_wav}{C.RESET}")
    print(f"   * Metadatos Video:  {C.WHITE}{metadata_json}{C.RESET}")
    print(f"{C.CYAN}{'='*80}{C.RESET}\n")


def run_interactive_menu():
    C = TerminalColors
    while True:
        print(f"\n{C.CYAN}================================================================================{C.RESET}")
        print(f"{C.BOLD}{C.WHITE}           PANEL DE CONTROL - AI VIDEO ENHANCER (US 2026/0341309 A1)           {C.RESET}")
        print(f"{C.CYAN}================================================================================{C.RESET}")
        print(f" {C.BOLD}Seleccione el modo de activacion:{C.RESET}")
        print(f"   {C.YELLOW}[1]{C.RESET} Perfil {C.BOLD}CHILD_SAFE{C.RESET} (Censura de insultos y violencia con Lip-Sync)")
        print(f"   {C.YELLOW}[2]{C.RESET} Perfil {C.BOLD}BRAND_COMPLIANCE{C.RESET} (Reemplazo de marcas por terminos genericos)")
        print(f"   {C.YELLOW}[3]{C.RESET} Perfil {C.BOLD}LOCALIZATION{C.RESET} (Adaptacion de modismos regionales a neutro)")
        print(f"   {C.YELLOW}[4]{C.RESET} Diálogo Personalizado (Escribir tu propio guion)")
        print(f"   {C.YELLOW}[5]{C.RESET} Ejecutar Suite de Pruebas Automatizadas (QA - 7 Tests)")
        print(f"   {C.RED}[0] Salir{C.RESET}")
        print(f"{C.CYAN}--------------------------------------------------------------------------------{C.RESET}")

        try:
            choice = input(f"{C.BOLD}Ingrese una opcion [0-5]: {C.RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo...")
            break

        if choice == "1":
            phrase = "maldicion que gran violencia veo en este lugar"
            process_audio_pipeline(phrase, ProfileType.CHILD_SAFE)
        elif choice == "2":
            phrase = "abro google en mi iphone tomando coca-cola y viendo netflix"
            process_audio_pipeline(phrase, ProfileType.BRAND_COMPLIANCE)
        elif choice == "3":
            phrase = "el chaval aparco el coche y compro un ordenador guay"
            process_audio_pipeline(phrase, ProfileType.LOCALIZATION)
        elif choice == "4":
            print(f"\n{C.BOLD}Perfiles disponibles:{C.RESET} 1=CHILD_SAFE, 2=BRAND_COMPLIANCE, 3=LOCALIZATION")
            p_choice = input("Elija perfil [1-3] (Default: 1): ").strip()
            p_map = {"1": ProfileType.CHILD_SAFE, "2": ProfileType.BRAND_COMPLIANCE, "3": ProfileType.LOCALIZATION}
            selected_p = p_map.get(p_choice, ProfileType.CHILD_SAFE)
            custom_phrase = input("Escriba la frase a procesar: ").strip()
            if not custom_phrase:
                custom_phrase = "maldicion tengo que cambiar este coche"
            process_audio_pipeline(custom_phrase, selected_p)
        elif choice == "5":
            from tests.run_tests import main as run_tests_main
            print(f"\n{C.CYAN}--- Ejecutando Pruebas de QA ---{C.RESET}")
            try:
                run_tests_main()
            except SystemExit:
                pass
        elif choice == "0":
            print(f"{C.GREEN}Finalizado.{C.RESET}\n")
            break
        else:
            print(f"{C.RED}Opcion no valida. Intente de nuevo.{C.RESET}")


def run_cli():
    parser = argparse.ArgumentParser(description="AI Video Post-Production Enhancer (Patent US 2026/0341309 A1)")
    parser.add_argument("--menu", action="store_true", help="Abrir menú interactivo")
    parser.add_argument("--profile", type=str, choices=["CHILD_SAFE", "BRAND_COMPLIANCE", "LOCALIZATION"], help="Perfil de audiencia")
    parser.add_argument("--text", type=str, help="Texto o guión del diálogo a procesar")
    parser.add_argument("--audio", type=str, help="Ruta al archivo WAV de entrada")

    args = parser.parse_args()

    if args.menu or (not args.profile and not args.text):
        # If run directly with no arguments, run interactive menu or single default demo
        if len(sys.argv) == 1:
            run_interactive_menu()
        else:
            run_interactive_menu()
    else:
        profile_enum = ProfileType(args.profile or "CHILD_SAFE")
        text = args.text or "hola este es un demo de maldicion y violencia con coca-cola en el coche"
        process_audio_pipeline(text, profile_enum, args.audio)


if __name__ == "__main__":
    run_cli()
