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




# A3. Compare nested Valuation keys
print("\nA3. Valuation key differences:")

valuation_patterns = Counter(
    tuple(sorted(record.get("Valuation", {}).keys()))
    for record in artwork_records
)

# Find the most common Valuation key structure
standard_valuation_keys = set(
    valuation_patterns.most_common(1)[0][0]
)

valuation_difference_count = 0

for index, record in enumerate(artwork_records, start=1):

    valuation = record.get("Valuation", {})
    valuation_keys = set(valuation.keys())

    missing = standard_valuation_keys-valuation_keys
    extra = valuation_keys-standard_valuation_keys

    if missing or extra:
        valuation_difference_count += 1

        print("\nRecord:", index)
        print("Asset Reference:", record.get("Asset Reference"))
        print("Missing Valuation fields:", missing)
        print("Extra Valuation fields:", extra)

print("\nRecords with different Valuation keys:",
      valuation_difference_count)




# A4. Find duplicate Asset References
print("\nA4. Duplicate Asset References:")

reference_counts = Counter(
    record.get("Asset Reference")
    for record in artwork_records
)

duplicates = {
    reference
    for reference, count in reference_counts.items()
    if count > 1
}

if duplicates:

    for reference in sorted(duplicates):

        print("\nAsset Reference:", reference)

        for record in artwork_records:

            if record.get("Asset Reference") == reference:

                value = record.get("Valuation", {}).get(
                    "Appraised Value (GBP)"
                )

                print("Appraised Value (GBP):", value)

else:
    print("No duplicate Asset References found.")




# A5. Blockers for writing to an immutable ledger
"""
Duplicate asset references and missing Appraiser ID's should be treated as
blocking issues since they raise concerns around asset identification.
Missing required fields and unexpected additional fields should also be
investigated before these records are added to an immutable ledger.
"""

print("\nA5. Blockers for writing to an immutable ledger.:")

valuation_patterns = Counter(
    tuple(sorted(record.get("Valuation", {}).keys()))
    for record in artwork_records
)

for keys, count in valuation_patterns.items():
    print("\nNumber of records:", count)
    print("Valuation fields:", keys)


# A6. Check missing or empty values
print("\nA6. Missing or empty top level values:")

missing_values = defaultdict(list)

for index, record in enumerate(artwork_records, start=1):
    for key in standard_keys:
        if key not in record or record[key] is None or record[key] == "":
            missing_values[key].append(index)

for key, record_numbers in missing_values.items():
    print(key, "is missing or empty in records:", record_numbers)


# A7. Check missing or empty Valuation values
print("\nA7. Missing or empty Valuation values:")

valuation_fields = set()

for record in artwork_records:
    valuation_fields.update(record.get("Valuation", {}).keys())

for field in sorted(valuation_fields):
    missing_records = []

    for index, record in enumerate(artwork_records, start=1):
        valuation = record.get("Valuation", {})

        if field not in valuation or valuation[field] is None or valuation[field] == "":
            missing_records.append(index)

    if missing_records:
        print(field, "is missing or empty in records:", missing_records)

print("\nEND OF TASK A")    



# TASK B: HASHING AND MERKLE ROOT


# Helper function: create a consistent SHA-256 hash
def calculate_hash(data):
    canonical_data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(canonical_data.encode("utf-8")).hexdigest()



# B1. HASH COMPARISON


print("\nTASK B1: HASH COMPARISON")

# The 9th record has index 8 in Python
record_9 = artwork_records[8]

# The 21st record has index 20 in Python
record_21 = artwork_records[20]

# Hash the 9th record twice
hashvalue1 = calculate_hash(record_9)
hashvalue2 = calculate_hash(record_9)

# Hash the 21st record
hashvalue3 = calculate_hash(record_21)

# Make a copy of the 9th record
record_9_changed = copy.deepcopy(record_9)

# Increase its appraised value by one penny
old_value = record_9_changed["Valuation"]["Appraised Value (GBP)"]
record_9_changed["Valuation"]["Appraised Value (GBP)"] = round(old_value + 0.01, 2)

# Hash the changed record
hashvalue4 = calculate_hash(record_9_changed)


# Function to compare two hash values
def compare_hashes(hash_a, hash_b):
    if hash_a == hash_b:
        print("The hashes are IDENTICAL.")
    else:
        print("The hashes are NOT IDENTICAL.")


