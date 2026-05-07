from __future__ import annotations

import os
from typing import List

from dietopt.types import FoodItem, SubjectProfile


def has_db_env() -> bool:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        # If python-dotenv isn't installed, just fall back to process env.
        pass

    return all(os.getenv(k) for k in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"))


def require_db_env() -> None:
    """Raise a clear error if DB env vars are missing.

    The notebook/workflow is expected to run on the real MySQL dataset.
    """

    if not has_db_env():
        missing = [k for k in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME") if not os.getenv(k)]
        raise RuntimeError(
            "Missing DB configuration in environment. "
            "Create a .env file (see .env.example) and set: "
            + ", ".join(missing)
        )


def load_foods_from_db() -> List[FoodItem]:
    from utils.database import comida_basedatos

    # database.py already returns dicts with these keys.
    return comida_basedatos()  # type: ignore[return-value]


def load_subjects_from_db() -> List[SubjectProfile]:
    from utils.database import sujetos_basedatos

    raw = sujetos_basedatos()
    subjects: List[SubjectProfile] = []
    for s in raw:
        subjects.append(
            SubjectProfile(
                sujeto_id=int(s["sujeto_id"]),
                edad=int(s["edad"]),
                calorias=float(s["calorias"]),
                gustos=list(s.get("gustos", [])),
                disgustos=list(s.get("disgustos", [])),
                alergias=list(s.get("alergias", [])),
            )
        )
    return subjects
