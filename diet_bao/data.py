from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from diet_bao.types import FoodItem, SubjectProfile


def require_db_env() -> None:
    load_dotenv()
    required = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Missing DB configuration: " + ", ".join(missing))


def _connect():
    try:
        import mysql.connector  # type: ignore
    except Exception as exc:
        raise RuntimeError("Missing mysql-connector-python dependency") from exc

    require_db_env()

    config: dict[str, Any] = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "raise_on_warnings": True,
    }
    if os.getenv("DB_PORT"):
        config["port"] = int(os.getenv("DB_PORT", "3306"))

    return mysql.connector.connect(**config)


def load_foods_from_db() -> list[FoodItem]:
    cnx = _connect()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT nombre, grupo, calorias, grasas, proteinas, carbohidratos FROM comida")
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows


def load_subjects_from_db() -> list[SubjectProfile]:
    cnx = _connect()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT s.id AS sujeto_id, s.edad, sc.calorias
        FROM sujetos s
        JOIN sujetos_calorias sc ON s.id = sc.id
        """
    )
    base = cursor.fetchall()

    def map_table(name: str) -> dict[int, list[str]]:
        cursor.execute(f"SELECT sujeto_id, grupo FROM {name}")
        out: dict[int, list[str]] = {}
        for row in cursor.fetchall():
            out.setdefault(int(row["sujeto_id"]), []).append(str(row["grupo"]))
        return out

    gustos = map_table("sujetos_gustos")
    disgustos = map_table("sujetos_disgustos")
    alergias = map_table("sujetos_alergias")

    cursor.close()
    cnx.close()

    subjects: list[SubjectProfile] = []
    for row in base:
        sid = int(row["sujeto_id"])
        subjects.append(
            SubjectProfile(
                sujeto_id=sid,
                edad=int(row["edad"]),
                calorias=float(row["calorias"]),
                gustos=gustos.get(sid, []),
                disgustos=disgustos.get(sid, []),
                alergias=alergias.get(sid, []),
            )
        )
    return subjects
