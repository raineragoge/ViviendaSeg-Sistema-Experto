import {test} from 'node:test';
import assert from 'node:assert/strict';
import {evaluate, schema} from '../functions/_shared/engine.js';
import {onRequestGet} from '../functions/api/schema.js';
import {onRequestPost} from '../functions/api/evaluate.js';

const base = {
  uso: 'habitual', anio: 2018, estructura: 'hormigon', electricidad: 'revisada',
  calefaccion: 'electrica', detectores: 'si', humedades: 'no', agua: 'no',
  estructura_estado: 'bien', conservacion: 'bueno', desocupacion: 'no',
  seguridad: 'ambas', inundaciones: 'no',
};
const run = (answers={}) => evaluate({...base, ...answers});

test('catálogo y reglas', () => {
  assert.equal(schema().questions.length, 19);
  assert.equal(schema().version, '1.1.0');
  assert.equal(run().trace.length, 16);
});
test('riesgo bajo cuando no hay factores', () => {
  assert.equal(run().level,'bajo');
  assert.equal(run().provisional,false);
});
test('madera con documentación favorable no sube el riesgo', () => {
  assert.equal(run({estructura:'madera', proteccion_madera:'si', informe_madera:'favorable'}).level,'bajo');
});
test('madera desfavorable activa riesgo alto', () => {
  const r = run({estructura:'madera',proteccion_madera:'no',informe_madera:'desfavorable'});
  assert.equal(r.level, 'alto'); assert.ok(r.triggered_rules.some(x=>x.id==='R01'));
});
test('madera sin informe -> provisional', () => {
  const r=run({estructura:'madera',proteccion_madera:'si',informe_madera:'sin_informe'});
  assert.deepEqual([r.level,r.provisional], ['medio',true]);
});
test('factor alto prevalece sobre respuestas desconocidas', () => {
  const r=run({estructura:'madera',proteccion_madera:'no',informe_madera:'desfavorable',electricidad:'unknown'});
  assert.deepEqual([r.level,r.provisional], ['alto',false]);assert.ok(r.missing.length);
});
test('una fuga de gas es urgente', () => {
  const r=run({calefaccion:'gas',caldera:'fuga'});
  assert.equal(r.level,'alto'); assert.equal(r.urgent,true);
});
test('los campos ocultos se descartan', () => {
  assert.equal(run({calefaccion:'electrica',caldera:'fuga'}).level,'bajo');
});
test('pregunta de madera estructural mixta', () => {
  const r=run({estructura:'mixta',material_mixto:'si',proteccion_madera:'no',informe_madera:'desfavorable'});
  assert.equal(r.level,'alto'); assert.ok(r.triggered_rules.some(x=>x.id==='R02'));
});
test('uso excluido', () => {
  assert.equal(run({uso:'alquilada'}).status,'excluded');
});
test('rechaza opciones inválidas', () => {
  assert.throws(()=>run({estructura:'diamante'}));
  assert.throws(()=>run({anio:3000}));
  assert.throws(()=>run({unsupported:'evil'}));
});
test('API schema sirve preguntas',async()=>{
  const r=onRequestGet(); assert.equal(r.status,200);
  const payload=await r.json(); assert.equal(payload.questions.length,19);
});
test('API evaluate procesa JSON y no guarda respuestas',async()=>{
  const request=new Request('https://example.pages.dev/api/evaluate', {method:'POST', headers:{'content-type':'application/json'},body:JSON.stringify(base)});
  const r=await onRequestPost({request}); assert.equal(r.status,200);
  assert.equal((await r.json()).level,'bajo');
});
test('API rechaza datos mal formados',async()=>{
  const request=new Request('https://example.pages.dev/api/evaluate', {method:'POST',body:'{' });
  const r=await onRequestPost({request});assert.equal(r.status,400);
});
