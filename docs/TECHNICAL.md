# How Hellpod Steering Unlocked works

The game's base hellpod avoidance system can steer a descending pod away from excluded areas instead of following the player's input. This mod disables that system's existing enable flag while leaving the rest of the manager data intact.

## Runtime scope

`src/steering_patch.lua` locates the manager through `game.dll` RVA `0x27706A8` and its owner through `0x277FF58`. Their required relationship is an offset of `0x7C5220`. The patch validates ownership, writable private memory, record/link limits, the internal self-pointer, set dimensions and map geometry relationships before changing the enable byte from `1` to `0`.

Uninitialized ship data is treated as waiting for a mission. Immediately before a write, the patch rechecks the manager, owner, original flag, set and dimensions to handle mission initialization races. A failed check stops modification; it does not broaden the accepted memory layout.

Only the base avoidance flag changes. Native instructions and the separate city-generation flag remain intact. Related hellpod placement checks that consume the base flag also see its disabled value. Other possible steering restrictions and unusable landing locations are outside this change.

## Startup and lifecycle

`scripts/module.py` compiles one named Lua resource containing this mod's Windows adapter, gameplay patch and lifecycle code. It contains no Wwise or boot override. The separately installed Bingus Shared Loader owns Wwise initialization, preserving the original callbacks before requiring installed gameplay modules. See [startup compatibility](COMPATIBILITY.md).

`src/archive_loader.lua` verifies both supported game-module hashes and installs one update wrapper. It preserves the earlier update function and all return values, including nil values. Because mission initialization resets the flag, it checks at 100 ms intervals and reapplies the one-byte edit when needed. It logs state transitions and stops its own checks on validation failure. It installs no shutdown callback.

The status file is `%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs/HellpodSteeringUnlocked.log`. `waiting_for_mission` is expected before initialized mission data; `avoidance_settings_ready` reports successful validation and the disabled flag. A status message alone does not verify gameplay behavior.

## Tests and compatibility

The offline suite uses synthetic local allocations to check the exact one-byte edit, mission resets, pointer/layout failures, rejected memory permissions and callback behavior. The separate loader project compares original audio callbacks against the unmodified bytecode. ZIP checks verify resource identity, hashes, artwork, Arsenal metadata and relocation.

With `HD2_BOUNCE_SOURCE` set, the suite also exercises Better Stratagem Bounce's actual loader and both mods' Windows adapters in fresh LuaJIT processes for each initialization order. The explicit pointer handling preserves compatibility with shared FFI declarations. A standalone build needs no other mod's source.

The separate-loader packaging migration is verified offline; in-game testing remains pending. The inspected HUD+ boot retains its update chain in offline execution. An unrelated Wwise override still needs coordination, and manager support does not imply automatic code merging.

Game compatibility is restricted to the module hashes in `scripts/archive.py`, Steam build **24826606** / EXE **1.8.45317.0**. The original callback hash belongs to the separate loader; all manager layout guards are in `src/steering_patch.lua`. Revalidate those together for a new game build. Offline tests cannot establish every steering, multiplayer, mission-transition or landing outcome.