print("\nComparison 1: hashvalue1 and hashvalue2")
compare_hashes(hashvalue1, hashvalue2)

print("\nComparison 2: hashvalue1 and hashvalue3")
compare_hashes(hashvalue1, hashvalue3)

print("\nComparison 3: hashvalue1 and hashvalue4")
compare_hashes(hashvalue1, hashvalue4)

print("\nOriginal appraised value:", old_value)
print("Changed appraised value:",
      record_9_changed["Valuation"]["Appraised Value (GBP)"])

print(
    "\nSHA-256 is highly sensitive: changing the value by only "
    "one penny produces a different hash."
)

# B2. MERKLE ROOT FUNCTION


print("\nTASK B2: MERKLE ROOT")


def merkle_root(transactions):

    # Case 1: Empty list
    if len(transactions) == 0:
        return hashlib.sha256(b"").hexdigest()

    # Create the first level of hashes (leaf nodes)
    level = []

    for transaction in transactions:
        transaction_string = json.dumps(
            transaction, sort_keys=True
        )
        transaction_hash = hashlib.sha256(
            transaction_string.encode("utf-8")
        ).hexdigest()

        level.append(transaction_hash)

    # Case 2: A single transaction
    if len(level) == 1:
        return level[0]

    # Build the tree until only one hash remains
    while len(level) > 1:

        next_level = []

        # Process hashes in pairs
        for i in range(0, len(level), 2):

            left = level[i]

            # If there is no right node, duplicate the last node
            if i + 1 < len(level):
                right = level[i + 1]
            else:
                right = left

            combined = left + right

            combined_hash = hashlib.sha256(
                combined.encode("utf-8")
            ).hexdigest()

            next_level.append(combined_hash)

        level = next_level

    return level[0]


# Test empty list
print("Empty list root:", merkle_root([]))

# Test one transaction
print("Single item root:", merkle_root([artwork_records[0]]))



# B3. MERKLE ROOT SENSITIVITY TEST


print("\nTASK B3: MERKLE SENSITIVITY TEST")

# Calculate the root of the first 9 artwork records
first_nine = copy.deepcopy(artwork_records[:9])

original_root = merkle_root(first_nine)

# Change one character in the first artwork title
changed_nine = copy.deepcopy(first_nine)

original_title = changed_nine[0]["Artwork Title"]
changed_nine[0]["Artwork Title"] = original_title + "X"

# Calculate the new Merkle root
changed_root = merkle_root(changed_nine)

print("\nOriginal Merkle root:")
print(original_root)

print("\nChanged Merkle root:")
print(changed_root)

# Check whether the root changed
if original_root != changed_root:
    print("\nRESULT: The Merkle root CHANGED.")
else:
    print("\nRESULT: The Merkle root DID NOT CHANGE.")
# Test Merkle Root with an odd number of items
odd_items = [
    "record1",
    "record2",
    "record3"
]

odd_root = merkle_root(odd_items)

print("\nOdd number of items root:", odd_root)
print("\nEND OF TASK B")



# Load data
with open("art_asset_register.json") as f:
    register = json.load(f)

with open("custody_access_requests.json") as f:
    requests_log = json.load(f)




# TASK C: ACCESS-CONTROL POLICY ENGINE

print("\nTASK C: ACCESS-CONTROL POLICY ENGINE")

# Policy tables from Section 2.7 of the brief
EVENT_CLEARANCE = {
    "Condition Inspection": 1,
    "Public Exhibition Loan": 2,
    "Valuation Update": 2,
    "Vault Transfer": 3,
    "Fractional Share Issue": 3,
    "Record Export": 3,
    "Collateral Pledge": 4,
    "Loan Drawdown": 4,
}

THIRD_PARTY_CHANNEL = "Third-Party API"
THIRD_PARTY_MIN_CLEARANCE = 3


# C1. LOOKUP STRUCTURE
print("\nC1. Building the asset lookup:")


def asset_clearance(record):
    """Minimum Clearance Level of an asset (0 if the field is missing)."""
    return record.get("Access Control", {}).get("Minimum Clearance Level", 0)


