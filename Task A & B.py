
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

