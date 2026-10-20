"""Native opportunity discovery, non-funding, stale quote and alert lifecycle."""


def extra(check):
    body = '''c:BRD = { set_variable = { name = bfi_alert_cash value = gold }
        set_variable = { name = bfi_alert_basis value = var:bfl_project_value }
        bfl_refresh_commenda_opportunity = yes }'''
    body += check('alert_discovers_named_eligible_cargo_without_funding', '''c:BRD = {
        has_variable = bfl_op_country exists = var:bfl_op_good exists = var:bfl_op_from exists = var:bfl_op_to
        var:bfl_op_cost > 0 var:bfl_op_surplus > 0 gold = var:bfi_alert_cash
        var:bfl_project_value = var:bfi_alert_basis
        cmf_is_alert_active = { alert = bfl_commenda_available }
        var:bfl_op_country = { NOT = { has_variable = bfl_venture_bank } NOT = { has_variable = bfl_venture_offer_bank } } }''')
    body += '''c:BRD = { set_variable = { name = bfi_alert_operator value = var:bfl_op_country }
        var:bfi_alert_operator = { set_variable = bfl_venture_guard }
        bfl_propose_commenda_opportunity = yes }'''
    body += check('alert_stale_operation_cannot_send_offer_or_move_cash', '''c:BRD = {
        gold = var:bfi_alert_cash var:bfl_project_value = var:bfi_alert_basis
        var:bfi_alert_operator = { NOT = { has_variable = bfl_venture_bank } NOT = { has_variable = bfl_venture_offer_bank } } }''')
    body += '''c:BRD = { var:bfi_alert_operator = { remove_variable = bfl_venture_guard }
        set_variable = { name = bfl_profile value = 1 } bfl_refresh_commenda_opportunity = yes }'''
    body += check('alert_removed_when_profile_ineligible', '''c:BRD = { NOT = { has_variable = bfl_op_country }
        NOT = { cmf_is_alert_active = { alert = bfl_commenda_available } } }''')
    body += '''c:BRD = { set_variable = { name = bfl_profile value = 2 }
        add_to_variable_map = { name = cmm key = flag:bfl_banking_finance_companies__finance_notifications value = 0 }
        bfl_refresh_commenda_opportunity = yes }'''
    body += check('alert_respects_finance_notification_preference', '''c:BRD = { NOT = { has_variable = bfl_op_country }
        NOT = { cmf_is_alert_active = { alert = bfl_commenda_available } } }''')
    body += '''c:BRD = { add_to_variable_map = { name = cmm key = flag:bfl_banking_finance_companies__finance_notifications value = 1 }
        bfl_refresh_commenda_opportunity = yes }'''
    body += check('alert_returns_after_notifications_enabled', '''c:BRD = { has_variable = bfl_op_country
        cmf_is_alert_active = { alert = bfl_commenda_available } gold = var:bfi_alert_cash }''')
    return body
