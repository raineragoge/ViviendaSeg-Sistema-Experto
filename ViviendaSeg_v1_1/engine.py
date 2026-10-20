"""Motor de inferencia explicable para una evaluación orientativa (no actuarial)."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parent
KB = json.loads((BASE / "knowledge.json").read_text(encoding="utf-8"))
QUESTION_MAP = {q["id"]: q for q in KB["questions"]}
ALLOWED_USAGE = {"habitual", "segunda", "desocupada"}


def _compare(actual, predicate):
    if "eq" in predicate:
        return actual == predicate["eq"]
    if "lt" in predicate:
        return isinstance(actual, int) and not isinstance(actual, bool) and actual < predicate["lt"]
    if "in" in predicate:
        return actual in predicate["in"]
    raise ValueError("Operador no reconocido en la base de conocimientos")


def _matches(condition, facts):
    """Evalúa condiciones simples y composiciones AND/OR del cuestionario."""
    if 'all' in condition:
        return all(_matches(part, facts) for part in condition['all'])
    if 'any' in condition:
        return any(_matches(part, facts) for part in condition['any'])
    return _compare(facts.get(condition['field']), condition)


def is_visible(question, facts):
    condition = question.get('show_if')
    return not condition or _matches(condition, facts)


def visible_questions(facts):
    return [q for q in KB["questions"] if is_visible(q, facts)]


def validate_and_normalize(payload):
    if not isinstance(payload, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON")
    if len(str(payload)) > 30000:
        raise ValueError("Formulario demasiado grande")
    facts = {}
    for key, value in payload.items():
        if key not in QUESTION_MAP:
            raise ValueError(f"Campo desconocido: {key}")
        question = QUESTION_MAP[key]
        if question["type"] == "choice":
            allowed = {o[0] for o in question["options"]}
            if not isinstance(value, str) or value not in allowed:
                raise ValueError(f"Respuesta no válida en {key}")
            facts[key] = value
        elif question["type"] == "year":
            if value == "unknown":
                facts[key] = value
            elif type(value) is int and 1800 <= value <= date.today().year:
                facts[key] = value
            else:
                raise ValueError("El año debe ser un entero válido o 'unknown'")
    # No permitimos inferencia basada en respuestas ocultas de ramas anteriores.
    return {k: v for k, v in facts.items() if is_visible(QUESTION_MAP[k], facts)}


def evaluate(payload):
    facts = validate_and_normalize(payload)
    if facts.get("uso") in {"alquilada", "no_residencial"}:
        return {
            "status": "excluded", "level": None, "provisional": False,
            "message": "La vivienda está fuera del alcance de esta versión del sistema.",
            "reason": "El prototipo se limita a viviendas propias de uso residencial, habituales, segundas residencias o desocupadas.",
            "triggered_rules": [], "missing": [], "recommendations": [], "trace": []
        }
    if facts.get("uso") not in ALLOWED_USAGE:
        return {"status":"incomplete", "level":"medio", "provisional":True,
                "message":"Falta indicar el uso de la vivienda.",
                "triggered_rules":[], "missing":[{"id":"uso","label":QUESTION_MAP['uso']['label']}],
                "recommendations":[],"trace":[]}
    applicable = visible_questions(facts)
    missing = [
        {"id":q["id"], "label":q["label"]}
        for q in applicable
        if q.get('required_for_confidence')
        and facts.get(q['id'], 'unknown') in q.get('uncertain_values', ['unknown'])
        and not (q['id'] == 'proteccion_madera' and facts.get('informe_madera') == 'favorable')
    ]
    triggered = []
    trace = []
    for rule in KB["rules"]:
        fired = all(_compare(facts.get(c["field"]), c) for c in rule["conditions"])
        if fired:
            triggered.append({k:rule[k] for k in ("id","tier","reason","recommendation","category")}
                             | {"urgent":rule.get("urgent",False)})
        trace.append({"rule_id":rule["id"], "matched":fired})
    high = any(r["tier"] == "alto" for r in triggered)
    medium = any(r["tier"] == "medio" for r in triggered)
    level = "alto" if high else "medio" if medium or missing else "bajo"
    # Si existen respuestas pendientes y no hay riesgo alto confirmado,
    # la etiqueta de medio siempre es provisional, incluso si hay reglas medias activas.
    provisional = bool(missing) and not high
    extra = []
    for x in KB["general_recommendations"]:
        if facts.get(x["field"]) == x["equals"]:
            extra.append(x["text"])
    suggestions = list(dict.fromkeys([r["recommendation"] for r in triggered] + extra))
    message = {
        "alto":"Existe al menos una condición clasificada como riesgo alto por las reglas del prototipo.",
        "medio":"Se han detectado condiciones de riesgo medio o faltan respuestas.",
        "bajo":"No se han activado factores de riesgo alto o medio y las respuestas solicitadas están completas."
    }[level]
    return {
        "status":"ok", "level":level, "provisional":provisional,
        "message":message, "triggered_rules":triggered,
        "missing":missing, "recommendations":suggestions,
        "trace":trace, "urgent":any(r["urgent"] for r in triggered),
        "knowledge_version":KB["version"],
        "scope_note":KB["disclaimer"]
    }


if __name__ == "__main__":
    import sys
    facts = json.load(sys.stdin)
    print(json.dumps(evaluate(facts), ensure_ascii=False, indent=2))
