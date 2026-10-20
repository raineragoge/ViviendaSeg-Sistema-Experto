"""Regenera el módulo de Cloudflare desde la base de conocimientos de Python."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / 'knowledge.json').read_text(encoding='utf-8'))
out = ROOT / 'functions' / '_shared' / 'knowledge.js'
serialized = json.dumps(source, ensure_ascii=False, separators=(',', ':'))
expected = '// GENERADO DESDE knowledge.json: no editar manualmente.\nexport default ' + serialized + ';\n'
if '--check' in sys.argv:
    if not out.exists() or out.read_text(encoding='utf-8') != expected:
        raise SystemExit('ERROR: knowledge.js desactualizado. Ejecuta python scripts/sync_knowledge.py')
    print('Conocimiento Cloudflare sincronizado')
else:
    out.write_text(expected, encoding='utf-8')
    print(f'Generado: {out}')