def build_lookup(records):
    """Map each Asset Reference to ONE register record.

    The register contains duplicate references (Task A4). For a duplicate we
    keep the copy with the HIGHEST Minimum Clearance Level, so the policy
    fails safe: an ambiguous asset is never treated as less restricted than
    any of its copies. If the clearances tie, the first copy is kept.
    """
    lookup = {}
    for record in records:
        reference = record.get("Asset Reference")

        if reference not in lookup:
            lookup[reference] = record
        elif asset_clearance(record) > asset_clearance(lookup[reference]):
            lookup[reference] = record

    return lookup


asset_lookup = build_lookup(artwork_records)

"""
Why a dictionary lookup is better than a nested loop:
A dictionary is a hash table, so finding a key takes roughly constant time
(O(1)) however large the register is. A nested loop would compare every
request with every artwork, which is 900 x 503 = 452,700 comparisons in the
worst case (O(n x m)), and it gets slower as either file grows. With the
dictionary we do 900 lookups in total, one per request.
"""

print("Register records:", len(artwork_records))
print("Unique Asset References in lookup:", len(asset_lookup))
print("Duplicate records collapsed (highest clearance kept):",
      len(artwork_records) - len(asset_lookup))


# C2. EVALUATE ONE REQUEST
def evaluate_request(request, lookup):
    """Apply the three Meridian rules in order and return (decision, reason).

    A request that breaks several rules is reported under the first one.
    """
    clearance = request.get("Clearance Level", 0)

    # Rule 1: the asset must exist in the register
    asset = lookup.get(request.get("Asset Reference"))
    if asset is None:
        return "DENIED", "Unknown Asset"

    # Rule 2: clearance must meet the larger of the event and asset levels
    event_level = EVENT_CLEARANCE.get(request.get("Event Type"), 0)
    required = max(event_level, asset_clearance(asset))
    if clearance < required:
        return "DENIED", "Insufficient Clearance"

    # Rule 3: Third-Party API requests need a clearance of at least 3
    if (request.get("Access Channel") == THIRD_PARTY_CHANNEL
            and clearance < THIRD_PARTY_MIN_CLEARANCE):
        return "DENIED", "Channel Not Permitted"

    return "APPROVED", "Policy Satisfied"


# C3. APPLY THE POLICY TO ALL REQUESTS
print("\nC3. Policy results for all requests:")

outcome_counts = Counter()          # (decision, reason) -> count
denials_by_role = Counter()         # Staff Role -> denied requests
requests_by_event = Counter()       # Event Type -> all requests
denials_by_event = Counter()        # Event Type -> denied requests

# C4. Approved requests, kept in their original order (input to Task D)
approved_events = []

for request in access_requests:
    decision, reason = evaluate_request(request, asset_lookup)

    outcome_counts[(decision, reason)] += 1
    requests_by_event[request["Event Type"]] += 1

    if decision == "APPROVED":
        approved_events.append(request)
    else:
        denials_by_role[request["Staff Role"]] += 1
        denials_by_event[request["Event Type"]] += 1

# Count for each decision and reason
for (decision, reason), count in sorted(outcome_counts.items()):
    print(decision, "-", reason, ":", count)

total_requests = len(access_requests)
total_approved = len(approved_events)
total_denied = total_requests - total_approved

print("\nTotal requests:", total_requests)
print("Approved:", total_approved)
print("Denied:", total_denied)

# Approval rate to one decimal place
approval_rate = total_approved / total_requests * 100
print("Approval rate: {:.1f}%".format(approval_rate))

# Denials by Staff Role, most to fewest
print("\nDenials by Staff Role (most to fewest):")
for role, count in denials_by_role.most_common():
    print(role, ":", count)

# Event Type with the highest denial rate (denied / all requests of that type)
denial_rates = {
    event: denials_by_event[event] / total * 100
    for event, total in requests_by_event.items()
}
worst_event = max(denial_rates, key=denial_rates.get)

print("\nEvent Type with the highest denial rate:")
print("{} - {:.1f}% ({} of {} requests denied)".format(
    worst_event,
    denial_rates[worst_event],
    denials_by_event[worst_event],
    requests_by_event[worst_event]))


# C4. APPROVED EVENTS
print("\nC4. approved_events list for Task D:")
print("Number of approved events:", len(approved_events))
print("Final batch size at 3 per block:", len(approved_events) % 3 or 3)

print("\nEND OF TASK C")
