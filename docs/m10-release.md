# M10 release integration

M10 remains **partial**. The canonical status and completion gate are in
[coverage.md](coverage.md). This change integrates conservative monthly credit
and deposit strategy, AI company policy and inspectable release measurements.
It does not relabel focused fixtures as full campaigns.

[Acceptance provenance](../tests/results/2026-10-21-m10-validation.json) records
**53 strategy + 114 accounts/bond + 46 credit = 213 native assertions**, twelve
monthly settlements and fresh-process reload, **140 offline tests**, native/CMF
pins, deterministic generation, Economy reconstruction and **335-file staging**.
The strategy suite runs shipping `f59f4d34…`. Accounts and credit regressions
retain their actual `ee2a4c1b…` hashes: only bank strategy traversal differs, and
those controlled suites explicitly keep it manual. Every underlying financial,
receipt, bond and company service and the GUI are byte-identical.

[Eight normal UI observations and five captures](../tests/results/2026-10-21-m10-ui.json)
cover both roles, opt-in, funded natural demand placements and manual management.
Captures retain their real earlier hashes; their GUI and localization are
byte-identical to shipping. Four are original window JPEGs; one is an unaltered
bank-panel crop excluding another application. Fixture cash, branches and
ownership are explicit setup, not measured campaign balance.

## Investment mandate

Economy → Credit → Lending & Investments starts with **Investment mandate**.
Players choose **Delegate investments** or **Manage investments**. Existing saves
acquire counters without resetting accounts, cash, profiles or accepted contracts.
An independent AI bank delegates automatically; a chartered AI bank does so only
when its live controller is also AI. Explicit manual policy persists after reload.

The strategy runs after settlement, expenses, dividends and the sovereign bond
facility. It stamps the period before dispatch. It considers up to twelve
credit candidates reached through owned completed current-capital branches and
registered companies in the bank's native market. When no credit offer is made,
it considers up to twelve accepting independent banks in the existing financial
institution register. It does not scan the world country registry per bank.
Register/building traversal still scales with its size; the evaluated-candidate
caps are not a claim of constant time independent of institution count.

Credit is a 100-gold, 60-month production offer, shared by both profiles for
sovereigns and restricted to Merchant Finance for companies. Candidate scoring
uses creditworthiness, current debt, income and operating balance. War, lack of
need, excessive rates, funding/capital shortfalls, missing branches and excessive
single-party exposure reject new business. Prospective annual rates must be at
most 15%; the new monthly coupon must fit within 25% of native monthly income.
Combined debt uses the existing 24-month income ceiling. New exposure, including
existing native claims, is capped at 25% of bank equity. A sent offer starts a
three-month cooldown. Offers move no cash until the normal acceptance service
rechecks the transaction. AI borrowers decline unnecessary or expensive credit.

The alternative is one 100-gold on-demand placement. It requires at least 600
free cash and 100 capital headroom, a positive offered rate, +50 admission
opinion, a solvent accepting independent bank and no reciprocal deposit chain.
Total deposit assets may not exceed 200 gold or 10% of current equity. A single
recorded depository prevents spreading small placements across an unbounded
number of banks. Low available cash or recipient distress requests normal
withdrawal; shortages remain claims under the existing recovery rules.

The card shows policy, candidate count, score, last action and cumulative offers,
placements and recalls. A policy click neither spends money nor runs another
monthly settlement. Manual policy stops new strategy business; the product
services continue to service accepted claims. Other independently authorized
goods, equity, branch and monetary policies retain their own services.

## Company controller

A native AI company with a live AI landed controller receives a trade mandate
once. A funded 100-gold controller contribution is considered at most quarterly
when company reserves are low and the controller retains at least 500 gold and
has a nonnegative budget. The existing contribution/authority service executes
the transfer. It does not become income. Human controller mandates are preserved.
Native route and exploration AI remain native; this controller does not invent
trade receipts or grant sailors, research, buildings or exploration progress.

**Fresh-1337 performance:** [Native timing evidence](../tests/results/2026-10-21-m10-performance.json) passes the predeclared 10% threshold: 2.271999 seconds/month with CMF and 2.314047 with CMF+BFI (**+1.85%**), using 36 measured native Month rows per arm after twelve warmup months. Both arms have no BFI-attributed errors. Three native banks and zero active custom-product records at the snapshot limit this to a fresh population; emergent AI histories differ. This does not close the populated late-game or full M10 performance gate.

## Reproduction and evidence boundaries

```powershell
python tools/generate_scripts.py
python -m unittest discover -s tests -q
python tools/validate_sources.py
python tools/audit_native.py --compare
./tools/run_campaign.ps1 -Suite m10 -Output tests/results/local-m10
python tools/benchmark_release.py --output tests/results/local-m10-performance.json
python tools/prepare_m10_ui.py --userdir dist/interactive-m10/user
```

The M10 engine suite exercises both management roles and profiles, cash/title
conservation, concentration, consent and replay boundaries, twelve consecutive
settlements and fresh-process reload. Existing financial suites explicitly keep
the new strategy manual so they remain controlled product regressions. The
dedicated strategy suite explicitly enables it. Fixture grants and cash shocks
are recorded test setup, never campaign balance evidence.

The benchmark runs CMF alone and CMF+BFI sequentially with identical fresh-1337
settings and no debug grants. It excludes twelve warmup months, retains 72 native
`gametimer` Month measurements per arm and reports machine, source and fixture
identity. The predeclared threshold is a median monthly ratio of at most 1.10.
Fresh populations and different emergent AI histories do not establish populated
late-game performance or identical-save causality. Run without concurrent game
processes. Failed, incomplete or changed-source runs cannot pass.

Actual-game UI observations and accepted native results are recorded separately
with their real runtime/fixture hashes. A queued CI job is not accepted evidence.

## Remaining M10 gate

- Both player roles and profiles through full integrated campaigns, covering
  natural age/research progression and later-age continuation of M1–M9 products.
- Recorded sustainable debt-led treasury scenarios with actual outside earnings,
  funding sources, losses, debt service and liquidity; no fixture cash refills.
- Broader venture origination/negotiation and company investment strategy and
  release-wide calibration of opportunity, maturity and portfolio decisions.
- Full language/translation coverage, additional responsive layouts, populated
  long ledgers, advance/outcome art and animation/FX acceptance.
- Populated late-game scale/performance and compatibility with additional mods;
  narrow native override reconstruction and patch/CMF source pins remain required.

These remain release gates. Neither the strategy fixture nor the fresh-1337
benchmark certifies all of M10 or changes the supported EUV/CMF versions.
