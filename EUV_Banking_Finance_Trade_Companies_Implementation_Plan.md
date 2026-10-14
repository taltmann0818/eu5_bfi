# Europa Universalis V: Banking, Finance and Trade Companies
## Implementation plan

**Prepared:** 13 October 2026  
**Revised:** 13 October 2026 — monthly royalties and activity dividends, native government-bond funding and resale, and two exclusive bank specializations.  
**Working mod name:** Banking, Finance and Trade Companies  
**Namespace:** bfl_  
**Deliverable:** A development specification, not an executable or campaign-tested mod.  
**Compatibility target:** One explicitly selected, installed EUV patch. Freeze that patch during the first implementation cycle.

**Navigation:** [Scope](#1-objective-and-agreed-scope) · [Evidence](#2-evidence-authority-and-patch-discipline) · [Mod layout](#3-euv-modding-conventions-and-project-layout) · [Native bridges](#4-native-bridges-and-role-separation) · [Accounting](#5-financial-records-and-accounting) · [Feature specifications](#6-implementation-specifications) · [Trade companies](#7-native-trade-company-implementation) · [UI and AI](#8-ui-interactions-and-ai) · [Milestones](#9-development-milestones) · [Tests](#10-validation-plan) · [Persistence](#11-processing-order-persistence-and-cleanup) · [Balance](#12-balancing-and-exploit-controls) · [Compatibility](#13-compatibility-and-release-requirements) · [Completion criteria](#14-definition-of-done) · [Sources](#15-source-register).


## 1. Objective and agreed scope

Build a financial playstyle for independent building-based banking nations and playable landed countries that charter an existing native State Bank subject. Integrate EUV's native trade companies as operating businesses that employ capital in trade, infrastructure, commodity inventories, exploration and commercial ventures.

The Chartered Bank is a separate native country subject with its own treasury, portfolio, deposits and liabilities. The landed overlord remains the playable country and receives the State Chartered Bank government reform and direct GUI management access. The charter is established through a decision, not by freely adopting a banking reform. A country may have at most ONE Chartered Bank.

Each bank chooses exactly one specialization through an event: Merchant Finance or Overseas Investment. Sovereign loan origination, native sovereign-loan purchasing and government-bond underwriting/resale are shared functions of both profiles. Merchant Finance adds commercial credit and commodity instruments; Overseas Investment adds commenda and company equity. Advanced instruments still require their advances and earliest ages.

The landed sovereign receives treasury cash through three explicit channels: a scalable monthly charter royalty, monthly dividends attributed to the bank's actual activities, and recurring low-interest financing through native government bonds funded by the bank where cash is available. The government owes interest and redemption on these bonds. The design makes debt the principal funding stream in the bank-led treasury playstyle; taxation and trade remain part of the fiscal base supporting debt service.

Ordinary eligible loan purchases retain the native regular-bank mechanism. Native bonds and already bank-held claims need a separate, narrowly scoped creditor-transfer bridge because the inspected native takeover action excludes them. Resale pays the existing holder, preserves the same native debt and releases bank liquidity; it does not pay the sovereign another issuance amount. Section 6.17 specifies the three treasury channels and their accounting.

### Final feature matrix

| Feature | Independent banking nations | Landed countries through their Chartered Bank subject |
| --- | --- | --- |
| Establishment and management | Newly created or initialized banks receive the specialization event; the bank-country player uses its own financial GUI. | A decision converts an existing native state_bank subject, transfers age-scaled investment, grants State Chartered Bank and opens the same GUI in authorized subject-management mode. |
| Capital and reserves | Track actual bank cash, assets, liabilities and shareholder equity. | Track these on the subject; initial sovereign investment is bank equity. Royalties and dividends reduce bank cash; bond underwriting exchanges cash for a sovereign credit asset. |
| Monthly charter royalty | An independent bank pays a comparable host fee only under an explicit host agreement; it has no automatic charter-sovereign levy. | Adjustable asset-based fee is transferred monthly from bank to sovereign; higher tiers reduce sovereign burgher satisfaction and subject loyalty, and can erode bank equity. |
| Monthly activity dividends | Pay shareholders from realized net activity earnings with cash and capital limits. | The sovereign receives its ownership-based share, itemized by sovereign credit/bonds and profile-permitted investments; no payout is created from principal or new funding. |
| Recurring sovereign bond facility | Both profiles can underwrite eligible external governments' native bonds using their own funds. | Both profiles fund the controller's recurring low-interest native government-bond issuance where liquid; the sovereign pays coupons and ultimately redeems principal. |
| Bond and bank-held debt resale | Trade the existing native bond/loan with payment to its current holder and native creditor transfer; retain instrument eligibility. | The subject can resell the controller's bonds to eligible banks, replenish liquidity and continue permitted funding; later coupons follow the new holder. |
| Demand and term deposits | Common banking functions; term-deposit expansion requires its advance. | Deposits are liabilities of the subject, serviced from its own treasury. Public guarantees require authorization and the relevant advance. |
| Foreign branches | Common servicing infrastructure subject to host permissions; branch instruments follow the bank's specialization and advances. | Subject-owned branches support the same functions; the overlord manages them through the GUI and negotiated permissions. |
| Sovereign lending | Shared by Merchant Finance and Overseas Investment; use native sovereign loans and audited rates. | Both profiles lend to sovereigns. Recurring financing of the bank's own landed controller uses native government bonds through the facility. |
| Native loan purchasing | Both profiles use regular banks' native takeover operation for eligible sovereign claims, retaining native filters, cost and estate compensation. Merchant company purchases additionally require Reformation Corporate Credit. | The GUI invokes takeover with the subject as buyer; the overlord pays no duplicate cost. |
| Debt restructuring | Both profiles restructure eligible sovereign debt from Renaissance after research; Merchant Finance also restructures eligible company debt after Reformation Corporate Credit. | Identical research and instrument gates apply to subject-owned native loans and bonds; tested bond-term support is required. |
| Creditor concessions and collateral | Contractual access concessions follow eligible lending; secured claims and revenue pledges require Absolutism collateralization. | The subject negotiates financial concessions; the overlord authorizes sovereign commitments and enforcement. |
| Commodity investments | Merchant Finance; native-goods positions require Discovery and the Commodity Investments advance. | The subject owns funded inventories; strategic procurement involving the bank follows the same permissions. |
| Commodity instruments | Merchant Finance; backed receipts and collateralized forwards require Absolutism and their advances; complex margining is later. | The same instrument restrictions apply, including custody and public-guarantee rules. |
| Bank shares | Founder ownership is recorded at creation; subscriptions and tradable equity unlock progressively for all profiles. | The initial investment adds or increases the state's bank equity; monetary authority remains with the authorized sovereign. |
| Commenda | Overseas Investment; project finance unlocks in Discovery through the Commenda advance. | The subject funds eligible operators under identical gates; native trade companies become operators when their own unlocks exist. |
| Currency and banknotes | Common servicing and legally permitted bills; advanced issuance follows dedicated research and host authorization. | The subject implements the sovereign's monetary mandate; advanced banknotes require their later-age advance. |
| Interest-rate policy | Set rates for the bank's permitted products; a rate setting cannot unlock a prohibited instrument. | The player sets subject rates and monetary policy in the GUI under State Chartered Bank, subject to research and operating limits. |
| Interbank liquidity | Common limited settlement liquidity; secured facilities require Absolutism collateralization and relevant research. | Advanced public liquidity facilities use the subject's treasury or explicitly authorized issuance, not the overlord's cash automatically. |
| Financial crises | Common deposit, liquidity and capital-resolution framework; instrument risks activate only when those instruments unlock. | Subject losses can call authorized guarantees or recapitalization; public costs are separate transfers. |
| Specialization and progression | Exactly one event-selected profile: Merchant Finance or Overseas Investment. Sovereign finance is common infrastructure. | The overlord chooses one of the same two profiles for its subject; the treasury channels work with either. |
| Native trade companies | Operating companies remain native subjects; banking services depend on profile and age. | The political overlord manages companies; the Chartered Bank finances them only through its permitted instruments. |
| Company equity and debt | Overseas Investment provides company equity; Merchant Finance provides corporate credit/debt from Reformation. | The subject has the same split. The overlord's ordinary company ownership does not grant the bank another profile. |
| Company operations and profits | Finance real operations; distributions reflect actual cash and permitted investments. | Native political control and bank financial ownership remain separate; bank receipts enter the subject treasury. |
| Company distress and contagion | Service existing obligations and resolve losses under the shared crisis system. | Subject losses, company liabilities and sovereign guarantees are reconciled separately. |

Fixed requirements include the existing charter decision architecture, one-bank limit, named reform and GUI; native loan purchasing; the three treasury channels and government-bond resale; sovereign lending in both exclusive profiles; and the specified earliest-age advances. Cost coefficients, royalty tiers, payout ratios, facility targets, reform bonus magnitudes and additional later-age instruments are proposed tuning defaults.

## 2. Evidence, authority and patch discipline

### 2.1 Source hierarchy

Use this authority order when implementing:

1. The installed patch's native scripts, .info schemas, generated scripting documentation and GUI data types.
2. The publisher's modding overview and EUV's official-hosted modding wiki.
3. Published copies of native definitions and engine-generated documentation.
4. Community templates and working mods as examples to inspect and test.

The public script-documentation mirror was read for effects, triggers, scopes, scope links, callbacks and GUI data functions. Published native trade-company definitions were also inspected. The official wiki's indexed metadata and debug-documentation guidance was available, but full page requests were blocked during preparation. The publisher's modding overview is linked as a canonical reference; its full text was not accessible. Those access limits are why this plan requires a local exact-patch audit rather than presenting every example as verified executable syntax. See the source register in section 15.

The public current_docs directory is mutable. Its presence does not establish the user's installed patch, and older community annotations describe earlier versions. The inspected 1.3.10 documentation change log records sell_bonds, redeem_bonds and related bond fields as additions: they cannot be assumed present on older patches. Pin a patch exposing the required native bond APIs and record source hashes and generated documentation before coding. [S1–S8, S23]

### 2.2 Capability labels

- **Documented native hook:** The published engine documentation or native definition contains the named mechanism. This does not prove a proposed combination works in-game.
- **Scripted addition:** A new ledger, rule, interaction or UI that the mod must implement.
- **Patch gate:** A behavior or API detail that must be demonstrated on the target patch before the dependent implementation is finalized.


### 2.3 Mandatory feasibility probes

| Probe | What must be established | Implementation response |
| --- | --- | --- |
| Charter decision | The patch's decision/own-country action loader, native state_bank eligibility, capital-market ownership test and subject selector. | Use the patch's native decision surface; do not invent an EU4-style decisions directory. |
| In-place conversion | change_subject_type preserves the bank tag, headquarters, assets, native loans and liabilities when converting state_bank to bfl_chartered_bank. | Compare pre/post identity and balances; keep this conversion as the charter architecture. |
| Investment and reform | The age-based cost transfers exactly once to bank cash/equity; State Chartered Bank is added to the overlord. | Use a single payment authority and guarded initialization; do not charge both a decision price and a second debit. |
| One-bank cap | Decision and lifecycle checks can enforce at most one direct Chartered Bank subject. | Resolve inherited duplicates by restoring additional banks to state_bank servicing status without deleting their obligations. |
| GUI authority | A landed-country player can operate an authorized subject's accounts through scripted GUI effects. | Bind controller and bank explicitly; validate both at execution. GUI management is a required feature, not a diplomatic-only fallback. |
| Native loan purchasing | Regular-bank eligibility, native purchase price, estate compensation and subject actor binding. | Keep the native takeover path unchanged economically; distinguish it from bond/bank-held resale. |
| Native government-bond funding | sell_bonds/redeem_bonds availability, native permission/capacity, lot size, creation identity, proceeds source, bond rate/time basis and coupon/redemption payee. | Demonstrate a bank-funded native bond with one sovereign credit, one bank debit and a persistent native bond; no ordinary-loan substitute. |
| Native bond/debt resale | Native owner transfer accepts bonds; existing-holder settlement and later coupons/redemption follow the transferred creditor. | Prefer a native resale dispatch; otherwise prove a minimal native-object transfer adapter. Hard-coded coupon routing must be resolved before the feature is release-ready. |
| Treasury payouts and loyalty | Royalty cash transfer, per-activity realized profits, bank reserve protection, burgher target satisfaction, subject loyalty and native budget display. | Replace fixed subject extraction with the three channels; transfer cash once, refresh tier modifiers without stacking, and reconcile displayed income with actual payments. |
| Bond-rate policy | Whether bond_interest changes outstanding coupons, only new issues, or both; whether change_loan_interest supports bonds. | Match verified native behavior and disclose rate repricing; retain a low positive coupon with funding/risk limits. |
| Native cash movements | Treasury changes on origination, purchasing, interest, repayment, renewal, default and subject payments. | Correct the accounting adapter before enabling the affected operation. |
| Rates and debt values | Interest units, repayment schedule, early-repayment rules and principal/remaining-debt distinction. | Follow native conventions, not guessed conversions. |
| Specialization and research | One immutable profile, bank/overlord advance ownership, action gating and later-age availability. | Use a shared permission service and explicit synchronization of permitted advances. |
| Records and prices | Variable-map persistence, goods price/stockpile accessors and supported scope keys. | Generate bounded contract slots or supported-good cases where required. |
| Company creation and cash flow | Correct native company assignment, prerequisites and company versus direct-overlord receipts. | Register native entities and distribute only verified available earnings. |
| Lifecycle callbacks | Loan, bankruptcy, exploration, annexation and overlord-change targets/timing. | Add bounded reconciliation when a callback cannot identify the required actors. |

These probes are milestone M0 and are implementation work, not requests for further user approval.

## 3. EUV modding conventions and project layout

### 3.1 Registration and load stages

Create the mod through the current launcher or a current EUV template. Keep .metadata/metadata.json at the mod root. Mirror the game's load-stage directories instead of importing EU4's descriptor and history layout. The template's game_id is eu5; replace its sample compatibility version with the version actually tested. [S2, S3, S12]

Schematic metadata:

~~~json
{
  "name": "Banking, Finance and Trade Companies",
  "id": "bfl_banking_finance_companies",
  "version": "0.1.0",
  "game_id": "eu5",
  "supported_game_version": "<tested patch>",
  "short_description": "Banking nations, chartered State Bank subjects and native trade-company finance.",
  "tags": ["Trade and Economics", "Government and Estates", "Gameplay"],
  "relationships": [],
  "game_custom_data": {}
}
~~~

Replace the compatibility placeholder before loading or publishing. Use the current metadata schema for dependencies and optional thumbnails. Keep documentation and development tooling outside game-loaded definition folders.

### 3.2 Encoding, identifiers and overriding

- Use the current EUV template's UTF-8 BOM convention for .txt, .yml and .gui game files. Use normal UTF-8 for this Markdown and development scripts. Preserve the installed files' line-ending conventions. [S12]
- Prefix every new gameplay identifier, variable, script value, modifier, GUI widget and localization key with bfl_. Use a separate event namespace such as bfl_finance.
- Declare new objects under new keys. For existing database objects, use the entry mode supported by that definition type on the installed patch.
- Prefer a narrowly tested injection for genuinely additive changes. Repeated scalar values and nested blocks do not necessarily merge in the intended way.
- When a full definition must change, use a deliberate replacement and preserve all required native fields. REPLACE: and REPLACE_OR_CREATE: are modes to evaluate against the local schema; they are not blanket instructions to prefix every file.
- Use a strict replacement when an expected native key must exist, so an upstream rename produces a visible failure. Reserve replace-or-create behavior for an intentional compatibility fallback.
- Extend native on_actions through an appended child hook. Keep financial sequencing in one mod-owned effect; do not assume separately fired events execute in a useful accounting order.
- Keep every override in an explicit manifest with the original key, patch, reason, changed fields and compatibility risk.
- Change installed game files only in a throwaway diagnostic copy. Ship modifications entirely in the mod directory.

### 3.3 Proposed file map

These paths are a planned layout. Confirm each loader and schema on the selected patch before creating executable definitions.

| Planned path | Responsibility |
| --- | --- |
| .metadata/metadata.json | Registration and supported version. |
| in_game/common/government_reforms/bfl_charters.txt | State Chartered Bank reform on the landed overlord; profile presentation on banks if needed. |
| in_game/common/subject_types/bfl_chartered_bank.txt | New Chartered Bank subject type, based on audited State Bank relationship rules. |
| in_game/common/generic_actions/bfl_charter_decision.txt | Establish a State Chartered Bank decision if this is the patch's decision loader; use the actual decisions loader if different. |
| in_game/common/advances/bfl_financial_advances.txt | Age-specific, profile-gated financial research tree. |
| in_game/common/laws/bfl_banking_laws.txt | Royalty/payout/facility policy, note authorization, reserve regime, guarantees and company mandates. |
| in_game/common/scripted_triggers/bfl_eligibility.txt | Institution/controller roles, decision prerequisites, profile checks and advance gates. |
| in_game/common/scripted_effects/bfl_chartering.txt | Investment transfer, subject conversion, reform grant and one-bank/lifecycle reconciliation. |
| in_game/common/scripted_effects/bfl_accounts.txt | Subject/independent-bank funding, deposits, transfers, reconciliation and payouts. |
| in_game/common/scripted_effects/bfl_credit.txt | Native lending/takeover and existing-holder resale, gated refinancing and later collateral. |
| in_game/common/scripted_effects/bfl_sovereign_treasury.txt | Monthly royalties, attributed dividends, recurring native bond underwriting, coupon reconciliation and redemption. |
| in_game/common/scripted_effects/bfl_companies.txt | Native company registration, management and distributions. |
| in_game/common/scripted_effects/bfl_commodities.txt | Goods purchases, sales, custody and instrument settlement. |
| in_game/common/scripted_effects/bfl_ventures.txt | Commenda lifecycle and settlement. |
| in_game/common/scripted_effects/bfl_resolution.txt | Crisis and lifecycle cleanup. |
| in_game/common/script_values/bfl_values.txt | Rates, risk, prices, limits and policy calculations. |
| in_game/common/country_interactions/bfl_finance.txt | Deposits, offers, market trades and company management. |
| in_game/common/building_types/bfl_branches.txt | Additional bank offices and warehouse support. |
| in_game/common/on_action/bfl_hooks.txt | Minimal native-hook extensions and mod-owned processing. |
| in_game/events/bfl_finance_events.txt | Offers, disputes, ventures, runs and resolution choices. |
| in_game/events/bfl_specialization_events.txt | One-time Merchant Finance / Overseas Investment selection and versioned legacy-choice migration. |
| in_game/common/scripted_guis/bfl_finance_gui.txt | Validated interactive GUI effects and gates. |
| in_game/gui/bfl_finance_window.gui | Financial and company management windows. |
| main_menu/localization/english/bfl_l_english.yml | Player-facing text, tooltips and notifications. |
| main_menu/common/static_modifiers/bfl_modifiers.txt | Named modifier definitions if required by the target schema. |
| tools/ | Offline generators, static checks and accounting-model tests. |
| docs/ | Capability audit, schema, override manifest and changelog. |

The exact schema determines whether a particular shared definition belongs at another load stage. In particular, verify modifier definitions and scripted GUI loading rather than assuming that another Paradox title's folders apply.

### 3.4 Initial source inspection

Run these commands from the installed game's game directory. They are read-only discovery commands:

~~~bash
rg -n "state_bank|banking_country|banking_office|trade_company_headquarters|trade_company_home_region|trade_company_subjects" in_game main_menu
rg -n "change_subject_type|give_loan|change_loan_owner|take_over_loan|request_loan|sell_bonds|redeem_bonds|is_bond|bond_interest|can_sell_bonds|subject_pays_trade_company" in_game main_menu
rg -n "monthly_country_pulse|on_loan_repaid|on_loan_taken|on_loan_renewed|on_bankruptcy|on_exploration_success|on_annexed" in_game main_menu
rg --files in_game main_menu loading_screen -g "*.info" -g "*readme*" -g "*scripted_gui*" -g "*metadata*"
~~~

Enable the documented debug mode, generate script_docs, and retain the resulting documentation and logs. Confirm output locations on the installed platform. Read .info files alongside real native examples; a token listed in documentation can still have constraints absent from its summary. [S2]

## 4. Native bridges and role separation

### 4.1 Documented native mechanisms

| Mechanism | Planned use |
| --- | --- |
| give_loan; change_loan_owner | Ordinary loan origination and audited creditor transfer; prove bond applicability. |
| sell_bonds; redeem_bonds | Native government-bond issuance and face-value redemption; ascertain funding source and current creditor payments. |
| bond_capacity; current_bonds; num_bonds; is_bond | Native issuance limits, outstanding debt/count and identification of actual government bonds. |
| bond_interest; can_sell_bonds; max_bonds; max_bonds_modifier | Native bond coupon/authorization/capacity fields; exact units and lifecycle are patch gates. |
| burghers_estate_target_satisfaction; subject_loyalty | Native modifier fields for current royalty-tier loyalty consequences; replace the active tier instead of stacking monthly penalties. |
| change_loan_interest; change_loan_amount | Negotiated debt changes. |
| every_lent_loan; every_loan | Portfolio reconciliation. |
| buy_goods_from_market; sell_goods_to_market | Physical commodity transactions. |
| estate_add_gold; estate_gold | Estate-level funding and payments. |
| create_trade; change_assigned_merchant_capacity | Company trading operations. |
| change_building_owner | Explicit facility ownership changes. |
| start_exploration | Eligible operator's expedition. |
| add_inflation | Monetary consequences. |
| market_price; stockpile_in_market | Market-linked pricing and inventory checks. |
| on_loan_taken; on_loan_repaid; on_loan_renewed | Credit lifecycle callbacks. |
| on_bankruptcy; on_exploration_success; on_annexed | Distress, venture and cleanup callbacks. |

Sources: engine-generated documentation, scope links and modifier definitions. Scope/signature checks, bond applicability and rate units remain M0 obligations. [S4–S8, S23, S24]

Use native lending and goods effects as authoritative cash-flow mechanisms. Do not surround them with additional gold debits or credits until testing establishes what the native effect already does. The goods-sale effect's documented capital-location requirement is an explicit test for building-based banks and companies.


### 4.2 Chartered Bank architecture and role separation

The native state_bank subject type is the prerequisite. Create bfl_chartered_bank with the display name Chartered Bank, preserving the audited building-based relationship and the existing bank country tag. Convert that subject in place using change_subject_type; do not annex/recreate it or move its assets onto the overlord. [S4, S18]

The inspected trade-company creation path can reuse the banking_country reform, so bank eligibility must explicitly exclude trade_company. Unchartered state_bank subjects retain their native role; the mod's expanded charter powers require conversion and the controlling reform. [S10, S11]

Structural classification excerpt; validate namespace syntax on the selected patch:

~~~text
bfl_is_independent_bank = {
    country_type = building
    has_reform = government_reform:banking_country
    NOT = { is_subject_type = trade_company }
    NOT = { is_subject_type = state_bank }
    NOT = { is_subject_type = bfl_chartered_bank }
}

bfl_is_chartered_bank = {
    is_subject_type = bfl_chartered_bank
}

bfl_is_operating_company = {
    is_subject_type = trade_company
}
~~~

Independence/subject eligibility for other native bank arrangements is an M0 audit; the excerpt distinguishes the three relevant roles, not every possible subject in EUV. Expanded charter operations additionally require a valid landed controller with State Chartered Bank, a consistent bank binding, a selected specialization, the relevant advances and an eligible operating state.

### 4.2.1 Establish a State Chartered Bank decision

Implement a decision on the landed country, with these execution requirements:

1. The actor is a landed, location-based country with a valid capital.
2. It has a directly controlled native state_bank subject eligible for conversion.
3. It has ZERO existing bfl_chartered_bank subjects and no charter-conversion operation in progress.
4. It controls the native market containing its capital: resolve capital -> market -> owner and require that owner to be the acting country. Trading there, owning a city there or having trade access is insufficient. Verify the installed patch's precise market-owner semantics.
5. Its treasury can pay the current-age investment cost.
6. The selected State Bank still exists, is still its direct subject and has no conflicting conversion/resolution operation.

If several State Bank subjects qualify, present an explicit bank selector. The decision does not create a missing State Bank or bypass vanilla requirements for obtaining one. Capital-market control is checked when chartering; losing it later does not silently delete the charter or its financial obligations.

Define one scripted value for the investment:

~~~text
charter_investment = base_investment * current_age_multiplier
~~~

Suggested tuning defaults, not claimed native prices:

| Native age | Identifier | Multiplier | Example investment with base 500 gold |
| --- | --- | --- | --- |
| Traditions | age_1_traditions | 1.0 | 500 |
| Renaissance | age_2_renaissance | 1.5 | 750 |
| Discovery | age_3_discovery | 2.0 | 1,000 |
| Reformation | age_4_reformation | 3.0 | 1,500 |
| Absolutism | age_5_absolutism | 4.0 | 2,000 |
| Revolutions | age_6_revolutions | 6.0 | 3,000 |

Use current native age identity, not a calendar-year approximation. Recompute and revalidate the displayed amount at execution; if an age change invalidates a confirmed price, require a refreshed confirmation. ALL of the cost becomes initial bank investment. No part is destroyed as an administrative fee.

Within one guarded effect, complete this sequence:

1. Resolve and validate the actor, selected bank, prerequisites and investment amount before any mutation.
2. Reserve a conversion-in-progress flag and snapshot the amount.
3. Debit the landed country's treasury and credit the same amount to the existing bank treasury exactly once.
4. Record that contribution as paid-in equity and update the sovereign's ownership units; it is not bank income or a depositor liability. Preserve pre-existing assets, liabilities and holdings.
5. Convert state_bank to bfl_chartered_bank on the same bank tag.
6. Bind controller and bank, mark charter registration and add bfl_state_chartered_bank to the landed country.
7. Enable bank GUI access, queue specialization selection if none exists, and clear the conversion flag.
8. Reconcile balances and the one-bank invariant.

Do not attach a second gold cost to the generic decision framework if the transfer effect already pays it. If the framework deducts the decision price itself, credit the recipient from that single authoritative deduction and test the full transaction.

### 4.2.2 State Chartered Bank reform

Display name: State Chartered Bank. Identifier: bfl_state_chartered_bank.

The decision grants this non-major reform to the landed overlord. Manual adoption is unavailable without the completed subject-conversion path. The reform supplies benefits, authorizes controller GUI actions and is required for new charter-bank financial business. Its activation hooks must not charge the investment again.

A proposed benefit package preserves the native State Bank's audited bank-interest reduction and government-bond capacity benefit as reform modifiers. The inspected definition uses bank_interest = -0.005 and max_bonds_modifier = 0.33; verify these on the target patch. Move the corresponding bonuses out of the converted subject's overlord-modifier block so that the same charter benefit is applied once. Additional benefits remain tuning options. [S18]

The bank subject retains native banking-country prerequisites. The landed reform authorizes all three treasury policies. Add a proposed modest bond_interest reduction, initially -0.005 in native percentage-point conventions after verification, to achieve preferential bond funding; bank_interest and bond_interest are distinct fields. Existing capacity/rate bonuses and later central-bank buildings must not be accidentally duplicated. [S18, S25, S26]

Basic unsecured charter funding is intended to be available after charter/profile activation on the selected bond-capable patch. Audit can_sell_bonds and any hard-coded issuance checks; use the reform as the mod's explicit native bond authorization where supported. This deliberately provides a charter route alongside vanilla Central Banking, whose inspected advance belongs to Absolutism. Do not auto-grant that later advance or its building, and do not bypass native capacity, issuer eligibility, funding or debt-service checks. If hard-coded eligibility cannot be extended, record that as a blocking M0 limitation, rather than replacing bonds with renamed ordinary loans. Advanced security, notes and backstops retain their agreed later-age gates. [S4, S23, S24, S27]

### 4.2.3 One-bank cap and lifecycle

Treat the live subject count as authoritative and use stored bank references only for navigation. Check the cap at decision execution, GUI operations, migration and relevant subject/overlord lifecycle changes.

A transfer, inheritance or annexation can introduce multiple chartered subjects without running the decision. Keep one explicitly selected/default deterministic incumbent; immediately restore additional banks to native state_bank status and legacy servicing mode. Preserve their assets, debts, specialization record and deposit obligations, but disable new expanded charter business. Do not destroy institutions to satisfy the cap.

Reconcile the reform and bank binding with the surviving direct Chartered Bank. A country losing its last Chartered Bank loses the associated authorization; the former bank services existing claims under a defined wind-down/transfer policy. A missing reform does not erase liabilities. GUI authority is checked again whenever an operation executes.

### 4.2.4 Player GUI control

An independent bank player manages its own institution. A landed player with State Chartered Bank opens the financial windows with the designated subject as the financial actor and the landed country as controller.

Every mutating GUI command validates the controller, direct subject relationship, reform, selected bank, profile, advance and available bank funds. Purchases, loans, deposits, shares, inventories and notes belong to the bank subject. Sovereign policy instructions and public guarantees additionally validate controller authority.

The GUI supports accounts, rates, permitted investments, native loan purchasing, bond/debt resale, company exposure and resolution directly. A Treasury Funding panel lets the landed player set royalty tier, per-activity payout policy and bond-facility cadence/limits, see actual receipts and projected coupon costs, and redeem eligible bonds. Diplomatic interactions supplement these controls.

### 4.3 Processing ownership

Each issuer or institution owns its authoritative financial records. Counterparties keep only the references or summaries required for navigation and reconciliation.

Schematic hook extension:

~~~text
monthly_country_pulse = {
    on_actions = { bfl_monthly_accounts }
}

bfl_monthly_accounts = {
    trigger = { bfl_has_servicing_accounts = yes }
    effect = { bfl_process_accounts = yes }
}
~~~

The bfl_ names above are definitions to implement. Test the target patch's append behavior and use a once-per-period stamp. Callback definitions whose documented expected scope is none do not justify assuming root is the borrower; inspect native callback consumers and probe the actual available targets.

## 5. Financial records and accounting

### 5.1 Canonical records

| Record | Authoritative owner | Minimum fields |
| --- | --- | --- |
| Institution account | Independent bank or Chartered Bank subject | Schema version, role, controller, two-choice specialization, operating state, actual treasury, reserve base, liabilities, retained earnings, capital and processing date. |
| Deposit | Receiving bank | Depositor country or estate identity, principal, accrued interest, demand/term status, rate, maturity, queued withdrawal. |
| Native credit metadata | Current lender | Safe native loan/bond reference, borrower, is_bond classification, face versus outstanding value, acquisition basis, coupon/rate regime, current creditor, encumbrance, takeover/resale audit and guarantees. |
| Sovereign funding policy | Landed charter controller | Bound bank, royalty tier, per-activity payout ratios, facility mode/cadence, requested funding, cash-buffer limits, coupon/debt-service ceilings, next review and last completed draw. |
| Royalty account | Chartered Bank subject | Assessed productive-asset base, fee due/paid/deferred, sovereign payee, active penalty tier and last monthly settlement; a deferred fee is not automatically a new native debt. |
| Activity profit register | Bank | Contract/activity attribution, external versus controller receipts, funding/operating costs, realized losses, royalty allocation, loss carryforward, distribution reserve and already-distributed amounts. |
| Bond facility audit | Sovereign issuer with linked bank metadata | Native bonds created in each guarded draw, lot size, bank funding source, cash changes, coupon owner, redemption status and idempotency stamp; no parallel custom principal ledger. |
| Equity register | Issuer bank subject, independent bank or company | Total units, holder identities, units per holder, initial sovereign investment, founder class, voting rules and dividend policy. |
| Commodity inventory | Asset owner | Native good, custody market/location, quantity, purchase basis, encumbered quantity, storage loss. |
| Forward/receipt | Issuer or contract custodian | Parties, good, quantity, settlement price, custody/delivery market, collateral, maturity and state. |
| Commenda | Operating company or eligible operator | Investors, contributions, profit/loss allocation, project, costs, attributable proceeds, dates and state. |
| Note issue | Issuer | Outstanding face amount, reserve backing rule, accepted jurisdictions, redemption demand, confidence. |
| Concession/guarantee | Contract issuer | Parties, underlying exposure, pledged asset/revenue, trigger, expiry, payment priority. |
| Company management | Native company tag | Overlord, financial owners, home region, mandate, cash buffer, budget, active routes/projects and last payout. |

All fields are proposed mod fields unless explicitly native. Native loans remain the debt ledger; native buildings and company tags remain operating entities.

### 5.2 Storage implementation

Start with ordinary persistent variables, native scope references and bounded registries. The published documentation lists variable maps; prototype their persistence and key/value behavior before depending on them.

A market/good/owner tuple is a logical schema, not proof that the engine accepts composite map keys. Generate one explicitly named inventory map per supported good, keyed by a validated market or custody scope. Alternatively generate fixed inventory/contract slots with separate fields.

Use build-time generators for repetitive slots, goods cases and instrument menus. Python or other development tools generate game scripts before release; they are not runtime dependencies.

Set configurable bounds on contracts, warehouses, share/instrument views and counterparties. Native estate-loan takeover has no custom listings; resale views enumerate existing native bank-held claims rather than creating duplicate debt records. Aggregate small estate deposits and bilateral demand balances. Do not create a fake country or character for every deposit, share holding or instrument. Preserve a distinction between missing references and legitimate zero balances.


### 5.3 Cash and equity rules

Bank equity is actual bank cash plus conservatively valued recoverable assets minus deposits, note obligations and other liabilities. The bank's own issued shares are not an asset of that bank.

For both independent banks and Chartered Bank subjects, native country gold is the institution's own spendable wallet. The landed country's treasury is a separate native wallet. There is no charter-cash allocation inside the landed treasury.

- The charter decision transfers real gold from overlord to subject and records the initial investment as equity.
- Later capitalization, royalties, dividends, bond underwriting/redemption, guarantees and emergency payments are explicit, reconciled movements between the relevant entities.
- Both profiles have sovereign-credit permission. Recurring charter-to-controller funding uses native government bonds; any ordinary bilateral sovereign loan remains a separate native instrument. Consolidated ownership does not cancel either obligation.
- Ordinary military/government spending by the overlord cannot consume subject bank reserves through a shared cash variable.
- Replace the converted subject's automatic native subject tribute/extraction with the dedicated royalty and dividend settlement. Prevent an unrestricted siphon or leftover subject_pays_vassal rule from becoming a fourth recurring charter-bank channel. Keep deposit withdrawals, shareholder capital transactions and emergency transfers separately classified.
- Capital contributions, deposit principal, bond proceeds, recovered asset principal and note issuance are excluded from operating profit. Only the realized gain/loss component of a resale can enter earnings.
- Subject ownership and controller authorization do not make bank assets immediately spendable sovereign cash. Monthly royalties reduce bank cash/equity; dividends reduce retained earnings; a funded bond draw swaps bank cash for a claim and increases sovereign debt.
- Present royalties and dividends as earned monthly treasury receipts, and bond proceeds as monthly financing inflows. The Treasury Funding panel combines them for cash planning without reporting borrowing as tax/trade income or bank profit.
- Coupons from the controller are real bank receipts and sovereign expenses. Their subsequent dividend partially returns an internal expense; consolidated sovereign-plus-bank wealth increases only through outside earnings or net outside funding, not by recirculating that coupon.

### 5.4 Transaction invariants

| Transaction | Required accounting |
| --- | --- |
| Charter investment of 100 | Overlord cash falls 100; subject bank cash/equity rise 100; sovereign ownership is updated; no bank profit or deposit liability is created. |
| External deposit of 100 | Depositor cash falls 100; bank cash rises 100; deposit liability rises 100; bank equity does not rise. |
| Withdrawal of 100 | Bank cash and deposit liability fall 100; depositor cash rises 100. |
| Interest credited to a deposit | Bank earnings/equity fall and the depositor's claim rises; crediting interest does not itself create cash. |
| Primary share subscription | Subscriber pays issuer; issuer equity and share units increase; no profit is booked. |
| Secondary share trade | Buyer pays seller; holder register changes; issuer receives only an explicitly charged fee. |
| Native loan origination | Native cash movement occurs once; the lender obtains a credit asset and borrower a debt. |
| Native estate-loan purchase | Bank pays native takeover cost; native banking estates receive prescribed compensation; native ownership changes; borrower receives no new proceeds. |
| Native bond draw of 100 | Sovereign cash rises 100 and native bond principal rises 100; bank cash falls 100 and gains the same native claim. No issuance profit or duplicate estate-funded proceeds are recorded. |
| Coupon of 1 | Sovereign cash falls 1; current native creditor receives the verified coupon once. Funding/expenses determine whether it contributes to bank profit. |
| Native bond/loan resale for 95 | Buyer cash falls 95; existing holder cash rises 95; the same native claim changes creditor. Sovereign cash, face value and outstanding principal do not rise; seller's gain/loss depends on basis. |
| Bond redemption of 100 | Sovereign pays native face value once; current holder receives the verified principal; the native bond closes. Principal recovery is not dividend profit. |
| Monthly royalty of 2 | Bank cash/equity fall 2; sovereign cash rises 2; the fee is a bank expense even if paid from accumulated capital. The active tier updates both loyalty consequences. |
| Commodity purchase/sale | Native market cash/stockpile effects occur once; the custom inventory changes by the same physical quantity. |
| Forward settlement | Delivery and consideration, or bilateral cash settlement, occur once; released collateral is not another gain. |
| Venture funding | Investor cash becomes a project investment; funding is not operator revenue. |
| Monthly activity dividend | Actual bank cash/retained earnings fall; sovereign and other entitled holders receive matching totals; activity reserves are consumed once. New borrowing/deposits/subscriptions are excluded. |
| Note-funded permitted lending or bond underwriting | Circulation liability and matching native credit asset are recorded; issuance is excluded from eligible reserve funding. Controller funding still passes through the bond facility. |
| Haircut/default | Receivables or equity are impaired; an impairment does not automatically cause another cash debit. |

Record acquisition cost separately from native debt face value. Principal recovery, return of venture capital and returned collateral are not interest income. Unrealized commodity or share-price gains cannot be distributed as cash profits.

## 6. Implementation specifications

### 6.1 Deposits

Common banking core; extended term accounts require the Renaissance deposit advance. Chartered accounts and liabilities reside on the subject, with GUI authority on its landed controller.

Implement deposit, withdraw, renew and request early withdrawal interactions. Validate the depositor, institution, currency regime, available funds and selected terms at execution.

Country and company deposits use real transfers between country treasuries. Estate deposits use actual estate gold. Household participation is a declared aggregate abstraction through estate pools. An institution records matching liabilities; it receives no automatic income merely from attracting deposits.

Accrue demand interest monthly and term interest at the specified contract interval. Early term withdrawal can apply an agreed penalty. A withdrawal shortage queues or restricts payouts under the bank's resolution rules. Maintain a depositor liquidity buffer before AI commits funds needed for normal native expenses.

**Acceptance:** Deposit/withdraw round trips preserve total cash; save/reload preserves claims; interest accrual affects liabilities and earnings once; inadequate liquidity produces the specified withdrawal outcome.

### 6.2 Foreign branches

Common branch servicing does not unlock another specialization. A Merchant Finance office can service commodity business only after Discovery research; an Overseas Investment office can service commenda only after its Discovery advance.

Extend eligible office construction and add branch functions using verified foreign-building rules, relations and access requirements. Track owner, host, deposit exposure and supported activities.

Branches attract business and lower servicing friction; they do not grant control over host territory. Offer host benefits such as negotiated access fees or project finance. Closure, confiscation and war affect custody and servicing according to the contract.

Use explicit branch and facility identities for investments. Avoid stacking uncapped global income bonuses as a substitute for bank operations.

**Acceptance:** The correct institution owns each branch; permissions are enforced; destroyed or seized custody assets invalidate or restructure the associated records safely.


### 6.3 Sovereign and company lending

Sovereign origination is common to Merchant Finance and Overseas Investment. Both profiles may lend to eligible sovereigns, underwrite their native government bonds and hold sovereign debt. Merchant Finance adds ordinary corporate credit to native trade-company tags only from Reformation after Corporate Credit research. Overseas Investment provides commenda and company equity; common sovereign credit does not grant it company working-capital loans.

Wrap native ordinary-loan origination with bank role, controller authority, instrument/advance checks, available funding, borrower acceptance, native borrowing limits and risk pricing. For recurring funding of its own landed controller, the Chartered Bank uses the native bond facility in section 6.17, with the sovereign as issuer and bank as actual funder/creditor.

Price new lending using a base rate and borrower spread, considering creditworthiness, cash flow, war, concentration and existing obligations. The charter-controller bond facility receives a preferential but positive coupon using verified bond-specific rate behavior. Before Absolutism collateral research, these exposures remain unsecured.

**Acceptance:** Both profiles originate eligible sovereign credit and fund actual native bonds; Overseas Investment still cannot originate corporate loans, and Merchant corporate credit fails before Reformation research.

### 6.4 Native loan purchasing and bond/debt resale

#### 6.4.1 Existing regular-bank takeover

Use EUV's regular-bank take_over_loan operation for eligible estate-origin claims. Preserve native selection, valuation, payment, creditor assignment and action prerequisites; add only controller, instrument, reserve and research checks.

The inspected action excludes bonds and claims already owned by a country. It selects eligible non-bond estate claims, applies maturity/rate/funding tests, compensates banking estates and changes the creditor to the acting bank. Re-read the exact filters and bank_loan_takeover_cost on the installed patch. Both profiles can purchase eligible sovereign claims; Merchant company purchases additionally need Reformation Corporate Credit and native company-target support. [S19]

Expose the same eligible-claim view and native operation through the GUI with the independent or subject bank as buyer. Prefer native dispatch; otherwise use a minimal audited adapter preserving native takeover economics. Do not pay the landed controller a second amount or create another loan.

#### 6.4.2 Resale of existing native bonds and bank-held claims

Government bonds, including bonds issued under the controller facility, must be resellable. Already bank-held ordinary claims can use the same existing-holder settlement bridge within their instrument permissions. This is a deliberate addition to the earlier takeover-only scope; simply removing is_bond = no from the estate-purchase action would route sale cash to the wrong payee.

Prefer an exposed native resale action that preserves the existing native debt. Otherwise implement a bounded offer/accept action using the existing loan-scope claim and tested change_loan_owner support:

1. Select an actual native bond/claim owned by the seller; validate native identity, live outstanding status, transfer permission and lack of an incompatible pledge.
2. Validate buyer, instrument permission, funding, concentration and sovereign eligibility. Both bank profiles can buy sovereign bonds; corporate claims remain Merchant-only after research.
3. Snapshot claim, owner, current terms, basis, quoted consideration and any accrued-coupon allocation. The seller may cancel before acceptance; execution revalidates the snapshot.
4. Buyer pays the current holder once; transfer the same native creditor relationship once. Transfer the associated acquisition-basis/guarantee/servicing metadata without cloning principal.
5. Confirm future native coupon and redemption receipts go to the current holder. The sovereign receives no resale proceeds and its contractual liability remains outstanding.

Use face-value consideration for the first prototype if compatible with native remaining-principal semantics and both parties agree; permit risk/yield-adjusted quotes after the ownership/coupon bridge works. Face-value sale is a tuning choice, not a claim that vanilla fixes every resale price. Unsold offers expire without income. A resale below basis realizes a loss, and selling at par is principal recovery rather than earned bank profit.

Use a live portfolio view and bounded offers rather than a full order book, clearing exchange or custom auction engine. Native estate-loan takeover retains its own fixed economic operation; it is not replaced by these quotes.

**Patch gate:** Published ownership-transfer documentation alone does not prove native bond coupons or redemption follow a country owner. M0 must demonstrate this on the selected patch. If routing is hard-coded, an engine-supported ownership/settlement integration must resolve it before release; a custom coupon paid on top of unchanged native coupon deductions is not an acceptable workaround.

**Acceptance:** Vanilla takeover parity holds for estate claims. Bond and bank-held resale pays the existing seller, preserves native debt, changes subsequent receipts to the current creditor and creates no extra borrower principal/proceeds or duplicate coupon.

### 6.5 Debt restructuring

Research Debt Restructuring from Renaissance. Both profiles can then renegotiate eligible sovereign debt; Merchant Finance may restructure company debt only after Reformation Corporate Credit as well. Overseas commenda/equity settlements retain their own risk-capital rules. Bond coupon/face adjustments or refinancing use the native bond path only where tested; rate/principal effects documented for ordinary loans are not automatically proven for bonds.

Offer negotiated rate cuts, principal reductions, partial repayment and refinancing. Ordinary loans may use a tested replacement-loan sequence for maturity extension when no direct native effect exists. Bonds use tested native term changes or explicit native issuance/redemption refinancing; do not replace a required bond with an ordinary loan or invent a maturity on a redeemable/perpetual instrument. Until Absolutism Collateralization, restructuring cannot introduce secured collateral, revenue pledges or equivalent security through a differently named concession.

Audit amount changes against native principal, coupons and remaining debt. Refinance without duplicate proceeds or parallel superseded obligations. Native purchases by a Chartered Bank of its overlord's debt leave a legitimate subject-to-overlord loan; retirement requires a separate tested repayment/forgiveness action and is not automatic.

**Acceptance:** Renaissance research is required; profile and corporate-age checks hold; only negotiated terms change; haircuts and refinancing are booked once.

### 6.6 Creditor concessions and guarantees

Commercial-access concessions accompany eligible lending/restructuring in both profiles. Collateral, secured revenue pledges, guarantee-backed security and asset-priority enforcement require Absolutism and the relevant advance. Both profiles may secure eligible sovereign exposures; Merchant Finance additionally secures its permitted corporate/commodity business, and Overseas Investment its permitted projects.

Define standardized contracts for revenue pledges, commercial access, collateral, construction rights and company governance rights. Store the underlying claim, expiry, trigger, payment priority and enforcement procedure.

Borrowers receive specified finance or relief in exchange. Requests can be rejected or renegotiated. Missed performance can unlock contractually defined sanctions or enforcement; ordinary lending does not automatically create a subject relationship or transfer land.

Public guarantees state the guarantor, beneficiary, coverage fraction, ceiling and triggering loss. Count them as contingent exposures before any payment is made.

**Acceptance:** A concession expires or terminates correctly; enforcement requires the agreed trigger; a guarantee cannot pay more than its coverage and does not duplicate native debt relief.

### 6.7 Commodity inventory

Merchant Finance only. Require the Age of Discovery or later plus Commodity Investments research. Financing a permitted commenda operator's actual purchases is distinct from granting Overseas Investment a speculative commodity-trading book.

Pilot with a small selection of native goods and markets. Buy through the native market effect, then add the acquired physical quantity to the owner's inventory. Sell only unencumbered quantities through the native sale effect.

The documented sale price is actor/capital-dependent, so the chosen market's headline price is not necessarily the realized liquidation price. Test this explicitly. Include storage cost, spoilage where appropriate, custody risk and conservative valuation.

Cross-market sale of stored goods requires a delivery procedure with time, costs, access and losses. Do not allow instantaneous profit from buying in one market and selling in another without the required transport. Native company trade routes can operate ordinary commerce; the explicit inventory ledger operates custody positions.

**Acceptance:** No naked sale creates goods; quantities reconcile with stockpile changes; custody, capacity, transport and capital-location requirements are enforced.

### 6.8 Warehouse receipts and forwards

Merchant Finance only. Backed warehouse receipts and collateralized forwards require Age of Absolutism or later, Collateralization and the relevant instrument advance. Advanced margining, broader transferability and clearing extensions are reserved for Revolutions.

A warehouse receipt transfers a claim to an encumbered inventory lot. The underlying goods remain in custody; issuing the receipt does not create another unencumbered lot.

Forward contracts specify parties, good, quantity, price, dates, delivery markets and collateral. Start with simple physical delivery or bilateral cash settlement. Verify terminal valuation and cash ownership before adding variation margin or tradable contracts.

Margin calls, delivery failure and losses feed the crisis system. Cap leverage and outstanding notional. A public procurement subsidy is a paid fiscal transfer, not an unexplained higher market price.

**Acceptance:** Receipt backing cannot be double-pledged; forward payouts reconcile between counterparties; losses and collateral shortfalls persist through save/reload.

### 6.9 Bank and company equity

Founder ownership and charter capitalization are recorded immediately. Expanded bank-share subscriptions require Renaissance research; public/secondary bank-share dealing is a Reformation upgrade. Bank equity funding is common to all profiles. Purchasing company equity is an Overseas Investment instrument requiring Reformation and the company-equity advance; corporate debt belongs to Merchant Finance.

Implement primary subscription, secondary transfer, dividends, voting rights and recapitalization. Register country holders, estate pools and a stable founder class. Initialize existing institutions from their actual balance sheets without minting capital.

New issuance changes the unit count and ownership proportions; secondary trading changes holders. Financial control permits defined management choices such as budgets, dividend policy and appointment influence.

For a Chartered Bank subject, reserve monetary-policy authority to its landed controller with State Chartered Bank regardless of private equity holdings. For a company, keep political overlordship as a separate native relationship. A control acquisition can enable a separately negotiated subject-transfer agreement; it does not silently change the overlord.

Use bounded equity cross-holdings and exclude an issuer's own shares from assets. Avoid recursively capitalizing two institutions from inflated mutual share values. Founder/sovereign ownership supports ordinary monthly dividends immediately; later subscription/dealing advances expand ownership functions. Section 6.17 allocates those dividends to actual activity earnings without duplicating shareholder distributions.

**Acceptance:** Ownership totals equal issued units; dilution is correct; dividends are funded; equity purchases do not transfer national territory or overlordship automatically.

### 6.10 Commenda ventures

Overseas Investment only. Require Age of Discovery or later and the Commenda advance. The historical reference supplies contract presets, not permission to bypass this gameplay age gate.

Use project-level risk capital, not an ordinary loan with guaranteed interest. A contract records the operator, investors, capital contributions, duration, profit share, loss allocation and attributable business receipts.

Offer historical presets: unilateral financing commonly allocates 75% of profit to the capital investor and 25% to the operator; bilateral financing can use two-thirds/one-third capital contributions and equal profit sharing. Terms are configurable design presets, not a rule that every historical agreement was identical. [S14]

From Discovery, before native trade companies unlock, eligible countries or estate commercial pools can operate ventures. Later, native companies become preferred operators. Successful projects can be converted into company equity through a new agreement.

For exploration-linked projects, fund a country/operator eligible to run native exploration and register the expedition or area link. Discovery success grants agreed future commercial access or project opportunities; it does not itself create a financial payout. Settlement requires actual sale receipts, attributable trade earnings or a separately funded contractual payment.

Lifecycle: proposed, funded, active, settling, closed or failed. Recover available capital first, then divide actual surplus. Project attribution must avoid counting the same company trade income in several concurrent ventures.

**Acceptance:** Successful, partial-loss and total-loss ventures settle correctly; recovery never exceeds available proceeds; discovery without commercial receipts creates no automatic profit.

### 6.11 Currency and note issuance

Monetary servicing is common banking infrastructure and does not grant another profile's investments. Basic mint-support follows native prerequisites. Bills are a Renaissance research stage; sovereign-authorized banknotes require Absolutism and note-issuance research; wider note acceptance and clearing are later upgrades.

Separate coinage support from paper/bill issuance. Reuse native minting where exposed and connect mint-related charter powers to the existing system. Do not create duplicate mint revenue from a bank action.

Private banks require host authorization for circulating redeemable claims. The landed controller with State Chartered Bank can authorize subject-issued sovereign notes and domestic tender once the required advances/laws are available.

The implementation is a currency abstraction coupled to native gold, not proof of engine-native national denominations or universal exchange-rate simulation. Record circulation liabilities, backing rules, redemption demand, acceptance and confidence.

Note-funded eligible lending or underwriting of a native controller bond creates a matching native credit asset and note obligation. Newly issued notes cannot increase their own eligible backing reserves. Classify issuance flows separately from deposits, shareholder subscriptions and earnings. Apply inflation and confidence consequences through verified native hooks and calibrated scripted rules.

Native gold cannot reveal the composition of every ordinary payment. Therefore do not promise to trace specie and every issuer's notes through all vanilla transactions. Reserve provenance and redemption are tracked for mod-managed financial operations, with conservative limits on aggregate issuance.

**Acceptance:** Issuance is capped, cannot manufacture its own collateral, is excluded from profits, records redemption obligations and produces the specified inflation/confidence response.

### 6.12 Interest-rate policy

Store separate deposit, lending-base, discount/policy and controller-bond facility rates. Ordinary bank_interest and sovereign bond_interest are distinct native fields; convert display rates to the verified native time basis in the relevant adapter. A percentage labeled annual in the GUI must not be passed unchanged to a monthly coupon field.

Banking nations price permitted products. Landed policy instructions guide subject loans, the bond facility and liquidity operations. Fixed ordinary loans retain their contracts unless restructured. Probe whether native bonds reprice with issuer bond_interest or retain issue terms; disclose verified behavior in the GUI. Prefer a tested issue-specific coupon for the low-interest facility. If only issuer-wide native rates are supported, apply and display that policy's scope rather than promising facility-only or fixed coupons. Do not repeatedly use a restructuring effect to bypass Renaissance research.

Wider domestic credit effects use existing verified country/estate modifiers or specified interactions. They are calibrated approximations. Defining a new modifier name alone does not make the engine apply a central-bank transmission mechanism.

**Acceptance:** Policy changes reprice eligible new business; fixed ordinary loans remain unchanged; native bond repricing follows its measured rate regime; interest costs and credited deposits use the correct time basis.

### 6.13 Interbank liquidity and public support

Limited settlement liquidity is common to all profiles under strict operating limits. Secured/discount facilities require Absolutism, Collateralization and Liquidity Facilities research; broad lender-of-last-resort and crisis-clearing powers are Revolutions upgrades. Liquidity services cannot be used as unlimited long-term investment lending outside a bank's profile.

Provide native interbank loans where institutions are valid counterparties. Record exposure limits and maturity; attach collateral only after the Absolutism security advance. Once security is available, earmark pledged assets so they cannot secure several facilities at once.

Public-bank discount facilities support solvent but illiquid institutions, with collateral haircuts and a penalty rate. Funding comes from the Chartered Bank subject treasury or separately authorized, capped subject note issuance. Overlord support is an explicit transfer.

Distinguish liquidity assistance from recapitalization. A loan does not repair negative equity by itself. Equity subscriptions, loss allocation or resolution address insolvency.

**Acceptance:** Assistance changes liquidity and obligations as intended; pledged assets cannot be reused; emergency support does not erase realized losses.

### 6.14 Crises and resolution

Calculate liquidity stress, capital impairment, concentration, depositor confidence and public backing. Native defaults and mod-managed losses update these measures through callbacks and reconciliation.

Use clear states: operating, stressed, withdrawal-restricted, insolvent, resolving and closed. State transitions determine permitted actions and notifications.

Resolution can suspend royalties, dividends and new facility draws, realize assets, convert eligible creditor claims into equity, apply agreed deposit losses, recapitalize or wind down. Public guarantees and rescues create actual fiscal costs; monetary support uses the issuance rules.

Voluntary restructuring, debt-to-equity conversion, security enforcement and advanced backstops require their applicable profile and research gates. Mandatory native default losses, basic accounting impairment and obligation servicing remain possible in every age; resolution is not an alternate route to originate an unresearched instrument.

Reconcile native bankruptcy cancellations before processing custom losses. Handle disappearance of a bank or company's last building, annexation, overlord changes, reform loss, subject conversion and saved-target invalidation; reconcile the one-Chartered-Bank cap.

**Acceptance:** Losses are booked once; claim priority is predictable; disappearing entities leave no payable duplicate claims or immortal asset references.


### 6.15 Exclusive specialization event

A bank chooses exactly ONE of Merchant Finance or Overseas Investment. Store the canonical choice on the bank, not the controller. Sovereign lending, sovereign-loan purchasing and native government-bond underwriting/resale are shared functions; there is no separate Sovereign Finance specialization.

Fire the event at independent-bank creation/first initialization or charter completion. The landed controller chooses for its subject; independent bank players choose for themselves; AI uses the same two mutually exclusive outcomes.

- Set one persistent profile value and a completed-choice flag.
- Require the committed choice for new financial business; common sovereign powers become available to either choice.
- Do not provide an ordinary respecialization decision or an advance that adds another profile.
- Save loading and later charter conversion retain a valid choice.
- Service inherited out-of-profile assets without allowing new prohibited business.
- For a save from the earlier three-profile design, migrate an old Sovereign profile through a once-only choice between the two current profiles. Preserve all claims, cash, reform and research; remove the obsolete profile flag. Existing Merchant/Overseas choices persist. This versioned migration is not a repeatable respec.

| Instrument or function | Merchant Finance | Overseas Investment |
| --- | --- | --- |
| Accounts, reserves, deposits, bank ownership, servicing branches, GUI and crises | Common core | Common core |
| Permitted rate policy and legally authorized monetary services | Common core | Common core |
| Sovereign loan origination and native sovereign-loan takeover | Common core | Common core |
| Native government-bond underwriting, holding and resale | Common core; native/charter authorization | Common core; native/charter authorization |
| Chartered controller royalty, activity dividends and recurring bond facility | All three channels | All three channels |
| Sovereign debt restructuring | Renaissance advance; tested bond support | Renaissance advance; tested bond support |
| Native company working-capital credit/debt and eligible claim purchases | Reformation Corporate Credit | No |
| Native company debt restructuring | Corporate Credit plus Renaissance restructuring research | No |
| Commodity investment book | Discovery advance | No |
| Warehouse receipts and collateralized forwards | Absolutism advances | No |
| Commenda/exploration-linked investment | No | Discovery advance |
| Company equity and long-term venture stakes | No | Reformation advances |
| Collateralization | Sovereign and permitted corporate/commodity exposures from Absolutism | Sovereign and permitted project exposures from Absolutism |
| Advanced clearing, risk management and crisis coordination | Later upgrades within permitted functions | Later upgrades within permitted functions |

The landed country retains its normal native trade, fiscal and political-company actions. Those actions do not let the subject bank bypass its two-choice profile restrictions.

### 6.16 Age-gated advance tree

Implement unlocks as native-style advances with prerequisites and explicit action checks. Age arrival alone is insufficient; the relevant advance must be researched. Check minimum age or later, not equality to one age that would disable the feature in the following era. Use the native age identifiers from the installed patch, not hard-coded calendar years. [S20, S21]

For an independent bank, the bank is the research owner. For a Chartered Bank, the landed controller researches the financial advance; synchronize only eligible, profile-permitted unlocks onto the bank subject where native action/building availability requires the advance on the actor. Existing native prerequisites remain required. An AI subject's independent research must not bypass the controller authorization or profile gate.

| Earliest age | Proposed advance | Prerequisites / profile | Unlock |
| --- | --- | --- | --- |
| Traditions | Existing banking foundations and charter registration | Eligible bank; native requirements; one of two profiles selected | Basic accounts, demand deposits, rates, branches and common sovereign loans/takeover. Chartered royalty, basic activity dividends and unsecured native bond facility use audited reform authorization on a bond-capable patch. |
| Renaissance | bfl_term_deposits | Banking foundations; common core | Expanded term deposits. |
| Renaissance | bfl_bank_capital_subscriptions | Accounting foundations; common core | Additional bank equity subscriptions. |
| Renaissance | bfl_debt_restructuring | Native credit foundations; both profiles | Eligible sovereign debt renegotiation/refinancing; native bonds require tested support. Merchant company use also needs later Corporate Credit. |
| Renaissance | bfl_commercial_bills | Deposit/payment foundations; common core | Permitted bills and payment instruments; no advanced sovereign-note regime. |
| Discovery | bfl_commodity_investments | Merchant Finance; branch/account foundations | Funded native-goods positions and commercial inventory investment. |
| Discovery | bfl_commenda | Overseas Investment; native exploration/trade eligibility | Profit-sharing voyage, exploration-linked and trading projects. |
| Reformation | bfl_corporate_credit | Merchant Finance; banking foundations; native company unlocks | Native credit/debt to trade-company actors and eligible native purchase paths. |
| Reformation | bfl_company_equity | Overseas Investment; commenda; native company unlocks | Company subscriptions and long-term ownership stakes. |
| Reformation | bfl_bank_share_dealing | Bank capital subscriptions; common core | Expanded transfer/public dealing in bank equity. |
| Absolutism | bfl_collateralization | Both profiles for sovereign credit; relevant profile for other instruments | Secured credit/bonds where native support exists, pledged revenue, encumbrance and priority rules. |
| Absolutism | Native central_bank_advance | Native Manufactories and embraced Banking prerequisites; verify target patch | Native Central Banking upgrades/building and capacity; distinct from the mod's basic charter authorization, not automatically granted by chartering. |
| Absolutism | bfl_warehouse_receipts | Merchant Finance; commodity investments; collateralization | Inventory-backed transferable claims. |
| Absolutism | bfl_commodity_forwards | Merchant Finance; commodity investments; collateralization | Collateralized forward contracts. |
| Absolutism | bfl_project_security | Overseas Investment; commenda/company equity; collateralization | Advanced security terms for project investments. |
| Absolutism | bfl_sovereign_banknotes | Chartered Bank; State Chartered Bank; bills and monetary authorization | Advanced sovereign-authorized subject note issuance. |
| Absolutism | bfl_liquidity_facilities | Common operating core; collateralization; eligible bank counterparties | Secured interbank discount/liquidity operations. |
| Revolutions | bfl_advanced_clearing | Relevant settlement/liquidity advances | Wider clearing and crisis coordination. |
| Revolutions | bfl_margining_and_risk_management | Merchant Finance; commodity forwards | More advanced margin procedures and financial-risk controls. |
| Revolutions | bfl_public_financial_backstops | Chartered Bank; notes/liquidity facilities; guarantee authorization | Broad emergency backstops and lender-of-last-resort procedures. |

A shared permission service applies controller/role, specialization, advance, minimum age, native prerequisites, funds and operating-state checks in GUI commands, diplomatic interactions, AI and callbacks. Ineligible advances should be unavailable to the profile where supported by the native research schema; execution checks remain mandatory even if research visibility is correct.

Research never changes specialization. Chartering grants the institution, reform and its basic treasury policies, not the full financial tree. Bond issuance follows the explicit charter authorization plus native feasibility/capacity checks; it is not collateralization or advanced banknote issuance. Preserve these exact earliest user requirements: debt restructuring in Renaissance; commodity investment and commenda in Discovery; company corporate credit/debt in Reformation; collateralization in Absolutism.

**Acceptance:** Profile selection is one-time and exclusive; all specified features fail before both age and research requirements, remain available in later ages after research, and cannot be invoked through another interface or subject actor to bypass restrictions.

### 6.17 Landed sovereign treasury: royalties, dividends and native bonds

#### 6.17.1 Three funding channels and policy authority

The landed controller manages all three channels through Treasury Funding under State Chartered Bank. The subject remains the financial actor and owns the paying/underwriting cash. The same treasury policy works with either specialization. The mandatory channels are:

| Channel | Sovereign treasury treatment | Bank treatment | Player control and limits |
| --- | --- | --- | --- |
| Royalty | Recurring monthly receipt actually paid by the subject. | Cash debit and expense/equity reduction; can draw on accumulated bank capital without current profit. | Graduated fee tier; monotonic burgher/subject loyalty cost; cash/reserve and resolution limits. |
| Activity dividends | Monthly receipts attributed to credit, debt and permitted investments. | Funded distribution of realized retained earnings after costs, losses and royalty; not another expense before profit. | Per-activity payout ratios and sovereign equity entitlement; earnings, capital and cash limits. |
| Bond facility | Recurring financing proceeds; native sovereign liability and ongoing interest expense. | Actual cash funding exchanged for a native government-bond asset; subsequent coupons/credit risk. | Debt-first or buffer mode, cadence, issue limits, preferential coupon policy, bank capacity, native bond capacity and debt-service ceiling. |

Automatic native subject tribute is replaced for the converted subject. Do not implement the royalty as an additive country-income modifier that mints sovereign cash while leaving the bank treasury unchanged. Use actual cash transfers once; use native budget categories only if their accounting hooks can display those same transfers without paying them again. Otherwise the mod's monthly statement is authoritative for the breakdown. Deposits held by the sovereign and later equity redemptions remain withdrawals/capital transactions, not extra operating-income channels.

Set defaults on chartering, show estimated and last-paid values, and require controller authorization whenever a policy changes. A pending specialization, missing reform, wrong overlord or resolution state blocks new draws/payouts as appropriate; existing sovereign bonds continue to be serviced.

#### 6.17.2 Scalable monthly charter royalty

Use a royalty distinct from profit dividends. Proposed assessment:

~~~text
royalty_due = annual_royalty_rate * opening_performing_asset_base / 12
royalty_paid = min(royalty_due, cash_available_after_protected_obligations)
~~~

The base is the conservative opening book value of funded, performing loans/bonds and permitted productive investments. Exclude cash, the bank's own shares, impaired/defaulted principal, unfunded commitments and inflated unrealized marks. Base value is snapshotted before this month's new issuance so a draw cannot generate an immediate fee on its own new principal. Applying an annual fee to asset book value is a design choice; it is not vanilla tax collection.

Illustrative royalty tiers, all tunable:

| Tier | Annual assessment on eligible assets | Burgher target-satisfaction penalty | Chartered subject-loyalty penalty |
| --- | --- | --- | --- |
| Waived | 0% | 0 display points | 0 display points |
| Light | 0.25% | -2 display points | -5 display points |
| Standard | 0.50% | -5 display points | -10 display points |
| Heavy | 1.00% | -10 display points | -20 display points |
| Exceptional | 2.00% | -20 display points | -35 display points |

Apply burghers_estate_target_satisfaction on the landed sovereign and subject_loyalty on the bank subject through one named, replaceable current-tier modifier. Convert display points to native units after M0; do not infer that the estate field uses a 0–100 scale. Refresh the active tier without stacking another penalty every monthly pass. The satisfaction target can affect actual burgher loyalty over time under native recovery/decay. A higher tier always carries a greater cost; cash shortages do not silently remove its policy penalty. [S24]

Settle the actual fee from the bank treasury to the sovereign treasury monthly. If it exceeds current profit, it reduces accumulated equity: this is permitted extraction with a visible capital consequence. Protect due depositor obligations and the applicable reserve floor, and suspend payment in resolution. Report assessed, paid and deferred amounts. For this cash-based royalty, book expense only when paid. A deferred assessment is a waivable, non-compounding administrative record, not an accrued bank liability or native bond; later collection creates the expense once and a waiver creates no cash. Show whether a payout draws on profits or capital. Lowering the tier replaces its current penalty but does not erase already realized business losses.

**Acceptance:** Increasing the tier raises the assessment and both loyalty penalties; 2 gold paid means bank cash falls 2 and sovereign cash rises 2; reload does not stack the modifier or repeat payment.

#### 6.17.3 Monthly dividends attributed to activity

Maintain a realized-profit register with separate buckets for:

- Sovereign ordinary-credit interest and native bond coupons, available in both profiles; identify controller coupons separately from external borrowers.
- Realized secondary-credit/bond sale gains or losses, excluding recovered principal.
- Merchant corporate-credit receipts from Reformation and commodity/instrument returns from their required ages.
- Overseas commenda surplus from Discovery and native-company dividends/equity gains from Reformation.
- Authorized fees, less deposit funding costs, operations, realized credit/investment losses and the royalty expense.

An instrument contributes no dividend until it produces actual attributable earnings. Allocate common costs and the royalty once across buckets using a stable documented rule. Carry losses forward across the institution before paying out winning buckets; do not hide losses by distributing only the positive projects. Company profits are first recognized by the company and distributed under section 7; only the bank's actual entitled receipt enters its activity register.

For each permitted bucket a, propose:

~~~text
eligible_profit_a = retained_realized_profit_a_after_costs_losses_and_royalty
requested_dividend_a = payout_ratio_a * max(0, eligible_profit_a)
sovereign_receipt_a = funded_total_dividend_a * sovereign_ownership_fraction
~~~

Cap total dividends by available unreserved cash and capital above the minimum requirement. Allocate a cash shortfall proportionately to requested bucket payouts; pay other shareholder entitlements consistently. A charter's initial paid-in equity determines sovereign ownership; private subscriptions may dilute it without taking away monetary-policy authority. Do not give the sovereign 100% of a dividend already owed to other holders. Any exceptional contractual profit-participation class must be explicitly funded and accounted for rather than added on top of the same profits.

Process monthly: if a venture realizes no profit that month, it pays no current dividend. The player may retain realized earnings in a bucket and release them gradually in subsequent monthly distributions; decrement that reserve after each payout. Unsettled projected profits, deposits, bond face proceeds, returned venture capital, recovered collateral, subscriptions and unrealized valuation gains cannot fund a dividend entitlement. Liquid cash arriving from those sources can improve liquidity, but cannot make a loss-making bank eligible for profit distributions.

**Acceptance:** Monthly sovereign receipts reconcile to ownership and specified activity; return of principal creates no dividend; total holder payouts consume the same earnings reserve once.

#### 6.17.4 Recurring preferential native government-bond facility

The facility automates repeated bank-funded native government-bond issuance. It does not automate give_loan with a bond label. Use documented sell_bonds for issuance and redeem_bonds for face-value retirement, with is_bond confirming the object. The government continues owing the native coupon and principal after bank resale. [S4, S5, S23]

Policy controls:

| Setting | Proposed implementation |
| --- | --- |
| Mode/cadence | Off, monthly debt-first, or treasury-buffer draw; yearly review may be offered as a convenience. Monthly is the core intended playstyle. |
| Funding target | In debt-first mode reserve a selected share of forecast spending for bond funding, with a proposed 60% campaign calibration target; buffer mode finances the forecast shortfall instead. |
| Treasury ceiling | Skip/reduce draws when projected cash already exceeds the configured operating buffer/ceiling, so unused financing does not accumulate indefinitely. |
| Available bank funding | Spendable bank cash after due withdrawals/costs, statutory reserves, committed investments and the current-period liquidity buffer. Capital and sovereign concentration also limit underwriting. |
| Native limits | Verified can_sell_bonds/issuer eligibility, native bond_capacity, count/amount caps and actual native lot size; issue only fully fundable lots. |
| Rate/service ceiling | A preferential positive native bond coupon, funding-cost/risk allowance and a ceiling on projected sovereign coupon/redemption burden. |
| Rollover | Optional explicit refinancing/rollover of eligible native bonds, subject to relevant research where terms are restructured and renewed funding/capacity checks. |

Rates must remain consistent with the audited native bond model. Prefer a facility-specific issue coupon when the native API supports it. If rates are issuer-wide or outstanding bonds reprice, show that scope and consequences; do not promise fixed, issue-specific terms without a successful probe. Government coupons are native obligations even if the issuer and original creditor share a controller.

Implement a guarded draw:

1. Bind landed issuer, its one valid bank, reform, completed profile and current policy; reject an already-processed period or stale command.
2. Forecast funding need and coupon burden; compute reserve-protected bank capacity and native issuer capacity. Reduce/skip the request when a constraint binds.
3. Use whole native bond lots if arbitrary amounts are not supported. Carry an unfilled target as a future request without creating debt or cash; show requested versus actual funding.
4. Issue through the native bond operation and capture the new native object using a verified creation target or safe before/after native portfolio selection. No concurrent command may capture another issuer's bond.
5. Ensure a single real bank cash debit funds a single sovereign cash credit and that the bank holds that native claim. Prefer native lender-directed issuance if exposed. If issuance initially uses an estate/abstract investor source, the adapter must reassign/settle that source and cancel its provisional cash/claim consequences using verified effects before finalizing bank ownership.
6. Reconcile coupon destination, issuer debt/count/capacity and bank acquisition basis; record the completed draw and refresh the monthly statement.

M0 must measure step 5 rather than guess it. An extra bank debit alongside unchanged outside-funded native proceeds is not automatically a correct bank-funded settlement; an extra sovereign credit is definitely a duplicate. Any source correction must preserve the tested estate/country cash accounting, native debt and creditor. If exposed scripting cannot implement genuine bank underwriting or route current-holder receipts, this is a blocking integration issue, not grounds to silently ship synthetic custom bonds.

Do not add a custom coupon on top of a native coupon or pay native principal a second time. Redemption pays the current holder, including an outside buyer after resale; a native perpetual/redeemable bond remains outstanding until its verified redemption/default rather than an invented amortization schedule. Refinancing replaces or rolls the native obligation explicitly and cannot erase debt without payment.

The bank may subsequently resell facility bonds through section 6.4. It recovers liquidity for further funding, reduces controller concentration and transfers credit risk; it gives up future coupons on the sold debt. Lower-interest sovereign bonds may need a discount to attract an outside buyer. Resale is possible, not guaranteed demand or par value.

**Acceptance:** A repeated facility draw produces actual native bonds, one set of proceeds and bank-funded claims in either profile. A dry/insolvent bank skips issuance; coupon cost persists; resale changes future payee; redemption closes the correct claim once.

#### 6.17.5 Debt-led treasury playstyle and the funding cycle

The intended loop is bank capitalization/deposits and outside earnings -> native bond underwriting -> sovereign spending on productive capacity and commerce -> larger bank business/earnings -> monthly royalties/dividends and capacity for further bonds. Resale adds outside financing and recycles underwriting liquidity. Native trade companies connect spending and finance to operating trade, projects and profits rather than being passive bonus subjects.

Debt-first funding can cover most regular cash needs when bank and investor capacity permit. For example, tune a sustainable fixture around 100 monthly expenditure, 35 native fiscal receipts, 5 funded royalty/dividend receipts and 60 net new bond proceeds. This is a proposed cash-budget scenario, not a claim that borrowing is profit or that debt service can grow indefinitely. Include the current coupon cost in expenditure and verify the facility can keep operating as bond capacity, external sales and real economic cash generation evolve. Do not automatically disable all native taxes/trade: the player can adjust fiscal reliance while those receipts underpin interest and redemption.

Primary issuance grows the bank's coupon-bearing portfolio but reduces its liquid cash. A royalty/dividend reduces its cash further. Expansion is beneficial only while returns, funding, debt service, liquidity and risk remain sound. Increasing issuance alone does not guarantee better bank performance.

Numerical accounting example: the bank underwrites a 100-gold native bond, so sovereign cash rises 100, bank cash falls 100 and the bank holds a 100 claim. A 1-gold monthly coupon moves 1 from sovereign to bank. If 0.5 is later returned as a valid dividend, the sovereign's net coupon cost is 0.5; the pair has not earned new external wealth from that internal coupon. If the bank resells the bond for 98, it receives outside buyer cash and realizes the appropriate basis loss; later coupon payments go to that buyer, and the sovereign receives no new 98 from the resale.

Display royalty/dividend earnings, gross issuance, redemption, net financing, coupon expense, outside-held debt and total cash change as separate rows. Track borrowing dependence and stress indicators so the player can see the funding cycle strengthening or breaking. Contraction, an unsuccessful resale, a deposit run or rising coupon burden feeds the existing restructuring/concession/crisis framework.

**Acceptance:** Campaign tuning demonstrates debt as the largest regular funding stream where feasible, while cash conservation, losses, native bond capacity and interest obligations remain visible and enforceable.


## 7. Native trade-company implementation

### 7.1 Preserve native identity

Register companies by their native trade_company subject classification and existing country tag. Preserve headquarters, home-region bookkeeping and the original political overlord. The published subject and headquarters definitions provide the starting structure, including company-specific buildings and creation fields. Their numerical modifiers must be re-audited on the selected patch. [S10, S11]

Financial ownership lives in the equity register. Political authority lives in native subject relationships. A foreign bank can own shares or a loan without becoming the company's overlord.

### 7.2 Initialization and existing-save migration

1. Discover native companies once during initialization or migration; make registration idempotent.
2. Inspect the creation path and grant only genuinely missing, intended construction/trade prerequisites. Do not assume an old reported unlock bug persists.
3. Preserve the native headquarters owner and register the actual home region.
4. Initialize shareholder ownership from an explicit founding rule. Existing cash/assets are opening capital, not a new cash grant.
5. Set operating cash buffers, commercial mandate, dividend policy and permitted counterparties.
6. Record the selected company's facilities and projects. New construction must assign to that company explicitly.
7. Run a bounded follow-up reconciliation for companies created through native events or headquarters construction.
8. Migrate schema versions without recreating existing company tags.

### 7.3 Operating controller

Implement a company budget with separate allocations for upkeep, trade, debt service, reinvestment, ventures and distributions. Treasury borrowing, share subscriptions and investor advances are financing flows.

Use native merchant capacity and trade creation/adjustment where verified. Candidate routes must respect market access, range, available goods, real trading costs and operating capacity. Projected trading margins do not become cash until the native operation generates receipts.

Construction choices should address a demonstrated capacity or commercial need. Prefer relevant native company buildings; introduce warehouse support only where the inventory system requires it. Verify that owned facilities belong to the selected company, especially when an overlord has several companies.

Use a company mandate for a goods family, region or business focus. Host privileges and commercial charters operate within negotiated permissions; they do not imply an engine-wide prohibition on every other country's trade.

### 7.4 Native income and distributions

Native company economics can deliver value both to the company and directly to its overlord. These streams must be identified before dividend logic is written.

The operating cash waterfall is:

1. Native operating costs and already-applied native obligations.
2. Required debt service and queued contractual payments.
3. Operating and liquidity buffers.
4. Authorized reinvestment and venture commitments.
5. Distributable realized earnings, capped by available company cash.

Do not subtract a native payment twice or pay shareholders out of income already credited directly to the overlord. Identify direct native overlord receipts separately from company-retained earnings. Any deliberate reallocation of those receipts requires an explicit, reconciled transfer.

If exact company profit attribution is initially unavailable, use a conservative distribution rule based on verified net operating receipts and cash. Borrowing/share subscriptions are not trading profit. A company dividend paid to the bank becomes a realized bank activity receipt; only its funded sovereign shareholder share flows onward in the bank's later monthly distribution. Direct native overlord receipts are shown separately and cannot enter that bank bucket again.

### 7.5 Company finance and failure

Company deposits use the common services. Company equity is an Overseas Investment instrument; corporate loans/debt are Merchant Finance instruments from Reformation; commodity receipts require its later Merchant Finance advances; commenda requires Discovery Overseas Investment research. Company assets secure debt only after Absolutism collateral research and when legal, profile-specific and recorded priority rules allow it.

A failed company enters workout before liquidation. Investor losses transmit to bank equity; company deposit withdrawals can transmit liquidity stress. Public guarantees connect corporate failure to the charter bank or government only when invoked.

On liquidation or disappearance, settle remaining instruments and invalidate target references. Avoid transferring the last headquarters blindly before handling the native company's continued existence.

## 8. UI, interactions and AI


### 8.1 Player interfaces

The same financial GUI serves an independent-bank player and a landed player controlling one Chartered Bank. Bind the selected bank as the financial actor; use the player/controller only for authorization and sovereign decisions.

| View | Required information and actions |
| --- | --- |
| Bank accounts | Subject/independent-bank identity, controller, profile, native treasury, reserves, liabilities, assets, earnings, rates and funding. |
| Native debt and investments | Native eligible estate-claim takeover; existing-holder bond/loan resale; current creditor, face/basis/quote/coupon and permitted investments. |
| Treasury Funding | Royalty tier and both loyalty costs; per-activity dividends/ownership; facility mode/cadence/target, available funding and coupon policy; sovereign cash forecast, actual receipts, issuance/redemption and outside-held bonds. |
| Ventures and companies | Native company identity, political overlord, financial owners, bank exposures, budgets, projects and realized receipts. |
| Monetary policy and distress | Permitted issuance, rates, confidence, guarantees, liquidity facilities and resolution. |
| Research and specialization | The chosen exclusive profile, its advance path, earliest ages and explanations for locked instruments. |

Build subject GUI binding and Treasury Funding policy scaffolding in M1. Add direct royalty/dividend settlement, recurring native bond issuance, current-holder resale/redemption, deposits, investments, company finance and resolution with their milestones. Diplomacy remains useful for foreign consent and negotiated contracts, but the management architecture is not diplomatic-interaction-only.

Every button repeats controller authority, current subject/reform binding, profile/advance/age permission, available bank funds and target-state checks. Gate disabled panels clearly by profile or research; a UI label alone is not enforcement.

Keep calculations in script services and use validated GUI accessors for display. Read-only displays and tooltips must not mutate simulation state. Show committed capital, realized income, unrealized value and possible losses. Financial actions execute once through synchronized commands; estate takeover keeps native costs/payouts and resale pays the current holder. Treasury Funding distinguishes financing from earned monthly receipts even if vanilla budget rows cannot expose new categories.

### 8.2 AI behavior

Independent and Chartered Bank AI scores only profile-, age- and advance-permitted lending and investment using expected return after funding and operating costs, credit risk, concentration and liquidity. Deposit competition reflects funding needs and confidence.

Company AI chooses trade and construction based on native capacity and projected margins, keeps an operating buffer and distributes only eligible profits. It prioritizes commercial management actions appropriate to its role.

Chartered Bank AI follows its two-choice profile and controller treasury policy, protects reserves/capital before royalties/dividends/underwriting, evaluates bond buyers and rollover exposure, and tracks controller concentration plus guarantees. Sovereign AI selects royalty tiers using loyalty/capital costs and limits debt-first draws by available funding and debt service. Emergency support considers collateral, fiscal capacity, issuance limits and systemic exposure.

Run bounded periodic reviews with cooldowns. Do not scan every bank against every country each month. Evaluate registered clients, counterparties, permitted local opportunities, native takeover targets and bounded native bond/claim resale offers; no global order-book matching is required.


## 9. Development milestones

| Milestone | Deliverable | Dependencies | Completion gate |
| --- | --- | --- | --- |
| M0: Native audit | Pin bond-capable patch; decision/conversion/market/GUI probes; native takeover; real bank-funded sell_bonds, creditor/coupon/redemption and resale tests; payout/loyalty/rate checks. | None | Required native bridges demonstrated, including genuine native bonds and current-holder payments. |
| M1: Charter and accounts | Existing decision/cost/conversion/reform/cap; separate bank treasury; GUI/Treasury Funding scaffolding; two-option profile event/migration. | M0 | Full paid investment once, valid controller/reform, one bank and one of two profiles; no leftover flat subject tribute. |
| M2: Operating companies | Native registration, facilities, budgets, working trade and conservative distributions. | M1 | Real company operations/receipts identified; financing and political authority remain distinct. |
| M3: Sovereign credit and bonds | Common sovereign origination/takeover; native bond underwriting, recurring facility, resale/redemption; gated restructuring and Merchant corporate-credit branch. | M1; M2 for company branch | Both profiles finance native bonds; proceeds/coupons/principal reconcile through transfer and reload. |
| M4: Treasury payouts and deposits | Royalty tiers/loyalty; monthly activity profit register and founder dividends; demand/term deposits, withdrawals and reserves. | M1, M3 | All three treasury channels work; bank cash is source, principal is excluded from profits and payouts respect liquidity/capital. |
| M5: Ownership | Subscriptions, transfers, dilution and company-equity branch; extend existing monthly dividends to new holders. | M1, M2, M4 | Monthly distributions reconcile to diluted ownership and attributable earnings; company equity stays Overseas. |
| M6: Goods finance | Discovery positions; Absolutism collateral/receipts/forwards; later margining. | M1, M2, M4 | Native quantities and activity earnings reconcile; age/advance/profile gates hold. |
| M7: Commenda | Discovery ventures, early operators and later native companies; monthly distribution of realized surplus. | M2, M5; M6 only for custody-linked variants | Real outcomes settle and enter the correct bank activity bucket; no discovery-only payout. |
| M8: Monetary system | Rates, staged notes, secured liquidity and Revolutions upgrades; native Central Banking progression. | M3–M7 | Native bond coupon behavior and later monetary powers follow their audited rules; no self-backed issuance. |
| M9: Resolution | Contagion, guarantee/recapitalization, payout/draw suspension, liquidation and lifecycle cleanup. | M3–M8 | Debt/coupons survive bank transfer appropriately; one-bank and controller rules preserve claims. |
| M10: Release integration | Full GUI, two-profile AI, age tree, debt-led treasury balance, compatibility and performance. | M1–M9 | Both player roles pass full campaigns; recurring finance is viable, constrained and transparent. |

Build each feature's GUI and AI with its milestone. M1 already demonstrates direct subject management; M3/M4 deliver the complete treasury loop before advanced commodity/venture instruments. Founder dividends do not wait for tradable-share research.

The first prototype contains a decision-converted bank, one independent bank, both specialization choices, all three treasury channels and a native bond resold between two banks. Test later modules in appropriate-age fixtures with advances. The release provides the union of feature sets across the two profiles plus their common sovereign core; debug grants never become automatic normal unlocks.

## 10. Validation plan

### 10.1 Meaningful automated checks

Use offline checks for generated script structure, localization coverage, identifier uniqueness, encoding, required metadata, override manifests and ledger arithmetic. Exercise account rules with transaction sequences and randomized amounts, including bounds and rounding.

Include accounting sequences for charter equity -> underwriting -> coupon -> royalty/dividend -> resale -> later coupon -> redemption; verify cash conservation and one persistent debt through every step. Cover loss carryforward, monthly idempotence, native lot limits and both profile permission maps.

Offline tests cannot establish engine cash movements, native bond payee behavior, loader semantics or callback order. In-game probes and campaigns remain required.


### 10.2 In-game acceptance matrix

| Test | Expected result |
| --- | --- |
| Missing native State Bank | Charter decision is unavailable; no substitute bank is silently created. |
| Capital-market prerequisite | Decision succeeds only if the actor controls the native market containing its capital; trade access alone fails. |
| Multiple eligible State Banks | Player explicitly chooses the subject to convert; unrelated banks remain intact. |
| Current-age investment | Displayed/executed amount uses the correct age coefficient; the full cost moves from overlord to subject equity exactly once. |
| In-place charter conversion | Country tag, headquarters, portfolio and obligations persist; only the intended subject type changes. |
| Government reform | State Chartered Bank is granted to the landed controller; benefits are not duplicated between subject and reform. |
| One-bank cap | A second charter is blocked; migration/inheritance restores extra banks to obligation-preserving State Bank servicing status. |
| GUI subject authority | Landed player manages its bound bank directly; wrong controller, target bank, reform or subject relationship fails. |
| Independent bank GUI | Bank-country player operates its own account without acquiring landed-controller privileges. |
| Separate treasuries | Native military spending by the overlord does not reduce subject reserves; investment/dividends/guarantees are explicit transfers. |
| Specialization event | Exactly one of two profiles is set; both retain sovereign origination/bonds. Reload/conversion does not respec; obsolete Sovereign-profile saves get one versioned choice. |
| Profile enforcement | GUI, native purchase adapter, diplomatic actions, AI and research reject disallowed instruments. |
| Renaissance restructuring | Age plus researched advance required; company use also requires its later corporate-credit permission. |
| Discovery commodity and commenda | Merchant commodities and Overseas commenda fail before Discovery/research and remain available in later ages after research. |
| Reformation corporate credit/debt | Merchant company credit requires Reformation, its advance and native company eligibility. |
| Absolutism collateralization | No earlier pledge, backed receipt, secured facility or re-labelled security bypasses the age/advance gate. |
| Later-age upgrades | Advanced notes, forwards, clearing and backstops unlock at their assigned age only after prerequisites/research. |
| Native takeover parity | Same eligible estate-origin claim, native cost, estate payout and creditor assignment; no second debit or borrower windfall. |
| Common sovereign functions | Merchant and Overseas banks can originate/purchase sovereign claims and underwrite native bonds; Overseas still cannot lend to companies. |
| Royalty payment/loyalty | Higher tier increases assessed fee and both native loyalty costs; actual payment debits bank and credits sovereign; modifiers do not stack. |
| Royalty capital/shortfall | Fee can consume accumulated equity; reserves/obligations limit cash payment; deferred assessment does not compound or become automatic debt. |
| Activity dividends | Monthly realized-profit/ownership allocation; costs, royalty and losses counted once; no dividend from principal, deposits, subscriptions or new bonds. |
| Native subject extraction | Converted subject has no leftover flat tribute/unrestricted siphon; royalty and dividend rows reconcile to the only recurring earned transfers. |
| Recurring bond facility | Either profile funds actual is_bond claims repeatedly; sovereign debt/proceeds rise once and bank cash falls once; dry bank skips. |
| Native lot/issuance limits | Lot size, can_sell_bonds, capacity and period stamp enforced; no fractional fake bond or duplicate concurrent issuance. |
| Bond rate and coupon routing | Low positive coupon uses verified units/repricing; sovereign pays once; current native holder receives once after resale. |
| Bond resale | Buyer pays current bank holder; same native claim transfers; sovereign receives no new principal and terms/coupon liability persist. |
| Redemption and refinancing | Native principal reaches current holder once and claim closes; explicit refinancing cannot erase debt for free. |
| Internal coupon cycle | Returning controller coupon through dividends reduces net sovereign service cost without creating consolidated outside profit. |
| Debt-led campaign | Debt-first policy supplies the largest regular funding stream in feasible fixtures; interest, losses, capacity and liquidity constrain continued issuance. |
| Deposit/withdrawal and maturity | Cash/liability changes match; interest and principal settle once after reload; shortage follows resolution rules. |
| Sovereign/company loan lifecycle | Correct bank subject creditor, borrower, repayments and default; profile and advance rules apply. |
| Bank-to-overlord borrowing | Recurring facility creates native government bonds on separate sovereign/bank accounts; ownership consolidation does not retire them. |
| Equity subscription/resale | Charter equity, dilution, holder payment and dividends reconcile; financial ownership does not transfer territory. |
| Company equity/debt separation | Overseas equity and Merchant credit permissions remain distinct; ordinary sovereign company ownership does not expand bank permissions. |
| Goods/forwards/receipts | Quantities, encumbrance, transport, collateral and bilateral settlement reconcile. |
| Commenda outcomes | Capital and surplus split correctly; Discovery timing applies; discovery without actual receipts pays no profit. |
| Note-funded operations and rates | Circulation is recorded; issuance cannot back itself; fixed ordinary debts retain terms, while native bond coupons follow the verified rate/repricing model. |
| Company income waterfall | Direct native overlord receipts and subject payments are reconciled before distributions. |
| Default, bank run and guarantees | Losses and authorized public payments occur once; bank and sovereign accounts remain separate. |
| Last-building loss, annexation and reform loss | Claims close, transfer or wind down safely; controller bindings and one-bank cap reconcile. |
| Existing-save migration | No duplicated bank, investment, profile choice, research grant, reform, capital or account. |
| Multiplayer | Authorized subject GUI and financial effects execute consistently through synchronized commands. |

Run controlled fixtures for each age and profile, then campaigns for an independent banking nation and a landed controller. Include Discovery commenda before native companies unlock, Reformation corporate finance, and Absolutism collateralized instruments. Test later-age continuation, not only the unlock date.

Set a performance target before release, for example no more than a 10% increase in median monthly simulation time over an identical baseline. This is a proposed target, not a measured result. Report contract/entity counts and machine configuration with timings.

## 11. Processing order, persistence and cleanup

Within one mod-owned account pass:

1. Check schema, controller/subject/reform binding, one-bank cap, two-choice profile and servicing state.
2. Reconcile native cash, loans/bonds, current creditors, coupons, subject payments and disappeared targets. Recognize already-applied native costs/payments without paying them again.
3. Snapshot the opening royalty asset base; settle due contracts/deposit accrual and update realized activity earnings, funding costs and losses.
4. Update conservative capital/liquidity, process withdrawals and crisis states, and reserve due obligations/committed capital.
5. Assess and settle the monthly royalty within allowed cash/capital state; allocate its expense to the profit register and refresh the single current-tier loyalty modifier.
6. Calculate institution-wide loss carryforward and cash/capital-limited monthly dividends; pay all entitled holders and decrement bucket reserves.
7. Recompute capacity after payouts; execute the due native bond facility draw if authorized/fundable, then permit other profile-/age-/advance-eligible commitments. New proceeds do not retroactively increase that period's profit or royalty base.
8. Process accepted native bond/claim resales through their guarded settlement, reconcile current-holder metadata, and stamp issuance, royalty, dividends and account completion separately.

GUI acceptances may occur outside the monthly pass; they use the same transaction services and cannot trigger a second scheduled draw or payout. Choose a consistent cutoff for activity earnings and receipts, and include only settled available cash.

This list does not establish order relative to the engine's budget/coupon pass or country pulses. M0 must measure it. Coordinate the sovereign/bank pair under one settlement owner, use captured native receipts and safe scheduling/reconciliation when needed, and never let both countries pay the same royalty/coupon. A deterministic period stamp and native-claim identity prevent duplicate issuance, ownership transfers and distributions after callback/reload.

Store schema versions and migrate obsolete profile records once. New/existing-save initialization is guarded. Lifecycle changes suspend future royalty/dividend/draw authorization while preserving native sovereign debts, current creditors and existing claims. A stale reference must never silently become another target.

## 12. Balancing and exploit controls

Implement these as model rules and acceptance tests:

- Charter formation requires a native State Bank, capital-market ownership, the age-scaled investment and zero existing Chartered Banks.
- All of the initial cost becomes subject equity; the decision, framework price and reform activation cannot charge it twice.
- Subject bank cash and landed-country cash are distinct; all cross-entity transfers are explicit.
- Specialization is exclusive and persistent; conversion/research cannot provide an ordinary respec.
- Shared execution gates cover GUI, diplomacy, native purchase adapters, AI, research and lifecycle actions.
- Native estate-loan takeover retains native valuation and estate payments. Bond/bank-held resale instead pays the existing holder and preserves the same native debt; do not reuse the estate-compensation formula for it.
- Cash funding and committed capital limits apply before native effects execute.
- Deposit liabilities, note obligations and guarantees constrain lending capacity.
- Credit exposure and liquidity limits apply to both sovereign and company portfolios.
- Principal, subscriptions, deposits and issuance are excluded from distributable earnings.
- Warehouse encumbrance and collateral cannot be counted several times.
- Bank/company share cross-holdings cannot recursively manufacture capital.
- Company self-dealing and related-party transactions require explicit limits.
- An institution cannot use its own notes as backing for further issuance.
- Debt purchases, buybacks and refinancing cannot reset obligations for free.
- Converted subjects use the royalty/dividend rules instead of flat native tribute; unrestricted siphoning cannot bypass protected obligations.
- Royalty tiers lower both burgher satisfaction and subject loyalty, reduce bank equity when capital-funded, and never stack per-pulse penalties.
- Dividends follow actual ownership and net realized activity earnings with loss carryforward; royalties are charged once before dividends.
- Native bond proceeds are financing, not bank or sovereign earned income; coupons and redemption remain payable to the current creditor.
- Recurring draws require bank funding and native issuer capacity; new face value cannot become immediate profit or self-created backing.
- Controller coupon recycling is an internal transfer. Outside operations/funding and adequate debt service sustain expansion; increasing issuance alone cannot guarantee returns.
- A bond resale replenishes bank liquidity at the buyer's expense, creates no sovereign proceeds and does not reset principal/rate or erase acquisition losses.
- Public rescue and capitalization remain visible transfers; resolution suspends new extraction/draws.
- Monetary support and commercial privileges have bounded effects and appropriate costs.
- Exact earliest-age gates apply to restructuring, commodities, commenda, corporate credit/debt and collateralization; later upgrades require further advances.

Calibrate rates, royalty/loyalty tiers, activity payout ratios, debt-first targets, bank reserves, sovereign debt service, resale discounts/demand, storage costs, risk spreads and confidence through recorded scenarios. Initial values are tuning parameters, not claimed historical constants.

## 13. Compatibility and release requirements

Maintain a manifest of every native override. Review native State Bank conversion rules; decision/GUI dispatch; estate-loan takeover; sell_bonds/redeem_bonds and can_sell_bonds/capacity; bond ownership/coupon/redemption routing and rate repricing; current-holder resale; royalty loyalty fields; subject tribute/siphon removal; advance ownership; branches; and company creation/native distributions.

Prefer custom interactions and appended child hooks over replacing large native files. Do not patch vanilla company payment formulas until measured receipts demonstrate why a change is needed. Preserve other mods' hooks in compatibility tests.

Keep the core independent of a third-party UI framework unless a verified requirement justifies a dependency. A community framework can provide optional menu integration, but it must not become an unexamined dependency or change financial simulation behavior.

Before each game-patch update:

1. Diff the native keys and schemas recorded at M0.
2. Regenerate scripting/GUI documentation.
3. Re-run native adapter and initialization probes.
4. Review all replacements and company payment/assignment behavior.
5. Re-run ledger, lifecycle, multiplayer and campaign tests.
6. Update supported_game_version only after the target version passes.

Release documentation must identify completed features, supported patches, required dependencies, save-compatibility limits, known abstractions and the override manifest. Respect licenses and obtain permission where required before distributing another mod author's code or assets; example repositories are references, not automatic reuse grants.


## 14. Definition of done

The implementation is complete when:

- A landed country with an eligible native State Bank, capital-market control and sufficient current-age investment can charter it through the decision.
- Conversion preserves the existing bank tag and transfers the entire cost into subject equity.
- The new subject type is Chartered Bank; the landed controller receives State Chartered Bank with benefits and direct financial GUI access.
- No country has more than one active Chartered Bank after chartering, migration or lifecycle reconciliation.
- Independent and chartered banks choose Merchant Finance or Overseas Investment exactly once; both have common sovereign-credit/bond functions and cannot originate the other profile's corporate/commodity/venture instruments.
- Eligible estate loans use regular banks' native takeover; existing native bonds/claims can be resold with payment to the current holder and preserved sovereign obligations.
- The landed Treasury Funding GUI controls scalable monthly royalty with both loyalty costs, realized activity dividends and recurring low-interest bank-funded native government bonds.
- Bond proceeds, coupon costs, redemption and current-holder receipts reconcile once; borrowing is the primary funding stream in feasible bank-led scenarios, without being counted as earned profit.
- Debt restructuring requires Renaissance; commodities and commenda require Discovery; trade-company corporate credit/debt requires Reformation; collateralization requires Absolutism; each requires its advance.
- Later ages progressively unlock the most advanced monetary, security, clearing and risk-management features.
- Native trade companies operate and receive profile-permitted banking services while political and financial ownership remain distinct.
- Cash, assets, deposits, equity, notes, guarantees and distributions reconcile on the correct bank/subject/sovereign entities.
- AI, direct GUI, diplomacy, saves, migration, lifecycle changes and multiplayer obey the same permissions.
- The release is tested against an identified patch with accurate overrides and player explanations.

## 15. Source register

Links are provided for development inspection. Native-file copies and documentation mirrors must be compared with the installed patch before implementation.

| ID | Source | How used and access status |
| --- | --- | --- |
| S1 | [Publisher: Tinto Talks #85 — Modding](https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-85-22nd-of-october-modding.1864004/) | Canonical publisher overview identified; full page inaccessible during preparation. Not treated as a fully read schema reference. |
| S2 | [Official-hosted EUV wiki: Modding](https://eu5.paradoxwikis.com/Modding) | Indexed metadata/debug/documentation guidance checked; full-page access blocked. |
| S3 | [Official-hosted EUV wiki: Mod structure](https://eu5.paradoxwikis.com/Mod_structure) | Indexed metadata requirement checked; full-page access blocked. |
| S4 | [Engine-generated effects mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/effects.log) | Retrieved: native loans/goods/estates and sell_bonds/redeem_bonds summaries. Issuance funding and bond payee transfer still require local probes. |
| S5 | [Engine-generated triggers mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/triggers.log) | Retrieved: creditworthiness/debt/estate inputs plus bond_capacity, current_bonds, num_bonds and is_bond. Exact units remain patch-specific. |
| S6 | [Engine-generated on_actions mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/on_actions.log) | Retrieved and relevant entries inspected: monthly, loan, bankruptcy, exploration and annexation callbacks and default scopes. |
| S7 | [Engine-generated event scopes mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/event_scopes.log) | Retrieved and relevant entries inspected: native entity/scope types, including loans, estates, markets and trades. |
| S8 | [Engine-generated scope links mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/event_targets.log) | Retrieved and relevant entries inspected: borrower, market price, stockpile and exploration links. |
| S9 | [Engine-generated GUI data types mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/data_types_gui.txt) | Relevant entries inspected for scripted GUI support; exact display/execute binding is a local prototype requirement. |
| S10 | [Native trade_company definition reproduced by EU5DB](https://eu5db.com/subject_type/trade_company) | Definition read: building-based republic subject and its native relationship rules. |
| S11 | [Native trade_company_headquarters definition reproduced by EU5DB](https://eu5db.com/building/trade_company_headquarters) | Definition read: creation, banking reform reuse, owner assignment, home region, subject registry and owner/overlord income hooks. |
| S12 | [Community Mod Toolkit](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-toolkit) | Repository and its metadata.json/.editorconfig read as primary template examples; sample supported versions are not compatibility claims for this mod. |
| S13 | [Bank Mechanic Improvements source](https://github.com/rob-marsh-dev/banking-mechanic-improvements) | Earlier banking interaction, reform and building examples inspected; use as implementation reference, not proof of target-patch compatibility. |
| S14 | [Commenda — user-provided historical reference](https://en.wikipedia.org/wiki/Commenda) | Article read for unilateral/bilateral partnership structure, profit allocation and capital-loss exposure. |
| S15 | [Official-hosted EUV wiki: Interface modding guide](https://eu5.paradoxwikis.com/Interface_modding_guide) | Implementation reading target; not fully accessed during preparation. Verify alongside local GUI schemas. |
| S16 | [Official-hosted EUV wiki: Scripted GUI](https://eu5.paradoxwikis.com/Scripted_gui) | Implementation reading target; verify against installed scripted GUI schema and data-type dumps. |
| S17 | [Official-hosted EUV wiki: Localization](https://eu5.paradoxwikis.com/Localization) | Implementation reading target; encoding and template layout were corroborated from the current toolkit. |
| S18 | [Native State Bank definition reproduced by EU5DB](https://eu5db.com/subject_type/state_bank) | Read for native state_bank identity, building-based relationship, existing overlord benefits and subject behavior; convert this existing entity. |
| S19 | [Native Take over Loan definition reproduced by EU5DB](https://eu5db.com/country_interaction/take_over_loan) | Read for native eligibility, purchase-cost script value, estate compensation and creditor assignment; no custom loan exchange is inferred. |
| S20 | [Native ages reproduced by EU5DB](https://eu5db.com/age) | Read for the six native age identifiers and their ordering; calendar years are not used as unlock checks. |
| S21 | [Native Trade Companies advance reproduced by EU5DB](https://eu5db.com/advance/trade_companies_advance) | Inspected as a native advance/unlock reference; exact financial-advance schema and actor research ownership remain target-patch audits. |
| S22 | [Native generic actions reproduced by EU5DB](https://eu5db.com/generic_action) | Read for own-country action patterns; confirm the installed patch's actual decision loader before implementing the charter decision. |
| S23 | [Versioned 1.3.10 script-documentation changes](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/1.3/1.3.10/changes_script_docs.md) | Retrieved: native government-bond effects, triggers and modifiers recorded as additions; requires patch capability verification. |
| S24 | [Engine-generated modifier definitions](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/modifiers.log) | Retrieved: bond_interest, can_sell_bonds, subject_loyalty and burghers_estate_target_satisfaction exist as country modifier fields; units/application require M0. |
| S25 | [Native Central Bank building](https://eu5db.com/building/central_bank) | Definition read for bond-specific interest/capacity/size modifiers and capital-building rules; not proof of creditor routing. |
| S26 | [Native Bank of England reform](https://eu5db.com/government_reform/bank_of_england_reform) | Definition read for bond_interest and max_bonds_modifier, illustrating that bond rate differs from bank_interest. |
| S27 | [Native Central Banking advance](https://eu5db.com/advance/central_bank_advance) | Definition read: Absolutism, Manufactories prerequisite, embraced Banking and central-bank building unlock. The mod's basic charter authorization is an explicit separate design choice. |

### Evidence boundary

The architecture, financial contracts, accounting model, AI rules, milestone sequence and acceptance criteria are original proposed mod design. The cited native hooks and structures are implementation foundations. No local EUV installation or campaign was available for validation while preparing this document; M0 converts the published evidence into a tested target-patch contract.

