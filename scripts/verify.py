
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
REPORT = ARTIFACTS / "pytest-results.xml"


def write_setup_failure_report(return_code):
    """Genera un reporte nuevo si falla la preparación."""
    suite = ET.Element(
        "testsuite",
        {
            "name": "setup",
            "tests": "1",
            "failures": "0",
            "errors": "1",
            "skipped": "0",
        },
    )
    case = ET.SubElement(
        suite,
        "testcase",
        {"classname": "setup", "name": "prepare_environment"},
    )
    error = ET.SubElement(
        case,
        "error",
        {
            "message": f"make setup terminó con código {return_code}",
            "type": "SetupError",
        },
    )
    error.text = (
        "Falló la preparación del entorno. "
        "Consulta la salida de make setup para ver el error."
    )

    ET.ElementTree(suite).write(
        REPORT,
        encoding="utf-8",
        xml_declaration=True,
    )


def main():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    # Elimina el reporte anterior para no confundir resultados antiguos.
    REPORT.unlink(missing_ok=True)

    print("Preparando el entorno...")
    setup = subprocess.run(["make", "setup"], cwd=ROOT)

    if setup.returncode != 0:
        write_setup_failure_report(setup.returncode)
        print(f"Falló make setup. Reporte: {REPORT}")
        return setup.returncode

    print("Ejecutando pruebas...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            f"--junitxml={REPORT}",
        ],
        cwd=ROOT,
    )

    if result.returncode != 0:
        print(f"Las pruebas fallaron. Reporte: {REPORT}")
    else:
        print(f"Pruebas aprobadas. Reporte: {REPORT}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
