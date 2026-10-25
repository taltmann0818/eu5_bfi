"""Build the two narrowly modified native definitions for historical founding."""
import argparse
import hashlib
import json
from pathlib import Path
from audit_native import balanced_block
from build_economy_gui import DEFAULT_GAME, MOD, ROOT, write

EVENT = 'in_game/events/DHE/flavor_ENG.txt'
NAMES = 'in_game/common/customizable_localization/country_name_construction.txt'
CALL = '\t\tbfl_found_bank_of_england = yes\n'
IMAGE = '\timage = "gfx/interface/illustrations/bfl/bank_of_england.dds"\n'
SOUTH_SEA_ADDITIONS = {
    'a': '''
        # BFI: the native decision leaves the failed subscriptions with their owners.
        if = {
            limit = { bfl_has_management = yes var:bfl_bank = { tag = BOENG bfl_is_chartered_bank = yes is_subject_of = root } }
            add_country_modifier = { modifier = bfl_dhe_south_sea_failures months = 60 mode = replace }
            var:bfl_bank = { add_country_modifier = { modifier = bfl_dhe_bubble_contagion months = 60 mode = replace } }
        }
''',
    'b': '''
        # BFI: the native six-month-income rescue carries the continuing public cost.
        if = {
            limit = { bfl_has_management = yes var:bfl_bank = { tag = BOENG bfl_is_chartered_bank = yes is_subject_of = root } }
            add_country_modifier = { modifier = bfl_dhe_public_bubble_relief months = 60 mode = replace }
            var:bfl_bank = { add_country_modifier = { modifier = bfl_dhe_bubble_restructuring months = 60 mode = replace } }
        }
''',
}
NAME_RULE = '''
    # Historical institutions already have complete names.
    text = {
        localization_key = country_name_construction_name
        trigger = { OR = { tag = BOENG tag = BWISS tag = BRIKS } }
    }
'''


def event_override(text):
    start = text.index('flavor_eng.28 = {')
    end = balanced_block(text, text.index('{', start))
    event = text[start:end]
    anchor = '\t\tadd_reform = government_reform:bank_of_england_reform\n'
    assert event.count(anchor) == 1
    event = event.replace(anchor, anchor + CALL, 1)
    event = event.replace('\toutcome = neutral\n', '\toutcome = neutral\n' + IMAGE, 1)
    text = text[:start] + event + text[end:]
    start = text.index('flavor_eng.215 = {')
    end = balanced_block(text, text.index('{', start))
    event = text[start:end]
    for choice, addition in SOUTH_SEA_ADDITIONS.items():
        anchor = f'\t\tname = flavor_eng.215.{choice}\n'
        assert event.count(anchor) == 1
        event = event.replace(anchor, anchor + addition, 1)
    return text[:start] + event + text[end:]


def names_override(text):
    anchor = 'country_name_construction = {\n'
    assert text.count(anchor) == 1
    return text.replace(anchor, anchor + NAME_RULE, 1)


HISTORICAL_EVENTS = {
    'in_game/events/DHE/flavor_hol.txt': ('flavor_hol.28', 'wisselbank', 'HOL'),
    'in_game/events/DHE/flavor_SWE.txt': ('flavor_swe.60', 'riksbank', 'SWE'),
}


def historical_event_override(text, event_id, bank, tag):
    start = text.index(event_id+' = {')
    end = balanced_block(text, text.index('{', start))
    event = text[start:end]
    event = event.replace('\toutcome = neutral\n', '\toutcome = neutral\n'+f'\timage = "gfx/interface/illustrations/bfl/{bank}.dds"\n', 1)
    anchor = f'\t\tname = {event_id}.a\n'
    assert event.count(anchor) == 1
    event = event.replace(anchor, anchor+f'\t\tbfl_found_{bank} = yes\n', 1)
    if tag == 'HOL':
        # Multiple tag entries are native DHE syntax (e.g. flavor_arm).
        event = event.replace('\t\ttag = HOL\n', '\t\ttag = HOL\n\t\ttag = NED\n', 1)
        event = event.replace('\ttrigger = {\n', '\ttrigger = {\n\t\tNOT = { country_exists = c:BWISS }\n', 1)
    return text[:start]+event+text[end:]


def build(game=DEFAULT_GAME):
    pins = json.loads((ROOT/'docs/baseline.json').read_text())['game_sources']
    transformations = [(EVENT, event_override), (NAMES, names_override)]
    for relative, args in HISTORICAL_EVENTS.items():
        transformations.append((relative, lambda text, args=args: historical_event_override(text, *args)))
    transformations.append(('in_game/common/building_types/unique_buildings.txt', branches_override))
    for relative, transform in transformations:
        source = game/relative
        if hashlib.sha256(source.read_bytes()).hexdigest() != pins[relative]:
            raise ValueError(f'Native source changed: {relative}')
        write(MOD/relative, transform(source.read_text(encoding='utf-8-sig')))


def branches_override(text):
    start = text.index('banking_office = {')
    end = balanced_block(text,text.index('{',start))
    block = text[start:end]
    anchor = '\t\thas_reform = government_reform:banking_country\n'
    assert block.count(anchor) == 1
    block = block.replace(anchor, '''        OR = { has_reform = government_reform:banking_country
            AND = { country_type = location bfl_has_management = yes
                var:bfl_bank = { bfl_is_chartered_bank = yes is_subject_of = prev } } }
''', 1)
    # Avoid paying for a duplicate of the same bank's existing or queued branch.
    block = block.replace('\tcountry_potential = {', '''    allow = {
        trigger_if = { limit = { scope:actor = { country_type = location bfl_has_management = yes } }
            NOT = { any_buildings_in_location = { building_type = building_type:banking_office
                owner = scope:actor.var:bfl_bank } }
        }
    }
\tcountry_potential = {''',1)
    return text[:start]+block+text[end:]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, default=DEFAULT_GAME)
    build(parser.parse_args().game)
