-- Run each initialization order in a fresh LuaJIT process: FFI declarations are
-- global and cannot be reset by constructing another Lua environment.
local hellpod_source, bounce_source, order = assert(arg[1]), assert(arg[2]), assert(arg[3])
assert(order == 'hellpod-first' or order == 'bounce-first')
local ffi = require('ffi')
local create_hellpod = assert(loadfile(hellpod_source .. '/windows_api.lua'))()
local create_bounce = assert(loadfile(bounce_source .. '/windows_api.lua'))()
local hellpod, bounce
if order == 'hellpod-first' then
    hellpod, bounce = create_hellpod(), create_bounce()
else
    bounce, hellpod = create_bounce(), create_hellpod()
end
local storage = ffi.new('uint8_t[2]')
local address = ffi.cast('uint8_t *', storage)
for index, api in ipairs({hellpod, bounce, create_hellpod(), create_bounce()}) do
    assert(api.writable_data(address, 2))
    assert(api.write(address + ((index - 1) % 2), string.char(index)))
    assert(not api.writable_data(api.module(nil), 1))
    assert(not api.write(api.module(nil), '\0'))
    assert(api.read(ffi.cast('uint8_t *', 1), 8) == nil)
end
assert(storage[0] == 3 and storage[1] == 4)
print('PASS: real Windows data APIs coexist in a fresh VM, ' .. order .. '; image writes still refused')
