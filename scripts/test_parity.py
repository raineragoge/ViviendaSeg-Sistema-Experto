"""Prueba de paridad Python vs JavaScript: mismo payload, misma conclusión.
No compara mensajes de error de Python/JS (pueden diferir).
"""
from __future__ import annotations
import json
import random
import subprocess
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import evaluate, KB

rng=random.Random(20261020)
base={
    'uso':'habitual','anio':2018,'estructura':'hormigon','electricidad':'revisada',
    'calefaccion':'electrica','detectores':'si','humedades':'no','agua':'no',
    'estructura_estado':'bien','conservacion':'bueno','desocupacion':'no',
    'seguridad':'ambas','inundaciones':'no'
}
inputs=[base,{**base,'estructura':'madera','proteccion_madera':'si','informe_madera':'favorable'},
        {**base,'estructura':'madera','proteccion_madera':'no','informe_madera':'desfavorable'},
        {**base,'estructura':'mixta','material_mixto':'si','proteccion_madera':'unknown','informe_madera':'sin_informe'},
        {},{'uso':'alquilada'}, {'uso':'no_residencial'}]
for i in range(500):
    v={**base}
    # Preguntas adicionales se incluyen deliberadamente incluso cuando quedan ocultas.
    for q in KB['questions']:
        if rng.random() < .4:
            if q['type']=='choice': v[q['id']]=rng.choice(q['options'])[0]
            elif q['type']=='year':v[q['id']]=rng.choice([1900,1985,2005,2006,2024,'unknown'])
        if rng.random()<.15: v.pop(q['id'],None)
    inputs.append(v)
node=subprocess.run(['node',str(ROOT/'scripts/runner.mjs')],input=json.dumps(inputs,ensure_ascii=False),text=True,capture_output=True,check=True)
responses=json.loads(node.stdout)
for idx,(payload,response) in enumerate(zip(inputs,responses)):
    expected=evaluate(payload)
    if not response['ok'] or response['data']!=expected:
        print(f'ERROR paridad escenario {idx}: {payload}')
        print('Python:',json.dumps(expected,ensure_ascii=False))
        print('JS:',json.dumps(response,ensure_ascii=False))
        raise SystemExit(1)
print(f'Paridad Python/JS verificada: {len(inputs)} escenarios')
