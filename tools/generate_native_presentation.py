"""Native implicit interaction/relation labels and notification definitions."""
import re
from audit_native import balanced_block


def generate(mod, loc, write):
    interactions = []
    for source in sorted((mod / 'in_game/common/country_interactions').glob('bfl*.txt')):
        text = source.read_text(encoding='utf-8-sig')
        cursor = 0
        for match in re.finditer(r'^\s*(bfl_\w+)\s*=\s*\{', text, re.M):
            if match.start() < cursor:
                continue
            cursor = balanced_block(text, text.index('{', match.start()))
            interactions.append(match[1])
    messages = ''
    for key in sorted(set(interactions)):
        for alias in ('PROPOSE_' + key, key + '_act', key + '_effect_text', key + '_effect_text_past'):
            loc(alias, '$' + key + '$')
        loc('dip_' + key + '_CATEGORY', 'Finance')
        for message in ('WE_PERFORM_' + key + '_ACTION', 'ACTION_' + key + '_PERFORMED_ON_US'):
            messages += f'''{message} = {{ log = yes onmap = no popup = no
                idle = no option = yes pausepopup = no message_category = diplomacy }}\n'''
            for suffix, value in {
                'SETUP': 'A financial instruction was submitted.',
                'HEADER': '$MESSENGER$', 'TITLE': '$' + key + '$',
                'EFFECTS': 'The instruction has been submitted. Accepted terms, funding and eligibility are checked by the financial service; the statement records the resulting transaction or remaining obligation.',
                'LOG': '$' + key + '$', 'BTN1': 'Acknowledge', 'BTN2': 'Acknowledge',
                'BTN3': '$common_string_go_to$', 'MAP': '',
            }.items():
                loc(message + '_' + suffix, value)
    # Native loads additional *_messagetypes.txt files alongside its own table.
    # This adds BFI definitions without replacing the native message registry.
    write('main_menu/gui/bfl_messagetypes.txt', messages)
    loc('LEAD_bfl_chartered_bank', 'Chartered Bank controller')
    loc('AM_bfl_chartered_bank', 'Chartered Bank')
    relation = 'bfl_workout_trade_access'
    for alias in (relation + '_relation', relation + '_effect_text', relation + '_effect_text_past',
                  'diplomatic_status_giving_' + relation + '_name',
                  'diplomatic_status_receiving_' + relation + '_name'):
        loc(alias, '$' + relation + '$')
    for alias in ('diplomatic_status_giving_' + relation + '_tooltip',
                  'diplomatic_status_receiving_' + relation + '_tooltip',
                  'giving_' + relation + '_list_who_tt', 'receiving_' + relation + '_list_who_tt'):
        loc(alias, '$' + relation + '_desc$')
