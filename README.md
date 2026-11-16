# Overkiz CPU Fix (Test)

Temporary HACS override for the built-in Overkiz integration in **Home Assistant
2026.11.0**. It uses the existing integration configuration and entities; do not
delete or re-add Overkiz. This is a personal test build, not an upstream release.

## Source and Scope

- Integration: Home Assistant Core `2026.11.0`, commit
  `74cf5a49c63ed8d4d87717844bf14f79c28c9cea`.
- Library: [Vaiz/ha-overkiz-api](https://github.com/Vaiz/ha-overkiz-api), commit
  `d025ac8890afe8c2b0b2cbbb6e46d607d6eea6bc`.
- The library version remains **2.3.1**. The wrapper's required custom-integration
  version is separate: **2026.11.0.1**.
- The library fix reuses retry wrappers instead of accumulating backoff handlers
  during event polling and listener unregistration. Retry budgets are unchanged.
- Integration Python files are copied unchanged from the release. Only packaging,
  manifest metadata, the pinned library requirement, English translations, and the
  official Overkiz icon are added or adapted.
- English labels are bundled. Other languages fall back to English.
- No entity IDs, helpers, secrets, or credential substitutions are required.
  Existing Overkiz credentials remain in Home Assistant, not this repository.

Compatibility outside HA 2026.11.0 is unverified. HACS enforces a minimum version,
not an upper bound. Remove this override before upgrading HA unless a matching
wrapper has been validated. Do not run a second HA instance against the same
account just to compare results; event listeners can interfere.

## Install Through HACS

1. Make a full Home Assistant backup and choose a maintenance window. Restarting
   interrupts HA and shutter automations temporarily.
2. Ensure HACS is installed. If you already have a manual
   `/config/custom_components/overkiz/` override, move it outside
   `custom_components` first and retain it for rollback; do not mix the files.
3. In HACS, open **Custom repositories**, add
   `https://github.com/Vaiz/ha-overkiz-test`, and select **Integration**.
4. Download **Overkiz CPU Fix (Test)**. HACS installs it into
   `/config/custom_components/overkiz/`. No YAML registration or includes are
   needed. Keep your existing Overkiz integration entry.
5. Run Home Assistant's configuration check. Inspect errors before proceeding.
6. Restart Home Assistant, not just the Overkiz integration. HA needs outbound
   HTTPS access to GitHub and its normal package indexes to install the pinned
   library archive and dependencies.
7. Check startup logs for custom Overkiz loading and dependency-installation
   errors. The custom-integration warning is expected. Confirm devices, entities,
   and credentials are retained.

HA 2026.11.0 passes direct-URL requirements to its package manager even when a
package with the same version is installed. The immutable URL identifies this
build; the displayed version alone cannot establish that the patch is loaded.

## Verify the Fix

- Take a short profiler capture after startup and another after several hours,
  ideally at least the uptime that previously produced spikes. Compare equivalent
  activity and uptime: restarting stock HA also clears the accumulated handlers.
- Confirm `backoff._ensure_coroutine` no longer reaches hundreds of thousands of
  calls through Overkiz polling, and CPU spikes do not grow with uptime.
- Observe state updates at rest. Test a single shutter movement only when safe,
  and check normal control and state feedback.
- Observe repeated polls and ordinary reconnection behavior. Unavailable inputs
  should still be surfaced; do not deliberately disrupt a safety-sensitive setup.
- After a later restart, confirm the override still loads and control works.

The patched library passed 668 offline tests, including wrapper reuse and bounded
refresh retries. This wrapper has offline packaging/syntax tests only; no live HA
schema check, HACS install, authentication, device control, or CPU improvement has
been verified in the user's instance.

## Roll Back

1. Remove this repository's downloaded integration using HACS. Do **not** delete
   the configured Overkiz entry from Settings > Devices & services.
2. Confirm only this wrapper's `/config/custom_components/overkiz/` directory was
   removed. If you had a previous custom override, restore that saved directory.
3. Run HA's configuration check and restart HA to return to the built-in code
   (or your restored override). Check logs and entity availability.

The fork deliberately uses the same library version as stock. Removing the
wrapper is therefore **not proof that stock library bytes were reinstalled**:
HA's normal `==2.3.1` requirement can accept the installed fork. A recreated
official HA Core container/runtime restores its bundled stock dependency; the
exact reinstall procedure depends on HA installation type. An ordinary restart
alone is insufficient to guarantee dependency rollback. Keep the pre-test backup
and use your installation's supported restore/reinstall procedure if needed.

## Local Validation and Maintenance

With Python 3.14 available, run:

```sh
uv run --python 3.14 --no-project python -m unittest discover -s tests -v
```

The tests do not import HA, connect to devices, or install anything in HA. For a
new HA release, refresh the integration files from that exact release, preserve
the license, resolve English translation references again, review compatibility,
and rerun validation before publishing. Library changes require updating the full
commit SHA in the manifest explicitly; this does not track the fork's branch.

## Attribution

Integration source is from [Home Assistant Core](https://github.com/home-assistant/core/tree/2026.11.0/homeassistant/components/overkiz)
under its Apache 2.0 license, included as `LICENSE.md`. The unmodified brand icon
comes from [Home Assistant Brands](https://github.com/home-assistant/brands/tree/master/core_integrations/overkiz).
Please report issues with this temporary wrapper to this repository, not upstream.