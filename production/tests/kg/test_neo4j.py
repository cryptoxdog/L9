# tests/kg/test_neo4j.py

from memory.shared.supabase_client import get_supabase
from l.l_memory.kg_client import KGClient

def test_neo_connection():
    kg = KGClient()
    kg.init()
    assert kg.connected is True

