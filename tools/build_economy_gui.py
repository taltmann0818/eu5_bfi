"""Generate the single native Economy override, refusing changes to pinned source."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'mod/bfl'
DEFAULT_GAME = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(('\ufeff' + text.lstrip('\ufeff')).replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))


def build(game, pin=False):
    relative = 'in_game/gui/economy_lateralview.gui'
    source = game / relative
    baseline_path = ROOT / 'docs/baseline.json'
    baseline = json.loads(baseline_path.read_text()) if baseline_path.exists() else {}
    actual_hash = digest(source)
    expected = baseline.get('game_sources',{}).get(relative)
    if not pin and expected != actual_hash:
        raise ValueError(f'Unknown Economy source hash {actual_hash}; review the upstream diff before repinning.')
    text = source.read_text(encoding='utf-8-sig')
    marker = '\nlateralview = {'
    if text.count(marker) != 1:
        raise ValueError('Expected exactly one native lateralview')
    pos = text.index(marker) + 1
    types, view = text[:pos], text[pos:]
    if 'template economy_main_tabs' not in types or 'template EstateIncomeBreakdownTooltip' not in types:
        raise ValueError('Native template manifest changed')
    anchor = '\t\t\t\t\t\t\t\t\t\t\t#tariff income'
    insert_pos = view.index(anchor)
    # Display funded borrowing separately; never change the native income total.
    insertion = '''
        bfl_income_dividends = {
            name = "bfl_income_dividends" datacontext = "[GetPlayer]"
            visible = "[Or(GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End), GreaterThan_CFixedPoint(GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bank_dividend_annual'), '(CFixedPoint)0'))]"
        }
        bfl_income_facility = {
            name = "bfl_income_facility" datacontext = "[GetPlayer]"
            visible = "[GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        }
        bfl_income_interest = {
            name = "bfl_income_interest" datacontext = "[GetPlayer]"
            visible = "[GreaterThan_CFixedPoint(GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_deposit_income_display'), '(CFixedPoint)0')]"
        }
        bfl_income_bond_coupons = {
            name = "bfl_income_bond_coupons" datacontext = "[GetPlayer]"
            visible = "[GreaterThan_CFixedPoint(GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_income_display'), '(CFixedPoint)0')]"
        }
    '''+'\n\n'
    view = view[:insert_pos] + insertion + view[insert_pos:]
    # File-scoped constants must accompany each extracted consumer.
    constants = '\n'.join(re.findall(r'^@[^\n]+', text, re.M))
    write(MOD / relative, (constants+'\n' if constants else '')+view)
    write(MOD / 'in_game/gui/vanilla/bfl_economy_vanilla_types.gui',types)
    if pin:
        baseline.setdefault('game_sources',{})[relative] = actual_hash
        baseline_path.parent.mkdir(parents=True,exist_ok=True)
        baseline_path.write_text(json.dumps(baseline,indent=2)+'\n')
    # Prove the sole logical change by reversing the extraction and injection.
    restored=view.replace(insertion,'',1)
    assert types + restored == text
    from generate_interface import build_credit
    build_credit(game, baseline, pin)
    from build_exchange_advance import build as build_exchange_advance
    build_exchange_advance(game)
    from generate_branches import build_native
    build_native(game)
    # Branch regeneration must retain the professional bank constitution in
    # native loan eligibility, just as the full script generator does.
    from generate_bank_reforms import build_native as build_bank_reforms
    build_bank_reforms(game)
    print('Economy generated: Balance income rows and Credit homepage; native templates owned once.')


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--game',type=Path,default=DEFAULT_GAME)
    ap.add_argument('--pin-reviewed-source',action='store_true')
    args=ap.parse_args()
    build(args.game,args.pin_reviewed_source)
