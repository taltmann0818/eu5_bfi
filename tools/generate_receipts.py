"""Native claim cash attribution; no duplicate native transfers."""


def generate(common, effect, loc):
    # Receipt metadata follows the earnings cutoff, not the calendar. A payment
    # received after this bank closes must survive into its next statement.
    init = '''if = { limit = { NOT = { has_variable = bfl_receipt_period } }
        set_variable = { name = bfl_receipt_period value = bfl_period }
    '''
    for field in ('native_interest', 'native_principal', 'native_recovery_gain', 'native_recovery_loss'):
        init += f'set_variable = {{ name = bfl_{field} value = 0 }}\n'
    common('scripted_effects', 'receipt_period', effect('bfl_open_receipt_period', init + '}'))
    sample = 'bfl_initialize_credit = yes\nbfl_open_receipt_period = yes\nsave_scope_as = bfl_receipt_bank\n'
    callback = 'bfl_open_receipt_period = yes\n'
    close = 'bfl_open_receipt_period = yes\n'
    reset = 'if = { limit = { exists = scope:bfl_restructure_claim }\n'
    for i in range(1, 33):
        n = f'bfl_cr_{i:02}'
        sample += f'''if = {{ limit = {{ var:{n}_state = 1 exists = var:{n}_loan
            var:{n}_loan = {{ owner = scope:bfl_receipt_bank }} }}
            if = {{ limit = {{ has_variable = {n}_observed_remaining has_variable = {n}_observed_face
                var:{n}_observed_face = var:{n}_loan.loan_amount
                var:{n}_observed_rate ?= var:{n}_loan.loan_interest
                has_variable = {n}_observed_months var:{n}_observed_months > var:{n}_loan.months_left
                var:{n}_observed_remaining > var:{n}_loan.remaining_debt
                var:{n}_repaid = 0 }}
                # With unchanged face, declining native remaining interest is the
                # native monthly coupon, not principal or a treasury delta.
                set_variable = {{ name = bfl_native_coupon value = {{ value = var:{n}_observed_remaining
                    subtract = var:{n}_loan.remaining_debt }} }}
                change_variable = {{ name = bfl_native_interest add = var:bfl_native_coupon }}
                var:{n}_party = {{ save_scope_as = bfl_source_party }}
                set_variable = {{ name = bfl_source_amount value = var:bfl_native_coupon }} bfl_source_add_credit = yes
            }}
            set_variable = {{ name = {n}_observed_remaining value = var:{n}_loan.remaining_debt }}
            set_variable = {{ name = {n}_observed_face value = var:{n}_loan.loan_amount }}
            set_variable = {{ name = {n}_observed_rate value = var:{n}_loan.loan_interest }}
            set_variable = {{ name = {n}_observed_months value = var:{n}_loan.months_left }}
        }}\n'''
        callback += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_repaid = 0 var:{n}_loan ?= scope:target }}
            # Native callback precedes its atomic wallet transfer. Recognition
            # waits for the claim's subsequent native invalidation.
            set_variable = {{ name = {n}_receipt value = scope:target.remaining_debt }}
            set_variable = {{ name = {n}_repaid value = 1 }} }}\n'''
        close += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_repaid = 1 NOT = {{ exists = var:{n}_loan }} has_variable = {n}_receipt }}
            set_variable = {{ name = bfl_released_native_basis value = {{ value = var:{n}_basis max = var:{n}_receipt }} }}
            change_variable = {{ name = bfl_native_principal add = var:bfl_released_native_basis }}
            var:{n}_party = {{ save_scope_as = bfl_source_party }}
            set_variable = {{ name = bfl_source_amount value = var:bfl_released_native_basis }} bfl_source_add_principal = yes
            set_variable = {{ name = bfl_native_gain value = {{ value = var:{n}_receipt subtract = var:{n}_basis }} }}
            if = {{ limit = {{ var:bfl_native_gain >= 0 }}
                change_variable = {{ name = bfl_profit_credit add = var:bfl_native_gain }}
                change_variable = {{ name = bfl_native_recovery_gain add = var:bfl_native_gain }}
                set_variable = {{ name = bfl_source_amount value = var:bfl_native_gain }} bfl_source_add_credit = yes
            }} else = {{
                change_variable = {{ name = bfl_loss_carryforward subtract = var:bfl_native_gain }}
                change_variable = {{ name = bfl_native_recovery_loss subtract = var:bfl_native_gain }}
                set_variable = {{ name = bfl_source_amount value = {{ value = var:bfl_native_gain multiply = -1 }} }} bfl_source_add_recovery_loss = yes }}
            remove_variable = {n}_receipt
        }}\n'''
        reset += f'''if = {{ limit = {{ var:{n}_loan ?= scope:bfl_restructure_claim }}
            set_variable = {{ name = {n}_observed_remaining value = var:{n}_loan.remaining_debt }}
            set_variable = {{ name = {n}_observed_face value = var:{n}_loan.loan_amount }}
            set_variable = {{ name = {n}_observed_rate value = var:{n}_loan.loan_interest }}
            set_variable = {{ name = {n}_observed_months value = var:{n}_loan.months_left }} }}\n'''
    common('scripted_effects', 'native_receipts', effect('bfl_sample_native_coupons', sample)
           + effect('bfl_capture_native_payoff', callback) + effect('bfl_recognize_native_payoffs', close)
           + effect('bfl_reset_restructured_receipt_basis', reset + '}'))
    statement = '''set_variable = { name = bfl_statement_period value = bfl_period }
        set_variable = { name = bfl_statement_native_interest value = var:bfl_native_interest }
        set_variable = { name = bfl_statement_principal value = var:bfl_native_principal }
        set_variable = { name = bfl_statement_recovery_gain value = var:bfl_native_recovery_gain }
        set_variable = { name = bfl_statement_recovery_loss value = var:bfl_native_recovery_loss }
        set_variable = { name = bfl_statement_losses value = var:bfl_loss_carryforward }
        set_variable = { name = bfl_statement_deposit_cost value = var:bfl_deposit_interest_cost }
        set_variable = { name = bfl_statement_operating_cost value = var:bfl_expense_due }
        # Recognized native surplus/deficit is a net channel, not a fabricated
        # gross native budget reconstructed from a different month's forecast.
        set_variable = { name = bfl_statement_native_gross value = var:bfl_profit_native }
        set_variable = { name = bfl_statement_native_total value = monthly_income_total }
        set_variable = { name = bfl_statement_native_balance value = monthly_balance }
        set_variable = { name = bfl_statement_cost_base value = bfl_operating_base_cost }
        set_variable = { name = bfl_statement_cost_accounts value = bfl_operating_accounts_cost }
        set_variable = { name = bfl_statement_cost_contracts value = bfl_operating_contracts_cost }
        set_variable = { name = bfl_statement_cost_branches value = bfl_operating_branches_cost }
        set_variable = { name = bfl_statement_cost_asset_types value = bfl_operating_asset_types_cost }
        set_variable = { name = bfl_statement_cost_reduction value = bfl_operating_total_reduction }
        set_variable = { name = bfl_statement_native_cost value = { value = var:bfl_native_monthly_net max = 0 multiply = -1 } }
        set_variable = { name = bfl_statement_impairment value = { value = var:bfl_credit_impairments subtract = var:bfl_reported_impairments min = 0 } }
        set_variable = { name = bfl_reported_impairments value = var:bfl_credit_impairments }
    '''
    for bucket in ('services', 'credit', 'controller', 'trading', 'goods', 'ventures', 'company', 'native'):
        statement += f'set_variable = {{ name = bfl_statement_{bucket} value = var:bfl_profit_{bucket} }}\n'
    statement += '''set_variable = { name = bfl_statement_loss_opening value = var:bfl_loss_opening }
        set_variable = { name = bfl_statement_loss_costs value = bfl_report_gross_expenses }
        set_variable = { name = bfl_statement_loss_adjustments value = {
            value = var:bfl_statement_losses subtract = var:bfl_statement_loss_opening subtract = var:bfl_statement_loss_costs } }
    '''
    for field in ('native_interest', 'native_principal', 'native_recovery_gain', 'native_recovery_loss'):
        statement += f'set_variable = {{ name = bfl_{field} value = 0 }}\n'
    statement += 'set_variable = { name = bfl_receipt_period value = bfl_period }\n'
    common('scripted_effects', 'activity_statement', effect('bfl_record_activity_statement', statement))
    loc('bfl_activity_title', 'Monthly activity statement')
    loc('bfl_activity_title_tip', 'Native coupon observations classify the native net budget; they never move gold twice. Settled native payoff proceeds release actual acquisition cost before recognizing a gain or loss. Company distributions and custom funded receipts enter their own buckets. Principal, deposits and subscriptions are excluded from profits.')
