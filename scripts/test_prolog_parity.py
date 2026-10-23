"""Contrasta el resultado final de Prolog con el motor Python.
Uso: python scripts/test_prolog_parity.py (requiere swipl en PATH).
NO cambia el despliegue web; las respuestas pasan la validacion Python.
"""
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import KB, evaluate, validate_and_normalize

BASE = {
    "uso": "habitual", "anio": 2018, "estructura": "hormigon",
    "electricidad": "revisada", "calefaccion": "electrica",
    "detectores": "si", "humedades": "no", "agua": "no",
    "estructura_estado": "bien", "conservacion": "bueno",
    "desocupacion": "no", "seguridad": "ambas", "inundaciones": "no"
}
CASOS = [
    BASE,
    {**BASE, "electricidad": "sin_revision"},
    {**BASE, "electricidad": "defectuosa", "detectores": "unknown"},
    {**BASE, "calefaccion": "gas", "caldera": "pendiente"},
    {**BASE, "calefaccion": "gas", "caldera": "fuga"},
    {**BASE, "calefaccion": "gas"},
    {**BASE, "estructura": "madera", "proteccion_madera": "no",
     "informe_madera": "desfavorable"},
    {**BASE, "estructura": "madera", "proteccion_madera": "unknown",
     "informe_madera": "favorable"},
    {**BASE, "estructura": "madera", "proteccion_madera": "si",
     "informe_madera": "sin_informe"},
    {**BASE, "anio": 1980},
    {**BASE, "uso": "alquilada"},
    {**BASE, "uso": "no_residencial"},
    {"anio": 2018},  # Uso omitido: el validador Python no admite "unknown" en uso.
    {}
]

aleatorio = random.Random(20261020)
for _ in range(500):
    datos = dict(BASE)
    for pregunta in KB["questions"]:
        if aleatorio.random() < .4:
            if pregunta["type"] == "choice":
                datos[pregunta["id"]] = aleatorio.choice(pregunta["options"])[0]
            elif pregunta["type"] == "year":
                datos[pregunta["id"]] = aleatorio.choice(
                    [1900, 1985, 2005, 2006, 2024, "unknown"]
                )
        if aleatorio.random() < .15:
            datos.pop(pregunta["id"], None)
    CASOS.append(datos)


def firma(respuesta):
    return {
        "status": respuesta["status"],
        "level": respuesta["level"],
        "provisional": respuesta["provisional"],
        "rules": sorted(
            (regla["id"], regla["tier"])
            for regla in respuesta.get("triggered_rules", [])
        ),
        "missing": sorted(
            x["id"] if isinstance(x, dict) else x
            for x in respuesta.get("missing", [])
        ),
    }


def main():
    exe = shutil.which("swipl")
    if not exe:
        raise SystemExit(
            "Falta SWI-Prolog. Instala https://www.swi-prolog.org/download/stable "
            "y confirma que 'swipl --version' funcione."
        )
    normalizados = []
    for indice, datos in enumerate(CASOS, 1):
        try:
            normalizados.append(validate_and_normalize(datos))
        except ValueError as error:
            print(f"CASO INVÁLIDO {indice}: {error}", flush=True)
            print("Datos:", datos, flush=True)
            raise SystemExit(1) from error
    proceso = subprocess.run(
        [exe, "-q", "-s", str(ROOT / "scripts" / "prolog_json.pl"),
         "-g", "main", "-t", "halt"],
        input=json.dumps(normalizados, ensure_ascii=False),
        text=True,
        capture_output=True,
        encoding="utf-8",
        timeout=90,
    )
    if proceso.returncode:
        raise SystemExit("Error al ejecutar Prolog:\n" + proceso.stderr)
    resultados = json.loads(proceso.stdout)
    if len(resultados) != len(CASOS):
        raise SystemExit("Prolog no devolvio todos los casos.")
    for indice, (entrada, recibido) in enumerate(zip(CASOS, resultados), 1):
        esperado = evaluate(entrada)
        if firma(esperado) != firma(recibido):
            print("DIFERENCIA en escenario", indice)
            print("Datos:", entrada)
            print("Python:", firma(esperado))
            print("Prolog:", firma(recibido))
            raise SystemExit(1)
    print("OK: paridad Python / Prolog comprobada en", len(CASOS), "escenarios")


if __name__ == "__main__":
    main()
