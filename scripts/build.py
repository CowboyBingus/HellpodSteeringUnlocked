"""Build and verify Hellpod Steering Unlocked without launching the game."""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

from archive import BOOT, BOOT_SHA, LUA, sha, EXE_SHA, GAME_DLL_SHA, GAME, ARCHIVE, make_archive
from package import package_release

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src'
TESTS = ROOT / 'tests'
REVISION = 'data-v4.1'
BUILD = ROOT / 'build'
CALLBACK = Path(os.environ.get('HD2_CALLBACK_RESOURCE', ROOT / 'artifacts/vanilla/wwise_flow_callbacks.lua.main'))
INSPECTOR = Path(os.environ.get('HD2_PATCH_INSPECT', ROOT / 'tools/bin/hd2-patch-inspect.exe'))
CALLBACK_SHA = '05BBF52978028758B39F5B91A30A695D20069CEABD774D88755F0582A296BEC9'
CALLBACK_NAME = 0x7251FDD9BB62480A


def run(args, **kwargs):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def literal(data):
    return '"' + ''.join(f'\\{byte:03d}' for byte in data) + '"'


def main():
    for relative, expected in [('bin/helldivers2.exe', EXE_SHA), ('data/game/game.dll', GAME_DLL_SHA)]:
        if sha((GAME / relative).read_bytes()) != expected:
            raise ValueError('Unsupported game build: ' + relative)
    boot, vanilla = BOOT.read_bytes(), CALLBACK.read_bytes()
    if sha(boot) != BOOT_SHA or struct.unpack('<II', boot[:8]) != (326, 2):
        raise ValueError('Vanilla boot resource changed')
    if sha(vanilla) != CALLBACK_SHA or struct.unpack('<II', vanilla[:8]) != (10263, 2):
        raise ValueError('Vanilla audio callback resource changed')
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / 'vanilla-boot.ljbc').write_bytes(boot[8:])
    (BUILD / 'vanilla-callbacks.ljbc').write_bytes(vanilla[8:])
    wrapper = f"assert(loadstring({literal(vanilla[8:])}, '@vanilla_wwise_callbacks'))()\n"
    for variable, name in [('create_api', 'windows_api.lua'), ('patch', 'steering_patch.lua'),
                           ('install_loader', 'archive_loader.lua')]:
        code = (SOURCE / name).read_text()
        for forbidden in ('VirtualProtect', 'FlushInstructionCache', 'CreateRemoteThread', 'LoadLibrary'):
            if forbidden in code:
                raise ValueError(f'Forbidden code-modification API in {name}: {forbidden}')
        wrapper += f'local {variable} = (function()\n' + code + '\nend)()\n'
    wrapper += "install_loader(create_api, patch, {revision = '" + REVISION + "', "
    wrapper += f"exe_sha256 = '{EXE_SHA}', game_sha256 = '{GAME_DLL_SHA}'" + '})\n'
    (BUILD / 'callbacks.wrapper.lua').write_text(wrapper)
    env = dict(os.environ, LUA_PATH=str(LUA.parent / '?.lua') + ';;')
    run([LUA, '-bsdW', BUILD / 'callbacks.wrapper.lua', BUILD / 'callbacks.ljbc'], env=env)
    bytecode = (BUILD / 'callbacks.ljbc').read_bytes()
    if bytecode[:5] != vanilla[8:13]:
        raise ValueError('LuaJIT bytecode mode differs')
    peer = os.environ.get('HD2_BOUNCE_SOURCE')
    peer_source = Path(peer).resolve() / 'src' if peer else None
    arguments = [LUA, TESTS / 'test_data.lua', SOURCE, BUILD, sha(LUA.read_bytes())]
    if peer_source is not None:
        if not (peer_source / 'windows_api.lua').is_file():
            raise ValueError('HD2_BOUNCE_SOURCE must point to the Bounce source repository')
        arguments.append(peer_source)
    tests = run(arguments, env=env)
    if peer_source is not None:
        for order in ('hellpod-first', 'bounce-first'):
            tests += run([LUA, TESTS / 'test_api_coexistence.lua', SOURCE, peer_source, order], env=env)
    (BUILD / 'offline-tests.txt').write_text(tests)
    data = BUILD / 'data'
    data.mkdir(exist_ok=True)
    (data / ARCHIVE).write_bytes(make_archive(struct.pack('<II', len(bytecode), 2) + bytecode, CALLBACK_NAME))
    for suffix in ('.stream', '.gpu_resources'):
        (data / (ARCHIVE + suffix)).write_bytes(b'')
    run([INSPECTOR, '--patch', data / ARCHIVE,
         '--out', BUILD / 'archive-inspection.json', '--extract-dir', BUILD / 'archive-resources'])
    inspection = json.loads((BUILD / 'archive-inspection.json').read_text())
    resources = inspection['resources']
    if (inspection['num_files'] != 1 or len(resources) != 1 or
            resources[0]['name']['hex'] != '0x7251fdd9bb62480a' or
            resources[0]['type']['hex'] != '0xa14e8dfa2cd117e2'):
        raise ValueError('Only the separate Wwise callback resource may be overridden')
    files = {f'data/{ARCHIVE}{suffix}': f'build/data/{ARCHIVE}{suffix}'
             for suffix in ('', '.stream', '.gpu_resources')}
    report = {
        'name': 'Hellpod Steering Unlocked', 'slug': 'HellpodSteeringUnlocked',
        'guid': 'e38527e8-6c29-4a73-8a13-cd752d66e287', 'revision': REVISION,
        'description': 'Steer your hellpod toward rooftops, rocks and high ground without being pushed away.',
        'game_exe_sha256': EXE_SHA, 'game_dll_sha256': GAME_DLL_SHA,
        'deployment_files': files, 'files': {path: sha((ROOT / path).read_bytes()) for path in files.values()},
        'vanilla_callback_sha256': CALLBACK_SHA, 'vanilla_callbacks_embedded_unchanged': True,
        'lua_resource': 'core/wwise/lua/wwise_flow_callbacks', 'lua_resource_hash': hex(CALLBACK_NAME),
        'data_change': {'manager_pointer_rva': '0x27706A8', 'owner_pointer_rva': '0x277FF58',
                        'owner_offset': '0x7C5220', 'offset': 0, 'before': '01', 'after': '00',
                        'mission_reset_check_seconds': 0.1, 'city_flag_changed': False},
        'continuous_update_hook': True, 'shutdown_hook': False, 'executable_code_writes': 0,
        'offline_tests': tests.strip().splitlines(), 'windows_adapter_interop': peer_source is not None,
    }
    sources = list(SOURCE.glob('*.lua')) + list(TESTS.glob('*.lua')) + list((ROOT / 'scripts').glob('*.py'))
    report['source_sha256'] = {path.relative_to(ROOT).as_posix(): sha(path.read_bytes()) for path in sources}
    release = package_release(ROOT, BUILD, report)
    package_tests = run([sys.executable, TESTS / 'test_package.py', release])
    (BUILD / 'package-tests.txt').write_text(package_tests, encoding='utf-8')
    report['package_tests'] = package_tests.strip().splitlines()
    arsenal_source = os.environ.get('HD2_ARSENAL_SOURCE')
    if arsenal_source:
        print(run(['node', ROOT / 'scripts/test_arsenal_archive.cjs', release, arsenal_source, BUILD]).strip())
        report['arsenal_tests'] = json.loads((BUILD / 'arsenal-compatibility.json').read_text())
    report['release'] = {'path': release.relative_to(ROOT).as_posix(), 'sha256': sha(release.read_bytes())}
    (BUILD / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(tests.strip())
    print(package_tests.strip())
    print('Built ' + release.name + '; no installation or game launch performed.')


if __name__ == '__main__':
    main()
