![Hellpod Steering Unlocked](assets/banner.png)

# Hellpod Steering Unlocked

Steer your hellpod toward rooftops, rocks and high ground without the game's base avoidance system pushing it away.

[Download Hellpod Steering Unlocked](https://github.com/CowboyBingus/HellpodSteeringUnlocked/releases/download/data-v5/HellpodSteeringUnlocked.zip), import the ZIP into **HDArsenal** or **HD2MM**, then enable and deploy it with the game closed. Use one manager for the installation. Remove any older manual installation before switching to a manager.

This prerelease introduces the shared Wwise loader. Native startup and offline HUD+ startup checks pass; gameplay validation remains pending. Import, deployment and removal pass HDArsenal 0.36.0 and HD2MM 1.3.0.1 backend checks in isolated folders.

The mod relaxes the base avoidance system. It does not guarantee unrestricted steering or a usable landing spot everywhere, and related hellpod placement checks also see the changed setting.

The current prerelease is **data-v5**, for Steam build **24826606** / EXE **1.8.45317.0**. Unsupported game binaries are rejected. This mod and [Better Stratagem Bounce](https://github.com/CowboyBingus/BetterStratagemBounce) now use an identical Wwise coordinator with separate modules. Each works independently; when using both, update both packages together.

Neither package replaces `boot`, avoiding the known HD2 HUD+ 0.1.3 startup conflict. Offline checks preserve its update chain. Other Wwise replacements still need coordination; see [compatibility](docs/COMPATIBILITY.md).

## Source

- `src/`: runtime Lua modules.
- `tests/`: synthetic memory, callback and package checks.
- `scripts/`: dependency setup, build, packaging and optional Arsenal validation.
- `cmd/`: tools for extracting and inspecting game resources.
- `assets/`: README banner and Arsenal thumbnail.

[Build from source](CONTRIBUTING.md) · [Technical walkthrough](docs/TECHNICAL.md) · [Third-party dependencies](THIRD_PARTY.md)

**AI disclosure:** GPT-6 Astra was used for research, implementation, debugging, documentation and artwork.
