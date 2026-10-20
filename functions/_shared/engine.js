/** Motor de inferencia de Pages Functions: porta la semántica de engine.py.
 * El catálogo de reglas se genera desde knowledge.json (scripts/sync_knowledge.py).
 * Ni identifica usuarios ni persiste respuestas.
 */
import KB from './knowledge.js';

const QUESTION_MAP = new Map(KB.questions.map((q) => [q.id, q]));
const ALLOWED_USAGE = new Set(['habitual', 'segunda', 'desocupada']);
const own = (obj, field) => Object.prototype.hasOwnProperty.call(obj, field);

function compare(actual, predicate) {
  if (own(predicate, 'eq')) return actual === predicate.eq;
  if (own(predicate, 'lt')) return Number.isInteger(actual) && actual < predicate.lt;
  if (own(predicate, 'in')) return predicate.in.includes(actual);
  throw new Error('Operador no reconocido en la base de conocimientos');
}

function matches(condition, facts) {
  if (own(condition, 'all')) return condition.all.every((part) => matches(part, facts));
  if (own(condition, 'any')) return condition.any.some((part) => matches(part, facts));
  return compare(facts[condition.field], condition);
}

function visible(question, facts) {
  return !question.show_if || matches(question.show_if, facts);
}

function normalize(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error('El cuerpo debe ser un objeto JSON');
  }
  if (JSON.stringify(payload).length > 30000) throw new Error('Formulario demasiado grande');
  const facts = {};
  for (const [key, value] of Object.entries(payload)) {
    const q = QUESTION_MAP.get(key);
    if (!q) throw new Error(`Campo desconocido: ${key}`);
    if (q.type === 'choice') {
      if (typeof value !== 'string' || !q.options.some(([v]) => v === value)) {
        throw new Error(`Respuesta no válida en ${key}`);
      }
    } else if (q.type === 'year') {
      const currentYear = new Date().getUTCFullYear();
      if (value !== 'unknown' && !(Number.isInteger(value) && value >= 1800 && value <= currentYear)) {
        throw new Error("El año debe ser un entero válido o 'unknown'");
      }
    }
    facts[key] = value;
  }
  return Object.fromEntries(Object.entries(facts).filter(([key]) => visible(QUESTION_MAP.get(key), facts)));
}

export function schema() {
  return {
    questions: KB.questions,
    name: KB.model_name,
    version: KB.version,
    references: KB.references,
    disclaimer: KB.disclaimer,
  };
}

export function evaluate(payload) {
  const facts = normalize(payload);
  if (['alquilada', 'no_residencial'].includes(facts.uso)) {
    return {
      status: 'excluded', level: null, provisional: false,
      message: 'La vivienda está fuera del alcance de esta versión del sistema.',
      reason: 'El prototipo se limita a viviendas propias de uso residencial, habituales, segundas residencias o desocupadas.',
      triggered_rules: [], missing: [], recommendations: [], trace: [],
    };
  }
  if (!ALLOWED_USAGE.has(facts.uso)) {
    return {
      status: 'incomplete', level: 'medio', provisional: true,
      message: 'Falta indicar el uso de la vivienda.',
      triggered_rules: [], missing: [{ id: 'uso', label: QUESTION_MAP.get('uso').label }],
      recommendations: [], trace: [],
    };
  }

  const missing = KB.questions.filter((q) => visible(q, facts) && q.required_for_confidence &&
    (q.uncertain_values || ['unknown']).includes(facts[q.id] === undefined ? 'unknown' : facts[q.id]) &&
    !(q.id === 'proteccion_madera' && facts.informe_madera === 'favorable'))
    .map((q) => ({ id: q.id, label: q.label }));

  const triggered = [];
  const trace = [];
  for (const rule of KB.rules) {
    const fired = rule.conditions.every((c) => compare(facts[c.field], c));
    if (fired) triggered.push({
      id: rule.id, tier: rule.tier, reason: rule.reason,
      recommendation: rule.recommendation, category: rule.category,
      urgent: rule.urgent || false,
    });
    trace.push({ rule_id: rule.id, matched: fired });
  }

  const high = triggered.some((r) => r.tier === 'alto');
  const medium = triggered.some((r) => r.tier === 'medio');
  const level = high ? 'alto' : (medium || missing.length > 0 ? 'medio' : 'bajo');
  const provisional = missing.length > 0 && !high;
  const extra = KB.general_recommendations.filter((r) => facts[r.field] === r.equals).map((r) => r.text);
  const recommendations = [...new Set([...triggered.map((r) => r.recommendation), ...extra])];
  const messages = {
    alto: 'Existe al menos una condición clasificada como riesgo alto por las reglas del prototipo.',
    medio: 'Se han detectado condiciones de riesgo medio o faltan respuestas.',
    bajo: 'No se han activado factores de riesgo alto o medio y las respuestas solicitadas están completas.',
  };
  return {
    status: 'ok', level, provisional, message: messages[level],
    triggered_rules: triggered, missing, recommendations,
    trace, urgent: triggered.some((r) => r.urgent),
    knowledge_version: KB.version, scope_note: KB.disclaimer,
  };
}
