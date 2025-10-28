#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import List, Tuple

BASE = Path('Final Proof') / 'Collection' / 'Formula'
OUT_FILE = Path('lab') / 'docs' / 'RLE_THEORY_APPENDICES.md'

TARGETS = [
	' miners law thermal paths.txt',
	' miners law.txt',
	' minor law final.txt',
	' RCF.txt',
	' warp threshold constant.txt',
	' Recursive_Feedback_Stabilization.csv',
	' Recursive_Processing_Model.csv',
	' Volume_8_Time_Memory_Observer.txt',
]
# Normalize names (files in listing may not have leading space). We'll fuzzy match by lowercase stripped.
TARGETS = [t.strip().lower() for t in TARGETS]

KEY_RE = re.compile(r"(T_sustain|t_sustain|time[- ]to[- ]limit|dT/dt|A_load|P[_/ ]rated|rated power|util|utilization|variance|std|stability|energy balance|entropy|P\s*=|Qdot|Wdot)", re.IGNORECASE)


def pick_files() -> List[Path]:
	candidates: List[Path] = []
	if not BASE.exists():
		return candidates
	# index files in BASE
	files = []
	for root, _, fns in os.walk(BASE):
		for fn in fns:
			p = Path(root) / fn
			files.append(p)
	# match targets by name
	for t in TARGETS:
		for p in files:
			if p.name.lower() == t:
				candidates.append(p)
				break
	return candidates


def extract_snips(path: Path, max_snips: int = 8) -> List[str]:
	try:
		text = path.read_text(encoding='utf-8', errors='ignore')
	except Exception:
		return []
	lines = text.splitlines()
	snips: List[str] = []
	for i, line in enumerate(lines):
		if KEY_RE.search(line):
			start = max(0, i - 1)
			end = min(len(lines), i + 2)
			s = '\n'.join(lines[start:end]).strip()
			if s and s not in snips:
				snips.append(s)
				if len(snips) >= max_snips:
					break
	return snips


def write_appendices(items: List[Tuple[Path, List[str]]]) -> None:
	lines: List[str] = []
	lines.append('# RLE Theory Appendices (Sourced)')
	lines.append('')
	lines.append('Primary technical sources from Final Proof/Collection/Formula relevant to RLE terms. Non-technical content omitted.')
	lines.append('')
	app_idx = 1
	for path, snips in items:
		if not snips:
			continue
		lines.append(f'## Appendix {app_idx}: {path.name}')
		lines.append(f'Path: `{path}`')
		lines.append('')
		for sn in snips:
			lines.append('```')
			lines.append(sn)
			lines.append('```')
			lines.append('')
		lines.append('---')
		lines.append('')
		app_idx += 1
	OUT_FILE.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
	files = pick_files()
	items: List[Tuple[Path, List[str]]] = []
	for p in files:
		snips = extract_snips(p)
		items.append((p, snips))
	write_appendices(items)
	print(f"Wrote appendices for {sum(1 for _, s in items if s)} sources → {OUT_FILE}")
