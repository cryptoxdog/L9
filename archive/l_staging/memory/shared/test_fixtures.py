# l/memory/shared/test_fixtures.py

class FakeSupabaseTable:
    def __init__(self):
        self.rows = []

    def insert(self, payload):
        self.rows.append(payload)
        return {"success": True, "data": payload}

class FakeSupabaseClient:
    def __init__(self):
        self.tables = {}

    def table(self, name):
        if name not in self.tables:
            self.tables[name] = FakeSupabaseTable()
        return self.tables[name]

fake_supabase = FakeSupabaseClient()

