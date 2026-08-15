#!/usr/bin/env python3
"""
Crée la structure vide de la base de données multi-traductions.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("bible.db")

CATHOLIC_ORDER = [
    ("GEN", "Genèse", "OT"),
    ("EXO", "Exode", "OT"),
    ("LEV", "Lévitique", "OT"),
    ("NUM", "Nombres", "OT"),
    ("DEU", "Deutéronome", "OT"),
    ("JOS", "Josué", "OT"),
    ("JDG", "Juges", "OT"),
    ("RUT", "Ruth", "OT"),
    ("1SA", "1 Samuel", "OT"),
    ("2SA", "2 Samuel", "OT"),
    ("1KI", "1 Rois", "OT"),
    ("2KI", "2 Rois", "OT"),
    ("1CH", "1 Chroniques", "OT"),
    ("2CH", "2 Chroniques", "OT"),
    ("EZR", "Esdras", "OT"),
    ("NEH", "Néhémie", "OT"),
    ("TOB", "Tobie", "OT"),
    ("JDT", "Judith", "OT"),
    ("EST", "Esther", "OT"),
    ("1MA", "1 Maccabées", "OT"),
    ("2MA", "2 Maccabées", "OT"),
    ("JOB", "Job", "OT"),
    ("PSA", "Psaumes", "OT"),
    ("PRO", "Proverbes", "OT"),
    ("ECC", "Ecclésiaste", "OT"),
    ("SNG", "Cantique des Cantiques", "OT"),
    ("WIS", "Sagesse", "OT"),
    ("SIR", "Ecclésiastique", "OT"),
    ("ISA", "Isaïe", "OT"),
    ("JER", "Jérémie", "OT"),
    ("LAM", "Lamentations", "OT"),
    ("BAR", "Baruch", "OT"),
    ("EZK", "Ézéchiel", "OT"),
    ("DAN", "Daniel", "OT"),
    ("HOS", "Osée", "OT"),
    ("JOL", "Joël", "OT"),
    ("AMO", "Amos", "OT"),
    ("OBA", "Abdias", "OT"),
    ("JON", "Jonas", "OT"),
    ("MIC", "Michée", "OT"),
    ("NAM", "Nahum", "OT"),
    ("HAB", "Habacuc", "OT"),
    ("ZEP", "Sophonie", "OT"),
    ("HAG", "Aggée", "OT"),
    ("ZEC", "Zacharie", "OT"),
    ("MAL", "Malachie", "OT"),
    ("MAT", "Matthieu", "NT"),
    ("MRK", "Marc", "NT"),
    ("LUK", "Luc", "NT"),
    ("JHN", "Jean", "NT"),
    ("ACT", "Actes", "NT"),
    ("ROM", "Romains", "NT"),
    ("1CO", "1 Corinthiens", "NT"),
    ("2CO", "2 Corinthiens", "NT"),
    ("GAL", "Galates", "NT"),
    ("EPH", "Éphésiens", "NT"),
    ("PHP", "Philippiens", "NT"),
    ("COL", "Colossiens", "NT"),
    ("1TH", "1 Thessaloniciens", "NT"),
    ("2TH", "2 Thessaloniciens", "NT"),
    ("1TI", "1 Timothée", "NT"),
    ("2TI", "2 Timothée", "NT"),
    ("TIT", "Tite", "NT"),
    ("PHM", "Philémon", "NT"),
    ("HEB", "Hébreux", "NT"),
    ("JAS", "Jacques", "NT"),
    ("1PE", "1 Pierre", "NT"),
    ("2PE", "2 Pierre", "NT"),
    ("1JN", "1 Jean", "NT"),
    ("2JN", "2 Jean", "NT"),
    ("3JN", "3 Jean", "NT"),
    ("JUD", "Jude", "NT"),
    ("REV", "Apocalypse", "NT"),
]


def create_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript("""
        PRAGMA journal_mode = WAL;
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS translations (
            id              INTEGER PRIMARY KEY,
            code            TEXT NOT NULL UNIQUE,
            name_short      TEXT NOT NULL,
            name_full       TEXT NOT NULL,
            authors         TEXT,
            year            INTEGER,
            language        TEXT NOT NULL DEFAULT 'fr',
            description     TEXT,
            source_ot       TEXT,
            source_nt       TEXT,
            license         TEXT,
            notes           TEXT
        );

        CREATE TABLE IF NOT EXISTS books (
            code            TEXT PRIMARY KEY,
            name_fr         TEXT NOT NULL,
            testament       TEXT NOT NULL CHECK(testament IN ('OT','NT')),
            order_num       INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS verses (
            translation_id  INTEGER NOT NULL,
            book            TEXT NOT NULL,
            chapter         INTEGER NOT NULL,
            verse           INTEGER NOT NULL,
            text            TEXT NOT NULL,

            PRIMARY KEY (translation_id, book, chapter, verse),
            FOREIGN KEY (translation_id) REFERENCES translations(id),
            FOREIGN KEY (book) REFERENCES books(code)
        );

        CREATE INDEX IF NOT EXISTS idx_verses_lookup
            ON verses(translation_id, book, chapter, verse);
        CREATE INDEX IF NOT EXISTS idx_verses_chapter
            ON verses(translation_id, book, chapter);
        CREATE INDEX IF NOT EXISTS idx_verses_book
            ON verses(book, chapter);
    """)
    conn.commit()
    print("✓ Schéma créé")


def insert_books(conn: sqlite3.Connection):
    cur = conn.cursor()
    for order_num, (code, name_fr, testament) in enumerate(CATHOLIC_ORDER, start=1):
        cur.execute("""
            INSERT OR IGNORE INTO books (code, name_fr, testament, order_num)
            VALUES (?, ?, ?, ?)
        """, (code, name_fr, testament, order_num))
    conn.commit()
    print(f"✓ {len(CATHOLIC_ORDER)} livres insérés")


def main():
    if DB_PATH.exists():
        print(f"Le fichier {DB_PATH} existe déjà.")
        answer = input("Voulez-vous le supprimer et recommencer ? (o/N) : ").strip().lower()
        if answer != "o":
            print("Annulé.")
            return
        DB_PATH.unlink()

    print(f"Création de la base : {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    try:
        create_schema(conn)
        insert_books(conn)
        print(f"\nBase vide créée avec succès → {DB_PATH.resolve()}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()