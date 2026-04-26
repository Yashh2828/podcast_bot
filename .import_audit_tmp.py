import ast
import sys
from pathlib import Path
from importlib import util, metadata
from packaging.utils import canonicalize_name

root = Path('.').resolve()
req_path = root / 'requirements.txt'

req_names = set()
for line in req_path.read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    name = ''
    for ch in line:
        if ch.isalnum() or ch in '._-':
            name += ch
        else:
            break
    if name:
        req_names.add(canonicalize_name(name))

local_toplevel = {p.name for p in root.iterdir() if p.is_dir()} | {p.stem for p in root.glob('*.py')}
exclude_parts = {'.venv', '__pycache__', '.git', 'node_modules'}
mods = set()
parse_errors = []
walk_errors = []
read_errors = []
scanned = 0

for py in root.rglob('*.py'):
    if set(py.parts) & exclude_parts:
        continue
    scanned += 1
    txt = None
    for enc in ('utf-8', 'latin-1', 'utf-16'):
        try:
            txt = py.read_text(encoding=enc)
            break
        except Exception:
            pass
    if txt is None:
        read_errors.append(str(py.relative_to(root)))
        continue
    try:
        tree = ast.parse(txt)
    except Exception as e:
        parse_errors.append((str(py.relative_to(root)), str(e)))
        continue

    try:
        nodes = list(ast.walk(tree))
    except Exception as e:
        walk_errors.append((str(py.relative_to(root)), str(e)))
        continue

    for n in nodes:
        if isinstance(n, ast.Import):
            for a in n.names:
                mods.add(a.name.split('.')[0])
        elif isinstance(n, ast.ImportFrom):
            if n.level and (n.module is None):
                continue
            if n.module:
                mods.add(n.module.split('.')[0])

stdlib = set(sys.stdlib_module_names)
third_party = sorted(m for m in mods if m not in stdlib and m not in local_toplevel)
missing_imports = [m for m in third_party if util.find_spec(m) is None]

pkg_map = metadata.packages_distributions()
used_dists = set()
unknown_modules = []
for m in third_party:
    dists = pkg_map.get(m)
    if dists:
        for d in dists:
            used_dists.add(canonicalize_name(d))
    else:
        unknown_modules.append(m)

not_in_requirements = sorted(d for d in used_dists if d not in req_names)

print('=== FULL CODE IMPORT AUDIT ===')
print(f'Python files scanned: {scanned}')
print(f'Imported top-level modules: {len(mods)}')
print(f'Third-party modules referenced: {len(third_party)}')
print(f'Unresolved third-party imports: {len(missing_imports)}')
print(f'Used distributions not listed in requirements.txt: {len(not_in_requirements)}')
print(f'Read errors: {len(read_errors)}')
print(f'Parse errors: {len(parse_errors)}')
print(f'Walk errors: {len(walk_errors)}')

if missing_imports:
    print('\n-- Missing imports in environment --')
    for m in missing_imports:
        print(m)

if not_in_requirements:
    print('\n-- Potentially used but not in requirements.txt --')
    for d in not_in_requirements:
        print(d)
