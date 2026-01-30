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
        enzo: kirby
        bob: zelda
        alice: samus
```

Add the following to `README.md`:
```md
<!-- SMASH_TEAM_START -->
<!-- SMASH_TEAM_END -->
```
