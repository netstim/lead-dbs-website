# Opt-in MATLAB integration (lab release handoff)

These helpers are prepared, not installed in a Lead-DBS release. The MATLAB
runtime is unavailable in the website environment, so a lab runtime test is
required before shipping. Do not describe this integration as deployed.

1. Confirm the deployed PHP collector and data policy. Its configured URL is
   `https://www.lead-dbs.org/release/analytics/collect.php`; change the helper if
   the lab selects another first-party endpoint.
2. Add both helper files to the toolbox and compiled-app packaging manifest.
3. Replace the entire legacy tracking block in `ea_firstrun_public.m` (the
   `if ~strcmp(handles.prod,'dbs_connectome')` block around webread/urlread of
   `stats.php`) with `ea_analytics(handles.prod);`. Do not leave the legacy call
   running beside the new helper. The audited public file's blob is
   `e90ed0939f5248d687caa3b224ce5d6af4d433c6`.
4. Add a user-selected Preferences menu action calling `ea_analytics_consent`.
   Do not enable analytics automatically or force a dialog during analysis.
5. Public/development variants must follow the same policy. Leave opted-out
   builds silent. Do not infer consent from the existence of old usage logs.

Release checks (MATLAB and standalone, on the supported OS matrix):

- Fresh preferences: startup makes no collect.php or legacy stats.php request.
- Enable via the dialog: startup makes one JSON request with the documented
  fields; no patient/path/free-text data. Verify server response and aggregate.
- Disable or Cancel: Disable stops requests; Cancel leaves preference unchanged.
- Unreachable service, 400, 429 and 503: the toolbox remains usable. Timeout is
  bounded to 2 seconds; no retry storm and no error payload upload.
- Multiple tools: verify the expected tool names and app/runtime versions.
- Compiled app: Java UUID, webwrite and preferences availability are verified.

No persistent installation ID is introduced. These remain opted-in request
statistics, not unique-installation or retention metrics. Participation is
unknown without a separate, approved measurement design.

Before release, the lab must supply the service privacy notice from the same
settings action, verify its webserver-log/backup disclosures, and demonstrate
the independent retention job. The prepared consent text describes scheduled
deletion; it does not assert that raw addresses cannot exist in server logs.
