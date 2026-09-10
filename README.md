![Hellpod Steering Unlocked](assets/banner.png)

# Hellpod Steering Unlocked

Steer your hellpod toward rooftops, rocks and high ground without the game's base avoidance system pushing it away.

[Download Hellpod Steering Unlocked](https://github.com/CowboyBingus/HellpodSteeringUnlocked/releases/download/data-v4.1/HellpodSteeringUnlocked.zip), import the ZIP into **HDArsenal** or **HD2MM**, then enable and deploy it with the game closed. Use one manager for the installation. Remove any older manual installation before switching to a manager.

If an earlier HD2MM import reported empty options, remove that entry from its library and import the corrected ZIP again. Import, deployment and removal are verified with the HDArsenal 0.36.0 and HD2MM 1.3.0.1 backends in isolated folders.

The mod relaxes the base avoidance system. It does not guarantee unrestricted steering or a usable landing spot everywhere, and related hellpod placement checks also see the changed setting.

The current source revision is **data-v4.1**, for Steam build **24826606** / EXE **1.8.45317.0**. Unsupported game binaries are rejected. Combined operation with [Better Stratagem Bounce](https://github.com/CowboyBingus/BetterStratagemBounce) has been reported working; offline tests also cover both initialization orders. Neither mod requires the other.

Another mod replacing `core/wwise/lua/wwise_flow_callbacks` needs a combined startup resource. Arsenal can manage these archives, but installing conflicting resources does not merge their code.

## Source

- `src/`: runtime Lua modules.
- `tests/`: synthetic memory, callback and package checks.
- `scripts/`: dependency setup, build, packaging and optional Arsenal validation.
- `cmd/`: tools for extracting and inspecting game resources.
- `assets/`: README banner and Arsenal thumbnail.

[Build from source](CONTRIBUTING.md) · [Technical walkthrough](docs/TECHNICAL.md) · [Third-party dependencies](THIRD_PARTY.md)

**AI disclosure:** GPT-6 Astra was used for research, implementation, debugging, documentation and artwork.
