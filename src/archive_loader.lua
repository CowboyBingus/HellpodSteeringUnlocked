return function(create_api, patch, build)
    if _G.HellpodSteeringUnlocked then return end
    local state = {revision = build.revision, active = false, status = ''}
    _G.HellpodSteeringUnlocked = state
    local function report(status, active)
        state.active = active
        if state.status == status then return end
        state.status = status
        print('[HellpodSteeringUnlocked] ' .. build.revision .. ': ' .. status)
        pcall(function()
            local directory = os.getenv('LOCALAPPDATA')
            if not directory then return end
            local file = io.open(directory .. '/HellpodSteeringUnlocked.log', 'w')
            if file then file:write(build.revision .. '\n' .. status .. '\n'); file:close() end
        end)
    end
    local ok, api, game = pcall(function()
        local api = create_api()
        local exe, game = api.module(nil), api.module('game.dll')
        assert(exe and game, 'Required game modules unavailable')
        assert(api.module_hash(exe) == build.exe_sha256, 'Unsupported executable; no change applied')
        assert(api.module_hash(game) == build.game_sha256, 'Unsupported game module; no change applied')
        assert(type(update) == 'function', 'Game update unavailable; no change applied')
        return api, game
    end)
    if not ok then report(tostring(api), false); return end
    report('waiting_for_mission', false)
    local previous = update
    local stopped, elapsed = false, 0.1
    local function check(dt)
        if stopped then return end
        elapsed = elapsed + ((type(dt) == 'number' and dt == dt and dt > 0) and dt or 0)
        if elapsed < 0.1 then return end
        elapsed = 0
        local called, accepted, reason, active = pcall(patch.apply, api, game)
        if not called then reason, accepted, active = tostring(accepted), false, false end
        if not accepted then stopped = true end
        report(tostring(reason), active == true)
    end
    local function forward(dt, ...)
        check(dt)
        return ...
    end
    update = function(dt, ...)
        return forward(dt, previous(dt, ...))
    end
end
