<?php
declare(strict_types=1);

// The address the contact and FOCUS forms post to (data/forms.yaml: action). README.md in this folder says how
// it is configured and deployed. Answers JSON to the page's script (assets/js/main/forms.js) and a small HTML
// page to a browser without script:
//   200 sent, 400 a field is missing or wrong, 403 posted from another site, 405 not a POST,
//   413 too large, 415 not a form, 429 too many from one address, 503 could not be passed on.
// A 400 for one field names it in the JSON reply ("field") and says what to fix.
ini_set('display_errors', '0');
require_once __DIR__ . '/FormHandler.php';

use LeadForms\FieldError;
use LeadForms\FormHandler;

header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');

$wantsJson = str_contains($_SERVER['HTTP_ACCEPT'] ?? '', 'application/json');
$config = null;
$form = is_string($_POST[FormHandler::FORM_FIELD] ?? null) ? $_POST[FormHandler::FORM_FIELD] : '';

/** ends the request with a status and the sentence the visitor reads (and, for a 400, the field to fix) */
function lead_forms_reply(int $status, string $text, ?string $field = null): never
{
    global $wantsJson, $config, $form;
    http_response_code($status);
    if ($status === 429) header('Retry-After: ' . ($config['window'] ?? 600));
    if ($wantsJson) {
        header('Content-Type: application/json; charset=UTF-8');
        $reply = ['ok' => $status === 200, 'message' => $text];
        if ($field !== null) $reply['field'] = $field;
        echo json_encode($reply, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        exit;
    }
    header('Content-Type: text/html; charset=UTF-8');
    header("Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'");
    $back = $config['pages'][$form] ?? '/';
    $e = static fn(string $s) => htmlspecialchars($s, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="robots" content="noindex"><title>', $status === 200 ? 'Sent' : 'Not sent', ' · Lead-DBS</title>',
        '<style>body{font:1.0625rem/1.6 system-ui,sans-serif;max-width:36rem;margin:15vh auto;padding:0 1rem;color:#1c1f24;background:#fff}',
        '@media (prefers-color-scheme:dark){body{color:#e6e8eb;background:#14171b}a{color:#8fb8ff}}</style></head><body>',
        '<p>', $e($text), '</p>';
    // without script there is no offline line from the page: the way by email is named here
    $to = $config['recipients'][$form] ?? '';
    if ($status !== 200 && $to !== '') echo '<p>Or write to <a href="mailto:', $e($to), '">', $e($to), '</a>.</p>';
    echo '<p><a href="', $e($back), '">Back to the page</a></p></body></html>';
    exit;
}

/** the private configuration (README.md): LEAD_FORMS_CONFIG, or lead-forms/config.json beside the web root */
function lead_forms_config(): array
{
    $root = $_SERVER['DOCUMENT_ROOT'] ?? '';
    $path = getenv('LEAD_FORMS_CONFIG') ?: dirname((string) realpath($root)) . '/lead-forms/config.json';
    return FormHandler::config($path, $root !== '' ? $root : null);
}

/** what the visitor should fix, for the field a FieldError names */
function lead_forms_field_message(FieldError $error): string
{
    return match ([$error->field, $error->problem]) {
        ['name', 'missing'] => 'Enter your name.',
        ['email', 'missing'] => 'Enter your email address.',
        ['email', 'invalid'] => 'Enter a valid email address.',
        ['message', 'missing'] => 'Enter your message.',
        ['academic', 'missing'] => 'Confirm that FOCUS will be used for academic research only.',
        default => 'Check the required fields and email address, then send again.',
    };
}

/** hands the email over for delivery: to PHP's mail(), or (for tests) into a folder */
function lead_forms_deliver(array $config, array $mail): bool
{
    if (($config['delivery'] ?? 'mail') === 'outbox') {
        $headers = '';
        foreach (['To' => $mail['to'], 'Subject' => $mail['subject']] + $mail['headers'] as $k => $v) $headers .= "{$k}: {$v}\r\n";
        $name = rtrim($config['outbox'], '/') . '/' . gmdate('Ymd\THis') . '-' . bin2hex(random_bytes(4)) . '.eml';
        return @file_put_contents($name, $headers . "\r\n" . $mail['body'], LOCK_EX) !== false;
    }
    $params = !empty($config['envelope_sender']) ? '-f' . $config['from'] : '';
    return mail($mail['to'], $mail['subject'], $mail['body'], $mail['headers'], $params);
}

$failed = 'Sending didn’t work. Please try again later.';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    lead_forms_reply(405, 'This address only takes form submissions.');
}
$type = strtolower(trim(explode(';', $_SERVER['CONTENT_TYPE'] ?? '')[0]));
if (!in_array($type, ['application/x-www-form-urlencoded', 'multipart/form-data'], true)) {
    lead_forms_reply(415, 'This address only takes form submissions.');
}
if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > FormHandler::MAX_BODY || !empty($_FILES)) {
    lead_forms_reply(413, 'The message is too long.');
}

try {
    $config = lead_forms_config();
} catch (Throwable $e) {
    error_log('Lead forms: configuration unavailable.');
    lead_forms_reply(503, $failed);
}

// a form posted from another site (a browser always names the origin of a cross-site POST)
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && !in_array($origin, $config['origins'] ?? [], true)) lead_forms_reply(403, $failed);

$sent = $form === 'downloadfocus'
    ? 'Request sent. The team will email you the download link.'
    : 'Message sent. We’ll reply by email.';

// a bot filled the field people never see: answer exactly as if sent, send nothing
if (($_POST[FormHandler::TRAP] ?? '') !== '') lead_forms_reply(200, $sent);

try {
    $clean = FormHandler::validate($form, $_POST);
} catch (FieldError $e) {
    lead_forms_reply(400, lead_forms_field_message($e), $e->field);
} catch (InvalidArgumentException $e) {
    lead_forms_reply(400, 'Check the required fields and email address, then send again.');
}

// the scheduled sweep (sweep.php) is what deletes old rate-limit files; this only helps it along
if (random_int(1, 50) === 1) {
    try {
        FormHandler::sweep($config['rate_dir']);
    } catch (RuntimeException $e) {
        error_log('Lead forms: the rate-limit sweep failed.');
    }
}

try {
    if (FormHandler::overLimit($config['rate_dir'], $config['rate_key'], $_SERVER['REMOTE_ADDR'] ?? '',
        $config['limit'], $config['window'])) {
        $minutes = (int) ceil($config['window'] / 60);
        lead_forms_reply(429, $minutes === 1
            ? 'Too many requests. Try again in a minute.'
            : "Too many requests. Try again in {$minutes} minutes.");
    }
    $mail = FormHandler::message($form, $clean, $config['recipients'][$form], $config['from'], $config['site']);
    if (!lead_forms_deliver($config, $mail)) throw new RuntimeException('Delivery refused.');
} catch (RuntimeException $e) {
    // no field values in the log: only that it failed and for which form
    error_log("Lead forms: {$form} could not be passed on for delivery.");
    lead_forms_reply(503, $failed);
}

lead_forms_reply(200, $sent);
