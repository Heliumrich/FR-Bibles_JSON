#!/usr/bin/env python3
"""
Ajoute une traduction dans la base bible.db à partir d'un fichier JSON.
"""

import json
import sqlite3
import argparse
from pathlib import Path

DB_PATH = Path("bible.db")


def add_translation(json_path: Path, meta: dict):
    if not DB_PATH.exists():
        print("Erreur : bible.db n'existe pas. Lance d'abord create_bible_db.py")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        verses = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # 1. Insérer la traduction
        cur.execute("""
            INSERT INTO translations (
                code, name_short, name_full, authors, year, language,
                description, source_ot, source_nt, license, notes
            ) VALUES (
                :code, :name_short, :name_full, :authors, :year, :language,
                :description, :source_ot, :source_nt, :license, :notes
            )
        """, meta)
        translation_id = cur.lastrowid
        print(f"✓ Traduction {meta['code']} ajoutée (id={translation_id})")

        # 2. Insérer les versets
        count = 0
        for v in verses:
            cur.execute("""
                INSERT INTO verses (translation_id, book, chapter, verse, text)
                VALUES (?, ?, ?, ?, ?)
            """, (
                translation_id,
                v["book"],
                v["chapter"],
                v["verse"],
                v["text"]
            ))
            count += 1
            if count % 5000 == 0:
                print(f"  ... {count} versets")

        conn.commit()
        print(f"✓ {count} versets importés pour {meta['code']}")

    except sqlite3.IntegrityError as e:
        print(f"Erreur (probablement code déjà existant) : {e}")
        conn.rollback()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Ajoute une traduction dans bible.db")
    parser.add_argument("json_file", help="Fichier JSON des versets")
    parser.add_argument("--code", required=True, help="Code court (ex: BDT, VUL, SAC)")
    parser.add_argument("--name-short", required=True)
    parser.add_argument("--name-full", required=True)
    parser.add_argument("--authors", default="")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--description", default="")
    parser.add_argument("--source-ot", default="")
    parser.add_argument("--source-nt", default="")
    parser.add_argument("--license", default="Domaine public")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    meta = {
        "code": args.code.upper(),
        "name_short": args.name_short,
        "name_full": args.name_full,
        "authors": args.authors,
        "year": args.year,
        "language": "fr" if args.code.upper() != "VUL" else "la",
        "description": args.description,
        "source_ot": args.source_ot,
        "source_nt": args.source_nt,
        "license": args.license,
        "notes": args.notes,
    }

    add_translation(Path(args.json_file), meta)


if __name__ == "__main__":
    main()