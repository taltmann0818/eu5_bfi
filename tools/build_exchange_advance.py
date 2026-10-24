"""Pinned native building-unlock override: change only exchange age/prerequisite."""
import hashlib
import json
from build_economy_gui import ROOT, MOD, DEFAULT_GAME, write
from audit_native import balanced_block


def build(game=DEFAULT_GAME):
    relative='in_game/common/advances/1_building_unlocks.txt'
    source=game/relative
    baseline=json.loads((ROOT/'docs/baseline.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=baseline['game_sources'][relative]:
        raise ValueError('Building advances changed; review the pinned native file first')
    text=source.read_text(encoding='utf-8-sig')
    start=text.index('stock_exchange_advance = {')
    end=balanced_block(text,text.index('{',start))
    original=text[start:end]
    assert original.count('age = age_5_absolutism')==1
    assert original.count('requires = absolutist_court')==1
    replacement=original.replace('age = age_5_absolutism','age = age_4_reformation').replace('requires = absolutist_court','requires = global_trade_advance')
    replacement=replacement.replace('ai_weight = {', '''ai_weight = {
        if = { limit = { bfl_has_management = yes NOT = { bfl_owns_stock_exchange = yes } } add = 20000 }''',1)
    updated=text[:start]+replacement+text[end:]
    assert updated.replace(replacement,original,1)==text
    write(MOD/relative,updated)
    relative='in_game/common/advances/0_age_of_absolutism.txt'
    source=game/relative
    if hashlib.sha256(source.read_bytes()).hexdigest()!=baseline['game_sources'][relative]:
        raise ValueError('Central banking source changed; review the pinned native file first')
    text=source.read_text(encoding='utf-8-sig')
    start=text.index('central_bank_advance = {')
    end=balanced_block(text,text.index('{',start))
    original=text[start:end]
    replacement=original.replace('age = age_5_absolutism','age = age_4_reformation').replace('requires = manufactories_advance','requires = stock_exchange_advance')
    updated=text[:start]+replacement+text[end:]
    assert updated.replace(replacement,original,1)==text
    write(MOD/relative,updated)
    print('Global Trade > Stock Exchange > Central Banking, all in Reformation; other native effects preserved.')


if __name__=='__main__': build()
