import sqlite3
import re

class MemorySynthesizer:
    # Map equivalent category aliases to a canonical category name
    CATEGORY_MAPPINGS = {
        "preference": "user_preference",
        "prefs": "user_preference",
        "project": "project_context",
        "context": "project_context"
    }

    def __init__(self, db_conn):
        self.conn = db_conn

    def normalize_category(self, category: str) -> str:
        cat_clean = category.strip().lower()
        return self.CATEGORY_MAPPINGS.get(cat_clean, cat_clean)

    def normalize_text(self, text: str) -> str:
        # Remove punctuation and normalize spaces for text comparison
        return re.sub(r'[^\w\s]', '', text).strip().lower()

    def consolidate_duplicates(self):
        """
        Scans database across normalized categories and facts, unifies equivalent 
        categories, and prunes older duplicate entries.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, fact_text, category, importance, created_at 
            FROM memories 
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()

        seen_facts = {}
        ids_to_remove = []

        for row in rows:
            mem_id, fact_text, category, importance, created_at = row
            
            norm_cat = self.normalize_category(category)
            norm_fact = self.normalize_text(fact_text)
            
            # Check normalized (fact, category) key
            fact_key = (norm_fact, norm_cat)

            if fact_key in seen_facts:
                existing_id, existing_imp = seen_facts[fact_key]
                if importance > existing_imp:
                    ids_to_remove.append(existing_id)
                    seen_facts[fact_key] = (mem_id, importance)
                else:
                    ids_to_remove.append(mem_id)
            else:
                seen_facts[fact_key] = (mem_id, importance)

            # Update record in DB if category needed normalization
            if norm_cat != category:
                cursor.execute("UPDATE memories SET category = ? WHERE id = ?", (norm_cat, mem_id))

        if ids_to_remove:
            placeholders = ",".join("?" for _ in ids_to_remove)
            cursor.execute(f"DELETE FROM memories WHERE id IN ({placeholders})", ids_to_remove)
            self.conn.commit()
            print(f"🧹 [SYNTHESIS COMPLETE] Unified category variants & pruned {len(ids_to_remove)} duplicate node(s).")
        else:
            self.conn.commit()
            print("✨ [SYNTHESIS] No cross-category duplicate memories detected.")

if __name__ == "__main__":
    print("Updated MemorySynthesizer ready.")
