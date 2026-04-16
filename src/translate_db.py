"""Translate selected database fields to English.

Safe defaults:
- Keeps all original Spanish/source columns untouched.
- Adds English columns if missing.
- Fills `sujetos.sexo_en` and `sujetos.actividad_en` with deterministic mappings.
- Fills `comida.nombre_en` as a copy of `comida.nombre` unless auto-translation is enabled.

Optional:
- `--translate-food-names` to auto-translate food names using deep-translator.
"""

from __future__ import annotations

import argparse
import os
from typing import Callable

import mysql.connector

try:
    from dotenv import load_dotenv
except ImportError:  # Optional dependency
    load_dotenv = None


SEX_MAP = {
    "H": "Male",
    "M": "Female",
}

ACTIVITY_MAP = {
    "Sedentario": "Sedentary",
    "Ligero": "Light",
    "Moderado": "Moderate",
    "Alto": "High",
    "Muy Alto": "Very High",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add/fill English translation columns in the nutrition database."
    )
    parser.add_argument(
        "--translate-food-names",
        action="store_true",
        help="Translate `comida.nombre` to English with deep-translator.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing translated values.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show intended actions without writing changes.",
    )
    return parser.parse_args()


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) AS c
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    return cursor.fetchone()["c"] > 0


def ensure_column(cursor, table: str, column: str, definition: str, dry_run: bool) -> None:
    if column_exists(cursor, table, column):
        return
    sql = f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
    if dry_run:
        print(f"[dry-run] {sql}")
        return
    cursor.execute(sql)
    print(f"[ok] Added column {table}.{column}")


def update_sujetos(cursor, dry_run: bool) -> None:
    cursor.execute("SELECT id, sexo, actividad FROM sujetos")
    rows = cursor.fetchall()
    updates = []
    for row in rows:
        updates.append((SEX_MAP.get(row["sexo"], row["sexo"]), ACTIVITY_MAP.get(row["actividad"], row["actividad"]), row["id"]))

    if dry_run:
        print(f"[dry-run] Would update {len(updates)} rows in sujetos")
        return

    cursor.executemany(
        """
        UPDATE sujetos
        SET sexo_en = %s, actividad_en = %s
        WHERE id = %s
        """,
        updates,
    )
    print(f"[ok] Updated sujetos translations: {len(updates)} rows")


def build_translator() -> Callable[[str], str]:
    try:
        from deep_translator import GoogleTranslator  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "deep-translator is required for --translate-food-names. "
            "Install with: pip install deep-translator"
        ) from exc

    translator = GoogleTranslator(source="es", target="en")
    return translator.translate


def update_comida(
    cursor,
    translate_food_names: bool,
    force: bool,
    dry_run: bool,
    has_nombre_en_column: bool,
) -> None:
    where_clause = ""
    if not force and has_nombre_en_column:
        where_clause = "WHERE nombre_en IS NULL OR nombre_en = ''"
    cursor.execute(f"SELECT id, nombre FROM comida {where_clause}")
    rows = cursor.fetchall()

    if not rows:
        print("[ok] No comida rows need translation")
        return

    if translate_food_names:
        translate = build_translator()
        translated = []
        for row in rows:
            translated.append((translate(row["nombre"]), row["id"]))
    else:
        translated = [(row["nombre"], row["id"]) for row in rows]

    if dry_run:
        mode = "auto-translate" if translate_food_names else "copy source text"
        print(f"[dry-run] Would update {len(translated)} rows in comida ({mode})")
        return

    cursor.executemany(
        "UPDATE comida SET nombre_en = %s WHERE id = %s",
        translated,
    )
    print(f"[ok] Updated comida.nombre_en: {len(translated)} rows")


def main() -> None:
    args = parse_args()

    if load_dotenv is not None:
        load_dotenv()

    config = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "database": os.getenv("DB_NAME"),
        "raise_on_warnings": True,
    }
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)

    try:
        ensure_column(cursor, "comida", "nombre_en", "VARCHAR(255) NULL", args.dry_run)
        ensure_column(cursor, "sujetos", "sexo_en", "VARCHAR(16) NULL", args.dry_run)
        ensure_column(cursor, "sujetos", "actividad_en", "VARCHAR(32) NULL", args.dry_run)
        has_nombre_en = column_exists(cursor, "comida", "nombre_en")

        update_sujetos(cursor, args.dry_run)
        update_comida(
            cursor,
            translate_food_names=args.translate_food_names,
            force=args.force,
            dry_run=args.dry_run,
            has_nombre_en_column=has_nombre_en,
        )

        if args.dry_run:
            print("[dry-run] Finished without committing.")
        else:
            cnx.commit()
            print("[ok] Translation committed.")
    finally:
        cursor.close()
        cnx.close()


if __name__ == "__main__":
    main()
