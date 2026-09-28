import sqlite3
from engine import RemenisEngine
from synthesizer import MemorySynthesizer

engine = RemenisEngine()
synthesizer = MemorySynthesizer(engine.conn)

print("--- PRE-SYNTHESIS AUDIT ---")
engine.audit_inspect()

print("--- RUNNING MEMORY SYNTHESIS ---")
synthesizer.consolidate_duplicates()

print("--- POST-SYNTHESIS AUDIT ---")
engine.audit_inspect()
