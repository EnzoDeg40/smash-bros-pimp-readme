import os

import yaml

import images

if __name__ == "__main__":
    characters_raw = os.environ.get("CHARACTERS")

    if not characters_raw:
        raise ValueError("No CHARACTERS input provided")

    characters = yaml.safe_load(characters_raw)

    print("Characters received:")
    for name, character in characters.items():
        print(f"- {name} → {character}")

    assets_path = "../target-repo/.smash/assets"
    os.makedirs(assets_path, exist_ok=True)

    i = 1
    for name, character in characters.items():
        img = images.generate_image(name, character, variante=1, player=i)
        if img:
            img.save(os.path.join(assets_path, f"{name}.png"))
            print(f"✅ Generated image for {name}")
        else:
            print(f"❌ Failed to generate image for {name}")
        i += 1

    # Update README in target repo
    readme_path = "../target-repo/README.md"

    with open(readme_path, "r") as f:
        content = f.read()

    # Generate renders content
    renders_content = "\n".join(
        [f"- {name}: {character}" for name, character in characters.items()]
    )

    # Replace content between markers
    start_marker = "<!-- SMASH_TEAM_START -->"
    end_marker = "<!-- SMASH_TEAM_END -->"

    if start_marker in content and end_marker in content:
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]
        new_content = f"{before}{start_marker}\n{renders_content}\n{end_marker}{after}"

        with open(readme_path, "w") as f:
            f.write(new_content)

        print(f"\nREADME updated at {readme_path}")
    else:
        print(f"\nWarning: Could not find markers in README")
