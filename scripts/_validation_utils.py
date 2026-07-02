from __future__ import annotations
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
OUT = ROOT / 'sample_outputs' / 'validation'
OUT.mkdir(parents=True, exist_ok=True)

def save_validation(name: str, result: dict):
    js = OUT / f'{name}.json'
    md = OUT / f'{name}.md'
    js.write_text(json.dumps(result, indent=2, default=str), encoding='utf-8')
    lines = [f'# {name.replace("_", " ").title()}', '', f"Status: **{result.get('status','unknown')}**", '']
    for k, v in result.items():
        if k == 'status': continue
        lines += [f'## {k.replace("_", " ").title()}', '']
        if isinstance(v, list): lines += [f'- {x}' for x in v]
        elif isinstance(v, dict): lines += [f'- **{a}**: {b}' for a,b in v.items()]
        else: lines += [str(v)]
        lines.append('')
    md.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'result': result, 'json': str(js), 'markdown': str(md)}, indent=2, default=str))
    return js, md

def fresh_db():
    from app.db.session import init_db, SessionLocal
    from app.db.seed import seed_database
    init_db(drop_existing=True)
    db = SessionLocal()
    seed_database(db, reset=False)
    return db


def ensure(condition: bool, message: str = "validation failed") -> None:
    if not condition:
        raise AssertionError(message)

def write_result(name: str, result: dict):
    status = "passed" if result.get("passed", True) else "failed"
    return save_validation(name, {"status": status, **result})
