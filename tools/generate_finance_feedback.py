"""Read-only presentation of committed financial facts; no animation bookkeeping."""


def generate(common, effect, loc, write):
    common('scripted_effects','feedback',effect('bfl_record_feedback','''
        if = { limit = { NOT = { has_variable = bfl_feedback_sequence } }
            set_variable = { name = bfl_feedback_sequence value = 0 } }
        change_variable = { name = bfl_feedback_sequence add = 1 }
        set_variable = { name = bfl_feedback_kind value = $KIND$ }
        set_variable = { name = bfl_feedback_amount value = $AMOUNT$ }
        set_variable = { name = bfl_feedback_period value = bfl_period }
    '''))
    common('scripted_guis','feedback','''
        bfl_motion_enabled = { scope = country is_shown = {
            has_variable_map = cmm
            "variable_map(cmm|flag:bfl_banking_finance_companies__reduced_motion)" ?= 0
        } }
    ''')
    loc('bfl_feedback_signature', "[Country.GetTag]:[Country.MakeScope.GetVariable('bfl_feedback_sequence').GetValue|0]")
    loc('bfl_feedback_note', 'Latest committed transaction · the amount is already booked. Opening this view does not replay past effects. Reduced motion retains the same receipt and warnings. Discovery alone produces no payment indicator.')
    labels = {1:'Charter capital received',2:'Deposit received',3:'Withdrawal paid',
              4:'Dividend paid',5:'Bond resale settled',6:'Venture proceeds received',
              7:'#O New liquidity warning#!',8:'Resolution closed · recorded losses remain visible',
              9:'#O Facility target was not funded#!'}
    for key,value in labels.items():
        loc('bfl_feedback_'+str(key),value)
    key = "Concatenate('bfl_seen_', Country.GetTag)"
    signature = "Localize('bfl_feedback_signature')"
    changed = f"Not(EqualTo_string(GetVariableSystem.Get({key}), {signature}))"
    motion = "GetScriptedGui('bfl_motion_enabled').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)"
    cache = f' on_start = "[GetVariableSystem.Set({key}, {signature})]"'
    states = f'''state = {{ name = bfl_feedback_init trigger_on_create = yes {cache} }}
        state = {{ name = bfl_feedback_static trigger_when = "[And({changed}, Not({motion}))]" {cache} }}'''
    for kind in range(1,10):
        duration = 0.6 if kind in (1,8) else 0.3
        offset = 8 if kind in (1,2,5,6) else -8 if kind in (3,4) else 0
        condition = f"And3({changed}, {motion}, EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_feedback_kind').GetValue, '(CFixedPoint){kind}'))"
        states += f'''state = {{ name = bfl_feedback_{kind} trigger_when = "[{condition}]"
            duration = {duration} alpha = 0.45 position_x = {offset} next = bfl_feedback_rest {cache} }}'''
    states += 'state = { name = bfl_feedback_rest duration = 0.2 alpha = 1 position_x = 0 }'
    rows = '\n'.join(f'''text_multi = {{ text = "bfl_feedback_{kind}" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12
        visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_feedback_kind').GetValue, '(CFixedPoint){kind}')]" }}'''
        for kind in labels)
    reasons = {1:'Check research, branch access, issuer income and coupon capacity.',
               2:'Protected cash leaves insufficient liquid bank funds.',
               3:'The new claim would exceed the bank’s capital headroom.',
               4:'Combined sovereign obligations have reached issuer debt capacity.',
               5:'Unpaid sovereign coupons block further issuance.',
               6:'The sovereign has already issued a bond this month.',
               7:'All sovereign bond record slots are occupied.'}
    for reason,label in reasons.items():
        loc('bfl_facility_reason_'+str(reason), '#O '+label+'#!')
        rows += f'''text_multi = {{ text = "bfl_facility_reason_{reason}" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12
            visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_facility_reason').GetValue, '(CFixedPoint){reason}')]" }}'''
    write('in_game/gui/bfl_feedback.gui',f'''types BFLFeedbackTypes {{
        type bfl_feedback = vbox {{ layoutpolicy_horizontal = expanding spacing = 2 tooltip = bfl_feedback_note
            visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_feedback_sequence').GetValue, '(CFixedPoint)0')]"
            {states}
            {rows}
            AMOUNTS
        }}
    }}'''.replace('AMOUNTS','\n'.join(f'''text_single = {{ raw_text = "{sign}[Country.MakeScope.GetVariable('bfl_feedback_amount').GetValue|2]@gold!" autoresize = yes fontsize = 12
        visible = "[{'Or' if len(kinds)==2 else 'Or4'}({', '.join(f"EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_feedback_kind').GetValue, '(CFixedPoint){kind}')" for kind in kinds)})]" }}'''
            for sign,kinds in [('+ ',(1,2,5,6)),('− ',(3,4)),('',(7,9))])))
    common('../events','resolution_notice','''namespace = bfl_resolution_notice
        bfl_resolution_notice.1 = { type = country_event title = bfl_resolution_notice_title
            desc = bfl_resolution_notice_desc image = "gfx/interface/illustrations/bfl/m10_resolution.dds" outcome = neutral
            option = { name = bfl_resolution_notice_acknowledge ai_chance = { base = 100 } }
        }''')
    loc('bfl_resolution_notice_title','Bank resolution closed')
    loc('bfl_resolution_notice_desc', "[ROOT.GetCountry.MakeScope.GetVariable('bfl_notice_bank').GetCountry.GetName] has closed its financial operations.\\n\\nDeposit recoveries paid: [ROOT.GetCountry.MakeScope.GetVariable('bfl_notice_bank').GetCountry.MakeScope.GetVariable('bfl_resolution_paid').GetValue|2]@gold!\\nConsented deposit losses: [ROOT.GetCountry.MakeScope.GetVariable('bfl_notice_bank').GetCountry.MakeScope.GetVariable('bfl_resolution_waived').GetValue|2]@gold!\\nRecorded statutory losses: [ROOT.GetCountry.MakeScope.GetVariable('bfl_notice_bank').GetCountry.MakeScope.GetVariable('bfl_resolution_statutory_loss').GetValue|2]@gold!\\n\\nRecorded losses are unpaid amounts, not recoveries or new income. Historical ownership and the final estate remain recorded; the closed institution cannot reopen.")
    loc('bfl_resolution_notice_acknowledge','Acknowledge the final outcome')
