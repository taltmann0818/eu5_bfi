"""Stage an unanswered production bank event in an isolated Florence UI scene."""
import argparse
import hashlib
import json
from pathlib import Path
import prepare_m5_ui
from campaign_suite import ROOT, write_script, runtime_hash


def prepare(directory, event='bfl_bank_flo.4'):
    directory=Path(directory).resolve()
    prior=prepare_m5_ui.prepare(directory)
    overlay=directory/'mod/bfi_campaign_checks'
    # Keep all shipping event files intact. Only this disposable setup bypasses dates.
    write_script(overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt','''
        on_game_started_after_lobby = { on_actions = { bfi_bank_event_ui_start } }
        bfi_bank_event_ui_start = { effect = { c:FLO = {
            bfi_m5_ui_setup = yes set_variable = bfl_florentine_choice_resolved
            "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 2000 } }
            create_character = { age = 30 artist = painter artist_skill = 0.8
                culture = culture:tuscan birth_location = location:florence }
            trigger_event_silently = { id = bfi_bank_event_ui.1 days = 7 }
        } } }
    ''')
    write_script(overlay/'in_game/events/bfi_bank_event_ui.txt',f'''namespace = bfi_bank_event_ui
        bfi_bank_event_ui.1 = {{ type = country_event hidden = yes
            immediate = {{ trigger_event_non_silently = {event} }} }}''')
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    prior.update(runtime_sha256=runtime_hash(),fixture_sha256=digest.hexdigest(),
        suite='Production bank event UI',event=event,
        scope='Disposable Florence; staged charter, Reformation, research, exchange and wallets. Production event file and options remain unchanged. Scheduled opening after seven days.')
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(prior,indent=2)+'\n')
    return prior


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--userdir',type=Path,required=True)
    parser.add_argument('--event',default='bfl_bank_flo.4')
    args=parser.parse_args();print(json.dumps(prepare(args.userdir,args.event),indent=2))
