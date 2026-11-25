
import json
from collections import Counter, defaultdict 
import hashlib
import datetime
import copy


#Load the artwork register
with open("art_asset_register.json", "r", encoding="utf-8") as file:
    artwork_records = json.load(file)

#Load the custody access requests
with open("custody_access_requests.json", "r", encoding="utf-8") as file:
    access_requests = json.load(file)

print("Artwork records:", len(artwork_records))
print("Access requests:", len(access_requests))


def canon(obj):
    """Canonical string form of a dict/list: sorted keys, so the hash is stable."""
    return json.dumps(obj, sort_keys=True)

def sha(text):
    """SHA-256 of a string as 64 hex characters."""
    return hashlib.sha256(text.encode()).hexdigest()

def merkle_root(transactions):
    """Merkle root of a list of items (Section 2.5)."""
    if len(transactions) == 0:
        return sha("")                          # empty list -> hash of empty string
    if len(transactions) == 1:
        return sha(canon(transactions[0]))      # single item -> hash of that item
    level = [sha(canon(t)) for t in transactions]   # leaves
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])             # duplicate last node when odd
        level = [sha(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]

# TASK A: REGISTER INTEGRITY PROFILE

print("\nTASK A: REGISTER INTEGRITY PROFILE")

# A1. Total number of artwork records
print("\nA1. Total artwork records:")
print(len(artwork_records))



# A2. Compare the top-level keys in all records
print("\nA2. Top-level key differences:")

key_patterns = Counter(
    tuple(sorted(record.keys()))
    for record in artwork_records
)

# Find the most common set of keys
standard_keys = set(key_patterns.most_common(1)[0][0])


missing_count = 0
extra_count = 0

for index, record in enumerate(artwork_records, start=1):

    record_keys = set(record.keys())

    missing = standard_keys-record_keys
    extra = record_keys-standard_keys

    if missing:
        missing_count += 1
        print("\nRecord:", index)
        print("Asset Reference:", record.get("Asset Reference"))
        print("Missing fields:", missing)

    if extra:
        extra_count += 1
        print("\nRecord:", index)
        print("Asset Reference:", record.get("Asset Reference"))
        print("Extra fields:", extra)

print("\nRecords with missing fields:", missing_count)
print("Records with extra fields:", extra_count)