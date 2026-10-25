"""Preserve custom event-image proportions in the native shallow frame."""
import hashlib
import json
from build_economy_gui import DEFAULT_GAME, ROOT, MOD, write

SOURCE = 'in_game/gui/eventwindow.gui'
ANCHOR = '\t\t\t\t\t\tvisible = "[EventWindow.HasUniqueImage]"\n\t\t\t\t\t\ttexture = "[EventWindow.GetUniqueImage]"\n'
ADDITION = '\t\t\t\t\t\tfittype = centercrop\n'


def build(game=DEFAULT_GAME):
    source = game / SOURCE
    pins = json.loads((ROOT/'docs/baseline.json').read_text(encoding='utf-8'))['game_sources']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == pins[SOURCE], 'Native event window changed; review required.'
    text = source.read_text(encoding='utf-8-sig')
    assert text.count(ANCHOR) == 2
    write(MOD/SOURCE, text.replace(ANCHOR, ANCHOR+ADDITION))


if __name__ == '__main__':
    build()
