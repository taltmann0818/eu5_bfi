"""Bounded counterparty attribution, sampled at the bank's earnings cutoff."""
FIELDS = ('credit', 'principal', 'recovery_loss', 'deposit_cost', 'company', 'trading', 'impairment', 'dividend_paid')
COUNT = 64


def record(field, party, amount):
    return f'''{party} = {{ save_scope_as = bfl_source_party }}
        set_variable = {{ name = bfl_source_amount value = {amount} }} bfl_source_add_{field} = yes'''


def generate(common, effect):
    init = 'if = { limit = { NOT = { has_variable = bfl_source_schema } } set_variable = { name = bfl_source_schema value = 1 }\n'
    for i in range(1, COUNT+1):
        for field in FIELDS:
            for prefix in ('source','source_closed'):
                init += f'set_variable = {{ name = bfl_{prefix}_{i:02}_{field} value = 0 }}\n'
    init += '}\n'
    body = effect('bfl_initialize_activity_sources', init)
    for field in FIELDS:
        add = '''bfl_initialize_activity_sources = yes
            if = { limit = { exists = scope:bfl_source_party var:bfl_source_amount > 0 }
                set_variable = { name = bfl_source_slot value = 0 }
        '''
        for i in range(1,COUNT+1):
            add += f'''if = {{ limit = {{ var:bfl_source_slot = 0 exists = var:bfl_source_{i:02}_party
                var:bfl_source_{i:02}_party = scope:bfl_source_party }} set_variable = {{ name = bfl_source_slot value = {i} }} }}\n'''
        for i in range(1,COUNT+1):
            add += f'''if = {{ limit = {{ var:bfl_source_slot = 0 NOT = {{ exists = var:bfl_source_{i:02}_party }} }}
                set_variable = {{ name = bfl_source_{i:02}_party value = scope:bfl_source_party }}
                set_variable = {{ name = bfl_source_slot value = {i} }} }}\n'''
        for i in range(1,COUNT+1):
            add += f'''if = {{ limit = {{ var:bfl_source_slot = {i} }}
                change_variable = {{ name = bfl_source_{i:02}_{field} add = var:bfl_source_amount }} }}\n'''
        body += effect('bfl_source_add_'+field,add+'}')
    close = 'bfl_initialize_activity_sources = yes\n'
    for i in range(1,COUNT+1):
        close += f'''remove_variable = bfl_source_closed_{i:02}_party
            if = {{ limit = {{ exists = var:bfl_source_{i:02}_party }}
                set_variable = {{ name = bfl_source_closed_{i:02}_party value = var:bfl_source_{i:02}_party }} }}
            remove_variable = bfl_source_{i:02}_party\n'''
        for field in FIELDS:
            close += f'''set_variable = {{ name = bfl_source_closed_{i:02}_{field} value = var:bfl_source_{i:02}_{field} }}
                set_variable = {{ name = bfl_source_{i:02}_{field} value = 0 }}\n'''
    body += effect('bfl_close_activity_sources', close)
    common('scripted_effects','activity_sources',body)
    values = ''
    for field in FIELDS:
        values += effect(f'bfl_source_total_{field}','value = 0\n'+''.join(f'add = var:bfl_source_closed_{i:02}_{field}\n' for i in range(1,COUNT+1)))
    common('script_values','activity_sources',values)
