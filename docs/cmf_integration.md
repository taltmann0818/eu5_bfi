# CMF 2.5.0 integration

The mod declares the installed `community_mod_framework` release **2.5.0** as a separate required dependency. `BFI_dev` contains BFI and CMF only, as the user confirmed. The full framework runtime is not copied into this mod.

Public services used: `cmm_register_bool_setting`, `cmf_set_alert_open_view`, `cmf_show_alert`, `cmf_remove_alert`, `cmf_log`, `cmf_log_decimal_value`; hooks: `cmf_on_mod_registration`, `on_game_load_after_lobby`, `cmf_on_country_transfer`, `cmf_monthly_human_country_pulse`. The native all-country pulse owns accounting; CMF human-only pulses own alerts. Registration never initializes money, changes profiles or settles accounts.

Three presentation preferences are registered idempotently, with CMM's `_name`/`_desc` localization convention. Initial feedback is static. Expanded-detail and notification preference consumption/callback behavior still require P12 and are not advertised as complete toggles. No financial policy is stored in CMM resettable preferences.

The inspected installed CMF release lacks an Economy injection slot and an extracted Economy definition set. BFI owns one explicit native Economy override and one extracted native types/template helper. The build proves these reconstruct the complete original file when the single finance insertion is removed. Other mods replacing Economy require a combined compatibility edit.

The public GitHub release list currently exposes **2.4.1**, while the installed Workshop release is **2.5.0**. A release-matched self-contained dependency popup was not available in the installed package. Rather than silently vendoring an older helper, this build relies on declared dependency metadata and the verified playset. Acquiring/reviewing a 2.5.0 helper remains release work.
