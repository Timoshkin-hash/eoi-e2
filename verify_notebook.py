"""Проверка выполнения Notebook задачи №2."""
from pathlib import Path
import json
import nbformat

root = Path(__file__).resolve().parent
nb_path = root / 'notebooks' / 'task_02_social_network.ipynb'
nb = nbformat.read(nb_path, as_version=4)
errors = []
for i, cell in enumerate(nb.cells):
    for output in cell.get('outputs', []):
        if output.output_type == 'error':
            errors.append((i, output.ename, output.evalue))
if errors:
    raise SystemExit(f'Notebook errors: {errors}')
figures = list((root / 'reports' / 'figures').glob('task_02_*.png'))
if len(figures) != 3 or any(p.stat().st_size == 0 for p in figures):
    raise SystemExit(f'Expected 3 non-empty figures, found {len(figures)}')
config = json.loads((root / 'data' / 'task_02_social_network_config.json').read_text(encoding='utf-8'))
if config['task_id'] != 2:
    raise SystemExit('Wrong task id')
text = ''.join(cell.get('source', '') for cell in nb.cells)
for expected in ['Критическая масса', 'NPV', 'Мэткалфа', 'ARPU', 'Стратегические']:
    if expected not in text:
        raise SystemExit(f'Missing section: {expected}')
print('PASS: notebook contains no execution errors')
print('PASS: all three figures exist and are non-empty')
print('PASS: task id and required sections are present')
