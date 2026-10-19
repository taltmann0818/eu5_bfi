# Europa Universalis V: Banking, Finance and Trade Companies
## Technical implementation specification

**Current authority:** [docs/coverage.md](docs/coverage.md) unifies the implementation plan, M0–M10 status, remaining work and acceptance evidence. This document remains an engineering reference; its older royalty/per-activity-payout examples are superseded by the unified deposit-interest, share-dividend and operating-expense rules. Follow the canonical plan and current runtime rather than implementing those obsolete examples.

Prepared 14 October 2026. Namespace: `bfl_`; event namespace: `bfl_finance`.

Revised 14 October 2026: Community Mod Framework (CMF) is a required dependency. Banking and finance management is embedded in the existing Economy panel; the mod adds no action bar or separate finance launcher.

This is the engineering companion to the [unified feature and implementation plan](docs/coverage.md). It describes file responsibilities, persistent records, transaction services, native integrations, interface, graphics, FX and verification for the complete mod. Illustrative skeletons are not evidence of completed gameplay; consult the unified milestone register for current delivery and validation.

The unified plan is the source of feature requirements. Illustrative scripts and references here must be evaluated against the installed game. Preserve the one-bank charter architecture, two profiles, native debt/companies and research gates, but apply the current deposit-interest/share-dividend/operating-expense policy in place of the original royalty channel and per-activity payout controls.

The later interface requirement supersedes the attachment's optional-framework recommendation: use CMF's shared services and keep the native economy interface as the player's management surface. CMF's Community Mod Menu (CMM) holds presentation preferences; institution accounts and financial commands remain in the Economy panel and the mod's accounting services.

**Evidence labels used below:** **Local** means inspected in this installation; **Published** means described in public documentation; **Design** means a proposed mod implementation; **Probe** means engine behavior still requiring an experiment. Code marked **skeleton** combines native patterns with mod services that must be written; it must not be copied into a release as a complete implementation.

## Contents

