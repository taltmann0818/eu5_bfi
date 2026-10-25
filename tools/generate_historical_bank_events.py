"""Individually authored post-charter dilemmas with native effect previews.

The catalogue below is the narrative/effects source. Shared helpers format
native effects; they do not impose a common choice on different historical events.
"""
from collections import defaultdict

DHE_ART_KEYS = ('eng_ways_means','eng_threadneedle_v2','eng_credit_1772',
    'flo_buondelmonti','flo_english_factors','flo_bardi_chapel','flo_english_default',
    'gen_imperial_credit','gen_grimaldi_albergo','gen_spinola_captains',
    'ven_three_years','ven_war_plague','ven_convertibility')


def generate(common, effect, loc, write):
    modifiers={}
    descriptions={
        'public_register':'Public subscriptions and transfers are recorded under a settled arrangement with the Bank.',
        'register_clerks':'A permanent staff keeps the public stock register and pays its dividends.',
        'exchequer_register':'The treasury maintains its own register, preserving independence at the cost of friction with the City.',
        'farmed_excises':'Private collectors guarantee the excises and exact their price from commerce.',
        'public_bubble_relief':'The public purse bears the cost of restoring confidence after the collapse of the subscriptions.',
        'bubble_contagion':'The collapse of speculative subscriptions weakens confidence in the bank’s quoted shares.',
        'bubble_restructuring':'The rescue supports confidence in the bank, while the administration of the restructured accounts increases its expenses.',
        'south_sea_failures':'Failed subscriptions and contested debts interrupt the ordinary business of the City.',
        'threadneedle_public':'A permanent public establishment brings the bank’s departments beneath an ordered administration.',
        'threadneedle_merchants':'The proprietors have paid for a permanent wing and a more efficient banking house.',
        'city_concessions':'The merchants’ contribution to the bank was secured by concessions to the City.',
        'hired_halls':'Scattered offices and crowded counters add to the expense of the growing bank.',
        'discount_1772':'Specialist clerks examine new credit business more closely, improving terms at a higher recurring cost.',
        'credit_relief_1772':'The treasury has committed resources to steadying credit through the crisis.',
        'reserves_1772':'A public contribution reinforces confidence in the bank’s reserves.',
        'credit_contraction_1772':'The failure of private credit bears down upon commerce and the revenues it sustains.',
        'guelph_compact':'The Bardi’s ancestral alliances bind public credit to the friends of the papacy.',
        'civic_neutrality':'The Signoria requires its bank to serve the commune across the divisions of party.',
        'english_wool_factors':'Factors follow the English wool trade, maintaining commercial connections and their own costly house.',
        'english_court_accounts':'Royal connections support more profitable new loan offers but require an expensive attendance at court.',
        'italian_concentration':'The bank reduces its distant commitments and the cost of maintaining them.',
        'bardi_patronage':'The splendor of the family’s chapel lends distinction to the banking house.',
        'ungilded_accounts':'Public resources have been kept among the accounts rather than spent upon family patronage.',
        'florentine_settlement':'A public settlement helps commerce recover while charging the treasury for the old disputes.',
        'partners_levy':'The partners bear an extraordinary levy, preserving public resources at the expense of their wider business.',
        'old_litigation':'The unresolved debts of the great banking houses continue to obstruct commerce.',
        'imperial_accounts':'Attendance upon the imperial court supports new lending terms and increases the cost of the bank’s affairs.',
        'european_factors':'A wider circle of factors connects the bank to several courts and markets.',
        'republic_first':'The republic favors its own revenues over the diplomatic advantages of foreign court accounts.',
        'grimaldi_concessions':'The republic has recognized family privileges in return for the continuing Grimaldi corporation.',
        'notarial_albergo':'Civic notaries bring the family’s obligations into a common, supervised order.',
        'civic_notaries':'The republic’s notaries maintain a clearer public account of the banking compact.',
        'banker_captains':'The banking families have acquired a settled influence over the republic’s offices and revenues.',
        'balanced_captains':'A shared magistracy balances rival houses, supporting commerce while dividing public revenues.',
        'separate_offices':'Bankers must negotiate with public officers rather than directing their own affairs of state.',
        'permanent_giro':'The Giro has a settled administration instead of a succession of expiring mandates.',
        'giro_senate':'The Senate accepts a continuing public charge for its permanent banking institution.',
        'annual_giro':'The bank may continue for another year, with its authority still dependent upon the Senate.',
        'giro_winddown':'The end of new business at the Giro disrupts merchants accustomed to its transfer books.',
        'plague_accounts':'The bank must maintain additional registers and clerks for the emergency appropriations.',
        'venetian_relief':'Public appropriations sustain civilian commerce while burdening the revenues of the republic.',
        'military_giro':'The republic gives military accounts priority over the ordinary business of its merchants.',
        'war_accounts':'The Giro keeps a separate and costly administration for military payments.',
        'parish_burden':'The parishes and neighborhoods carry relief which the public treasury has declined to fund.',
        'giro_specie':'Treasury reserves and staffed counters support the reputation of the new specie facility.',
        'giro_measured_specie':'A smaller facility provides a measured accommodation, with continuing expense to the bank.',
        'giro_transfer_office':'The Giro favors inexpensive book transfers despite the merchants’ demand for a broader specie facility.',
    }
    def mod(key, title, fields, months=120, bank=False):
        description=descriptions[key]
        key='bfl_dhe_'+key
        modifiers[key]=fields
        loc(key,title)
        loc(key+'_desc',description)
        command=f'add_country_modifier = {{ modifier = {key} months = {months} mode = replace }}'
        return '\n'+(f'scope:bfl_event_bank = {{ {command} }}' if bank else command)+'\n'
    def estate(kind, amount):
        return f'\nadd_estate_satisfaction = {{ type = estate_type:{kind}_estate value = {amount} }}\n'
    def opinion(amount='favored', country=None):
        if country:
            return f'\nc:{country} ?= {{ add_opinion = {{ target = root modifier = bfl_dhe_{amount} }} }}\n'
        return f'\nscope:bfl_event_bank = {{ add_opinion = {{ target = root modifier = bfl_dhe_{amount} }} }}\n'
    def spend(amount, bank=False):
        return '\n'+(f'scope:bfl_event_bank = {{ add_gold = -{amount} }}' if bank else f'add_gold = -{amount}')+'\n'
    def option(label, effects, gate='', ledger='', preview='', weight=30):
        return dict(label=label,effects=effects,gate=gate,ledger=ledger,preview=preview,weight=weight)
    events=[]
    def event(country, number, key, title, desc, start, end, options, gate='', immediate=''):
        events.append(dict(country=country,id=number,key=key,title=title,desc=desc,start=start,end=end,options=options,gate=gate,immediate=immediate))

    event('eng',1,'eng_ways_means','The Ways and Means of Public Credit',
        'The Commons has found a new use for the Bank of England. Instead of leaving every subscription, transfer and dividend in the hands of the Exchequer, the bank would keep a public register of government stock. The directors offer to subscribe to an issue themselves, provided that its interest is honored. Treasury officials object that the keeper of the register will become the gatekeeper of public credit. The excise farmers, meanwhile, promise revenue without surrendering so much authority to the City.',
        '1715.1.1','1730.12.31',[
        option('Entrust the register to the Bank, at five percent.',
            mod('public_register','The Bank’s Public Register','tax_income_efficiency = 0.025')+mod('register_clerks','The Public Register’s Clerks','bfl_bank_operating_expenses_modifier = 0.05',120,True)+estate('burghers',0.05),
            gate='bfl_dhe_can_issue_annuity = yes',ledger='bfl_dhe_issue_annuity = yes',
            preview='add_gold = 100 scope:bfl_event_bank = { add_gold = -100 } custom_tooltip = bfl_dhe_annuity_tt',weight=55),
        option('Pay for an independent Exchequer register.',
            spend(150)+mod('exchequer_register','An Independent Exchequer Register','tax_income_efficiency = 0.05 diplomatic_reputation = -0.5')+opinion('rebuffed'),gate='gold >= 150'),
        option('Let the excise farmers find the money.',
            mod('farmed_excises','Excises Farmed to Private Collectors','tax_income_efficiency = 0.075 trade_income = -0.075')+estate('burghers',-0.10))])

    event('eng',3,'eng_threadneedle_v2','The Threadneedle Street Establishment',
        'The bank’s hired rooms are crowded with ledgers, cashiers and proprietors waiting for their dividends. Its directors have secured plans for a permanent establishment in Threadneedle Street. A public building would give the treasury a firm hand in its administration, but the price is considerable. The merchant proprietors offer a cheaper subscription of their own, in return for concessions to the City. Remaining in the old rooms would save money today, while leaving the growing expense of scattered offices to the bank.',
        '1734.1.1','1760.12.31',[
        option('Build an establishment worthy of the public credit.',
            spend(600)+mod('threadneedle_public','The Threadneedle Street Establishment','bfl_bank_operating_expenses_modifier = -0.15',-1,True)+'add_prestige = 10',gate='gold >= 600',weight=45),
        option('Accept the proprietors’ wing and their concessions.',
            '"estate(estate_type:burghers_estate)" = { estate_add_gold = { value = -300 } }'+mod('threadneedle_merchants','The Proprietors’ Wing','bfl_bank_operating_expenses_modifier = -0.10 bfl_base_share_value_modifier = 0.05',-1,True)+mod('city_concessions','Concessions to the City','burghers_estate_max_tax = -0.05',240)+estate('burghers',0.05),gate='"estate(estate_type:burghers_estate)" = { estate_gold >= 400 }'),
        option('Keep the hired halls and the treasury’s coin.',
            mod('hired_halls','Crowded Hired Halls','bfl_bank_operating_expenses_modifier = 0.075',120,True)+opinion('rebuffed'))])

    event('eng',4,'eng_credit_1772','The Bills of June',
        'A broken chain of bills has carried distress from London to Scotland and across the sea. Houses which appeared prosperous cannot obtain the coin to meet tomorrow’s payments. The Bank of England is asked to widen its accommodation, yet its directors insist that a sound commercial bill must be distinguished from the paper of a ruined speculator. Merchants demand relief without humiliating inquiries. The treasury can strengthen the bank instead, or declare that the losses belong to those who incurred them.',
        '1772.1.1','1780.12.31',[
        option('Open a supervised discount office for sound business.',
            spend(200,True)+mod('discount_1772','The Supervised Discount Office','bfl_loan_profitability_modifier = 0.05 bfl_bank_operating_expenses_modifier = 0.15',120,True)+estate('burghers',0.05),
            gate='scope:bfl_event_bank = { bfl_free_cash >= 200 bfl_capital_headroom >= 200 }',ledger='scope:bfl_event_bank = { change_variable = { name = bfl_loss_carryforward add = 200 } }',weight=45),
        option('Put treasury coin behind the Bank’s reserves.',
            spend(300)+'scope:bfl_event_bank = { add_gold = 300 }'+mod('credit_relief_1772','The Treasury’s Credit Relief','tax_income_efficiency = -0.05',60)+mod('reserves_1772','Reserves Reinforced in the Credit Crisis','bfl_base_share_value_modifier = 0.05',60,True),gate='gold >= 300'),
        option('There shall be no public accommodation.',
            mod('credit_contraction_1772','The Contraction of Credit','trade_income = -0.125 tax_income_efficiency = -0.05',60)+estate('burghers',-0.10)+'add_stability = -3')])

    event('flo',1,'flo_buondelmonti','The Buondelmonti Obligation',
        'The Bardi have not forgotten the alliances which first made their house a power in Florence. Their kinsmen invoke the old Buondelmonti cause and ask that the city’s chartered bank stand openly with the friends of the papacy. The Signoria’s officers fear that every account will acquire a factional color. A public bank may strengthen the city’s party, but merchants whose business crosses the old divisions would rather its doors remained open to both sides.',
        '1360.1.1','1480.12.31',[
        option('Honor the Guelph compact.',
            opinion('papal_friend','PAP')+mod('guelph_compact','The Bardi Guelph Compact','diplomatic_reputation = 0.5 clergy_estate_target_satisfaction = 0.05 burghers_estate_max_tax = -0.05')+estate('nobles',0.05)+opinion(),weight=40),
        option('The bank shall serve Florence before any party.',
            mod('civic_neutrality','A Bank Above the Factions','tax_income_efficiency = 0.05 clergy_estate_target_satisfaction = -0.05')+estate('burghers',0.05)+opinion('rebuffed')),
        option('Buy a reconciliation between the houses.',
            spend(100)+'add_stability = 5'+opinion('papal_respect','PAP')+estate('nobles',-0.05),gate='gold >= 100')],gate='var:bfl_bank = { tag = BRD }')

    event('flo',2,'flo_english_factors','Wool, Bills and an English Crown',
        'Our bankers’ factors in England bring two kinds of business before the Signoria. Wool merchants offer a steady commerce of bales, bills and customs receipts. Royal agents offer access to a much greater purse, though the purse is seldom opened promptly. The directors would renew their English house under the protection of our charter. The question is whether its clerks should follow the wool ships, cultivate the court, or leave English promises to another bank.',
        '1360.1.1','1500.12.31',[
        option('Let the factors follow the wool ships.',
            spend(150,True)+mod('english_wool_factors','The English Wool Factors','trade_income = 0.05 global_merchant_capacity_modifier = 0.10 bfl_bank_operating_expenses_modifier = 0.05',180,True)+opinion('trade_friend','ENG'),
            gate='scope:bfl_event_bank = { bfl_free_cash >= 150 bfl_capital_headroom >= 150 }',
            ledger='scope:bfl_event_bank = { change_variable = { name = bfl_loss_carryforward add = 150 } } location:london = { if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office owner = scope:bfl_event_bank building_level > 0 } } } change_building_level_in_location = { building = building_type:banking_office value = 1 owner = scope:bfl_event_bank } } }',
            preview='location:london = { if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office owner = scope:bfl_event_bank building_level > 0 } } } change_building_level_in_location = { building = building_type:banking_office value = 1 owner = scope:bfl_event_bank } } }',weight=45),
        option('Court the crown, and accept the political price.',
            spend(100)+opinion('royal_friend','ENG')+opinion('royal_rival','FRA')+mod('english_court_accounts','The English Court Accounts','bfl_bank_loan_yield_bonus = 0.005 bfl_bank_operating_expenses_modifier = 0.10',180,True),gate='gold >= 100'),
        option('Concentrate our accounts in Italy.',
            mod('italian_concentration','An Italian Concentration','bfl_bank_operating_expenses_modifier = -0.05 global_merchant_capacity_modifier = -0.05',180,True)+opinion('rebuffed','ENG'))],
        gate='var:bfl_bank = { OR = { tag = BRD tag = PRZ } } country_exists = c:ENG location:london = { owner = c:ENG }')

    chapel_art='location:florence = { create_art = { quality = 85 artist = scope:bfl_chapel_artist type = work_of_art_type:painting key = bfl_bardi_chapel_cycle } }'
    altar_art='location:florence = { create_art = { quality = 55 artist = scope:bfl_chapel_artist type = work_of_art_type:painting key = bfl_florentine_altar } }'
    event('flo',3,'flo_bardi_chapel','The Bankers and the Friars',
        'The friars of Santa Croce have approached the Bardi with plans for a painted chapel. The family would have its piety remembered in color and stone, while the Signoria would have the world remember that Florence is more than a city of account books. A great cycle of paintings would honor the bank’s patrons. A humbler altar, paid for in the city’s name, might win more affection beyond the family. The cashiers see only the demands already waiting at their desks.',
        '1360.1.1','1500.12.31',[
        option('Commission a chapel cycle in the Bardi name.',
            spend(250)+chapel_art+'add_prestige = 10'+mod('bardi_patronage','The Splendor of Bardi Patronage','bfl_base_share_value_modifier = 0.05',180,True)+estate('nobles',0.05),gate='gold >= 250 exists = scope:bfl_chapel_artist scope:bfl_chapel_artist = { is_alive = yes }',weight=45),
        option('Give the city an altar, without a family’s triumph.',
            spend(80)+altar_art+'add_prestige = 3'+estate('clergy',0.05)+estate('burghers',0.05),gate='gold >= 80 exists = scope:bfl_chapel_artist scope:bfl_chapel_artist = { is_alive = yes }'),
        option('Keep the money among the bank’s accounts.',
            estate('clergy',-0.10)+mod('ungilded_accounts','Accounts Before Patronage','tax_income_efficiency = 0.025',120))],
        gate='var:bfl_bank = { tag = BRD } any_artist = { artist_type = painter }',
        immediate='random_artist = { limit = { artist_type = painter } save_scope_as = bfl_chapel_artist }')
    loc('bfl_bardi_chapel_cycle','The Bardi Chapel Cycle')
    loc('bfl_bardi_chapel_cycle_desc','A cycle of frescoes for a Franciscan chapel in Florence, commissioned in the Bardi name. Scenes from the life of Saint Francis unfold across painted architecture: the renunciation of worldly possessions, the care of the poor, and the saint’s final blessing. Quiet faces and deliberate gestures give the sacred story the gravity of a witnessed event. The donors kneel below the saints, their costly garments set against the friars’ plain habits. The contrast proclaims both the family’s devotion and the uneasy place of great wealth beside apostolic poverty. Beyond the altar, the Bardi arms preserve the memory of the house which paid for these walls.')
    loc('bfl_florentine_altar','The Altar of the Florentine Commune')
    loc('bfl_florentine_altar_desc','An altarpiece offered in the name of the Florentine commune rather than a single banking dynasty. The Virgin and Child occupy the center, attended by Saint John the Baptist and Saint Francis; below them, small scenes show almsgiving, honest labor and the relief of a household in distress. Restrained gilding catches the chapel light without overwhelming the clear colors and measured figures. The city’s lily appears among the lower ornaments, while no donor family claims the foremost place. Its modest scale invites worship at close quarters, presenting civic charity as a shared obligation rather than a monument to one house’s fortune.')

    event('flo',4,'flo_english_default','The Reckoning of the English Debts',
        'The failures of the great banking houses left more than unpaid English promises behind them. The surviving books contain contested claims, advances against wool and accounts whose owners insist that the city must now protect them. Our charter has reopened the argument: should Florence pay for a public settlement, compel the partners to bear an extraordinary levy, or leave the old claims in the courts? The English crown is only one name in a history of war, withdrawals and broken confidence, but it is the name most often spoken in the chamber.',
        '1360.1.1','1420.12.31',[
        option('Purchase a public settlement of the disputed accounts.',
            spend(250)+mod('florentine_settlement','The Public Settlement of the Old Accounts','trade_income = 0.05 tax_income_efficiency = -0.025')+estate('burghers',0.10)+opinion(),gate='gold >= 250',weight=40),
        option('Levy the banking partners, not the whole city.',
            '"estate(estate_type:burghers_estate)" = { estate_add_gold = { value = -200 } }'+mod('partners_levy','The Levy on the Banking Partners','tax_income_efficiency = 0.025 global_merchant_capacity_modifier = -0.05')+estate('burghers',-0.10)+'add_stability = 3',gate='"estate(estate_type:burghers_estate)" = { estate_gold >= 300 }'),
        option('Let the courts and creditors untangle the losses.',
            mod('old_litigation','The Litigation of the Old Banking Debts','trade_income = -0.075',120)+opinion('rebuffed')+estate('burghers',-0.05))])

    event('gen',1,'gen_imperial_credit','The Emperor’s Account',
        'An imperial envoy has come to San Giorgio with promises of revenues and requests for further credit. The protectors know the advantage of an account which reaches across Europe, and the danger of allowing one great debtor to overshadow the rest. The republic’s merchants would profit from imperial favor. Its diplomats warn that favor at one court is suspicion at another. The bank’s directors must be told whether the republic wants an imperial connection, a wider circle of borrowers, or a smaller book of safer business.',
        '1520.1.1','1558.12.31',[
        option('Bind the imperial account more closely to San Giorgio.',
            opinion('royal_friend','HAB')+opinion('royal_rival','FRA')+mod('imperial_accounts','The Imperial Accounts of San Giorgio','bfl_bank_loan_yield_bonus = 0.005 bfl_bank_operating_expenses_modifier = 0.10',240,True)+estate('burghers',0.05),weight=40),
        option('Send our factors to several courts instead.',
            spend(200,True)+mod('european_factors','San Giorgio’s European Factors','global_merchant_capacity_modifier = 0.15 bfl_bank_operating_expenses_modifier = 0.05',240,True)+'add_prestige = 5',gate='scope:bfl_event_bank = { bfl_free_cash >= 200 bfl_capital_headroom >= 200 }',ledger='scope:bfl_event_bank = { change_variable = { name = bfl_loss_carryforward add = 200 } }'),
        option('The republic’s accounts must come first.',
            mod('republic_first','The Republic Before Foreign Crowns','tax_income_efficiency = 0.05 diplomatic_reputation = -0.5',240)+opinion('rebuffed','HAB')+opinion('rebuffed'))],gate='var:bfl_bank = { tag = SAGEO } country_exists = c:HAB')

    event('gen',2,'gen_grimaldi_albergo','The Grimaldi Albergo',
        'The Grimaldi propose to bind their scattered family interests within an albergo. Common articles, common responsibilities and a common name would give their bank a permanence which no single household can promise. The family asks that its own elders govern the compact. Civic notaries offer another arrangement, placing the books under public supervision. Either settlement would strengthen the house; the question is who would acquire the keys to its affairs.',
        '1400.1.1','1650.12.31',[
        option('Recognize the albergo and the authority of its elders.',
            'scope:bfl_event_bank = { add_reform = government_reform:bfl_grimaldi_albergo }'+mod('grimaldi_concessions','The Grimaldi Family Concessions','burghers_estate_max_tax = -0.075 nobles_estate_target_satisfaction = 0.05',240),
            ledger='scope:bfl_event_bank = { set_variable = bfl_albergo_authorized }',weight=45),
        option('Let civic notaries draw up a supervised compact.',
            spend(200)+mod('notarial_albergo','The Notarial Compact','bfl_bank_operating_expenses_modifier = -0.05',240,True)+mod('civic_notaries','The Republic’s Notaries','tax_income_efficiency = 0.025',240)+opinion('rebuffed'),gate='gold >= 200'),
        option('No family shall make a state within the republic.',
            estate('nobles',-0.10)+estate('burghers',0.05)+opinion('rebuffed')+'add_stability = -3')],gate='var:bfl_bank = { tag = GRIML NOT = { has_reform = government_reform:bfl_grimaldi_albergo } }')

    event('gen',3,'gen_spinola_captains','The Captains’ Precedent',
        'The Spinola bankers have brought an old precedent into the council chamber. Galeotto Spinola and Raffaele Doria once held the captaincy together, ending the ascendancy of the king of Naples in Genoa. Their descendants argue that the men who sustain the republic’s credit should again have a settled place in its government. Some favor a banker’s captaincy, others a balance between rival houses. The magistrates would prefer that lenders remained outside the offices which must judge their claims.',
        '1400.1.1','1650.12.31',[
        option('Give the bankers a settled voice in the captaincy.',
            mod('banker_captains','The Banker Captains','tax_income_efficiency = 0.075 diplomatic_reputation = -0.5 nobles_estate_target_satisfaction = 0.05',240)+estate('burghers',-0.05)+opinion(),weight=35),
        option('Balance the houses beneath a shared magistracy.',
            spend(150)+mod('balanced_captains','The Balanced Magistracy','trade_income = 0.05 tax_income_efficiency = -0.025',240)+estate('nobles',-0.05)+'add_stability = 3',gate='gold >= 150'),
        option('The republic’s officers shall not be its bankers.',
            'add_stability = 5'+opinion('rebuffed')+mod('separate_offices','Separate Public and Banking Offices','bfl_bank_operating_expenses_modifier = 0.05',180,True))],gate='var:bfl_bank = { tag = SPINL }')

    giro_options=[
        option('Make the Giro a permanent institution of the republic.',
            spend(200)+mod('permanent_giro','The Permanent Banco del Giro','bfl_bank_operating_expenses_modifier = -0.10',-1,True)+mod('giro_senate','The Senate’s Permanent Banking Charge','tax_income_efficiency = -0.025',240),gate='gold >= 200',ledger='set_variable = bfl_giro_permanent',weight=50),
        option('Renew it for one year, at the Senate’s pleasure.',
            spend(50)+mod('annual_giro','An Annual Mandate for the Giro','bfl_bank_operating_expenses_modifier = -0.025',12,True)+estate('burghers',-0.025),gate='gold >= 50',
            ledger='set_variable = { name = bfl_giro_review_due value = { value = bfl_period add = 12 } }'),
        option('End the experiment; service the existing accounts.',
            estate('burghers',-0.10)+opinion('rebuffed')+mod('giro_winddown','The Winding Down of the Giro','trade_income = -0.05',120),
            ledger='scope:bfl_event_bank = { set_variable = bfl_giro_closing set_variable = { name = bfl_accept_deposits value = 0 } }')]
    event('ven',1,'ven_three_years','The Giro’s Three Years',
        'The Banco del Giro was meant to be an expedient: three years to order the republic’s transferable obligations, and then its business would be wound down. The deadline has arrived, but the merchants’ books contain more transfers than ever. The Senate must choose between an enduring public institution, another short mandate, and an orderly end to new business. Each delay makes the temporary bank harder to dismiss; each permanent obligation binds the republic more closely to its creditors.',
        '1619.1.1','1700.12.31',giro_options,
        gate='has_variable = bfl_giro_first_period bfl_period >= bfl_giro_initial_review NOT = { has_variable = bfl_giro_permanent }')
    # Scripted anniversary, not another random historical founding. The same
    # three political alternatives remain real at every annual review.
    event('ven',4,'ven_three_years','Another Year for the Giro',
        'Another annual mandate has run its course. The Giro’s clerks are again asking the Senate whether they should prepare new books or begin closing the old ones. Merchants who once welcomed a temporary expedient now treat its transfers as part of ordinary commerce. Renewing the mandate preserves the Senate’s discretion, but requires another appropriation. Permanence would settle the question; closing new business would leave the republic to meet the consequences.',
        None,None,giro_options,gate='has_variable = bfl_giro_review_due bfl_period >= var:bfl_giro_review_due NOT = { has_variable = bfl_giro_permanent }')

    event('ven',2,'ven_war_plague','The Books of War and Pestilence',
        'The Giro’s books have become a meeting place for the republic’s emergencies. Victuallers present military accounts while the officers of public health seek payment for their own charges. To honor every demand promptly would burden the treasury; to favor the galleys would leave civilian commerce waiting. Some senators would throw the work upon parishes and neighborhoods, sparing the public purse at the expense of those already carrying the heaviest burdens.',
        '1628.1.1','1640.12.31',[
        option('Pay for relief, and keep the public accounts moving.',
            spend(250)+mod('plague_accounts','The Giro’s Relief Accounts','bfl_bank_operating_expenses_modifier = 0.10',60,True)+mod('venetian_relief','The Republic’s Relief Appropriations','trade_income = 0.05 tax_income_efficiency = -0.05',60)+estate('peasants',0.10),gate='gold >= 250',weight=45),
        option('Give the military accounts priority.',
            mod('military_giro','Priority for the Military Accounts','tax_income_efficiency = 0.05 trade_income = -0.10',60)+mod('war_accounts','The Giro’s Military Registers','bfl_bank_operating_expenses_modifier = 0.05',60,True)+'add_war_exhaustion = -2'+estate('burghers',-0.05),gate='at_war = yes'),
        option('Let the parishes and neighborhoods carry the relief.',
            estate('clergy',-0.10)+estate('peasants',-0.10)+mod('parish_burden','The Burden on the Venetian Parishes','tax_income_efficiency = 0.025 trade_income = -0.05',60))])

    event('ven',3,'ven_convertibility','Silver for the Giro’s Money',
        'The merchants no longer want a good entry in a public book to be the end of the matter. They ask for a regular window at which balances can be met in silver, and warn that the reputation of the Giro depends upon the answer. The senators can pay for a well-funded specie facility, require the bank to prepare a narrower window from its own resources, or favor the cheaper machinery of transfers. A promise of ready coin will require coin in the vaults and clerks at the counter.',
        '1666.1.1','1680.12.31',[
        option('Fund a public specie window with treasury reserves.',
            spend(200)+'scope:bfl_event_bank = { add_gold = 200 }'+mod('giro_specie','The Giro’s Public Specie Window','bfl_base_share_value_modifier = 0.075 bfl_bank_operating_expenses_modifier = 0.10',240,True)+estate('burghers',0.10),gate='gold >= 200',weight=45),
        option('Let the bank prepare a narrower window at its own cost.',
            spend(100,True)+mod('giro_measured_specie','The Measured Specie Window','bfl_base_share_value_modifier = 0.025 bfl_bank_operating_expenses_modifier = 0.05',180,True)+estate('burghers',0.025),
            gate='scope:bfl_event_bank = { bfl_free_cash >= 100 bfl_capital_headroom >= 100 }',ledger='scope:bfl_event_bank = { change_variable = { name = bfl_loss_carryforward add = 100 } }'),
        option('Preserve the cheaper public transfer office.',
            mod('giro_transfer_office','The Public Transfer Office','bfl_bank_operating_expenses_modifier = -0.05 bfl_base_share_value_modifier = -0.05',180,True)+estate('burghers',-0.10))])

    common('government_reforms','grimaldi_albergo','''bfl_grimaldi_albergo = {
        major = no potential = { tag = GRIML bfl_is_bank = yes }
        allow = { has_variable = bfl_albergo_authorized }
        country_modifier = { bfl_bank_operating_expenses_modifier = -0.10
            bfl_base_share_value_modifier = 0.05 global_merchant_capacity_modifier = 0.05 }
    }''')
    loc('bfl_grimaldi_albergo','The Grimaldi Albergo')
    loc('bfl_grimaldi_albergo_desc','Common articles bind the Grimaldi households into a continuing corporation. Family elders govern its shared obligations and preserve its credit beyond the fortunes of any one branch.')
    # South Sea consequences belong to the two original native options.
    # Build the modifier definitions here, but do not register a competing DHE.
    mod('bubble_contagion','The Bank and the Failed Subscriptions','bfl_base_share_value_modifier = -0.05',60,True)
    mod('bubble_restructuring','The South Sea Restructuring Accounts','bfl_bank_operating_expenses_modifier = 0.10 bfl_base_share_value_modifier = 0.05',60,True)
    mod('public_bubble_relief','The Public Cost of the South Sea Rescue','tax_income_efficiency = -0.05',60)
    mod('south_sea_failures','Failures in Exchange Alley','trade_income = -0.10 tax_income_efficiency = -0.025',60)
    write('main_menu/common/static_modifiers/bfl_historical_bank_events.txt','\n'.join(effect(k,v) for k,v in modifiers.items()))
    common('biases','historical_bank_events','''
        bfl_dhe_favored = { value = 20 yearly_decay = 2 }
        bfl_dhe_rebuffed = { value = -20 yearly_decay = 2 }
        bfl_dhe_papal_friend = { value = 40 yearly_decay = 2 }
        bfl_dhe_papal_respect = { value = 10 yearly_decay = 1 }
        bfl_dhe_trade_friend = { value = 20 yearly_decay = 2 }
        bfl_dhe_royal_friend = { value = 40 yearly_decay = 2 }
        bfl_dhe_royal_rival = { value = -25 yearly_decay = 2 }
    ''')
    for k,v in {'favored':'Supported the Bank’s Position','rebuffed':'Rejected the Bank’s Position','papal_friend':'Honored the Guelph Compact','papal_respect':'Reconciled the Florentine Houses','trade_friend':'Welcomed the English Factors','royal_friend':'Cultivated the Crown’s Account','royal_rival':'Favored a Rival Crown'}.items():
        loc('bfl_dhe_'+k,v)
    common('script_values','historical_bank_events',effect('bfl_giro_initial_review','value = var:bfl_giro_first_period add = 36'))
    common('scripted_triggers','historical_bank_events',effect('bfl_dhe_can_issue_annuity','''
        bfl_dhe_context = yes bfl_can_draw_custom_bond = yes
        monthly_income_total >= { value = bfl_bond_monthly_coupon add = 0.41667 multiply = 4 }
    '''))
    common('scripted_effects','historical_bank_events',effect('bfl_dhe_issue_annuity','''
        if = { limit = { bfl_dhe_can_issue_annuity = yes }
            bfl_initialize_bonds = yes
            set_variable = { name = bfl_dhe_old_bond_rate value = var:bfl_bond_rate }
            set_variable = { name = bfl_bond_rate value = 0.05 }
            scope:bfl_event_bank = { set_variable = { name = bfl_bond_amount value = 100 }
                bfl_underwrite_sovereign_bond = yes }
            set_variable = { name = bfl_bond_rate value = var:bfl_dhe_old_bond_rate }
            remove_variable = bfl_dhe_old_bond_rate
        }
    '''))
    loc('bfl_dhe_annuity_tt','Create a funded government bond of 100@gold! held by the Bank, paying a fixed 5% annual coupon. Existing bonds retain their rates.')
    common('on_action','giro_anniversaries','''monthly_country_pulse = { on_actions = { bfl_giro_anniversary } }
        bfl_giro_anniversary = { effect = { if = { limit = { bfl_dhe_ven = yes }
            if = { limit = { NOT = { has_variable = bfl_giro_first_period } }
                set_variable = { name = bfl_giro_first_period value = bfl_period } }
            if = { limit = { has_variable = bfl_giro_review_due bfl_period >= var:bfl_giro_review_due
                NOT = { has_variable = bfl_giro_permanent } NOT = { has_variable = bfl_dhe_open } }
                trigger_event_non_silently = bfl_bank_ven.4 }
        } } }
    ''')

    files=defaultdict(list)
    for row in events:
        ns='bfl_bank_'+row['country'];eid=f'{ns}.{row["id"]}'
        for suffix,value in [('title',row['title']),('desc',row['desc']),('entry',row['title'])]:loc(eid+'.'+suffix,value)
        tags=['ENG','GBR'] if row['country']=='eng' else [row['country'].upper()]
        dhe='' if row['start'] is None else ('fire_only_once = yes dynamic_historical_event = { '
            +' '.join('tag = '+tag for tag in tags)+f' from = {row["start"]} to = {row["end"]} monthly_chance = 5 }}')
        body=f'''{eid} = {{ type = country_event title = {eid}.title desc = {eid}.desc
            image = "gfx/interface/illustrations/bfl/events/{row['key']}.dds" outcome = neutral
            {dhe}
            trigger = {{ bfl_dhe_{row['country']} = yes NOT = {{ has_variable = bfl_dhe_open }} {row['gate']} }}
            immediate = {{ bfl_dhe_begin = yes {row['immediate']} }}
        '''
        for index,opt in enumerate(row['options']):
            key=eid+'.'+chr(97+index);loc(key,opt['label'])
            # Native preview shows actual icons, durations, linked modifiers,
            # estate satisfaction, art creation, reforms and scoped payments.
            # Execution repeats the same gates to protect an event left open.
            gate='bfl_dhe_context = yes '+opt['gate']
            body+=f'''option = {{ name = {key} ai_chance = {{ base = {opt['weight']} }}
                trigger = {{ {gate} }}
                show_as_tooltip = {{ {opt['effects']} {opt['preview']} }}
                hidden_effect = {{ if = {{ limit = {{ {gate} }}
                    {opt['ledger']} {opt['effects']}
                    remove_variable = bfl_dhe_open
                }} }}
            }}'''
        body+='''option = { name = bfl_dhe_stale ai_chance = { base = 100 }
            trigger = { NOT = { bfl_dhe_context = yes } }
            hidden_effect = { remove_variable = bfl_dhe_open } }
        }'''
        files[ns].append(body)
    for ns,blocks in files.items():write(f'in_game/events/DHE/{ns}.txt','namespace = '+ns+'\n'+'\n'.join(blocks))
