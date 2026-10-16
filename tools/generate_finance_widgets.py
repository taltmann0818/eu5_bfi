"""Native tooltip building blocks shared by the bank statements."""


def icon_texture(art):
    # Resolve the installed game's government-bond art; never redistribute its DDS.
    if art == 'bond':
        return "[GetConceptTexture('government_bond')]"
    return f'gfx/interface/icons/bfl/{art}.dds'


def swatch(color):
    return f'''icon = {{ size = {{ 14 22 }} texture = "gfx/interface/component_tiles/bookmark_white.dds"
        color = {color} }}'''


def row(left, right, index=0, visible='', color=None, art=None):
    background = 'background = { using = tooltip_table_field_texture }' if index % 2 == 0 else ''
    leading = swatch(color) if color else ''
    if art:
        leading += f'icon = {{ size = {{ 20 20 }} texture = "{icon_texture(art)}" }}'
    return f'''widget = {{ {visible} size = {{ -1 30 }} layoutpolicy_horizontal = expanding
        {background} hbox = {{ layoutpolicy_horizontal = expanding margin = {{ 10 2 }} spacing = 8
            {leading} text_single = {{ raw_text = "{left}" autoresize = yes }} expand = {{ }}
            text_single = {{ raw_text = "{right}" autoresize = yes align = right|nobaseline }} }} }}'''


def list_block(title, content, visible=''):
    return f'''TooltipListBase = {{ {visible}
        blockoverride "block_title" {{ visible = yes text = "{title}" }}
        {content} }}'''


def scroll_rows(content, width=420, height=270):
    return f'''TooltipListScrollArea = {{
        blockoverride "block_scrollarea" {{ maximumsize = {{ {width} {height} }} }}
        blockoverride "scrollarea_content" {{ TooltipContentSection = {{
            set_parent_dimension_to_minimum = height spacing = 0 {content} }} }} }}'''


def tooltip_type(name, title, subtitle, art, content):
    return f'''type {name} = ContextualTooltipType {{
        blockoverride "title_icon" {{ icon = {{ using = tooltip_title_icon_size
            texture = "{icon_texture(art)}" }} }}
        blockoverride "title_text" {{ text = "{title}" }}
        blockoverride "concept_link" {{ text = "{subtitle}" }}
        blockoverride "tooltip_content" {{ vbox = {{ size = {{ 420 0 }}
            set_parent_size_to_minimum = yes ignoreinvisible = yes spacing = 6 {content} }} }}
    }}'''
