import os

print("Searching for fifa2026_predictions.db...")
for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".db"):
            print("Found database at:", os.path.join(root, f))
