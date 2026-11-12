function ea_analytics(tool)
% Optional aggregate usage reporting. Off unless the user explicitly enables it.
% No installation ID, patient identifier, path, project name or error text.
try
    if ~ispref('LeadDBS', 'analyticsEnabled') || ...
            ~isequal(getpref('LeadDBS', 'analyticsEnabled'), true)
        return;
    end
    allowed = {'dbs', 'group', 'connectome', 'anatomy'};
    if ~any(strcmp(tool, allowed))
        tool = 'other';
    end
    appVersion = ea_getvsn('local');
    appVersion = regexprep(appVersion, ' Standalone$', '');
    if isempty(regexp(appVersion, '^\d{1,3}(\.\d{1,4}){0,3}(-[a-z0-9]{1,12})?$', 'once'))
        appVersion = 'unknown';
    end
    event = struct('schema', 1, 'event_id', char(java.util.UUID.randomUUID()), ...
        'kind', 'access', 'item', tool, 'app_version', appVersion, ...
        'runtime_version', ['R', version('-release')], 'outcome', 'request', ...
        'consent', true);
    options = weboptions('MediaType', 'application/json', 'Timeout', 2);
    % Lab must activate this endpoint before releasing this integration.
    webwrite('https://www.lead-dbs.org/release/analytics/collect.php', event, options);
catch
    % Analytics must never interrupt scientific work or report private errors.
end
end
