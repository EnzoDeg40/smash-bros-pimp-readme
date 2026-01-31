Create `.github/workflows/smash.yml` with the following content:
```yml
name: Generate Smash Characters

on:
  push:
    branches:
      - main

jobs:
  call:
    permissions:
      contents: write
    uses: enzodeg40/smash-bros-pimp-readme/.github/workflows/characters.yml@main
    with:
      characters: |
        enzo:
          character: kirby
          github: enzodeg40
          variant: 2
        bob:
          character: zelda
          github: bobsmith
        alice:
          character: samus
          github: alicecoder
          variant: 3
```

**Configuration options:**
- `character`: The fighter name (required). Check list of [fighters](assets/fighters).
- `github`: GitHub username to link the image (optional).
- `variant`: Character variant number (optional, default: 1). Available variants depend on the character.

**Simple format** (backward compatible):
```yml
characters: |
  enzo: kirby
  bob: zelda
```

Add the following to `README.md`:
```md
<!-- SMASH_TEAM_START -->
<!-- SMASH_TEAM_END -->
```
