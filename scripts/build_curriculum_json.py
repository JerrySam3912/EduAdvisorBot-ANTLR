from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DATA = ROOT / 'apps' / 'backend-api' / 'app' / 'data'


def main() -> None:
    index_path = BACKEND_DATA / 'curriculum_index.json'
    if not index_path.exists():
        raise FileNotFoundError(f'Index file not found: {index_path}')

    with index_path.open('r', encoding='utf-8') as f:
        index = json.load(f)

    curricula = index.get('curricula', {})
    missing = []
    for key, file_name in curricula.items():
        path = BACKEND_DATA / file_name
        if not path.exists():
            missing.append(f'{key} -> {file_name}')

    if missing:
        raise FileNotFoundError('Missing runtime curriculum files:\n' + '\n'.join(missing))

    print('curriculum_index.json OK')
    print(f'Found {len(curricula)} curriculum mappings')


if __name__ == '__main__':
    main()
