<?php
declare(strict_types=1);
ini_set('display_errors', '0');
require_once __DIR__ . '/bootstrap.php';
header('Cache-Control: no-store');
header('Content-Type: application/json');
// Honour explicit privacy signals without opening storage.
if (($_SERVER['HTTP_DNT'] ?? '') === '1' || ($_SERVER['HTTP_SEC_GPC'] ?? '') === '1') { http_response_code(204); exit; }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { header('Allow: POST'); http_response_code(405); exit; }
if (strtolower(trim(explode(';', $_SERVER['CONTENT_TYPE'] ?? '')[0])) !== 'application/json') { http_response_code(415); exit; }
$body = file_get_contents('php://input', false, null, 0, 4097);
if ($body === false || strlen($body) > 4096) { http_response_code(413); exit; }
try {
    $event = json_decode($body, true, 8, JSON_THROW_ON_ERROR);
    if (!is_array($event) || array_is_list($event)) throw new InvalidArgumentException('Expected event object.');
    // Direct clients can submit access requests only. Download outcomes must be
    // recorded by the server integration that actually selected the response.
    if (($event['kind'] ?? '') !== 'access') throw new InvalidArgumentException('Server-only event.');
    LeadAnalytics\Collector::validate($event);
    $result = lead_analytics_collector()->record($event, $_SERVER['REMOTE_ADDR'] ?? '', $_SERVER['HTTP_USER_AGENT'] ?? '');
    http_response_code($result === 'rate_limited' ? 429 : 204);
    if ($result === 'rate_limited') header('Retry-After: 60');
} catch (InvalidArgumentException | JsonException $e) {
    http_response_code(400);
} catch (Throwable $e) {
    // Do not leak paths, addresses, payloads or credentials to clients/logs.
    error_log('Lead analytics collection failed.');
    http_response_code(503);
}
