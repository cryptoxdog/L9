# tests/memory/test_l1_memory.py

from l.memory.l1.l1_writer import writer
from l.memory.l1.l1_reader import reader
from l.memory.l1.l1_query import query
from memory.shared.supabase_client import get_supabase

def test_l1_connection():
    sb = get_supabase()
    res = sb.table("l_directives").select("id").limit(1).execute()
    assert res is not None

def test_l1_writer_basic():
    payload = {
        "directive": {"cmd": "test"},
        "source": "unit_test",
        "priority": 1
    }
    res = writer.write("l_directives", payload)
    assert res.data is not None

def test_l1_reader():
    rows = reader.read("l_directives")
    assert isinstance(rows.data, list)

def test_l1_query_recent():
    rows = query.get_recent("l_directives", 10)
    assert isinstance(rows.data, list)