1. [Installed baseline and feasibility](#1-installed-baseline-and-feasibility)
2. [Repository, mod folder, and file responsibilities](#2-repository-mod-folder-and-file-responsibilities)
3. [Script conventions and native adapters](#3-script-conventions-and-native-adapters)
4. [Persistent records and accounting](#4-persistent-records-and-accounting)
5. [Initialization, monthly processing, and lifecycle](#5-initialization-monthly-processing-and-lifecycle)
6. [Chartering, reform, and specialization](#6-chartering-reform-and-specialization)
7. [Permission service and advance tree](#7-permission-service-and-advance-tree)
8. [Deposits and foreign branches](#8-deposits-and-foreign-branches)
9. [Native credit, government bonds, resale, and restructuring](#9-native-credit-government-bonds-resale-and-restructuring)
10. [Royalty, dividends, and recurring treasury funding](#10-royalty-dividends-and-recurring-treasury-funding)
11. [Concessions, guarantees, and security](#11-concessions-guarantees-and-security)
12. [Commodity inventory, receipts, and forwards](#12-commodity-inventory-receipts-and-forwards)
13. [Equity and commenda](#13-equity-and-commenda)
14. [Native trade-company operations](#14-native-trade-company-operations)
15. [Currency, rates, and interbank liquidity](#15-currency-rates-and-interbank-liquidity)
16. [Crises and resolution](#16-crises-and-resolution)
17. [GUI, interactions, localization, and AI](#17-gui-interactions-localization-and-ai)
18. [Graphics and FX production](#18-graphics-and-fx-production)
19. [Build, testing, compatibility, and release](#19-build-testing-compatibility-and-release)
20. [Requirement coverage and evidence register](#20-requirement-coverage-and-evidence-register)

## 1. Installed baseline and feasibility

### 1.1 Paths and version identity

| Purpose | Path or value |
| --- | --- |
| Working repository | `C:\Users\Thomas Altmann\Documents\ChatGPT\EU5_BFI` |
| Installed game, read only | `C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V` |
| Game content root, called `GAME` below | `<installed game>\game` |
| Workshop subscription cache, read only | `C:\Program Files (x86)\Steam\steamapps\workshop\content\3450310` |
| User data and existing logs | `C:\Users\Thomas Altmann\Documents\Paradox Interactive\Europa Universalis V` |
| Installed uploader | `C:\Users\Thomas Altmann\Downloads\release-windows-gui-amd64` |
| Installed CMF, read only | `C:\Program Files (x86)\Steam\steamapps\workshop\content\3450310\3692202776` |
| CMF baseline | Release `2.5.0`; metadata targets `1.4.*` and records `cmf_last_updated_game_version = 1.4.0` |
| Steam application | `3450310` |
| Steam manifest at inspection | `buildid = 25606497`; `BetaKey = 1.4-open-beta` |

**Local:** The Steam manifest identifies the branch/build above. The Windows executable's version resource reports `1.0`, which is not sufficient to identify the gameplay patch. Before implementation, record the displayed game version and checksum as well as this build ID. Do not interpret the branch name as proof of a particular final 1.4 release or advertise compatibility with every 1.4 build. Existing logs are historical evidence, not a fresh test run.

Develop under the repository. Let the current EU5 mod tools register a development mod and establish its local discovery path; use their generated metadata as the starting point. The Workshop directory is a downloaded-content cache, not the source workspace or the development install destination. Do not edit the installed game or subscribed mods to implement this project.

### 1.2 What the local audit establishes

All paths in this table are relative to `GAME`.

| Local source | Observed implementation consequence |
| --- | --- |
| `in_game/common/decisions/test_decisions.txt`, `manila_galleon_charter.txt` | This build has an actual decisions loader. Use `decision_category`, `potential`, `allow`, `option`, and option `effect` for chartering. The original plan's warning against assuming a decisions directory is resolved for this build. |
| `in_game/common/subject_types/state_bank.txt` | Building subject; native tribute uses `subject_pays_vassal`; overlord bonuses are `bank_interest = -0.005`, `max_bonds_modifier = 0.33`. Copy the relationship into a new subject definition, remove automatic extraction, and move these bonuses to the charter reform once. |
| `in_game/common/prices/03_diplomacy.txt` | Vassal tribute is `scaled_gold = 0.2`; company tribute is `scaled_gold = 0.5`. These are prices, not custom income variables. Do not globally change either price. |
| `in_game/common/government_reforms/country_specific.txt`, `banking_country` | Banking eligibility already explicitly excludes `trade_company`. Continue to classify companies by their subject type first. |
| `in_game/common/advances/0_age_of_renaissance.txt`, `banking_advance` | Native Renaissance banking grants `can_sell_bonds = yes`. Basic bond permission is not confined to Absolutism Central Banking in this installation. |
| `in_game/common/advances/0_age_of_absolutism.txt`, `central_bank_advance` | Requires Manufactories, tests embraced Banking, unlocks the central-bank building, adds five bonds. Preserve this separate later progression. |
| `in_game/common/advances/0_age_of_reformation.txt`, `trade_companies_advance` | Native companies and their buildings unlock in Reformation and require `safe_exploration_techniques_advance`. Discovery commenda therefore needs earlier eligible country/estate operators. |
| `in_game/common/country_interactions/take_over_loan.txt` | Native takeover excludes bonds and country-held loans. It pays banking estates and transfers the same loan. A bond resale needs a different settlement path. |
| `in_game/common/script_values/bank_loan_takeover.txt` | Takeover price is loan amount plus interest using buyer `bank_interest`, remaining months, and division by 12. Preserve the expression and rounding. |
| `in_game/common/building_types/trade_company_buildings.txt` | Headquarters creates a building country, assigns subject type, sets capital/home region, transfers headquarters ownership, and records company registries. There are both company-owner and direct-overlord income hooks. |
| `in_game/common/building_types/unique_buildings.txt`, `banking_office` | Existing foreign bank office requires good relations, banking reform, settlement eligibility, and maintenance; it already provides owner income. Extend servicing around this real facility. |
| `in_game/common/on_action/_hardcoded.txt` | Loan callbacks document country root, loan `scope:target`, and optional lender `scope:owner`. Do not assume a lender exists for estate claims. |
| `in_game/common/scripted_guis/scripted_guis.info` | Scripted GUI supports `saved_scopes`, availability checks, effects, and AI fields. Native economy GUI demonstrates `GetScriptedGui(...).Execute(GuiScope...)`. |
| `main_menu/gui/scripted_widgets/_scripted_widgets.info` | A text registry can mount an external GUI widget without replacing a large native window. Registered widget visibility must evaluate a function. |
| `main_menu/common/modifier_type_definitions/00_modifier_types.txt` | Burgher target satisfaction is a percentage field. Subject loyalty is numeric. `bond_interest` is a percentage with a declared minimum of `0.01`. Test actual coupon units and clamping before specifying a low rate. |
| Installed CMF `.metadata/metadata.json`, `in_game/common/on_action/cmf_on_actions.txt` | CMF 2.5.0 supplies registration, load/transfer, and human-player lifecycle hooks. These supplement the all-institution accounting scheduler. |
| Installed CMF `in_game/gui/vanilla/` and published extraction coverage | No extracted economy GUI or economy injection slot was found. An explicit, versioned `economy_lateralview.gui` override is required; CMF does not make same-widget overrides automatically composable. |

### 1.3 Native feasibility audit — completed

M0 is complete for the pinned single-player baseline. The [final audit](docs/m0-probes.md) answers P01–P12 with measured native outcomes, normal UI evidence and explicit unsupported boundaries. The questions below preserve the original engineering requirements; production adapters and broader campaign acceptance belong to later milestones. Source documentation alone does not expose the executable's complete bond accounting. [Published effect documentation](https://raw.githubusercontent.com/Europa-Universalis-5-Modding-Co-op/modding-digests/main/current_docs/effects.log) describes country-scope bond issuance, loan-target redemption, loan-scope creditor changes, and country market purchases/sales. These descriptions do not establish bank-directed funding or payment routing.

The completed development-only probe suite runs separately from production adapters. Use two banks, one sovereign, one company, and controlled estate balances. For each operation log before/after cash, estate gold, native debt, count, owner, face, rate, and available capacity; advance time through a coupon boundary and save/reload.

| Probe | Exact question | Completion condition |
| --- | --- | --- |
| P01 charter | Does `change_subject_type` preserve the same country, buildings, native claims, and mod variables? Does a zero tribute price work? | Same bank and obligations, no automatic native tribute or siphon path. |
| P02 GUI | Can a player-root command act on a saved subject bank through the native scripted-GUI command? | Controller validated at execution; wrong-controller command rejected; single-player authority validated. |
| P03 sovereign issuance | Native ownership feasibility was audited; the authorized custom ledger replaces that target. | One bank debit and issuer credit; persistent custom identity and no issuance profit. |
| P04 sovereign holder | Custom current-holder secondary transfer, coupon/redemption and acquisition basis. | Both Stock Exchange research/building gates, funded same-claim settlement, replay and reload. Native ordinary-claim resale remains blocked. |
| P05 rate | Custom fixed annual coupons, monthly cent carry and prospective controls. | Existing issues never reprice; native note/circulation semantics retain their own gate. |
| P06 native credit | Does `give_loan` move both wallets? When do interest, repayment, renewal, default, and bankruptcy mutate balances and fire callbacks? | Adapters never duplicate native transfers; realized interest is distinguishable from principal. |
| P07 receipt observation | Can actual per-instrument coupon/interest receipts and net company operating receipts be read or reliably observed? | Profit register uses settled earnings, not unexplained treasury deltas or forecasts. |
| P08 storage | Are country/estate/loan/building references persistent? Which scopes accept variables? Are variable maps iterable and stable? | Reload and destroyed-target tests pass; bounded slots work where maps do not. |
| P09 goods | Can a bank purchase/sell at its capital and permitted branch custody? Does requested amount equal executed amount? | Stockpile, cash, price, and capital/access semantics measured. |
| P10 scheduling | Where are native budget and coupon processing relative to monthly country pulses? | One documented cutoff and one owner for pair settlement; no double monthly execution. |
| P11 native commands | Can native loan takeover, bonds, trade creation, and exploration be dispatched by the subject actor? | Subject, rather than controller, owns the financial action and pays its cost. |
| P12 CMF/economy integration | Do CMF 2.5.0 registration/load hooks and the economy override preserve native controls, data contexts, templates, authority? | Finance is usable inside the existing Economy view; native tabs/budgets still work; no BFL action-bar element, launcher, or duplicate settlement. |

The native country-creditor bridge failed the installed-build probe. On 15 October 2026 the user authorized custom sovereign bonds. The funded issuer-owned custom ledger replaces the native-bond requirement; no custom operation creates or pays a native bond. Other native credit/goods/project adapters retain their own gates. Secondary selling and buying both require the native Stock Exchange advance and an owned built Stock Exchange.

## 2. Repository, mod folder, and file responsibilities

### 2.1 Source tree

The following is the **proposed** repository layout. Only `mod/bfl/` is packaged as the playable mod. This document does not create these folders.

```text
EU5_BFI/
  EUV_Banking_Finance_Trade_Companies_Technical_Implementation.md
  README.md
  docs/
    baseline.json                    # branch/build/version/checksum and source hashes
    native_capabilities.md           # P01-P12 results and measured signatures
    ledger_schema.md                 # enums, fields, owners, units and migrations
    overrides.csv                    # native keys touched, reasons, hashes, patch
    cmf_integration.md               # tested CMF release, hooks, settings and GUI ownership
    acceptance.md                    # fixtures, evidence, pass/fail
    balance.md                       # tuning scenarios and results
    asset_register.csv               # artwork, source, license, export and consumer
  design/
    instruments.json                 # permissions and progression, one source of truth
    advances.json                    # ordered prerequisite graph
    slots.json                       # bounds, field lists and enum values
    goods.json                       # selected native goods and storage rules
    tuning.json                      # rates, buffers, limits and royalty tiers
  tools/
    generate_scripts.py              # deterministic slots, selectors and gates
    validate_sources.py              # names, paths, braces, BOM and localization
    ledger_reference.py              # offline transaction arithmetic model
    stage_release.ps1                # copies explicit allowlist to dist/
    compare_native.ps1               # read-only hashes/diffs against pinned build
    build_economy_gui.py              # pinned economy definitions + minimal panel insertion
  tests/
    accounting/                      # offline sequences and rounding fixtures
    fixtures/                        # age/profile/scenario setup descriptions
    probe_mod/                       # separate mod; never packaged with production
    results/                         # logs and recorded native balances
  assets_source/
    icons/                           # editable layered originals
    illustrations/
    models/                          # only if optional map art is developed
    fx/                              # storyboard, particles and timing references
  publishing/
    manager-config.json
    steam_page_english.bbcode
    change_notes/english/0.1.0.bbcode
  mod/bfl/
    .metadata/metadata.json
    thumbnail.png
    in_game/
      common/
        decisions/bfl_charter_decisions.txt
        subject_types/bfl_chartered_bank.txt
        government_reforms/bfl_charter_reform.txt
        advances/bfl_financial_advances.txt
        prices/bfl_prices.txt
        building_types/bfl_warehouse_buildings.txt
        production_methods/bfl_warehouse_methods.txt
        country_interactions/
          bfl_deposit_interactions.txt
          bfl_credit_interactions.txt
          bfl_debt_resale_interactions.txt
          bfl_security_interactions.txt
          bfl_equity_interactions.txt
          bfl_commenda_interactions.txt
          bfl_monetary_interactions.txt
        scripted_triggers/
          bfl_roles.txt
          bfl_authority.txt
          bfl_permissions.txt
          bfl_contract_validation.txt
        script_values/
          bfl_tuning.txt
          bfl_capital_and_liquidity.txt
          bfl_rates_and_quotes.txt
          bfl_treasury_policy.txt
          bfl_ai_scores.txt
        scripted_effects/
          bfl_bootstrap.txt
          bfl_charter.txt
          bfl_transaction_core.txt
          bfl_native_credit_adapter.txt
          bfl_native_bond_adapter.txt
          bfl_native_goods_adapter.txt
          bfl_native_trade_adapter.txt
          bfl_native_receipts_adapter.txt
          bfl_reconciliation.txt
          bfl_monthly_settlement.txt
          bfl_deposits.txt
          bfl_branches.txt
          bfl_treasury_payments.txt
          bfl_security.txt
          bfl_commodities.txt
          bfl_equity.txt
          bfl_commenda.txt
          bfl_company_operations.txt
          bfl_monetary.txt
          bfl_resolution.txt
          bfl_migrations.txt
          bfl_generated_slots.txt
          bfl_cmf_registration.txt
          bfl_cmf_alerts_and_log.txt
        scripted_guis/
          bfl_navigation.txt
          bfl_account_commands.txt
          bfl_treasury_commands.txt
          bfl_investment_commands.txt
          bfl_company_commands.txt
          bfl_resolution_commands.txt
        on_action/
          bfl_hooks.txt                # all-institution/native financial callbacks
          bfl_cmf_hooks.txt            # CMF registration, load, player transfer and UI refresh
        customizable_localization/bfl_finance_text.txt
      events/bfl_finance/
        bfl_specialization.txt
        bfl_contract_offers.txt
        bfl_distress.txt
        bfl_notifications.txt
        bfl_migration_choices.txt
      gui/
        economy_lateralview.gui        # explicit native-path override; finance stays inside
        bfl_economy_finance.gui         # finance section types/templates, no top-level window
        bfl_finance_components.gui
        bfl_company_sections.gui       # company detail content hosted by economy section
        vanilla/bfl_economy_vanilla_types.gui  # only while CMF lacks economy extraction
    main_menu/
      common/
        static_modifiers/bfl_financial_modifiers.txt
        game_concepts/bfl_finance_concepts.txt
        modifier_icons/bfl_finance_icons.txt
        named_colors/bfl_finance_colors.txt
      gui/cmf_dependency_check.gui      # release-matched CMF dependency popup template
      gui_animations/bfl_finance_animations.json
      localization/english/
        bfl_core_l_english.yml
        bfl_actions_l_english.yml
        bfl_advances_l_english.yml
        bfl_events_l_english.yml
        bfl_gui_l_english.yml
        bfl_tooltips_l_english.yml
        bfl_cmf_l_english.yml           # CMM preferences, CMF alerts and log entries
      gfx/interface/
        icons/bfl/                    # directly referenced GUI textures
        icons/subject_types/bfl_chartered_bank.dds
        icons/government_reforms/illustrations/bfl_state_chartered_bank.dds
        icons/buildings/bfl_bonded_warehouse.dds
        advance/                     # one bfl_<advance-key>.dds per custom advance
        illustrations/bfl/            # charter, profiles, venture, distress
      gfx/models/bfl/                 # optional .asset/.mesh/material files
      gfx/particles/bfl/              # optional .particle2 and exported textures
  dist/                              # generated release staging; ignored by Git
```

Folder assignment follows the inspected load stages: gameplay in `in_game`, reusable interface textures/localization/static modifiers in `main_menu`. `scripted_modifiers` contains AI/weight macros in this engine; it is not the place for royalty country modifiers. Definitions in `main_menu/common/modifier_type_definitions` are unnecessary unless adding a genuinely new modifier value consumed by mod scripts.

The warehouse is the only proposed new gameplay building. Omit its definition and production-method files if existing native warehouse custody is sufficient after P09. Optional model/particle directories ship only when their verified consumers exist. No setup/history override is required to initialize existing banking countries and companies dynamically.

The economy override keeps the native filename and widget identity deliberately. Its extracted vanilla definitions preserve native identifiers; new finance types use `bfl_` identifiers. There is no finance scripted-widget launcher registry. See section 17 for the CMF coverage boundary and the build rule that prevents duplicate extracted definitions.

### 2.2 Metadata and file writing

Metadata follows the [community toolkit's EU5 example](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-toolkit/blob/main/.metadata/metadata.json). This is a template; replace the version placeholder after testing.

```json
{
  "name": "Banking, Finance and Trade Companies",
  "id": "bfl_banking_finance_companies",
  "version": "0.1.0",
  "game_id": "eu5",
  "supported_game_version": "<tested semantic version>",
  "short_description": "Banks, chartered sovereign finance and native trade-company investment.",
  "tags": ["Trade and Economics", "Government and Estates", "Gameplay"],
  "relationships": [
    {
      "rel_type": "dependency",
      "id": "community_mod_framework",
      "display_name": "Community Mod Framework",
      "resource_type": "mod",
      "version": "2.*"
    }
  ],
  "game_custom_data": {}
}
```

Use UTF-8 with BOM for game script/GUI/localization files where required by the current EU5 template and preserve native newline conventions. Use plain UTF-8 for Markdown, JSON generators, and Python. Localization starts with `l_english:` and uses unique quoted keys/values. Validate the exact metadata schema in the installed mod tools; a branch/build record belongs in development documentation, not an invented launcher field.

Do not put `.metadata` below `in_game`, add an EU4 `descriptor.mod` as the assumed discovery mechanism, or copy the whole game folder. Package new keys and narrowly required compatibility edits only. Generator output is committed or reproducibly built before packaging; Python is never needed by the running game.

### 2.3 CMF dependency and integration contract

Declare CMF using the [framework's dependency metadata](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework#getting-started), and add [CMF Workshop item 3692202776](https://steamcommunity.com/sharedfiles/filedetails/?id=3692202776) as a required item on the eventual mod page. The declared `2.*` relationship identifies the framework API family; the initial audit baseline and in-game test target is **2.5.0**, not an assertion that every 2.x release works. Verify resolved playset order with CMF active and BFL's native-path economy override winning its intended file. Successful runtime compatibility remains a P12 acceptance requirement.

Pin the installed release's metadata and relevant source hashes alongside the game baseline. At this audit, GitHub `main` at commit `38fe85623ada459207adc73fe8acffcd039e71ba` described a `2.4.1` development package for `1.3.*` with ID `community_mod_framework.dev`, while the installed Workshop release was `2.5.0` with ID `community_mod_framework`. Do not install that development package as though it were the target dependency or use mutable wiki examples to override inspected 1.4 hook definitions.

Use CMF concretely for:

- Idempotent registration through `cmf_on_mod_registration` and public CMM setting effects for presentation preferences.
- Verified post-lobby/load/player-transfer hooks to rebuild navigation and UI-derived state.
- Existing alert-bar notifications that open the native `economy` view.
- Shared action-log entries for meaningful completed financial/policy actions.
- Its established vanilla-definition extraction approach when maintaining the economy override, subject to the missing-coverage rule in section 17.

Do not call `cmf_add_action_bar_element`, register a BFL action-bar button, replace the topbar, or expose a separate finance launcher/window. Optional CMF features used by other mods do not change BFL's entry point. CMM settings must not hold deposits, portfolios, profile choice, royalty policy, or bank-facility state.

Include the release-matched, self-contained `main_menu/gui/cmf_dependency_check.gui` template described by the [CMF dependency-popup documentation](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/Dependency-Check-Popup); retain its required identifiers/license and audit any front-end conflict. Missing CMF is an unsupported dependency state, not permission to create a fallback action bar. Do not bundle CMF's full runtime or edit its subscribed installation; distribute the declared dependency and only the documented helper template.

## 3. Script conventions and native adapters

### 3.1 Naming and service boundaries

Every mod database key, variable, effect, trigger, script value, widget, and localization key starts with `bfl_`. Use event IDs such as `bfl_finance.100` with `namespace = bfl_finance`. Refer to native objects through their existing identifiers: `subject_type:state_bank`, `government_reform:banking_country`, native good keys, ages, buildings, and companies.

Preserved native economy definitions and the official CMF dependency-helper identifiers are explicit exceptions to renaming: retain their required keys to preserve framework/native consumers. Do not replace CMF core effects, CMM storage, or private `_cmf_`/`_cmm_` implementations. Extend documented hooks only by appending BFL child hooks.

Write `bfl_roles.txt` with an explicit classification order: native trade company first; valid chartered bank second; unchartered native State Bank third; independent banking country last. Independent banking requires building-country identity, the native banking reform, and **no subject relationship**, not merely absence of the two bank subject types. Unchartered State Banks keep native operations and obligation servicing; they do not receive expanded charter authorization before the decision. Other bank arrangements require a separately audited eligibility rule.

Each command has an explicit scope contract, written above its definition:

```text
# bfl_accept_debt_resale -- CONTRACT, not an engine function signature
# root: authorized human/AI command actor
# saved scopes: bfl_bank (buyer), bfl_seller, bfl_borrower, bfl_claim
# inputs: offer slot + generation; quote already stored on authoritative seller
# effects: one buyer-to-seller payment; same native claim gets new owner
# rejection: no balance/claim changes; return a localized reason
```

Pass arguments using the installed engine's scripted-effect macro conventions, saved scopes, and persistent slot fields. These comments are not a new runtime parameter language. A service must not rely on an undocumented chain of `prev` or assume player/root always equals the bank.

### 3.2 Native integration layer

Only adapter files call native financial effects. All user, diplomatic, event, and AI routes call the same validated `bfl_` services. One adapter owns each native action's accounting.

| Adapter/service | Required inputs | Native authority and required output |
| --- | --- | --- |
| `bfl_native_credit_adapter` | lender, borrower, amount, rate, duration | Native `give_loan`; capture actual loan and wallet changes. No second origination transfer. |
| `bfl_native_takeover` in credit adapter | buyer, eligible borrower/claim | Native takeover filters, exact price, estate payout, same claim owner change. |
| `bfl_bond_issuance` / `bfl_bond_settlement` | issuer, underwriting bank, policy | Funded custom issue and fixed-rate current-holder settlement; native issuance remains unused. |
| `bfl_bond_trading` | custom issuer/slot/generation, seller, buyer, price | Both Stock Exchange gates, funded existing-holder sale, preserved fixed terms and basis; native ordinary-claim transfer remains separately blocked. |
| `bfl_native_receipts_adapter` | native claim/company and cutoff | Actual interest/coupon/profit facts already settled by native accounting. Never pay again. |
| `bfl_native_goods_adapter` | owner, market, good, quantity, custody | Executed purchase/sale cash and physical stock changes. |
| `bfl_native_trade_adapter` | company, markets, good, merchant, capacity | Native trade operation under company actor; actual capacity/cost/income behavior. |

Adapter headers record native source path/hash, scope/signature, cash authority, rate units, callback timing, invalid-target behavior, and probe ID. Unsupported adapters reject commands before changing cash. Do not define a custom effect with the same name as a native effect to hide missing engine functionality.

### 3.3 Transaction protocol

1. Resolve participants and authoritative record; verify role, ownership, consent, profile, research, age, funds, capacity, and live native object.
2. Verify offer/slot generation and quote revision. Expired/stale offers fail before payment.
3. Acquire a mod operation guard on each affected institution in a deterministic order; reject re-entry.
4. Snapshot all values and reserve destination slots before financial mutation. Fail cleanly on registry exhaustion.
5. Execute the tested native action, or one paired transfer for a wholly custom cash transaction.
6. Update liabilities, asset basis, ownership, earnings classification, and exposure exactly once.
7. Reconcile expected/native outcomes, close or advance the record, set transaction/period stamps, release guards, and refresh display snapshots.

Scripts do not provide database rollback. Therefore prevalidate every stage, keep the committed effect chain immediate and short, and make repair states explicit. If a native operation's postconditions fail, freeze the affected record and alert the player/developer; do not guess compensation by creating cash. Never show an acceptance event between debit and credit.

For deterministic amounts, use the engine's measured fixed-point precision. Compute each payment once, retain division remainder on its account, and use the same amount for payer and payee. Generated distribution slots pay in a stable order and give a deterministic final remainder; independently rounded ownership fractions must not create or destroy money.

## 4. Persistent records and accounting

### 4.1 Storage model

Use existing countries, buildings, markets, estates, and native loan objects. No dummy country/character per contract. Native country `gold` is spendable bank/company/sovereign cash. Never mirror it into a second authoritative cash variable.

Start with generated fixed slots using ordinary variables and scope-valued variables. Variable maps are an optimization after P08 proves valid keys, persistence, iteration, and GUI use. Composite keys such as `(good, market, owner)` are a logical design, not an assumed native map feature.

Suggested configurable initial bounds per bank: 32 aggregate depositor accounts, 32 custom contract slots, 16 inventory/custody lots, 16 shareholder pools, 16 outstanding resale offers, and 16 branch records. These are tuning defaults; capacity exhaustion disables creation with an explanation and never overwrites a live obligation. Native debt remains native even when a custom view reaches its display page limit.

Example generated field names:

```text
bfl_dep_01_active                 # bool
bfl_dep_01_generation             # increasing number for safe slot reuse
bfl_dep_01_party                  # persistent country or approved estate identity
bfl_dep_01_principal              # gold, nonnegative
bfl_dep_01_interest_due           # gold; liability, not new cash
bfl_dep_01_annual_rate            # internal annual fraction
bfl_dep_01_maturity_period        # normalized simulation period
bfl_dep_01_withdrawal_requested   # gold
bfl_dep_01_state                  # enum: demand/term/queued/closed
```

Store each optional scope with an existence check. A missing scope is not a zero balance or permission to substitute the current player. If native estate scopes are not durable, store depositor country plus native estate type; resolve the live estate at execution. For loan metadata, prefer fields on the native loan if that scope accepts persistent variables; otherwise use a tested persistent loan reference from a bounded lender slot. Borrower/amount/rate alone is not a unique claim identifier.

### 4.2 Institution and contract schema

| Owner | Persistent fields to implement |
| --- | --- |
| Bank country | `bfl_schema`, registration, role, canonical profile, choice-complete flag, controller reference, operating state, paid-in capital, retained realized earnings, loss carryforward, rates, reserve settings, concentrations, period stamps, slot registries. |
| Charter controller | Bank navigation reference, royalty tier, dividend policies, bond mode, cadence, target/buffer/ceiling, coupon/debt-service limits, guarantee authorizations, policy revision. Live subjects remain authoritative. |
| Bank deposit slot | Party, estate identity if needed, principal, accrued claim, rate/time basis, maturity, withdrawal queue, early-exit terms, status/generation. |
| Native claim metadata | Native reference, issuer/borrower, instrument classification, current creditor, purchase basis, native face/outstanding snapshots, principal recovered, realized receipts, encumbrance, origin audit, servicing-only flag. No duplicate payable principal. |
| Bank profit register | Sovereign external coupons, controller coupons, realized debt-sale gains/losses, Merchant corporate/commodity earnings, Overseas commenda/company earnings, fees, funding/operating costs, royalties, institution-wide losses, distribution reserves. |
| Equity issuer | Issued units, holder pools/units, founder/state contribution, ownership class, voting policy, cash/earnings distribution record, generation. |
| Inventory owner | Good, custody location and market, quantity, unencumbered quantity, cost basis, storage loss/cost, shipment link, backing claims. |
| Contract custodian | Type, parties, cash/asset commitments, collateral/backing, consideration, permission snapshot, maturity, priority, state/generation, settlement stamp. |
| Venture operator | Investor contributions, capital account, eligible project, attributed costs/receipts, profit/loss terms, dates, exploration link, actual distributable cash, state. |
| Note issuer | Face outstanding, eligible backing, excluded issuance funding, acceptance jurisdictions, redemption queue, issuance cap, confidence, authority revision. |
| Company | Native identity/overlord/home region, financial holders, mandate, operating buffer, trade/project budgets, financing flows, actual distributable earnings, payment stamps. |
| Resolution authority | Frozen operations, creditor classes, losses already recognized, realized recoveries, guarantee claims paid, settlement priorities and successor/closure record. |

Centralize enum definitions in `design/slots.json`, then generate numeric script constants, tests, and localization. Suggested enums: profile `0 pending / 1 Merchant / 2 Overseas`; operating state `0 operating / 1 stressed / 2 restricted / 3 insolvent / 4 resolving / 5 closed`. Legacy servicing is a separate flag so an inherited forbidden asset can be collected in any appropriate state.

### 4.3 Balance sheet and spendable cash

```text
assets = native treasury
       + recoverable native credit carrying value
       + inventory at conservative realizable value
       + permitted equity/project carrying value
liabilities = deposit principal and credited interest
            + notes outstanding + other enforceable payable claims
equity = assets - liabilities

protected_cash = due withdrawals + due costs and contractual payments
               + statutory reserve floor + committed cash not already counted
               + operating buffer
free_cash = max(0, native treasury - protected_cash)
```

Keep contingent guarantees separate from booked liabilities until their trigger, while including stressed guarantee exposure in risk capacity. Avoid counting the same queued withdrawal both as a due payment and a reserve-base requirement. An impairment changes asset carrying value/equity, not cash; a subsequent cash recovery reduces the impaired asset and recognizes only the appropriate recovery/gain.

Funding constraints also require sufficient post-transaction capital and permitted concentration. A 100-gold deposit adds 100 cash and 100 liabilities, not 100 equity. A subscription adds cash and equity; a royalty reduces cash and equity; a dividend reduces cash and retained earnings; lending exchanges cash for a credit asset.

### 4.4 Profit recognition

Assign every financial flow a class: principal/financing, operating receipt, operating expense, realized gain/loss, shareholder distribution, or valuation-only. A native coupon is recognized only once after native settlement. Resale gain equals net consideration minus unrecovered acquisition basis; face value is not the gain. Returned venture capital, released collateral, new deposits, share subscriptions, bond proceeds, and note issuance cannot enter the dividend reserve.

Net treasury change is not profit: it includes construction, wars, borrowing, native transfers, and manual spending. Maintain explicit transaction classifications and verified native receipt observations. If native company or instrument attribution cannot be measured sufficiently, distribute only verified attributable receipts and report the unclassified amount. Never silently distribute a positive unexplained cash delta.

## 5. Initialization, monthly processing, and lifecycle

### 5.1 Bootstrap and migration

`bfl_bootstrap.txt` performs a guarded discovery pass on the installed 1.4 native `on_game_started_after_lobby` hook and the CMF `on_game_load_after_lobby` hook, both no-scope entry points. Attach BFL child hooks in `bfl_cmf_hooks.txt`; use bounded country-pulse registration for later-created institutions. Register an eligible existing bank or native company once; derive opening capital from real cash/assets/liabilities without granting money. Newly spawned native Fugger/Welser-style banks are detected through their banking role. Do not modify their founding events solely to add duplicate startup cash. Exclude CMF's storage country `c:CMF`; no financial ledger belongs on that framework country.

Use `bfl_schema` migrations in ascending order. Migrate an obsolete Sovereign Finance profile to one pending choice between Merchant and Overseas, preserving debts, balances, research, and capital. Existing valid choices persist. Mark completion so reload cannot offer a repeatable respecialization.

On charter conversion retain the original bank's records. On inherited out-of-profile assets set servicing-only permission; do not delete or sell them automatically. A downgrade/missing research blocks new commitments while allowing repayment, withdrawals, and contractual wind-down.

### 5.2 Hooks and scheduler

`in_game/common/on_action/bfl_hooks.txt` attaches mod child hooks to native callbacks. Verify additive merge behavior before release; if a native hook requires explicit replacement, preserve all native children and list the override. Native `.info` warns that an on-action effect and its event list are separate chains; do not rely on one to initialize data used concurrently by the other.

`bfl_cmf_hooks.txt` handles CMF integration separately. Registration can run repeatedly and on CMF's storage country: it registers presentation settings, never grants charter investment, selects a profile, accrues interest, or pays money. Use the installed 2.5.0 hooks as authoritative; its comments deprecate `on_game_start_after_lobby` in favor of native `on_game_started_after_lobby` on EU5 1.4. The similarly named hooks are not interchangeable.

| Hook | BFL responsibility | Scope/boundary |
| --- | --- | --- |
| `cmf_on_mod_registration` | Re-register CMM presentation preferences; configure available notification routes idempotently | Country; may be framework storage country. No finance initialization/settlement. |
| `on_game_started_after_lobby` | Once-per-new-game institutional discovery and schema setup | Native 1.4 no-scope hook used by CMF; preserve its existing child chain. |
| `on_game_load_after_lobby` | Existing-save migration/reconciliation and safe navigation rebuild | CMF no-scope hook; loading does not pay a period twice. |
| `cmf_on_country_transfer` | Clear/re-resolve the active player's economy-panel bank selection | New player country, with `scope:old_country`/`scope:new_country`; do not move institutions' ledgers with the player. |
| `cmf_monthly_human_country_pulse` | Human-facing alert eligibility and derived summary refresh | Human countries only; never the authoritative AI/subject-bank settlement scheduler. |
| `cmf_on_callback` | Handle changed presentation settings or notification callbacks | Filter the exact BFL callback key and repeat authority checks for any command. |

CMF transfers CMM preferences when a player changes country. It must not transfer bank portfolios, deposits, notes, profile, or company ownership to that player's new country. Native annexation/overlord-change callbacks remain necessary; a player-country transfer hook is not a universal subject-relationship callback.

**Native-pattern skeleton:**

```text
monthly_country_pulse = {
    on_actions = { bfl_monthly_accounts }
}
bfl_monthly_accounts = {
    trigger = { bfl_has_servicing_accounts = yes }
    effect = { bfl_process_accounts = yes }
}

# Separate file: bfl_cmf_hooks.txt
cmf_on_mod_registration = {
    on_actions = { bfl_on_cmf_registration }
}
bfl_on_cmf_registration = {
    effect = { bfl_register_cmf_presentation = yes }
}
cmf_monthly_human_country_pulse = {
    on_actions = { bfl_refresh_human_finance_alerts }
}
```

The **bank** owns settlement of its royalty/dividend/facility pair; the controller's pulse does not repeat it. Company settlement is company-owned. Use separate stamps for native receipt observation, deposits, royalty, dividends, draw, and completed account pass, plus per-contract settlement stamps. Choose a normalized `year * 12 + month` period or tested date representation exposed by the target engine; do not invent a `current_month_id` token.

Processing sequence inside one mod-owned pass:

1. Migrate; resolve live role, controller, reform, cap, profile, and servicing state.
2. Observe/reconcile native debt, current creditors, already-applied receipts/defaults, company payments, and dead references.
3. Snapshot opening productive assets; accrue due deposit costs and classify realized earnings/losses at the measured cutoff.
4. Recompute capital/liquidity; fulfill eligible withdrawals; apply crisis transitions; reserve upcoming obligations.
5. Assess/pay permitted royalty; replace tier modifiers; allocate expense once.
6. Offset losses; fund holder dividends; consume activity reserves once.
7. Recompute remaining cash/capital; perform the due custom bond draw and other authorized commitments.
8. Settle accepted resale commands through their own guarded service; refresh snapshots; stamp completion.

GUI commands may settle between scheduled passes, but call the same services and stamps. Company dividends received after the bank's cutoff enter the following bank period. Prefer this documented one-period lag to assuming country iteration order. Never have a GUI refresh advance time, accrue interest, or execute a payout.

### 5.3 Lifecycle cleanup

Use verified loan, bankruptcy, annexation, subject/overlord, building-destruction, and exploration hooks for prompt reconciliation, plus a bounded periodic registry audit for missed events. The loan callbacks' `scope:owner` is optional. Snapshot metadata before an object disappears if its lifecycle permits; otherwise close via native portfolio reconciliation with previously recorded basis and recovery evidence.

After overlord change, suspend new charter business until the new landed controller is valid. Enforce at most one direct chartered bank: keep the valid bound incumbent or a stable registered fallback, convert extras back to `state_bank`, and preserve their servicing records. Remove orphaned reform/GUI authority without canceling debt. Market ownership lost after chartering does not retroactively destroy the bank.

Do not blindly move a company's last headquarters or a bank's last building. Reconcile outstanding contracts, native tag survival, custody, and succession first. Invalid target references enter a visible workout/repair state; they never retarget the player by default.

## 6. Chartering, reform, and specialization

### 6.1 Decision and bank selection

Author `bfl_establish_chartered_bank` in `bfl_charter_decisions.txt` using the actual decision loader. Its availability requires a landed/location country, capital, eligible direct `state_bank`, no existing direct `bfl_chartered_bank`, no conversion/resolution guard, capital-market ownership, and sufficient current-age investment.

Resolve `capital -> market -> owner` and compare to the actor using the tested native links. Trading access, a branch, or owning one city in that market is insufficient. When several banks qualify, the decision opens a mod selector; no funds move until the final bank selection is validated. Closing the selector changes nothing.

```text
# Decision skeleton; all bfl_* services below must be authored.
bfl_establish_chartered_bank = {
    decision_category = economy_decisions
    image = "gfx/interface/illustrations/bfl/charter.dds"
    potential = { bfl_can_show_charter_decision = yes }
    allow = { bfl_can_begin_charter = yes }
    ai_will_do = { value = bfl_ai_charter_score }
    option = {
        name = bfl_establish_chartered_bank.a
        ai_chance = { value = 100 }
        effect = { bfl_open_charter_selector = yes }
    }
}
```

Investment script value: base 500 gold multiplied by the **current native age**: Traditions 1, Renaissance 1.5, Discovery 2, Reformation 3, Absolutism 4, Revolutions 6. These produce 500/750/1,000/1,500/2,000/3,000. Store displayed policy/age revision; if it changes before execution, refresh the quote. The whole investment goes to the selected bank.

`bfl_commit_charter` validates everything first, debits sovereign and credits bank once, records equity at an explicit subscription valuation, changes the same bank's subject type, binds controller/bank, grants reform, initializes treasury policy, and requests specialization only if absent. Native existing assets and minority ownership must be valued rather than overwritten to give the sovereign a fictitious 100% stake.

There is no second decision `price` debit, reform activation cost, or new bank creation. If the native decision loader requires a price mechanism, use exactly one measured debit authority and a matching bank credit; demonstrate full-transfer accounting in P01. CMF registration/settings never charge the investment.

### 6.2 Chartered subject and reform

Create a new `bfl_chartered_bank` definition by copying the pinned `state_bank` relationship and preserving all relevant war, ruler, diplomacy, building-country, cancellation, and visibility fields. Replace tribute with a new zero-gold price `bfl_no_automatic_tribute` using the native prices schema (`gold = 0`, subject to loader validation). Verify that no default tribute appears. Do not zero the global vassal price.

Remove the copied `overlord_modifier` bank-interest/capacity bonuses and grant them once from `bfl_state_chartered_bank`. Keep native bank-country prerequisites on the bank. A mod-owned permission gate separately authorizes the expanded operations.

`bfl_state_chartered_bank` is a non-major landed reform displayed as **State Chartered Bank**. Its manual adoption is locked/denied through the target reform schema; scripted addition follows committed conversion. `potential` requires the completed valid charter relationship. Use `country_modifier` for the audited `bank_interest = -0.005`, `max_bonds_modifier = 0.33`, and explicit bond permission if supported. A proposed `bond_interest = -0.005` reduction is tunable and subject to the observed engine minimum and measured time basis; it is not a promise of a 0.5% annual coupon.

Audit all native bank extraction actions, not only monthly tribute. Block unrestricted siphoning of charter cash, including native actions whose generic eligibility would otherwise accept the new subject. Public recapitalization, legitimate deposit withdrawal, and capital redemption remain separate explicit transactions. Track any required native action edit in `overrides.csv`.

### 6.3 Exclusive profile event

`bfl_specialization.txt` defines the two-choice country event, with Merchant Finance and Overseas Investment options. Target the independent bank player, or the landed controller with the intended bank saved explicitly. AI uses the same outcomes. Revalidate the bank/controller and pending status when an option executes.

Set `bfl_profile` to 1 or 2 and choice-complete once. The canonical choice belongs to the bank. Pending choice blocks new financial business but allows servicing; both completed choices permit sovereign finance, deposits, ownership, branches, and treasury policies. No ordinary action or research changes the profile. Do not create a third Sovereign specialization.

Native event structure can follow `events/economy/banking.txt`: `type = country_event`, `title`, `desc`, `image`, and `option`. Save-based guards on the bank are authoritative; a once-only event property alone is insufficient for a controller who later acquires another institution.

## 7. Permission service and advance tree

### 7.1 One permission matrix

Generate named triggers from `design/instruments.json`, then use them in decision options, scripted GUIs, diplomacy, events, AI, research, and callbacks that originate new business. Each permission checks **actor authority + live institution + completed profile + minimum age + researched advance + native prerequisites + target/instrument + funds/capital + operating state**.

Separate `bfl_can_originate_*`, `bfl_can_acquire_*`, `bfl_can_service_*`, and `bfl_can_resolve_*`. Servicing inherited assets must not grant origination rights. Foreign consent, public guarantees, note authorization, and sovereign commitments have additional sovereign/host authority checks.

For “age or later,” generate an OR of the permitted native age IDs. Do not use calendar years, age equality alone, or unverified ordering comparisons. Advance arrival and research are separate conditions. For a charter, research owner is the controller; independent banks research on their own tag. Sync only the eligible financial advances to the subject when an exposed native action requires them there. Recheck controller research/profile at execution; subject autonomous research is not authorization.

### 7.2 Advances to author

Put definitions in one topologically ordered `bfl_financial_advances.txt`; prerequisites precede dependents. Use locally observed `age`, `icon`, repeated `requires`, `potential`, `allow`, and `ai_weight` fields. Mod action gates are mandatory even if research visibility is correct.

| Advance | Earliest age | Prerequisites and permission | What the implementation enables |
| --- | --- | --- | --- |
| Basic registration, no new advance | Traditions | Native bank prerequisites, valid charter/independent role, selected profile | Demand deposits, rates, branches, sovereign credit/takeover, charter royalty/founder dividends and tested unsecured custom sovereign-bond facility. |
| `bfl_term_deposits` | Renaissance | Common banking foundations | Maturity accounts, renewal and early-exit terms. |
| `bfl_bank_capital_subscriptions` | Renaissance | Common accounting foundations | Additional bank capital subscriptions and recapitalization issuance. |
| `bfl_debt_restructuring` | Renaissance | Common native credit foundations | Negotiated sovereign workouts; company workouts additionally require Corporate Credit. |
| `bfl_commercial_bills` | Renaissance | Common payment/deposit foundations | Funded or explicitly backed commercial bills; no advanced sovereign notes. |
| `bfl_commodity_investments` | Discovery | Merchant; servicing/account foundations | Funded inventory investment. |
| `bfl_commenda` | Discovery | Overseas; native operator/project eligibility | Risk-capital voyage/trade/exploration projects. |
| `bfl_corporate_credit` | Reformation | Merchant; native company unlocks | Company working-capital loans, debt purchases, eligible corporate workouts. |
| `bfl_company_equity` | Reformation | Overseas; Commenda; native company unlocks | Company subscription, transfer, and stakes. |
| `bfl_bank_share_dealing` | Reformation | Common; Bank Capital Subscriptions | Expanded secondary/public bank-share dealing. |
| `bfl_collateralization` | Absolutism | Common sovereign credit; profile-limited other exposure | Pledged assets/revenue, enforceable security and priorities. |
| Native `central_bank_advance` | Absolutism | Native Manufactories and Banking conditions | Existing native building/capacity; keep native definition. |
| `bfl_warehouse_receipts` | Absolutism | Merchant; Commodity Investments + Collateralization | Fully backed transferable custody claims. |
| `bfl_commodity_forwards` | Absolutism | Merchant; Commodity Investments + Collateralization | Collateralized bilateral forwards. |
| `bfl_project_security` | Absolutism | Overseas; project/equity foundation + Collateralization | Security terms on eligible projects. |
| `bfl_sovereign_banknotes` | Absolutism | Charter/controller reform; Commercial Bills; monetary authorization | Capped subject sovereign-note regime. |
| `bfl_liquidity_facilities` | Absolutism | Common; Collateralization; eligible banks | Secured discount/interbank liquidity. |
| `bfl_advanced_clearing` | Revolutions | Relevant settlement/liquidity foundations | Wider clearing and coordinated settlement. |
| `bfl_margining_and_risk_management` | Revolutions | Merchant; Commodity Forwards | Variation margin and additional risk controls. |
| `bfl_public_financial_backstops` | Revolutions | Charter; notes/liquidity; public authorization | Broad emergency support and lender-of-last-resort powers. |

Use native `banking_advance` as a prerequisite only where doing so does not accidentally delay the plan's Traditions core. Record the chosen “banking foundations” prerequisite explicitly in `advances.json`; do not auto-grant all native Banking or Central Banking to satisfy a mod action. Controller financial-tree visibility must follow the bound bank profile, while common advances remain common.

**Native-pattern skeleton:**

```text
bfl_commodity_investments = {
    age = age_3_discovery
    icon = bfl_commodity_investments
    potential = { bfl_research_owner_has_merchant_bank = yes }
    allow = { bfl_research_owner_has_registered_bank = yes }
    ai_weight = { add = bfl_ai_commodity_research_score }
}
```

Add the explicit chosen prerequisites to the generated definition. A custom advance does not need a fictitious engine `unlock_financial_instrument` field: the shared action trigger tests `has_advance = bfl_commodity_investments` on the authoritative research owner.

## 8. Deposits and foreign branches

### 8.1 Deposit services

Implement `bfl_open_deposit`, `bfl_add_deposit`, `bfl_request_withdrawal`, `bfl_pay_withdrawal`, `bfl_renew_term`, and `bfl_accrue_deposit_interest` in `bfl_deposits.txt`. Interactions select the institution, amount preset, demand/term product, and accepted terms; the account GUI exposes the same services. Store offers on the receiving bank and require depositor acceptance for contractual changes.

Country/company deposit: one payer treasury debit and matching bank credit, followed by a matching deposit liability. Estate deposit: resolve the depositor country and estate type, read actual estate gold, and use the verified estate payment effect; household participation is aggregated through this estate pool. No estate wealth or deposit may be inferred from national tax income.

Aggregate demand balances by depositor/product/rate regime. Term slots retain maturity and fixed contract rate. Demand-rate changes apply prospectively; term-rate changes require renewal/consent. Interest accrual increases the deposit claim and decreases bank earnings/equity; it does not credit cash to the bank. Cash payment then reduces the accrued claim. Do not both capitalize interest and pay it as a second expense.

Internal formula for a simple annual-rate product:

```text
monthly_interest = principal * annual_fraction / 12 + carried_rounding_remainder
withdrawal_paid = min(requested_claim, cash_allowed_by_withdrawal_priority)
new_claim = old_claim + credited_interest - withdrawal_paid - agreed_loss
```

Define interest-bearing principal explicitly: principal only, or capitalized principal after a stated interval. Term early-exit penalties are bounded by the contract and classified as bank fee income only when paid/retained. Never silently consume more than the depositor's claim.

On shortage, record a queued unpaid claim and trigger the appropriate stress/restriction state; do not auto-mint cash. Requests against closed/destroyed banks move into resolution. AI depositors retain native expense buffers and respect exposure/guarantee limits. Public guarantees are separate authorized contracts.

**Verification:** A 100 deposit/withdrawal round trip conserves cash; 1 credited interest adds 1 liability and reduces equity by 1 without creating money; term maturity and queue order survive reload; simultaneous repeat commands cannot withdraw twice.

### 8.2 Branch servicing

`bfl_branches.txt` registers actual `banking_office` facilities with owner bank, host, location/market, permission agreement, custody capacity, allowed products, and closure status. Preserve native foreign-building requirements and maintenance; do not automatically build offices through account initialization.

Branch discovery is bounded to registered bank facilities and changes, with a periodic audit. A branch may support deposits/payment servicing, eligible client acquisition, and lower specified service costs. Investment permissions still come from the bank profile and research. It provides no land ownership, host-market control, universal trade monopoly, or second specialization.

Host agreement fields: eligible bank/host, access scope, term, explicit fee, legal note/custody permissions, war/sanction clause, seizure terms, and revocation notice. Transfer host fees from bank to host once and classify them as an operating expense; native building income is observed separately to avoid double revenue.

Closing a branch disables new local business and reconciles custody/contracts. Deposits remain bank liabilities. Confiscation recognizes the actual seized asset loss and contractual recovery rights; a destroyed office does not erase all bank obligations. Map navigation selects the existing location/building rather than creating visual-only proxy countries.

## 9. Native credit, government bonds, resale, and restructuring

### 9.1 Ordinary loan origination

`bfl_originate_native_credit` validates bank role/profile, eligible sovereign borrower, native capacity, acceptance, funding, risk price, and duration. Corporate borrowers must be native company tags and require Merchant Finance plus Reformation Corporate Credit. Overseas cannot route a company working-capital loan through the common sovereign gate.

The inspected `request_loan.txt` runs this native pattern on the lender:

```text
# Native loan-call shape; amount/rate/duration are service inputs in production.
scope:bfl_bank = {
    give_loan = {
        target = scope:bfl_borrower
        amount = 100
        interest = 0.05
        months = 60
    }
}
```

The numbers are illustrative, not approved pricing. P06 establishes the native rate/time basis and cash mutations. Save acquisition basis and capture the resulting native loan. Do not add a second lender debit or borrower credit around a native action that already moves both wallets.

Rate service: internal annual policy rate + borrower risk spread + maturity/concentration/funding adjustments, then convert through the verified adapter. Existing fixed loans retain their terms. A native loan is the debt ledger; custom fields describe basis, permission, security, and attributed receipts, not another payable loan.

### 9.2 Native regular-bank takeover

Preserve these local filters exactly for the native estate-origin operation:

```text
is_bond = no
NOT = { exists = owner }
months_left > 40
loan_interest > scope:actor.modifier:bank_interest
scope:actor.gold > remaining_debt
```

Native selection orders by `remaining_debt`, with `max = 1`. Native `bank_loan_takeover_cost` uses:

```text
loan_amount + loan_amount * buyer.bank_interest * months_left / 12
```

The local effect debits the actor by that price, compensates the borrower's banking estates through `distribute_gold_to_banking_estates`, and runs `change_loan_owner = scope:actor` on the same loan. Borrower receives no new principal. Preserve native target/action prerequisites and ordering. Add stricter reserve/capital checks against the **actual purchase cost**, since the native visibility test alone compares cash with remaining debt.

Prefer dispatching the native interaction with bank as actor. If subject dispatch is unavailable, implement a minimal copy of the audited operation inside `bfl_native_takeover`, preserving price, estate recipient, filters, and native selection. Its actor binding must be tested; a landed GUI player is not the paying buyer. Do not remove the bond filter and call that bond resale.

### 9.3 Funded custom sovereign bonds

`tools/generate_sovereign_bonds.py` generates issuer-owned initialization, issuance, settlement, asset statements, trading, GUI and diplomacy services. See [the authoritative transaction details](docs/sovereign-bonds.md) and [the living plan](docs/coverage.md). A bond is an issuer/slot/generation with current holder, face, basis, fixed annual coupon, due coupons, fractional carry and last accrual. No native loan/bond identity is created.

Either profile may underwrite its live controller. One bank cash debit funds one sovereign credit; the bank books acquisition cost, never issue profit. Manual and scheduled draws share one issue/month stamp and 100-gold cap. Debt/coupon limits use native income and include native debt; reserves, capital, arrears and bounded capacity gate execution. Fixed annual rates apply prospectively. Coupons settle from actual issuer cash and remain due on shortage; principal reaches the current holder once on perpetual-bond redemption.

### 9.4 Stock Exchange-gated secondary trading

Seller and buyer each need `stock_exchange_advance` and an owned location with a native `stock_exchange`. A chartered bank uses its live controller's advance/building. Recheck at acceptance, including loss after listing. This gate applies to secondary trading only.

One issuer has one three-month offer for a currently owned whole bond, initially at 98% of face. Bind seller, issuer/slot/generation, price and expiry. A buyer pays the seller, takes the same claim and fixed coupon, and records actual cost as basis. Issuer cash and principal do not rise. Reject invalid holders, stale/expired/replayed offers, self-purchases, arrears and insufficient funding; bank buyers additionally need protected free cash and capital. A bank seller recognizes only consideration minus basis as gain/loss. Coupon/redemption pay the new holder; that holder can subsequently list its acquired bond. Native ordinary-claim resale remains disabled.

### 9.5 Redemption and restructuring

Native redemption targets the actual bond, pays the current holder, and closes it once. Call the verified `redeem_bonds` target form; do not assume it is a country-scope block accepting a custom amount. No additional scripted coupon/principal payment accompanies a native payment. Outstanding perpetual/redeemable bonds receive no invented amortization date.

`bfl_restructure_native_claim` requires Renaissance Debt Restructuring, creditor/borrower acceptance, and claim eligibility. Merchant company restructuring also requires Reformation Corporate Credit. Offer rate reduction, partial repayment, principal haircut, or tested refinancing. Use loan amount/interest mutations only after their effects on native debt/coupons are measured. Lower principal records a creditor impairment, not another cash debit.

For ordinary maturity extension without a native setter, a tested payoff/replacement-loan chain must leave exactly one live obligation and one net financing change. Custom bond restructuring remains gated pending a separate accepted-terms implementation; native ordinary-loan setters cannot mutate custom claims. Collateral/security additions remain locked until Absolutism. Taking over the controller's debt does not retire it; forgiveness or repayment is an explicit separate operation.

**Required integrated fixture:** charter equity → funded custom issue → fixed annual coupon → funded deposit interest/share dividend → Stock Exchange-gated resale → next coupon to buyer → redemption to buyer. Track sovereign, both banks, and any native estate funding source throughout.

## 10. Royalty, dividends, and recurring treasury funding

### 10.1 Royalty policy and expense

`bfl_treasury_payments.txt` owns cash settlement; `bfl_treasury_policy.txt` owns pure script values; `bfl_treasury_commands.txt` validates controller policy changes. Royalty is assessed monthly on the conservative **opening performing productive-asset base**, excluding cash, own shares, impaired/defaulted value, unfunded commitments, and unrealized appreciation.

```text
due = opening_eligible_assets * annual_royalty_fraction / 12
paid = min(due + authorized_prior_deferred_collection, protected_free_cash)
```

Policy must explicitly choose whether to collect a prior deferral; it is not automatic compounding debt. Paid amount debits bank, credits sovereign, reduces equity as an expense, and enters cost allocation once. Unpaid assessment is a waivable administrative record, not an accrued liability/native loan. Collection recognizes its expense when paid; waiver creates no gain/cash. Capital-funded extraction is allowed subject to protected obligations and crisis state, and displayed clearly.

| Tier | Annual asset assessment | Burgher target display penalty | Bank subject-loyalty display penalty |
| --- | --- | --- | --- |
| Waived | 0% | 0 | 0 |
| Light | 0.25% | −2 percentage points | −5 points |
| Standard | 0.50% | −5 percentage points | −10 points |
| Heavy | 1.00% | −10 percentage points | −20 points |
| Exceptional | 2.00% | −20 percentage points | −35 points |

These are proposed balance values from the feature plan. Use `main_menu/common/static_modifiers/bfl_financial_modifiers.txt` for named tier definitions. Burgher target satisfaction is applied on the sovereign; subject loyalty on the bank. Its locally declared percent formatting suggests −0.05 for −5 percentage points of burgher target; validate effective units in P01. Subject loyalty is numeric and must be tested separately. Never feed both fields the same assumed scale.

On tier change, remove the prior named tier modifiers and apply the new pair once (or use a proven replace mode). Monthly refresh must not stack them. Payment shortage does not remove the selected tier's political cost. Resolving/closed institutions suspend extraction. Independent banks have no automatic charter royalty; an explicit host-fee agreement may levy an analogous paid expense.

### 10.2 Activity dividends

Maintain distribution reserves for actual net earnings in each permitted bucket:

| Bucket | Eligible realized receipts |
| --- | --- |
| Sovereign external credit | External ordinary-loan interest and funded custom sovereign-bond coupons. |
| Controller credit | Controller interest/coupons, separately labeled internal to the sovereign-bank group. |
| Debt trading | Net realized native claim sale gains/losses after basis and costs. |
| Merchant corporate | Permitted company loan interest/fees after Reformation research. |
| Merchant goods/instruments | Realized inventory/receipt/forward result after relevant gates. |
| Overseas ventures | Settled commenda surplus, excluding recovered capital. |
| Overseas company ownership | Actual company dividends and realized stake gains, excluding subscription/refund principal. |
| Services | Authorized fees less direct service costs. |

Deduct direct expenses in their bucket. Allocate common funding/operating costs and royalty once using a stable rule: proportionally to opening funded carrying value of active earning assets; if no eligible assets, use a common loss bucket. Do not use gross current receipts as the denominator if it allows idle/risky assets to avoid their costs.

Apply institution-wide loss carryforward against positive reserves before any payout. Then:

```text
requested_a = policy_payout_ratio_a * max(0, distributable_reserve_a)
cash_cap = free_cash_after_royalty
capital_cap = max(0, equity - required_equity)
funded_total = min(sum(requested_a), cash_cap, capital_cap)
funded_a = proportional_allocation(funded_total, requested_a)
holder_payment_a = funded_a * holder_units / total_units
```

Pay all holder entitlements from the same funded total, consume reserves once, and carry rounding remainder. Sovereign receives only its actual ownership share; private dilution reduces that share without removing monetary authority. Founder/state ownership supports dividends immediately, before expanded subscriptions or public share dealing unlock.

Retained realized profits may be distributed gradually in later months. Unrealized gains or newly borrowed/deposited money do not create distributable entitlement. Company distributions become bank earnings only when actually received. If both company and bank settle in different pulse orders, use the declared next-period recognition cutoff.

### 10.3 Recurring preferential bond facility

`bfl_run_controller_bond_facility` executes after payouts. Policy fields on controller: off/debt-first/buffer mode, cadence, requested spending fraction, operating cash target/ceiling, coupon limit, sovereign debt-service ceiling, per-period issuance cap, bank concentration cap, and policy revision. Default new charters to disclosed conservative settings; no silent unlimited draws.

Debt-first mode requests a selected share of forecast spending (initial scenario target 60%); buffer mode requests the forecast cash gap. Forecast rows distinguish native fiscal receipts, coupons/expenses, royalty/dividends, redemption, and borrowing. If a native forecast is not exposed, use a clearly labeled conservative estimate from measured recent periods; never report it as an exact engine projection.

```text
requested = policy_need_after_treasury_ceiling
fundable = min(requested, bank_free_cash, bank_risk_capacity,
               sovereign_native_issue_capacity, period_issue_cap,
               debt_service_headroom_as_issue_capacity)
lots = floor(fundable / verified_native_lot_cost)
```

Coupon headroom uses the measured actual native rate regime, all existing issuer obligations, outside-held debt, and any redemption reserve. Whole-lot sizing may leave a target unfilled. Revalidate after each lot. Commit through the native adapter, mark the draw period, and expose the exact reason a target was reduced/skipped. Repeated GUI execution cannot draw a scheduled period twice.

The facility swaps bank cash for a native sovereign asset. It creates no bank profit. New bonds are excluded from that period's opening royalty base and profit reserve. A dry, restricted, or insolvent bank skips underwriting. Recurring funding uses available bank cash; deposits, capital, retained external earnings, and actual resale replenish it. No setting guarantees continuous outside demand.

Resale of facility bonds pays the bank seller and transfers later coupons. If preferential coupons require a discount to attract buyers, record that loss. Native redemption reduces sovereign cash/debt and pays the current holder. Refinancing/rollover must remain explicit, capacity-limited, and subject to applicable restructuring research when terms change.

### 10.4 Treasury statement and consolidated interpretation

Display these separate rows for the latest closed period and forecast: native fiscal receipts; royalty assessed/paid/deferred; dividends by activity and ownership; gross bond issue proceeds; redemption principal; net financing; native coupon expense; outside-held debt; bank free cash; total sovereign cash change. Native budget integration may display a custom transfer only if it does not also pay it again; otherwise the mod statement is the detailed accounting surface.

Test the proposed 100 spending / 35 native receipts / 5 actual payouts / 60 net financing scenario with coupons included in spending. It demonstrates the intended debt-led playstyle only when capacity, external buyers, and real operating cash support it. Taxes/trade remain the fiscal base for debt service.

An internal controller coupon of 1 followed by a valid 0.5 dividend lowers its net coupon burden to 0.5; it does not generate external wealth. Report this distinction in tooltips. Increasing debt principal alone cannot improve consolidated profit or create reserve backing.

## 11. Concessions, guarantees, and security

Author standardized offer/accept contracts in `bfl_security_interactions.txt` and settlement/enforcement in `bfl_security.txt`. Common fields: issuer, creditor, beneficiary/guarantor, linked claim, scope of access or pledged asset/revenue, consideration, coverage, ceiling, expiry, default trigger, cure period, enforcement rights, priority, and consent revision.

Unsecured commercial access and construction/governance permissions may accompany eligible lending where native diplomacy supports them. A private agreement records only enforceable mod/native rights; it must not promise hard-coded host monopolies. Ordinary finance cannot silently transfer territory or create a subject relationship.

Collateral, revenue pledges, guarantee-backed security, and asset-priority enforcement require Absolutism Collateralization plus instrument/profile permission. Project security additionally requires its Overseas advance. A guarantee described as security cannot be offered earlier under an alternative label. Record contingent public exposure and explicit sovereign authorization; funding comes from the guarantor when called.

Use one encumbrance registry. Each pledged asset has recoverable value, haircut, senior claim, available residual value, and legal custody. Initial implementation prohibits repledging the same lot/claim; later upgrades may support explicit ranked claims within conservative value. An expired concession removes its effects and prevents future enforcement without deleting unrelated debt.

Guarantee call:

```text
entitled = min(verified_eligible_loss * coverage_fraction,
               remaining_contract_ceiling,
               underlying_loss_not_already_recovered)
paid = min(entitled, authorized_guarantor_available_cash)
```

Record paid/unpaid separately, reduce remaining coverage, and prevent native relief, collateral recovery, and guarantee proceeds from compensating the same loss twice. Any subrogated claim is explicit. Native default cancellation is reconciled before custom loss claims. Security realization uses an actual asset sale/transfer or funded revenue diversion; it is not a free gold reward.

## 12. Commodity inventory, receipts, and forwards

**Current M6 implementation:** [goods finance product and acceptance](docs/m6-goods.md). The native-good pilot is wheat, salt, iron, cloth and pepper, with sixteen separate ten-unit opening lots (no lot merging). Capital custody and one accepted host-owned Customs House capital-market branch use a persistent country-owned ledger; no duplicate warehouse building is added. Storage is an explicit administrative cost, and two-month shipments are a disclosed custody abstraction. Receipts sell ownership of existing backing. Physical forwards prefund buyer consideration plus 100% seller security, settle to receipts and compensate missing quantity from that security. Revolutions margining locks replacement-cost increases; it does not pay speculative mark gains. General cash derivatives, ship-specific cargo and Clearing House netting are not part of this bounded physical pilot. The canonical plan retains later money, resolution and release gates.

### 12.1 Funded goods positions

Merchant Finance requires Discovery and `bfl_commodity_investments`. `goods.json` selects the pinned native wheat, salt, iron, cloth and pepper definitions. Generate explicit cases; do not add duplicate commodity definitions or assume dynamic string-to-good scope resolution.

`bfl_buy_inventory` checks legal market access, native available stock, affordable buy price, custody capacity, free cash, and permission. Invoke the native purchase once, measure executed quantity/cost, then create the matching custody lot at that basis. The custom quantity is an owned inventory record removed from market supply by the native purchase, not an additional market stockpile. `bfl_sell_inventory` permits only physically available, unencumbered quantity and invokes the native sale once.

P09 established that native purchase uses selected-market stock/price and native sale realization is actor/capital dependent. The production guard requires the bank's current capital market or a live accepted host Customs House agreement for the recorded custody market. Do not use a chosen market's headline price as guaranteed sale proceeds or silently sell at the host owner's price.

Lots remain separate at their own actual acquisition basis; no weighted-average merging occurs in this pilot. The corresponding basis arithmetic is:

```text
new_basis_total = old_basis_total + actual_purchase_cost
sold_basis = basis_total * quantity_sold / quantity_before_sale
realized_result = actual_sale_proceeds - sold_basis - attributable_costs
```

Spoilage reduces physical quantity and associated basis once. Storage charges are real operating cash costs if they represent paid services; explicitly defined administrative sinks are disclosed. Value remaining stock conservatively at recoverable net proceeds, with unrealized losses recognized as appropriate and gains withheld from dividend entitlement.

### 12.2 Custody and transport

The bank's capital and a consenting foreign host's completed, host-owned Customs House provide the bounded custody gateways. Sixteen persistent lots cap capacity at 160 opening units. No additional warehouse building, free merchant capacity or territorial control is created. Receipt backing refers to a real acquired custody lot, not just the existence of a building.

Cross-market movement creates a shipment slot with origin, destination, good/quantity, owner, funded transport cost, access, departure/arrival period, risk/loss policy, and state. Remove quantity from sellable origin stock while in transit; add actual arrival quantity to destination. Destruction/blockade/permission loss delays or loses the defined shipment and feeds impairment. Avoid a second native market purchase at delivery that would charge for the same goods again.

Native company trade routes remain normal commerce. A scripted owned-inventory shipment is an explicit abstraction, not proof that the engine tracks a particular physical ship's cargo. Set bounded travel time/cost and disclose that abstraction. Overseas may fund an operator's legitimate procurement within commenda; it does not obtain a speculative commodity book.

### 12.3 Backed warehouse receipts

Require Merchant, Absolutism, Collateralization, and Warehouse Receipts. `bfl_issue_receipt` reserves a named quantity in custody, allocates one live claim to its holder, and updates encumbrance. Selling a receipt transfers the claim/consideration, not a second physical lot. Its issuer retains the custody obligation.

Redemption checks current holder and generation, releases/physically delivers the backing once, and closes the claim. Neither issuer nor holder can sell/pledge the underlying quantity separately. Custody losses allocate the real shortage to the defined claims and trigger resolution/guarantee rules. Aggregate receipt quantity cannot exceed backing after losses.

### 12.4 Collateralized forwards and later margining

Require Merchant, Absolutism, Collateralization, and Commodity Forwards. Contract fields: parties, good, quantity, strike, custody/delivery market, settlement date, physical/cash mode, collateral amount/custodian, margin rule, failure/cure/closeout terms, and unique settlement stamp.

Physical settlement reserves the whole acquired lot, prefunds buyer consideration and equal seller security, then converts surviving backing to a receipt at maturity. Missing quantity refunds its pro-rata contract price plus equal compensation from seller security. Obligations and unused security close once; released collateral is principal, not extra profit. This milestone's bounded product uses physical delivery; cash derivatives are outside this contract design.

Variation margin and broader receipt transfer require Revolutions Margining/Risk Management. Reserve only the additional replacement-cost exposure above the existing seller security; a failed call attempts an early physical close and otherwise preserves the obligation. Marks do not pay speculative profits. Fixed physical capacity and full buyer/seller cash cover bound opening notional. Clearing remains an M8 service with its own acceptance gate.

Procurement involving the sovereign requires explicit authorization and profile gates. A subsidy is a sovereign debit/recipient credit, distinct from market price and bank profit. Delivery failure, loss, and collateral shortfall persist through reload and feed the shared crisis services.

## 13. Equity and commenda

### 13.1 Issuer equity registers

`bfl_equity.txt` handles opening founder ownership, primary subscriptions, secondary transfers, voting, recapitalization, and dividends. It operates on a bank/company issuer and bounded country/estate/founder holder pools. The initial register allocates units against existing actual equity; this is an ownership record, not a cash grant.

Primary subscription requires Renaissance Bank Capital Subscriptions for expanded bank issues, or Reformation Company Equity with Overseas permission for bank investment in companies. Subscription amount moves buyer → issuer; new units are issued at an explicit disclosed valuation. If pre-money equity is positive:

```text
new_units = subscription_amount * existing_units / agreed_pre_money_equity
ownership_after = holder_units_after / total_units_after
```

An insolvent issuer needs an explicit resolution/recapitalization valuation rather than division by zero or a negative share price. Freeze registry revision during acceptance. Preserve existing units and founder classes according to disclosed terms.

Secondary bank-share dealing requires its Reformation advance. Buyer pays seller; issuer receives no proceeds except a separately disclosed paid fee. Company stake acquisition by a bank remains Overseas-only. Holder-unit totals always equal total issued units; avoid independently rounded percentages as the authoritative register.

Financial voting can influence company budget, manager appointment, reinvestment, and distributions within defined permissions. Native political overlordship remains separate. A control stake may open a separately negotiated native subject-transfer agreement, with sovereign consent; it does not automatically change overlord or territory. Private owners of a chartered bank do not gain sovereign monetary authority.

Prevent recursive capital creation: exclude own shares, cap cross-holdings, and value connected bank holdings conservatively with deductions rather than recursive upward marks. Related-party transfers use explicit limits and valuations. The bank's ordinary dividends remain the single activity distribution service, extended to its actual current holders.

### 13.2 Commenda contract and funding

Overseas requires Discovery and `bfl_commenda`. `bfl_commenda_interactions.txt` proposes eligible operator/project and terms; `bfl_commenda.txt` owns funding, project accounting, settlement, failure, and optional equity conversion.

State machine: proposed → accepted → funded → active → settling → closed, with failed/workout alternatives. Funding is a real investor-to-operator transfer classified as project capital. The investor carries project exposure; the operator records the capital obligation/project account separately from operating revenue. Multiple investors occupy bounded contribution slots.

Presets from the supplied plan: unilateral investor capital with 75/25 profit split; bilateral two-thirds/one-third contributions with equal profit split. These are configurable contract terms, not guaranteed historical outcomes or fixed interest. Store loss allocation explicitly; no project promises risk-free principal plus interest under a commenda label.

Discovery operators can be eligible native countries or estate commercial pools. Reformation native companies become preferred operators after their own native unlock. Each project needs an attributable budget, costs, revenue source, duration, and available cash. Assign a route/project receipt to one contract or explicit nonoverlapping fractions; concurrent ventures cannot each claim the same full company trade income.

### 13.3 Project settlement and exploration

At settlement, reconcile actual project receipts/costs, funded obligations, and available cash. Recover available capital under the agreed loss waterfall first, then split actual surplus. Returned capital reduces basis; only surplus enters investor profit. Partial/total loss reduces asset value once. Interim distributions require verified receipts and reduce the same project entitlement.

Exploration-linked ventures fund an operator eligible for native exploration. Bind the expedition/area/country through verified `start_exploration` and success callback targets. Exploration success opens the agreed future commercial access or project opportunity; it creates no automatic gold payout. Financial returns require real sales, trade receipts, or a separately funded contractual payment.

If native exploration attribution is too coarse, bind one eligible project to a defined operator/area and disclose that limitation; do not falsely attach any exploration success to every active venture. Conversion to company equity requires a new accepted valuation/agreement, native company eligibility, Overseas Reformation equity research, and extinguishment/reclassification of the old project claim without duplicate assets.

## 14. Native trade-company operations

### 14.1 Registration and identity

Identify by native `trade_company` subject type, preserve country tag, political overlord, headquarters ownership, capital, `trade_company_home_region`, and the native subject/region registries. The inspected headquarters creates the company without the old plan's assumed banking-reform reuse; classification must follow current definitions.

Registration discovers existing and newly created companies once. Reconcile native construction unlocks before granting anything: this build already defines Reformation `trade_companies_advance`. Do not auto-research company technology for every bank or apply an earlier reported community bug fix without reproducing the bug.

Opening cash/assets become opening company capital and founder ownership under a documented rule. Initial mod registration adds no money. Financial shareholders and bank creditors are independent of the native political relationship.

### 14.2 Mandate, budget, trade, and construction

`bfl_company_operations.txt` owns mandate, budget, route candidates, projects, facility assignment, and distributable-receipt calculation. A mandate selects region/goods family and risk/reinvestment preference. The company retains native trade access, range, tariffs, merchant capacity, building rules, and costs.

Budget order: native upkeep already applied → due debt/contract payments → operating buffer → funded trade/construction/reinvestment commitments → eligible shareholder distributions. Borrowing, subscription, and venture advances are financing, not trading profit. Do not charge native upkeep twice.

Native market trade creation in this build uses company actor with `from`, `to`, `merchant`, `goods`, `desired`, and `locked` fields. Validate these against `generic_actions/markets.txt`; `desired` is assigned capacity, not guaranteed sale quantity/profit. Prefer native route management and finite company AI candidate lists over rewriting all engine trade logic.

Evaluate access, distance/range, stock, available capacity, actual trading costs, tariffs, and projected margin. Only realized native operation receipts enter earnings. Rebalance routes on a bounded cadence, not every UI refresh. Record native trade references only where P08 proves persistence; otherwise rescan that company's native route list by safe native identity.

Construct relevant native facilities only against commercial/capacity needs. Headquarters, harbor, garrison, governance, local venture, and influence buildings keep native prerequisites. Assign a new facility explicitly to the selected company and verify its owner after construction. Do not pick a random same-overlord company or assume all companies share a home region.

### 14.3 Native company income and dividends

The local headquarters has `scaled_gold_to_building_owner = 0.2`, `scaled_gold_to_building_owner_overlord = 0.5`, and the subject type uses a separate `subject_pays_trade_company` price. These are distinct native mechanisms; measure actual receipts/deductions rather than adding their coefficients as a promised profit rate.

P07 identifies which earnings stay with company and which reach overlord directly. Keep direct-overlord native receipts in a separate statement row. Company dividends can use only verified company-retained realized earnings after costs/obligations and buffer/reinvestment policy. If native tribute already removes that income, it cannot also be distributed as if still retained.

A deliberate reallocation of native company tribute requires a narrow tested override and matching cash reconciliation. Begin by preserving native company payment rules and distributing only the remaining eligible earnings. This avoids disrupting every company or duplicating the overlord's receipt.

Pay company holders according to units from one funded dividend total. The bank's actual share enters its Overseas company-earnings bucket; the sovereign's later bank dividend is limited by its bank ownership and net bank earnings. The same company receipt cannot be counted as direct overlord income, company dividend, and full bank income independently.

### 14.4 Company finance and distress

Company deposits use common bank services. Merchant corporate debt requires Reformation Corporate Credit; Overseas company equity requires Reformation Company Equity; commenda requires Discovery Overseas research plus eligible operator; Merchant custody instruments require their later advances. Company security needs Absolutism and legal priority rules.

Workout precedes liquidation. Distressed company cash, collateral, surviving facilities, and obligations determine recoveries. Bank credit/project losses impair its assets; company deposit withdrawals affect bank liquidity. Guarantees connect failure to public funds only under an authorized triggering contract.

Before last-headquarters loss or political transfer, reconcile native entity survival and mod obligations. On disappearance, record available final recoveries, close/invalidate all linked slots, and retain an audit summary. Do not leave immortal receivables or move the last building to satisfy an equity sale without verifying the native country's survival.

## 15. Currency, rates, and interbank liquidity

### 15.1 Staged monetary services

Common banking services do not unlock investment profiles. Basic mint support follows native minting prerequisites and exposed actions; observe its native fiscal effect instead of creating another mint revenue stream. Renaissance Commercial Bills supports legally permitted payment claims; Absolutism Sovereign Banknotes enables the chartered subject's authorized advanced regime.

Implement bills as explicit funded/accepted obligations with face, payer/issuer, holder, maturity, transfer restrictions, backing, and settlement state. Unless a tested native bill object exists, this is a mod contract, not an engine-wide new currency. New unsecured bill credit must stay within profile/borrower permissions; a bill cannot bypass corporate-credit or collateral gates.

Private circulating claims require host authorization. Sovereign tender/note mandate requires the landed controller, State Chartered Bank, research, and applicable native law permissions. Independent legally authorized services remain distinct from sovereign note powers.

### 15.2 Banknote accounting and reserve provenance

`bfl_issue_notes`, `bfl_redeem_notes`, `bfl_update_note_confidence`, and `bfl_set_note_authority` live in `bfl_monetary.txt`. The game wallet is native gold; note issuance is an explicit monetary abstraction whose permitted conversion into spendable gold must be recorded with a matching note liability. It is not evidence of native national denominations or universal FX markets.

Issue only into an identified mod-managed payment/credit operation: increase outstanding face, record issuer liability and recipient/acceptance regime, create only the permitted spendable monetary amount once, then use the relevant separately verified native credit or custom bond service when financing a claim. For controller finance the asset remains a funded custom sovereign bond. Prevent reuse of the issuance step on command replay.

```text
new_issue <= authorized_issue_ceiling - outstanding_face
outstanding_face <= backing_multiple * eligible_preexisting_backing
eligible_backing excludes own notes, new issuance cash, own shares,
                    circular related-party claims and impaired assets
```

If the engine cannot identify note provenance in vanilla spending, retain a conservative aggregate excluded-funding amount and eligibility haircut for mod operations. Never claim precise specie/note composition of every native payment. Note repayment/redemption reduces outstanding liability and retires the corresponding monetary abstraction exactly once under tested cash semantics; any coin payout is part of that same settlement, not an extra refund.

Store redemption demand and confidence; apply calibrated `add_inflation`/verified native consequences only on issuance or specified monetary events, not every GUI display. Issuance is financing, never distributable earnings, and cannot provide its own backing. Restriction/default enters resolution; an unpaid note is not deleted merely to restore a reserve ratio.

### 15.3 Rate policy

Store internal annual fractions for deposit, new ordinary lending, discount/liquidity, and facility policy. Adapter conversions expose measured native units. Display annual and native-period equivalents where needed; never pass an annual 5% value directly to a monthly 5% field.

Ordinary loans retain fixed terms until eligible accepted restructuring. Demand deposits can reprice prospectively; term deposits retain contracts. Custom bond rate controls apply only to future issues. Existing issues retain their accepted annual coupon; monthly settlement carries fractional cents and preserves unpaid coupons. Native bond policy is separate.

Domestic transmission is a calibrated gameplay approximation using verified modifiers and explicit actions. A new named modifier has no automatic engine effect unless used by scripts or registered native mechanics. Avoid adding generic income bonuses as a substitute for funded lending or operating profits.

### 15.4 Interbank and clearing services

Common limited settlement liquidity is narrowly capped by amount, short duration, counterparty eligibility, and purpose. It cannot become unlimited long-term out-of-profile investment finance. Use native interbank loans only if both banks qualify as valid native lender/borrower; otherwise this bridge remains a probe, not a silently synthetic native loan.

Absolutism Liquidity Facilities + Collateralization adds secured discount lending: verify solvency, haircut eligible collateral, reserve it once, price a penalty spread, and fund from actual charter-bank cash. Overlord support is a distinct paid fiscal transfer; permitted note-funded assistance follows the capped issuance service. A liquidity loan changes cash and debt but does not repair negative equity.

Revolutions Advanced Clearing can net **mod-managed accepted obligations** among registered participants at a shared cutoff. Calculate bilateral/net positions, reserve funded settlement capacity, pay matching debits/credits, retain residual defaults, and preserve an audit trail. It cannot net arbitrary unknown native payments or erase native loans by offsetting custom variables.

Public Financial Backstops adds authorized broad crisis support and lender-of-last-resort procedure. It still requires funding, solvency/resolution distinctions, exposure caps, and instrument permissions. Equity subscriptions/loss allocation repair capital; emergency liquidity is not free recapitalization.

## 16. Crises and resolution

`bfl_resolution.txt` calculates liquidity coverage, conservative equity, required capital, concentration, confidence, guarantee burden, and native-default exposure. Thresholds and recovery hysteresis are tuning values in `bfl_tuning.txt`; avoid hard-coded random bankruptcy merely because a crisis event fired.

| State | New-business rule | Servicing and response |
| --- | --- | --- |
| Operating | Permitted products subject to capacity | Normal withdrawals, payouts, underwriting, accounting. |
| Stressed | Reduced exposure and tighter buffers | Notifications; lower dividends; liquidity review. |
| Withdrawal-restricted | Block expansion as defined | Queue claims; announce restrictions; seek funded support. |
| Insolvent | Block new ordinary commitments and extraction | Recognize losses; propose recapitalization/workout. |
| Resolving | Suspend royalty/dividends/new facility draws | Asset realization, guarantee calls, creditor waterfall, agreed restructuring. |
| Closed | No new business | Final recoveries and invalidation; retain audit summary. |

Mandatory accounting losses/default servicing are always possible; voluntary financial instruments retain research/profile gates. Resolution is not a route to introduce Renaissance workouts, Absolutism security, tradable shares, or advanced backstops early. A basic statutory/native loss allocation may resolve old obligations without originating a newly prohibited instrument; distinguish it from a voluntary researched debt-to-equity agreement.

Resolution steps: reconcile native cancellations → freeze affected commands → inventory actual assets/liabilities/encumbrance → realize recoverable assets → apply explicit guarantee/support payments → distribute available recoveries by agreed legal priority → record remaining losses/authorized conversion → close or restore institution under capital/liquidity tests. Do not impair a native canceled claim twice or pay a coupon on debt already removed by bankruptcy.

Maintain per-claim cumulative recovery and recognized loss. Proposed priority order is explicit secured recoveries from pledged assets, required resolution costs, legally prioritized deposits/notes, then other creditors and residual equity; the exact classes must be visible in contract terms and balance fixtures. Unsecured deposits cannot be retroactively described as secured to improve priority before research.

Model contagion through real exposures: defaulted company assets reduce bank equity; queued company deposits pressure liquidity; interbank loss affects counterparties; an authorized public guarantee burdens the guarantor. Confidence events may increase modeled withdrawal demand within existing claims, but cannot create deposits or claim principal from nothing. Notify once on meaningful state changes with cooldowns.

## 17. GUI, interactions, localization, and AI

### 17.1 Existing Economy panel integration and authority

The primary flow is **open the existing Economy panel → expand Banking & Finance → use its inline sections**. Keep the native `economy` lateral-view route, `economy_lateralview` widget/name, header, economic summary, graph, and Balance/Credit/Markets/Trade Policies/Trades navigation. Add a compact bank/treasury summary and expandable finance content within the existing economy body. This is a section of that panel, not a new lateral-view route, standalone window, global navigation row, or CMF action-bar element.

Place the `bfl_finance_section` instance inside the native `blockoverride "panel_content"` inner layout, after the native overview/graph and before the native `balance_subheader` budget region. Keep its default collapsed height small; expanded details use bounded internal scrolling and accordion rows so taxes, minting, expenses, native loans, and existing economy navigation remain usable. Bank/company selectors live inside the section. Company details render there through `bfl_company_sections.gui`.

**The inspected CMF release does not provide an economy-tab registration effect or an economy injection slot.** The [CMF override guide](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/Improved-Vanilla-Top-Level-Widget-Overrides) explains its extracted-definition approach; economy is absent from the inspected coverage. Implement this concrete ownership arrangement:

1. `mod/bfl/in_game/gui/economy_lateralview.gui` replaces the native file at the same path. Preserve the complete native top-level lateralview and make only the finance-section insertion. Record this explicit override and its baseline hash.
2. `in_game/gui/vanilla/bfl_economy_vanilla_types.gui` contains the pinned native `EconomyLateralviewTypes` types and native templates extracted from the original file. Keep `economy_main_tabs`, `EstateIncomeBreakdownTooltip`, and other native definitions unchanged so Credit and other consumers still resolve them. Remove those definitions from the replacement file to avoid two copies.
3. `in_game/gui/bfl_economy_finance.gui` defines the new `bfl_` section/row types and local layout; instantiate those types directly from the economy override. It contains no separately mounted top-level finance window.
4. Preserve file-scoped `@` constants wherever each generated file needs them. Do not assume moving a constant into the helper makes it visible inside the replacement lateralview file.
5. `tools/build_economy_gui.py` generates the split deterministically from the pinned native file, verifies the insertion anchor and native definition manifest, and refuses an unknown/changed upstream structure. It does not edit the installed game or CMF Workshop files.

If a future tested CMF release adds economy extraction, use that release's matching definitions and omit the BFL vanilla helper. The build must select exactly one owner of each native type/template; shipping both extraction sets causes duplicate definitions. Follow the upstream coverage process only as a later compatibility improvement, not an unfulfilled prerequisite for the initial design.

This arrangement uses CMF services and its extraction pattern while owning a real economy-file override. It does not solve conflicts with another mod replacing the same economy widget: use one reviewed combined override/compatibility patch that includes both changes. Do not claim that merely requiring CMF enables automatic merging.

**Layout skeleton; native surrounding content must be retained:**

```text
# The finance section instance goes within the existing economy body.
# All bfl_* types are authored in bfl_economy_finance.gui.
bfl_finance_section = {
    name = "bfl_finance_section"
}
```

Use local presentation variables following the native graph control's pattern, for example `LateralView.Vars.Toggle('bfl_finance_expanded')` and `LateralView.Vars.Exists('bfl_finance_expanded')`. The existing native `OpenLateralView('economy')` route remains the entry point. Do not invent a new engine tab enum or `cmf_register_economy_tab` call. Never globally override `economy_main_tabs` merely to add finance; it is shared by other native economy views.

Independent mode resolves player as bank. Charter mode resolves player/controller → live designated direct charter bank. The inline header always identifies the financial actor, controller, specialization, state, and cash/reserve basis. Keep native `Player`/`EconomyView` context on all vanilla content; scope bank data only inside finance child widgets. The government's native budget must not change its displayed actor to the bank. Every command re-resolves authority, relationship/reform/profile/research/state/funds. Financial mutation belongs to the bank; controller commands authorize policy, guarantees, and sovereign monetary actions.

**Scripted-GUI skeleton for a controller policy preset:**

```text
bfl_set_royalty_light = {
    scope = country
    is_shown = { bfl_root_has_charter_management = yes }
    is_valid = { bfl_root_may_change_treasury_policy = yes }
    effect = { bfl_commit_royalty_light_policy = yes }
}
```

Native GUI command expression shape:

```text
onclick = "[GetScriptedGui('bfl_set_royalty_light').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
```

This uses the locally observed `Execute/GuiScope.SetRoot(...).End` pattern. The `bfl_` effect resolves the bank and repeats authority checks internally. Preset commands avoid pretending an unverified slider/amount API exists. For row selections, use the installed `saved_scopes` and generated GUI data-type API after P02, or generate bounded slot-specific commands that resolve the authoritative slot/generation themselves. Never trust an arbitrary client-supplied controller reference.

GUI selection, sorting, pagination, expansion, and hover are presentation state. Read-only widgets and tooltips cannot initialize accounts, settle money, or repeatedly execute effects through animation callbacks. Synchronized commands handle game-state changes; single-player authority testing verifies the command actor and any selected targets.

### 17.2 Required in-panel sections

| Embedded section/file consumer | Display and actions |
| --- | --- |
| Overview/accounts | Native cash; protected/free cash; asset carrying values; deposits/notes; capital; profile; state; last accounting cutoff; deposits/withdrawal queue; bank rates. |
| Treasury Funding | Tier, political costs, royalty due/paid/deferred; activity reserves/payout ratios; holder share; facility modes/targets/limits; actual bond draws; coupon forecast; redemptions; native/outside-held debt. |
| Debt portfolio | Native takeover candidates, current holdings and issuer; face/outstanding/basis/coupon; native versus mod metadata; accepted quotes; resale/repayment/restructure commands with eligibility reasons. |
| Goods and custody | Lot/good/market/location; owned/encumbered/in-transit quantities; basis; actual liquidation estimate; storage costs; receipts/forwards; settlement and margin deadlines. Merchant gated. |
| Ventures | Operator, project, contributions, costs/receipts, capital at risk, realized surplus, exploration link, settlement status. Overseas gated. |
| Companies/ownership | Native company and political overlord; financial holders/units; bank exposures; mandate, budget, native routes/facilities; distributable receipts; subscription and voting actions. |
| Monetary policy | Rate/time basis, bills/notes/acceptance, backing exclusions, redemption queue, inflation/confidence, interbank support and guarantees. |
| Distress/research | State transition reasons, claim priority, resolution proposals, authorized rescue cost; chosen profile, earliest ages, prerequisites, researched versus merely available advances. |

Use shared row types in `bfl_finance_components.gui`; keep display calculations in pure script values/accessors. Cache only read-only statement snapshots at the accounting cutoff. Native data remains current for command validation. Display a “stale quote” reason when a row's revision differs.

Use the native Economy panel's width, scaling, open/close controls, layout widgets, and fonts. Expand a local section or select an inline detail page rather than adding another row of global navigation buttons. The finance summary remains visible when details collapse; closing Economy closes its finance content. Do not persist a screen selection as sovereign policy or move it into a shared/global simulation variable. Support 1280×720 minimum fixture, 1920×1080, 2560×1440, ultrawide, and UI-scale extremes; long tooltips and translated labels must wrap without hiding native or financial controls.

### 17.3 Interaction and event writing

New `country_interactions` use the locally observed category/type, `potential`, `allow`, `select_trigger`, consent/chance, and `effect` patterns. Selection is informational until commit. Borrower/depositor/host consent requires an offer/accept record, not an implied acceptance from a positive tooltip score. The accept side invokes the same transaction service as GUI/AI.

Organize event ID ranges: 100–199 initialization/profile, 200–299 offers, 300–399 ventures/company outcomes, 400–499 distress, 500–599 policy notifications, 900–999 migrations. This is a proposed convention, not an engine limit. Events use localization keys and scoped actor names. Notices summarize completed facts; an event image or popup does not itself settle a transaction.

### 17.4 Localization and concepts

Example UTF-8-BOM localization content:

```yaml
l_english:
 bfl_state_chartered_bank: "State Chartered Bank"
 bfl_chartered_bank: "Chartered Bank"
 bfl_merchant_finance: "Merchant Finance"
 bfl_overseas_investment: "Overseas Investment"
 bfl_free_cash: "Cash available after protected obligations"
 bfl_facility_skipped_reserves: "The bank must retain cash for protected obligations."
 bfl_bond_proceeds_explanation: "Bond proceeds provide financing and increase government debt."
```

Add titles/descriptions for advances, reform, subject, decisions, events, actions, every disabled reason, variables displayed as statuses, and confirmation/notification strings. Use tested scope/name/number formatters; do not invent GUI methods in localization. Concepts explain cash versus equity, principal versus profit, custom sovereign-bond ownership, internal coupons, encumbrance, guarantees, and servicing-only assets. Link tooltips to native concepts where possible.

Provide clear confirmation for meaningful contractual/fiscal decisions, showing concrete amount, participants, risk, and revised terms. Ordinary view changes need none. In-game confirmation is a player UX choice, not a requirement for the developer to seek additional design approval.

### 17.5 AI implementation

Keep AI scores in `bfl_ai_scores.txt`, reusable triggers in `bfl_permissions.txt`, and execution in the same services as players. Diplomatic AI uses native action cadence/score fields; scheduled internal management evaluates registered clients and bounded local opportunities. Do not enable autonomous scripted-GUI AI and scheduled AI for the same action without one shared cooldown/stamp.

Bank score components: expected net yield after funding/operations, borrower/default risk, liquidity coverage, required equity, concentration, maturity mismatch, host permission, and profile/research. AI cannot treat a capital-funded royalty or internal coupon loop as external profit. Charter AI follows controller policy but reduces/skips infeasible draws.

Controller AI selects royalty tier against loyalty/capital costs and debt-service prospects, sets bounded payout/facility targets, and authorizes support within fiscal limits. Company AI funds upkeep/buffers, evaluates native routes/construction by margin/capacity, and distributes only eligible earnings. Depositor AI keeps expense buffers and reacts to confidence/exposure.

Review a bounded number of candidates per institution per period, stagger heavier reviews across periods, and retain cooldowns. Avoid all-banks × all-countries or global order-book searches each month. Stable tie-breaking and synchronized randomness preserve deterministic single-player authority behavior.

### 17.6 CMF settings, alerts, and action log

`bfl_cmf_registration.txt` registers CMM **presentation preferences** through public CMF/CMM effects. A reduced-motion toggle, expanded activity-detail preference, and finance-notification preference are appropriate. Royalty tiers, payout ratios, bond policy, bank rates, contract acceptance, and monetary authority remain Economy-panel financial commands and canonical `bfl_` records, never CMM settings or resettable preferences.

**Installed 2.5.0 registration-call skeleton:**

```text
bfl_register_cmf_presentation = {
    cmm_register_bool_setting = {
        mod_id = bfl_banking_finance_companies
        setting_id = reduced_motion
        tab_id = presentation
        group_id = interface
        default_value = 0
    }
}
```

The inspected public setting effect registers its containing group/tab/mod implicitly. Supply the required generated CMM localization keys, including the mod name/description, presentation tab/group, and setting label/description; use the release-matched CMM schema for exact key composition. Registration is safe to repeat and must not reset existing choices. Read setting values through the tested CMM accessor contract and convert them into presentation behavior; do not call private `_cmm_` internals or assume player-country preferences describe subject-bank policy. CMF's `is_host` helper is relevant to any later global debug settings, not a substitute for landed-controller authorization.

`bfl_cmf_alerts_and_log.txt` exposes wrappers around installed CMF alert and log APIs. Show a finance alert only for a human with current authority over the affected institution; update on a meaningful new/changed condition and remove when the condition clears. Suitable cases: deposit withdrawal restriction, facility blocked by cash/capacity, imminent contractual settlement, guarantee call, and resolution requiring player action. Reconcile stale alerts after load/controller change. Respect CMF dismiss/mute behavior; a notification preference does not cancel the underlying obligation.

**Installed alert routing example, in the authorized human country scope:**

```text
cmf_set_alert_open_view = {
    alert = bfl_liquidity_warning
    view = economy
}
cmf_show_alert = { alert = bfl_liquidity_warning }
```

Gate repeated show calls by the wrapper's condition/state transition or verified active-alert membership. Clicking opens the existing Economy view, whose finance summary shows the problem; inline expansion is presentation-only. Do not route to a separate finance window or register an action-bar shortcut. Selecting a precise local subsection from an alert requires a separately proven UI callback; opening Economy itself is the route validated in P12.

After a successful transaction/policy change, call `cmf_log`, `cmf_log_with_scope_args`, or the installed `cmf_log_decimal_value` from the appropriate actor country scope, with localized BFL action keys. Log charter commitment, accepted debt resale, significant policy changes, and rescue/resolution decisions; avoid flooding the shared log with every accrual or GUI refresh. Log only committed facts and use transaction stamps to prevent duplicates. CMF's log is an inspectable history, not the financial ledger or the authority for native payments.

## 18. Graphics and FX production

### 18.1 Visual direction and verified native sizes

Use EU5's existing parchment, restrained metallic trim, painted institutional symbols, and readable flat finance/status glyphs. Distinguish Merchant with a ledger/scales/warehouse motif and Overseas with a compass/ship/partnership seal. Use shape and text in addition to color; gold/green/red alone cannot communicate state accessibly.

The following dimensions and formats were read from **local DDS headers**, not inferred from screenshots:

| Native reference below `main_menu/` | Width × height | Observed header |
| --- | --- | --- |
| `gfx/interface/advance/banking_advance.dds` | 256 × 256 | DXT5 / BC3 |
| `gfx/interface/icons/buildings/banking_office.dds` | 125 × 125 | DXT5 / BC3 |
| `gfx/interface/icons/subject_types/state_bank.dds` | 128 × 128 | DXT5 / BC3 |
| `gfx/interface/icons/government_reforms/illustrations/banking_country.dds` | 64 × 90 | DX10 extension; inspect its exact DXGI format before matching |
| `gfx/interface/illustrations/institutions/banking.dds` | 1080 × 440 | DXT1 / BC1 |
| `gfx/interface/icons/flat_icons/balance/government_bond.dds` | 128 × 128 | DXT5 / BC3 |

Match the **consumer's** dimensions, alpha, color-space, and mip behavior. These examples are not universal texture requirements. Non-power-of-two 125×125 building icons are native here; do not force them into a different size merely for a generic texture rule. GUI can usually reference a texture path directly, as native windows do; do not assume EU4 sprite `.gfx` registration is required.

### 18.2 Required asset manifest

Create editable masters under `assets_source`, export only runtime textures into the mod, and list each export/consumer/license in `asset_register.csv`.

| Asset group | Proposed names/count and runtime destination | Purpose and production requirement |
| --- | --- | --- |
| Charter identity | `bfl_chartered_bank.dds`, 128×128 subject icon; `bfl_state_chartered_bank.dds`, 64×90 reform illustration | Banking seal/institution facade; readable silhouette; match consumer alpha/format. |
| Profile identity | `merchant_finance.dds`, `overseas_investment.dds` under `icons/bfl/` | 128×128 transparent masters/exports, legible at small header size. |
| Inline section labels | About eight icons: accounts, treasury, debt, custody, ventures, companies, monetary, distress/research | 128×128 BC3 proposed exports, usually displayed at 20–32 px beside accordion/section labels inside Economy. These are not action-bar or topbar icons. Reuse native motifs by reference where adequate. |
| CMF finance alerts | Liquidity, blocked funding, settlement, guarantee, resolution symbols as needed | Follow CMF 2.5.0 alert localization/texture contract; reuse suitable native/BFL status art and the framework's alert rendering. Alert clicks open Economy. |
| Actions/instruments | Deposit, withdraw, subscribe, share transfer, loan, bond, takeover, resale, redeem, royalty, dividend, receipt, forward, commenda, note, collateral/liquidity | About 16 reusable symbols under `icons/bfl/`; consistent outlines, transparent padding, no embedded text/numbers. |
| Operating states | Six icons for operating/stressed/restricted/insolvent/resolving/closed; plus locks/security badges as needed | Distinct silhouettes and labels, visible on parchment in grayscale. |
| Advances | 18 custom advance icons in `gfx/interface/advance/` | 256×256 BC3 matching the local advance reference. Filename equals `icon` value plus `.dds`, e.g. `bfl_commenda.dds`; no doubled namespace. |
| Warehouse | `icons/buildings/bfl_bonded_warehouse.dds` if new building is needed | 125×125 reference size; clear warehouse/receipt motif. Existing native warehouse may be referenced in prototype. |
| Illustrations | `charter.dds`, `merchant_finance.dds`, `overseas_investment.dds`, `company_venture.dds`, `bank_run.dds`, `resolution.dds` under `illustrations/bfl/` | Six proposed 1080×440 opaque painted scenes: sovereign charter signing; merchant counting house; overseas partnership/voyage; company activity; withdrawal panic; negotiated rescue. Composition leaves readable UI space. |
| Shared panel details | Optional seal, divider, backing/custody badge, royalty-tier marks | Prefer native frames/paper types. Custom art should add meaning rather than duplicate the entire UI skin. |
| Workshop thumbnail | `thumbnail.png` at mod root | Proposed 1024×1024 source/export, tested with installed uploader; title readable at small size; original artwork. This size is a design target, not a verified uploader limit. |

Native good/estate/market/country flags should be displayed through native assets/accessors; no new commodity art is needed when using existing goods. Bank/company names and generated native flags remain dynamic. Do not replace every independent bank with one mod flag. A custom issuer emblem is optional display art and separate from native country identity.

Reference vanilla art from the installed game where appropriate instead of redistributing copied proprietary assets. The [Modding Co-op graphical-assets repository](https://github.com/Europa-Universalis-5-Modding-Co-op/graphical-assets) is a useful template source; its inspected README currently lists Images as empty. Do not plan the mod around an available banking asset pack or assume a reuse license from the repository name. Verify individual assets and permissions before incorporating any later additions.

### 18.3 Export and integration procedure

1. Author icons at a larger editable resolution with separate symbol/background/highlight layers. Keep text in localization.
2. Export to the target pixel size and inspect at the actual displayed size on both light/dark UI backgrounds.
3. Convert using a DDS-capable tool with the verified consumer format. BC3 suits the measured alpha-icon references; BC1 suits opaque examples. A DX10 header alone does not identify BC7 or any other exact format.
4. Match alpha treatment/color space and any mip levels required by the native consumer. Test fringes, blur, compression, and downscaling; keep unused transparent padding consistent.
5. Put exports in the mirrored load-stage texture path. Use custom `icon` keys for advances and explicit paths for GUI/event images. Add modifier-icon mappings only for modifiers that need them; declaring an icon does not create a gameplay modifier.
6. Validate path casing, dimensions/header, file presence, and every consumer reference. Inspect in-game at all target UI scales and after a fresh reload to catch cached assets.

For illustrations, preserve focal characters/objects outside the text overlay and crop region. Regional variants can follow later, but the core needs all required event outcomes represented. Source artwork/edits stay outside the Workshop payload.

### 18.4 Required interface FX

“FX” here includes visual feedback and animation, distinct from the scripted gameplay `effect` blocks described earlier. Core features need interface feedback; they do not require custom 3D shaders or particles.

| Trigger | Proposed FX | Implementation and limit |
| --- | --- | --- |
| Charter completed | Seal reveal and brief frame highlight, 0.5–0.8 s | GUI state/timeline on completed notification, once per charter. |
| Deposit, withdrawal, resale, dividend settled | Small directional transfer pulse and updated amount, 0.2–0.4 s | Display the committed transaction result; animation must not call settlement again. |
| Locked instrument | Static lock plus exact profile/research/age reason | No repeated flashing or misleading enabled hover. |
| Facility target reduced/skipped | Amber indicator and persistent cause tooltip | Animate once on a new meaningful condition; show requested versus actual. |
| Margin call or withdrawal restriction | Brief outline pulse, then static warning badge | Trigger on state/notice change with cooldown, not continuously per frame/month. |
| Company/venture pays | Route/project marker highlight and receipt row | Actual receipt only; exploration discovery alone has no profit animation. |
| Resolution closes | Stamp/crossfade to final recoveries, 0.4–0.8 s | Show residual losses and closed state; no celebratory payout for unpaid claims. |

Use existing `.gui` state/animation patterns for opacity, position, and highlight transitions. The local `main_menu/gui_animations/test_asset.json` demonstrates timeline `animationSets`, paths, durations, and keyframes; it is an example, not proof of automatic binding to the embedded finance section. Write `bfl_finance_animations.json` only after its binding/consumer is demonstrated; otherwise embed the required states in the mod GUI files. Respect the CMM reduced-motion preference and confine finance animation to its Economy-panel content or appropriate event/alert notification.

Respect pause/UI state, avoid infinite notification loops, and provide a reduced-motion option or static equivalent. FX read already committed facts and never modify accounting, scopes, or random gameplay outcomes. Optional sound can reuse verified native UI sounds; inspect the installed sound-event interface before adding assets. No new audio bank is necessary for the core specification.

### 18.5 Optional map models and particles

The core can reuse native bank/company/warehouse map visuals. If custom facilities later need world art, build one counting-house/warehouse model with era/culture-compatible variants, textures/materials, appropriate LODs and scale, and a tested link from the building's graphical tags to the entity. Native assets include `.asset` model definitions and `.particle2` effects; use their exact exporter/schema pipeline after inspection.

Optional restrained FX: a short commissioning marker above a selected newly completed office, or a selected-company route highlight. Attach to a real building/location/route, respect visibility/fog, clean up on closure/destruction, and limit active instances. Do not place permanent particle emitters on every deposit, bond, or monthly dividend. Existing weather/fire/crisis graphics should be reused where appropriate; financial insolvency alone does not imply a burning city.

Keep optional runtime model/particle files under `main_menu/gfx/models/bfl/` and `main_menu/gfx/particles/bfl/` only if matching consumers/load stage are confirmed. Particle edit metadata, source meshes, and editor projects remain in `assets_source`. No shader replacement under `gfx/FX` is required; finance feedback should use native UI shaders unless a concrete verified visual need justifies a custom one.

## 19. Build, testing, compatibility, and release

### 19.1 Implementation sequence

| Stage | Concrete output | Gate to proceed |
| --- | --- | --- |
| M0 — complete | Pinned game/CMF 2.5.0 baseline; P01–P12 native audit; 56 engine assertions, 20 numerical checks, 114 account/bond assertions and separate 25-observation normal UI record. | No M0 checks remain. Native capabilities/limits, country-owned record/guard requirements, funded custom bonds, subject authority, CMF hooks and recorded Economy UI are established for single-player. Later production adapters and release campaigns retain their own milestone gates. |
| M1 | Charter decision/selector, subject/reform, account schema, profile event/migration, embedded Economy finance/Treasury shell, CMM preferences | Same bank tag; investment once; no tribute; one bank; correct authority/profile; no BFL action bar/launcher. |
| M2 | Native company registration, routes/facilities/budgets, income classification | Real operating income and direct-overlord streams identified. |
| M3 | Ordinary sovereign credit/takeover, custom sovereign bonds/facility/Stock Exchange-gated resale/redemption, researched restructuring | Native ordinary debt and custom sovereign bonds pass their respective cash, identity and permission checks in both profiles. |
| M4 | Royalty/loyalty, activity reserves/founder dividends, deposits/withdrawals | All three funding channels conserve cash and protect obligations. |
| M5 | Subscriptions/transfers/dilution/company equity | Unit totals, ownership entitlements, authority separation pass. |
| M6 | Funded goods/custody/shipments, later receipts/forwards/margin | Physical stock, backing, settlement, and gates pass. |
| M7 | Discovery operators/commenda/exploration, later company conversion | No discovery-only profit; actual surplus/loss settlement. |
| M8 | Rate UI, bills/notes, liquidity/clearing/backstops | Correct units, backing, retirement, solvency distinctions. |
| M9 | Full resolution/contagion/lifecycle cleanup | Losses/recoveries once, debt ownership survives transfer, safe disappearance. |
| M10 | Full art/FX/localization, AI, compatibility, campaign/balance results | Complete feature matrix passes on identified build. |

Build player GUI and AI alongside each feature. Implement shared resolution guards and cleanup early; M9 completes the full system. The minimum integrated prototype includes an independent bank, a decision-converted bank, both profiles, funded deposit interest/share dividends and a custom sovereign bond traded by exchange-qualified counterparties. Later research is tested in appropriate-age fixtures, not granted in normal gameplay.

### 19.2 Offline build checks

Generators read the JSON design inputs and write only known generated script/localization files. Emit a deterministic file manifest and generated-content hashes. Validate unique identifiers, references, prerequisite ordering/cycles, bounds/generation fields, localization coverage, BOM/UTF-8, metadata schema, texture paths/sizes, and override declarations. Brace balancing is a useful preliminary check, not an EU5 parser or proof of script validity.

Validate the CMF relationship and release baseline, all CMF public-effect/hook references, CMM localization, alert routes, and the economy-definition ownership manifest. Check that the generated economy override contains exactly one native `economy_lateralview`, preserves the native navigation/controls, and instantiates the inline finance section. Reject a BFL `cmf_add_action_bar_element` call, finance launcher registry, or separately mounted finance window. When CMF adds economy extraction in a later release, fail builds that retain the redundant BFL extraction helper.

`ledger_reference.py` models transaction arithmetic independently of engine adapters. Test mixed sequences and edge amounts: deposits, subscriptions/dilution, royalties, institution-wide loss offsets, activity payouts, basis recovery/resale, collateral, margin, note caps, guarantees, and rounding. A reference model cannot prove native effects, loader behavior, GUI authority, or coupon routing; those require game tests.

Build release staging from an explicit allowlist of `.metadata`, runtime stage folders, thumbnail, and player-facing release notes. Exclude probe mods, debug grants/actions, design JSON, generators, editable art, test saves, logs, `.git`, and publishing configuration. Validate no placeholder supported version or dead adapter ships as an enabled feature.

### 19.3 In-game acceptance suite

| Fixture | Required result |
| --- | --- |
| Missing bank / wrong capital-market owner / no funds | Charter unavailable or final execution rejects without mutation. |
| Multiple eligible State Banks | Explicit selector; only selected existing entity converts. |
| Each age investment / stale age quote | Correct multiplier/full transfer; changed quote refreshes before commit. |
| Existing bank minority owners/claims | Preserved balances/units; sovereign investment fairly adds equity. |
| Second charter / inherited duplicates | Second blocked; extras restored to native servicing status with claims intact. |
| Reform manual adoption / orphaned reform | No free charter/recharge; authority follows valid live institution. |
| Treasury separation / native siphoning | Overlord spending cannot consume bank reserves; no fourth extraction path. |
| Independent and charter GUI / hostile stale target | Correct actor pays; unauthorized command fails; UI refresh changes no finance. |
| Economy integration / CMF alone and CMF+BFL | CMF alone preserves the native baseline; CMF+BFL adds inline Banking & Finance. Native Balance/Credit/Markets/Trade Policies/Trades, graph, minting, taxes, expenses, native loan controls, and hotkeys remain functional. |
| No added action bar / repeated panel opens | No BFL action-bar element, topbar button, finance launcher, standalone finance window, or duplicate native widget. Reopening does not mutate finance. |
| Missing CMF / wrong release / future extraction coverage | Dependency is explicit and diagnosed; target release is enforced by release testing; native types/templates have exactly one owner. |
| CMM register/reset/preferences and player tag switch | Presentation choices re-register safely; reset/tag switch does not reset or transfer bank/company ledgers, profile, or policy. |
| CMF alert/log load, mute, click, and clearance | Authorized player sees current condition; click opens Economy; no duplicate log/settlement; obsolete alerts clear. |
| Another mod replaces economy_lateralview.gui | Conflict is detected/documented; one combined compatibility override preserves both intended contributions. |
| Profile choice/reload/legacy Sovereign save | Exactly one persistent choice; one migration choice; no repeat respec. |
| Every instrument one age before/at/later, unresearched/researched | Full profile+age+research+native gates through GUI/diplomacy/events/AI. |
| Term/demand/estate deposits | Cash/claims/interest/queues and real estate funding reconcile through reload. |
| Branch construction/war/closure/seizure | Correct owner/access; actual custody loss; deposit liabilities persist. |
| Native loan/takeover | Native filters/price/estate compensation preserved; no duplicate principal/proceeds. |
| Bank-funded bond issue and dry-bank skip | Actual `is_bond`; real bank funder; one sovereign credit; capacity/lot limits. |
| Coupon/rate changes | Measured units/minimum/repricing; credited once to correct owner. |
| Native claim resale and stale/encumbered offers | Buyer pays seller; same debt; no sovereign proceeds; invalid offer has no effect. |
| Coupon boundary resale/reload/redemption | Current-holder routing and accrued treatment correct; principal closes once. |
| Restructuring/refinancing | Consent/research; correct native obligation count; no free cancellation/security. |
| Royalty each tier / reload / shortage / resolution | Monotonic cost/penalties; one modifier pair; cash/equity consequence; proper deferral/suspension. |
| Activity dividends with losses/private holders | Net realized reserves, global loss offset, ownership share, cash/capital caps, no principal payout. |
| Debt-led treasury cycle | Proposed financing share sustainable within measured cash/capacity/risk; coupon/external exposure visible. |
| Goods partial fills/spoilage/transport | Owned quantities, executed cash, basis, custody and delayed delivery reconcile. |
| Receipt double pledge / forward delivery / margin failure | Backing once; bilateral funded result; prior margin not paid again; persistent shortfall. |
| Equity issue/trade/insolvency/cross-holdings | Unit totals/dilution; buyer-to-seller transfer; no circular capital creation. |
| Commenda success/partial/total loss and exploration only | Real capital recovery/surplus; discovery alone pays nothing; no duplicate attribution. |
| Native company creation/multiple companies/distributions | Correct tag/owner/home region; real retained earnings; direct native overlord income not duplicated. |
| Notes authorization/self-backing/redemption | Cap/liability/backing/inflation; excluded issuance funds; no duplicate monetary retirement/payment. |
| Interbank/guarantee/recapitalization | Liquidity versus equity distinct; actual public cost; coverage and collateral limits. |
| Bankruptcy/annexation/last building/overlord change | Native cancellation reconciled once; safe references; claims preserved or resolved. |
| Monthly repeat/callback re-entry/load midway | Period and generation guards prevent duplicate settlement. |
| Multiplayer — retired | Unsupported by user decision; no multiplayer or hotjoin acceptance remains. Single-player reload/authority checks remain in the relevant product campaigns. |
| Graphics/localization/FX | No missing texture/key, correct sizes/crops, legible layouts, animation never settles money. |

Use documented EU5 debug mode and generated scripting/GUI docs for the installed build. The [wiki modding overview](https://eu5.paradoxwikis.com/Modding) is a reference entry point, but direct access returned 401 during this audit; exact console commands and dump locations must be checked locally. Retain fresh script/error logs and before/after fixtures under `tests/results`, not inside the Workshop payload.

Run controlled fixtures before full campaigns for each playable role. Include Discovery ventures before native companies, later-age continuation, bank resale during coupon boundaries, prolonged runs, contraction, and exhausted investor demand. Suggested performance criterion from the plan: no more than 10% median monthly-time increase versus identical baseline, reported with entity/contract counts and machine/settings. It is a target, not a measured result.

### 19.4 Compatibility and overrides

Create `overrides.csv` columns: native path/key, baseline hash/build, entry mode, reason, affected mods, preserved fields, probe/test, and reviewer result. Prefer new objects, native action wrappers, and appended child hooks. Do not assume all scalar/nested fields merge safely or apply `REPLACE:` indiscriminately; verify entry modes for each database type.

Expected compatibility touchpoints: native and CMF on-actions, charter subject extraction/siphoning eligibility, the explicit economy GUI override/extracted-definition owner, CMF dependency-popup helper, CMM preferences and alert/log callbacks, bank takeover dispatch, bond operations, branch ownership, native company income/creation, and research synchronization. New `bfl_` subject/reform keys should minimize changes to `state_bank` itself. Never globally change tribute prices or replace all native company buildings merely to add registration.

List `in_game/gui/economy_lateralview.gui` as a required override, with baseline native SHA-256 `675763819DE9C0F368761DEC5D01541553C78D9A9E25EA68135A5667BB2D621D`, the inserted finance section, preserved native definitions, and expected CMF 2.5.0 coverage. Other mods replacing this same file require a combined patch. CMF dependency alone does not resolve that collision. Carry any necessary file-scoped constants and ensure other native views still resolve the shared economy templates.

For each game or CMF update, compare both pinned source sets, regenerate docs, re-run P01–P12, verify overrides and economy extraction coverage, then repeat affected fixtures and campaign checks. Update `supported_game_version` and the supported CMF matrix only after passing. Publish save-schema changes and downgrade limitations; never promise a safe removal from a save with unpaid mod-managed obligations without a tested wind-down/export path.

### 19.5 Workshop staging and uploader

The [pdx-workshop-manager project](https://github.com/kaiser-chris/pdx-workshop-manager) supports EUV Workshop publishing. Its README requires Steam running/logged in and describes `id = 0` as first-upload creation. The installed sample uses **`change-note-directories`**; the public README shows an older singular form. Preserve the installed release's schema and verify it before publishing.

Proposed configuration for release staging (not executed by this specification):

```json
{
  "game": 3450310,
  "mods": [
    {
      "id": 0,
      "directory": "C:\\Users\\Thomas Altmann\\Documents\\ChatGPT\\EU5_BFI\\dist\\bfl",
      "thumbnail": "thumbnail.png",
      "names": { "english": "Banking, Finance and Trade Companies" },
      "descriptions": {
        "english": "C:\\Users\\Thomas Altmann\\Documents\\ChatGPT\\EU5_BFI\\publishing\\steam_page_english.bbcode"
      },
      "change-note-directories": {
        "english": "C:\\Users\\Thomas Altmann\\Documents\\ChatGPT\\EU5_BFI\\publishing\\change_notes\\english"
      }
    }
  ]
}
```

Use one configured mod entry; remove empty sample rows. Preserve the assigned Workshop ID after first creation to update that item. Save configuration, review staged contents, and upload from the GUI only when release publication is requested. The source task authorizes this document, not a Workshop upload. The installed executable/configuration was inspected, not launched or changed.

The eventual Workshop page must list CMF item `3692202776` under Required Items and identify the tested game/CMF combination, Economy-panel entry point, and economy-override conflicts. Do not assume uploader metadata alone establishes Steam's required-item relationship. Package BFL's runtime files and the documented dependency helper, not the framework's full runtime or development package.

## 20. Requirement coverage and evidence register

### 20.1 Feature-to-file coverage

Paths in this table are relative to the proposed `mod/bfl/` tree; short filenames refer to their folders in section 2.

| Feature from supplied plan | Implementation service and principal files | Detailed section |
| --- | --- | --- |
| Independent banks and charter management | `bfl_roles.txt`, bootstrap, embedded Economy finance/account commands | 5, 6, 17 |
| Decision conversion, full age investment, reform, one-bank cap | `bfl_charter_decisions.txt`, `bfl_charter.txt`, charter subject/reform, reconciliation | 6 |
| Capital/reserves and separate treasury | transaction core, schema/slots, capital/liquidity values | 3–5 |
| Monthly royalty and political costs | treasury payments/policy, financial static modifiers, Treasury GUI | 10 |
| Monthly activity dividends and loss carryforward | receipt adapter, treasury payments, equity, profit registers | 4, 10, 13 |
| Recurring funded custom sovereign bonds | issuer-owned ledger, facility policy/commands, account scheduler | 9, 10 |
| Custom sovereign bond resale/redemption | Stock Exchange-gated offers, current-holder settlement, cost basis; native ordinary resale remains gated | 9 |
| Demand/term/estate deposits | deposits effects/interactions, generated slots, account commands | 8 |
| Foreign branches | branches effects, native office, access/security contracts | 8 |
| Common sovereign lending and native takeover | credit adapter/interactions, exact native price/filters | 9 |
| Debt restructuring | credit/bond adapters, credit interactions, restructuring advance | 9 |
| Concessions, collateral, guarantees | security effects/interactions, encumbrance/guarantee records | 11 |
| Commodity investments | goods adapter, commodities, optional warehouse/methods | 12 |
| Receipts/forwards/later margining | commodity/security contracts, settlement, advanced gates | 12 |
| Bank shares/company equity and governance | equity effects/interactions, holder registers, company commands | 13, 14 |
| Commenda/exploration-linked ventures | commenda effects/interactions, operator accounts, outcome events | 13 |
| Currency, bills, notes, monetary mandate | monetary effects/interactions, note/acceptance registry | 15 |
| Interest policy | rates/quotes values, native adapters, monetary GUI | 15 |
| Interbank liquidity, clearing, public support | monetary/security/resolution effects, later advances | 15, 16 |
| Crises, contagion, recapitalization, wind-down | resolution, distress events, lifecycle hooks/migrations | 16 |
| Exactly two profiles and age/advance progression | specialization event, permission generator, financial advances | 6, 7 |
| Native company registration/operations/profits/failure | company operations, trade/receipt adapters, company GUI | 14 |
| Player controls, diplomacy, AI, synchronization | scripted GUIs, interactions, AI scores, transaction services | 17 |
| Required CMF integration without a new action bar | CMF metadata, `bfl_cmf_hooks.txt`, registration/alerts/log, native economy override and inline finance types | 2.3, 5, 17 |
| Graphics and FX | texture manifest, GUI states/timelines, optional map assets | 18 |
| Persistence, migration, compatibility, release | schema/migrations, hooks/stamps, manifests, tests/uploader | 5, 19 |

### 20.2 Local source links

The exact files were inspected read-only. These links open the installed references; they are not mod output files.

- [Native State Bank](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/subject_types/state_bank.txt>), [trade company](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/subject_types/trade_company.txt>), and [subject payment prices](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/prices/03_diplomacy.txt>).
- [Native takeover](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/country_interactions/take_over_loan.txt>), [takeover valuation](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/script_values/bank_loan_takeover.txt>), and [request-loan example](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/country_interactions/request_loan.txt>).
- [Decision examples](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/decisions/test_decisions.txt>), [Manila charter decision](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/decisions/manila_galleon_charter.txt>), and [banking events](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/events/economy/banking.txt>).
- [Renaissance advances](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/advances/0_age_of_renaissance.txt>), [Reformation advances](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/advances/0_age_of_reformation.txt>), [Absolutism advances](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/advances/0_age_of_absolutism.txt>), and [banking reform](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/government_reforms/country_specific.txt>).
- [Company buildings/creation](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/building_types/trade_company_buildings.txt>), [banking office](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/building_types/unique_buildings.txt>), [central bank](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/building_types/capital_buildings.txt>), and [native trade command](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/generic_actions/markets.txt>).
- [Scripted GUI schema](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/scripted_guis/scripted_guis.info>), [native economy GUI](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/gui/economy_lateralview.gui>), [scripted-widget registration](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/gui/scripted_widgets/_scripted_widgets.info>), and [animation example](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/gui_animations/test_asset.json>).
- [On-action schema](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/on_action/on_actions.info>), [native callback comments](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/in_game/common/on_action/_hardcoded.txt>), and [modifier type definitions](<C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/common/modifier_type_definitions/00_modifier_types.txt>).
- [Steam build manifest](<C:/Program Files (x86)/Steam/steamapps/appmanifest_3450310.acf>) and [installed uploader sample](<C:/Users/Thomas Altmann/Downloads/release-windows-gui-amd64/manager-config.json>).
- [Installed CMF 2.5.0 metadata](<C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776/.metadata/metadata.json>), [CMF lifecycle/registration hooks](<C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776/in_game/common/on_action/cmf_on_actions.txt>), and [extracted government GUI example](<C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776/in_game/gui/vanilla/cmf_government_lateralview_vanilla_types.gui>).
- [CMF alert effects](<C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776/in_game/common/scripted_effects/cmf_alert_effects.txt>), [CMF log effects](<C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776/in_game/common/scripted_effects/cmf_log_effects.txt>), [CMM boolean setting API](<C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776/in_game/common/scripted_effects/cmm_core_bool_setting_effects.txt>), and [CMF core triggers](<C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776/in_game/common/scripted_triggers/cmf_core_triggers.txt>).

### 20.3 Reproducible audit hashes

SHA-256 hashes recorded on 14 October 2026. Relative native paths are below `GAME`. Changes invalidate the corresponding source assumption and require adapter review.

| Source | SHA-256 |
| --- | --- |
| Supplied implementation plan | `6CF0F838C92F56DACC239152DD4148A83B01BF3CB13BB1D712455EF67E90107F` |
| `in_game/common/subject_types/state_bank.txt` | `7EB6A35B8961B8E7F2464BB00DA69EB0936462A2289C0A9ED157D5A6F430EC7D` |
| `in_game/common/country_interactions/take_over_loan.txt` | `710176339E75CDE1B0CAECEE499B28B6435C29997889707C0153DA08E4F3B6FE` |
| `in_game/common/building_types/trade_company_buildings.txt` | `30254D00521C9A4EB3B4A40AAAB4526A83F8CD05BEBE580EC31B3DB53CB1859E` |
| `in_game/common/advances/0_age_of_renaissance.txt` | `B2CAE08AFB4AA380BFC0275C9AC46550A0FCC7E6C5DB2857F27A3EACA938B705` |
| `in_game/common/scripted_guis/scripted_guis.info` | `D890908B3E579243B00198CE84572EC9E812E6BC73314742B878CD391EE2257C` |
| Native `in_game/gui/economy_lateralview.gui` | `675763819DE9C0F368761DEC5D01541553C78D9A9E25EA68135A5667BB2D621D` |
| CMF `.metadata/metadata.json` | `668C214D279F0DAF827417D2E280E1F495F0776A8DFD027D889F0C8D6933A5F8` |
| CMF `in_game/common/on_action/cmf_on_actions.txt` | `3F14E4C92196FC440BCA6D10CAE4C73D86FE74EA7B0C46041E6A99063911440C` |
| CMF `in_game/common/scripted_effects/cmf_alert_effects.txt` | `79A7A97D0270802B3149877A66B8F6CD78ED2B27A27C51DB23CBCE710E8D085C` |
| CMF `in_game/common/scripted_effects/cmm_core_bool_setting_effects.txt` | `2305B100729C2238BD44F1F3A8F5A6BB3ADAF7D273D188D6D69870B71BBA85EB` |

CMF paths in this table are relative to the installed Workshop framework root from section 1, not `GAME`. These hashes record source inspection, not successful P12 runtime execution.

### 20.4 Public references and evidence limits

- [EU5 wiki Modding](https://eu5.paradoxwikis.com/Modding) and [Mod structure](https://eu5.paradoxwikis.com/Mod_structure): requested reference pages; direct fetch returned 401. Local schemas/examples supply the implementation evidence here.
- [Engine-generated effects mirror](https://raw.githubusercontent.com/Europa-Universalis-5-Modding-Co-op/modding-digests/main/current_docs/effects.log): checked bond/loan/goods operation summaries. Mutable documentation is corroboration, not a substitute for this build's generated docs or cash-flow probes.
- [Engine scope-link mirror](https://raw.githubusercontent.com/Europa-Universalis-5-Modding-Co-op/modding-digests/main/current_docs/event_targets.log): checked the loan-to-borrower scope link; regenerate for the selected build before coding.
- [Community mod toolkit metadata](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-toolkit/blob/main/.metadata/metadata.json): structural metadata example; its sample compatibility version is not this mod's supported version.
- [Community Mod Framework](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework): required dependency and public integration entry point. [Metadata at audited GitHub commit](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/blob/38fe85623ada459207adc73fe8acffcd039e71ba/.metadata/metadata.json) identifies the development package and explains why it is not the installed 2.5.0 release baseline.
- [CMF vanilla-widget override documentation](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/Improved-Vanilla-Top-Level-Widget-Overrides) and [extraction tool at audited commit](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/blob/38fe85623ada459207adc73fe8acffcd039e71ba/tools/cmf_extract_vanilla_types.py): definition extraction and file-scoped constants; the inspected coverage omits economy. BFL's explicit replacement/definition ownership is specified in section 17.
- [CMF basic registration](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/Basic-Setup), [CMM setup](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/CMM-Basic-Setup), and [on-action documentation](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/On-Action-Hooks): public integration conventions, checked against installed 2.5.0 sources; older post-lobby hook names must not override local deprecation comments.
- [CMF custom alerts](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/Custom-Alerts), [action log](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/Mod-Action-Log), and [dependency popup](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-framework/wiki/Dependency-Check-Popup): framework notification/history/dependency services; exact release-matched calls and GUI templates are covered by the completed P12 audit; release compatibility remains M10.
- [Graphical assets](https://github.com/Europa-Universalis-5-Modding-Co-op/graphical-assets): template reference with no promised banking pack; inspect actual future assets/licenses individually.
- [pdx-workshop-manager](https://github.com/kaiser-chris/pdx-workshop-manager): publishing workflow reference; installed sample informs the proposed configuration schema.

Completion means the full feature set is implemented across both exclusive profiles and their common sovereign core, all required native bridges pass on the pinned game/CMF combination, and both player roles pass persistence, performance, and campaign tests. Banking and finance management must work inside the existing Economy panel with native controls preserved and no added BFL action bar or separate finance launcher. This document supplies the technical design and evidence boundary; no game execution, mod installation, media generation, or Workshop publication was performed while preparing it.
