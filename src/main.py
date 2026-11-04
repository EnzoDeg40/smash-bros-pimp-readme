import os

import yaml

import coauthors
import images

if __name__ == "__main__":
    characters_raw = os.environ.get("CHARACTERS")

    if not characters_raw:
        raise ValueError("No CHARACTERS input provided")

    characters = yaml.safe_load(characters_raw)

    print("Characters received:")
    for name, config in characters.items():
        # Support both old format (string) and new format (dict)
        if isinstance(config, str):
            character = config
            github = None
            variant = 1
        else:
            character = config.get("character")
            github = config.get("github")
            variant = config.get("variant", 1)
        print(f"- {name} → {character} (variant: {variant}, github: {github or 'N/A'})")

    assets_path = "../target-repo/.smash/assets"
    os.makedirs(assets_path, exist_ok=True)

    i = 1
    for name, config in characters.items():
        # Support both old format (string) and new format (dict)
        if isinstance(config, str):
            character = config
            variant = 1
            controller = None
        else:
            character = config.get("character")
            variant = config.get("variant", 1)
            controller = config.get("controller")

        img = images.generate_image(
            name, character, variante=variant, player=i, controller=controller
        )
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

    # Generate renders content with GitHub links
    renders_lines = []
    github_logins = []
    for name, config in characters.items():
        if isinstance(config, str):
            github = None
        else:
            github = config.get("github")
        
        if github:
            github_logins.append(str(github))
            renders_lines.append(f"[![{name}](.smash/assets/{name}.png)](https://github.com/{github})")
        else:
            renders_lines.append(f"![](.smash/assets/{name}.png)")
    
    # No separator: a newline would render as a space between the images
    renders_content = "".join(renders_lines)

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

    # Kept outside target-repo so it doesn't end up in the commit
    with open("../commit-message.txt", "w") as f:
        f.write(coauthors.build_commit_message(github_logins))
