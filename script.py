import os
import yaml

characters_raw = os.environ.get("CHARACTERS")

if not characters_raw:
    raise ValueError("No CHARACTERS input provided")

characters = yaml.safe_load(characters_raw)

print("Characters received:")
for name, character in characters.items():
    print(f"- {name} → {character}")

# Update README in target repo
readme_path = "../target-repo/README.md"

with open(readme_path, "r") as f:
    content = f.read()

# Generate renders content
renders_content = "\n".join([f"- {name}: {character}" for name, character in characters.items()])

# Replace content between markers
start_marker = "<!-- RENDERS_START -->"
end_marker = "<!-- RENDERS_END -->"

if start_marker in content and end_marker in content:
    before = content.split(start_marker)[0]
    after = content.split(end_marker)[1]
    new_content = f"{before}{start_marker}\n{renders_content}\n{end_marker}{after}"
    
    with open(readme_path, "w") as f:
        f.write(new_content)
    
    print(f"\nREADME updated at {readme_path}")
else:
    print(f"\nWarning: Could not find markers in README")
