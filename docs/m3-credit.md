# M3 sovereign credit and bond acceptance

This branch implements M3 from `docs/coverage.md`, including native accepted
credit offers, acquisition basis and default bookkeeping, researched consensual
restructuring, Merchant corporate credit, and the sovereign bond desk.

Secondary bond trading requires a completed owned Stock Exchange on each side.
Research is not a transaction prerequisite: event-granted early exchanges must
work. Primary issuance and servicing remain independent of exchange access.

The bond interface will separate issuance terms, recurring funding, outstanding
obligations and secondary offers, with space for current holders and cash flows.
Financial services remain the authority for all transactions.

M3 is in progress. Engine, reload and visual acceptance will be recorded here;
source implementation and offline tests alone do not establish completion.
