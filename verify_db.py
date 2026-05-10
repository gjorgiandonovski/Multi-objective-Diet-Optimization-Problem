"""Database connectivity check.

Loads foods and subject profiles from MySQL and prints a summary. Run from the
project root with the venv active:

    python verify_db.py
"""
from __future__ import annotations

import sys
from collections import Counter


def main() -> int:
    try:
        from diet_bao.data import load_foods_from_db, load_subjects_from_db
    except Exception as exc:  # pragma: no cover - diagnostic path
        print(f"[FAIL] Cannot import diet_bao.data: {exc}")
        print("       Run 'pip install -e .' inside the project root first.")
        return 1

    try:
        foods = load_foods_from_db()
    except Exception as exc:
        print(f"[FAIL] load_foods_from_db raised: {exc}")
        print("       Check .env values (DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT).")
        return 1

    try:
        subjects = load_subjects_from_db()
    except Exception as exc:
        print(f"[FAIL] load_subjects_from_db raised: {exc}")
        return 1

    print(f"[OK] foods loaded: {len(foods)}")
    print(f"[OK] subjects loaded: {len(subjects)}")

    if foods:
        sample = foods[0]
        print(f"[OK] sample food keys: {sorted(sample.keys())}")
        print(f"     sample row: {sample}")

        groups = Counter((row.get('grupo') or '') for row in foods)
        top = groups.most_common(10)
        print("[OK] top food groups:")
        for grupo, n in top:
            print(f"     {grupo!r}: {n}")

    print("\n[OK] Subject profiles:")
    for s in subjects:
        print(
            f"  id={s.sujeto_id} edad={s.edad} kcal_target={s.calorias} "
            f"gustos={len(s.gustos)} disgustos={len(s.disgustos)} alergias={len(s.alergias)}"
        )

    print("\n[ALL GOOD] Database is reachable and the schema matches diet_bao expectations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
