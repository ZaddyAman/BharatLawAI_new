#!/usr/bin/env python3
"""
Database migration script to add performance indexes to the judgments table.
Run this script to improve search performance without losing existing data.
"""

import sqlite3
import os
from pathlib import Path

def add_performance_indexes():
    """Add indexes for better search and query performance"""

    # Find the database file
    db_paths = [
        Path("../sql_app.db"),  # Database is in parent directory
        Path("sql_app.db"),
        Path("langchain_rag_engine/sql_app.db"),
        Path("app.db"),
        Path("database.db")
    ]

    db_path = None
    for path in db_paths:
        if path.exists():
            db_path = path
            break

    if not db_path:
        print("ERROR: No database file found!")
        print("Looking for database in:", [str(p) for p in db_paths])
        return

    print(f"Found database: {db_path}")

    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check existing indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='judgments'")
        existing_indexes = [row[0] for row in cursor.fetchall()]
        print(f"Existing indexes on judgments table: {existing_indexes}")

        # Add performance indexes if they don't exist
        indexes_to_create = [
            ("idx_judgments_case_title", "CREATE INDEX idx_judgments_case_title ON judgments(case_title)"),
            ("idx_judgments_year", "CREATE INDEX idx_judgments_year ON judgments(year)"),
            ("idx_judgments_judgment_date", "CREATE INDEX idx_judgments_judgment_date ON judgments(judgment_date)"),
            ("idx_judgments_citation", "CREATE INDEX idx_judgments_citation ON judgments(citation)")
        ]

        created_indexes = []
        for index_name, create_sql in indexes_to_create:
            if index_name not in existing_indexes:
                try:
                    cursor.execute(create_sql)
                    created_indexes.append(index_name)
                    print(f"[SUCCESS] Created index: {index_name}")
                except Exception as e:
                    print(f"[ERROR] Failed to create index {index_name}: {e}")
            else:
                print(f"[INFO] Index already exists: {index_name}")

        # Verify indexes were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='judgments'")
        final_indexes = [row[0] for row in cursor.fetchall()]
        print(f"\nFinal indexes on judgments table: {final_indexes}")

        conn.commit()

        if created_indexes:
            print(f"\n[SUCCESS] Created {len(created_indexes)} new indexes:")
            for idx in created_indexes:
                print(f"   - {idx}")
            print("\n[PERFORMANCE] Search performance should now be significantly improved!")
        else:
            print("\n[INFO] All performance indexes already exist.")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("[START] Starting database performance optimization...")
    add_performance_indexes()
    print("[COMPLETE] Database optimization complete!")