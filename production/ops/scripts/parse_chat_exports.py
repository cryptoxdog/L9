#!/usr/bin/env python3
# Version: 1.0.0
Canonical-Source: 10X Governance Suite
Generated: 2025-10-06T17:10:32Z

Parse chat export data into structured memory index
import os, json, hashlib, datetime
BASE = os.path.join(os.getcwd(), "ops/logs/chat_exports")
INDEX = os.path.join(os.getcwd(), "ops/logs/memory_index.json")
entries = []

for root, _, files in os.walk(BASE):
    for f in files:
        path = os.path.join(root, f)
        entries.append({"file": path, "hash": hashlib.sha256(open(path, 'rb').read()).hexdigest()})

with open(INDEX, "w") as out:
    json.dump({"updated": datetime.datetime.utcnow().isoformat() + "Z", "entries": entries}, out, indent=2)
print(f"Parsed {len(entries)} files into memory index.")
