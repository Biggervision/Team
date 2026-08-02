#!/usr/bin/env python3
"""Concatenate the modular apps-script/*.gs files (filename order) into a
single pasteable file: dist/AscensionOS.gs"""
import glob, os

SRC = os.path.join(os.path.dirname(__file__), '..', 'apps-script')
OUT = os.path.join(os.path.dirname(__file__), '..', 'dist', 'AscensionOS.gs')

parts = []
for path in sorted(glob.glob(os.path.join(SRC, '*.gs'))):
    name = os.path.basename(path)
    with open(path, encoding='utf-8') as f:
        body = f.read().rstrip()
    parts.append(f'/* ═══════════════ {name} ═══════════════ */\n\n{body}\n')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(parts) + '\n')
print('wrote', OUT, f'({sum(len(p) for p in parts)} chars, {len(parts)} modules)')
