import os
import yaml

characters_raw = os.environ.get("CHARACTERS")

if not characters_raw:
    raise ValueError("No CHARACTERS input provided")

characters = yaml.safe_load(characters_raw)

print("Characters received:")
for name, character in characters.items():
    print(f"- {name} → {character}")
