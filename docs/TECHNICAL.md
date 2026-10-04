# How Hellpod Steering Unlocked works

The game's base hellpod avoidance system can steer a descending pod away from excluded areas instead of following the player's input. This mod disables that system's existing enable flag while leaving the rest of the manager data intact.

## Runtime scope

`src/steering_patch.lua` locates the manager through `game.dll` RVA `0x346D578` and its owner through `0x347CF18`. Their required relationship is an offset of `0x7C8C90`. The patch validates ownership, writable private memory, record/link limits, the internal self-pointer, set dimensions and map geometry relationships before changing the enable byte from `1` to `0`. Each check reads into buffers made once and decodes them in place, so it allocates nothing.

Uninitialized ship data is treated as waiting for a mission. Immediately before a write, the patch rechecks the manager, owner, original flag, set and dimensions to handle mission initialization races. A failed check stops modification; it does not broaden the accepted memory layout.

The patch writes the flag only over the game's own value. Mission initialization sets `1`, the only value the patch replaces (with `0`); a `0` needs nothing. Any other value in an otherwise valid manager was written by someone else: the patch leaves it alone, reports `avoidance_flag_set_by_another_writer` once and keeps checking, and clears the flag again once mission initialization sets `1`. Before, such a value counted as a layout mismatch and stopped the mod. Another mod that writes `1` cannot be told apart from the game's own reset by the flag alone, so that value is still cleared.

Only the base avoidance flag changes. Native instructions and the separate city-generation flag remain intact. Related hellpod placement checks that consume the base flag also see its disabled value. Other possible steering restrictions and unusable landing locations are outside this change.

## Startup and lifecycle

`scripts/module.py` compiles one named Lua resource containing Bingus Shared Runtime v1, this mod's Windows adapter, gameplay patch and lifecycle code. The runtime is three files kept byte-identical to the canonical copies: `src/bingus_runtime.lua` (the core: the update guard and the session table every copy shares), `src/bingus_memory.lua` (reads, page checks and module hashes) and `src/bingus_write.lua` (writes checked right before they land). The loader takes the core; the Windows adapter, `src/windows_api.lua`, takes the read side extended by the write side. The resource contains no Wwise or boot override. The separately installed Bingus Shared Loader owns Wwise initialization, preserving the original callbacks before requiring installed gameplay modules. See [startup compatibility](COMPATIBILITY.md).

`src/archive_loader.lua` verifies both supported game-module hashes and installs the update guard of `bingus_runtime.lua`, the family's update-chain policy, around `update` and `shutdown`. The hashes come from the runtime's `module_hash`, which reads each module's file at most once per session for every mod that asks (`BingusRuntime.hashes`). The earlier update runs outside pcall, so its errors reach the game unchanged, and every argument and return value passes through, including nil values. Because mission initialization resets the flag, the mod checks at 100 ms intervals, after the earlier update has returned, and reapplies the one-byte edit when needed. It logs state transitions.

- A validation failure stops the mod at once. Its own errors stop it after 8 in a burst; a count starts again after 3600 error-free frames.
- After an error in an update below it, the mod puts the game's value back over its own write and pauses. It restores only when the flag still holds its `0` in the same manager, owner, set and dimensions, with the layout still valid, rechecked right before the store. Once the updates below have returned on 60 frames in a row, it starts afresh and checks at once. Eight such errors in a burst stop it.
- When the mod stops, it puts the game's value back the same way. At shutdown it writes nothing: the game is freeing its memory.
- The guard's status is in `BingusRuntime.statuses.HellpodSteeringUnlocked`; the first failure survives shutdown.

The status file is `%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs/HellpodSteeringUnlocked.log`. `waiting_for_mission` is expected before initialized mission data; `avoidance_settings_ready` reports successful validation and the disabled flag; `avoidance_flag_set_by_another_writer` reports a flag value the mod leaves to another writer; `paused: ...` and `stopped: ...` come from the update guard, with `avoidance_restored` appended when the game's value was put back. A status message alone does not verify gameplay behavior.

## Tests and compatibility

The offline suite uses synthetic local allocations to check the exact one-byte edit, mission resets, pointer/layout failures, rejected memory permissions and callback behavior. The separate loader project compares original audio callbacks against the unmodified bytecode. ZIP checks verify resource identity, hashes, artwork, Arsenal metadata and relocation.

With `HD2_BOUNCE_SOURCE` set, the suite also exercises Better Stratagem Bounce's actual loader and both mods' Windows adapters in fresh LuaJIT processes for each initialization order. Bounce's adapter is called as its build calls it, whichever runtime its source vendors: the split runtime, the single-file runtime v1 or none. This mod takes its Windows functions only from the runtime, which declares them under private, versioned FFI names (`bingus_memory1_*`, `bingus_write1_*`), so another mod's declarations cannot change them. A standalone build needs no other mod's source.

The separate-loader packaging migration is verified offline; in-game testing remains pending. The inspected HUD+ boot retains its update chain in offline execution. An unrelated Wwise override still needs coordination, and manager support does not imply automatic code merging.

Game compatibility is restricted to the module hashes in `scripts/archive.py`, Steam build **25480438** / EXE **1.8.46015.0**. The original callback hash belongs to the separate loader; all manager layout guards are in `src/steering_patch.lua`. Revalidate those together for a new game build. Offline tests cannot establish every steering, multiplayer, mission-transition or landing outcome.

## Open follow-up

Another mod that writes `1` is still cleared, because the flag alone cannot tell it apart from the game's own mission reset. Telling them apart needs an in-game capture: the flag, the manager and owner pointers, the set and the dimensions across mission initialization, between missions and on the ship, to learn whether the game ever sets `1` without re-initializing the manager. Until then the rule above stays.
