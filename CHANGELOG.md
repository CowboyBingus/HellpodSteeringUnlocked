# v7.4

- Checks memory protection only when a write will follow; previously every 10 Hz poll repeated the query after the settings were already applied, and in game that query costs about 0.3 ms.
- Reuses one read buffer instead of allocating per read.
- Measured in real play: about 0.039 ms to 0.003 ms of main-thread time per frame in missions. Behavior is unchanged.

# v7.3

- Refresh the game-build checks for Steam build 25480438.
- Preserve the high-ground steering adjustment.
- Offline builds and package checks pass; live gameplay validation remains pending.

# v7.2

- Update compatibility for game build 25327279.
- Restore the hellpod steering settings for the updated game.

# v7.1

- Moves logs to `%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs`.
- Requires Bingus Shared Loader v14 for the shared log folder.
