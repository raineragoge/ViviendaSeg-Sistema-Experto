"""Adaptador de evaluación Python -> SWI-Prolog -> respuesta para la web.

Requiere SWI-Prolog (comando swipl) en PATH. No modifica el motor
JavaScript utilizado en la versión publicada en Cloudflare Pages.
"""
import json
import subprocess
from pathlib import Path

from engine import KB, QUESTION_MAP, validate_and_normalize

ROOT = Path(__file__).resolve().parent
REGLAS = {r["id"]: r for r in KB["rules"]}

MENSAJES = {
    "alto": "Existe al menos una condición clasificada como riesgo alto por las reglas del prototipo.",
    "medio": "Se han detectado condiciones de riesgo medio o faltan respuestas.",
    "bajo": "No se han activado factores de riesgo alto o medio y las respuestas solicitadas están completas."
}


def evaluate(datos):
    """Valida hechos, consulta Prolog y enriquece sus conclusiones."""
    hechos = validate_and_normalize(datos)

    proceso = subprocess.run(
        [
            "swipl", "-q", "-s",
            str(ROOT / "scripts/prolog_json.pl"),
            "-g", "main", "-t", "halt"
        ],
        input=json.dumps(hechos, ensure_ascii=False),
        capture_output=True,
        text=True,
        timeout=15
    )

    if proceso.returncode != 0:
        raise RuntimeError(
            "Error del motor Prolog: " + proceso.stderr
        )

    salida = json.loads(proceso.stdout)

    for activada in salida["triggered_rules"]:
        regla = REGLAS[activada["id"]]
        activada.update({
            "reason": regla["reason"],
            "recommendation": regla["recommendation"],
            "category": regla["category"],
            "urgent": regla.get("urgent", False)
        })

    salida["missing"] = [
        {"id": campo, "label": QUESTION_MAP[campo]["label"]}
        for campo in salida["missing"]
    ]

    recomendaciones = [
        r["recommendation"]
        for r in salida["triggered_rules"]
    ]

    for rec in KB["general_recommendations"]:
        if hechos.get(rec["field"]) == rec["equals"]:
            recomendaciones.append(rec["text"])

    salida["recommendations"] = list(
        dict.fromkeys(recomendaciones)
    )

    salida["urgent"] = any(
        r["urgent"] for r in salida["triggered_rules"]
    )

    if salida["status"] == "excluded":
        salida["message"] = "Vivienda fuera del alcance."
        salida["reason"] = (
            "El prototipo solo evalúa viviendas propias "
            "de uso residencial."
        )
    elif salida["status"] == "incomplete":
        salida["message"] = "Falta indicar el uso de la vivienda."
    else:
        salida["message"] = MENSAJES[salida["level"]]

    activadas = {r["id"] for r in salida["triggered_rules"]}

    salida["trace"] = [
        {"rule_id": r["id"], "matched": r["id"] in activadas}
        for r in KB["rules"]
    ] if salida["status"] == "ok" else []

    salida["knowledge_version"] = KB["version"]
    salida["scope_note"] = KB["disclaimer"]

    return salida
