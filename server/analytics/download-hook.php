<?php
declare(strict_types=1);
require_once __DIR__ . '/bootstrap.php';

/** Call from the existing handler AFTER it determines its result. Never send a response here. */
function lead_analytics_download(string $artifact, string $outcome, string $version = 'unknown'): bool {
    if (($_SERVER['HTTP_DNT'] ?? '') === '1' || ($_SERVER['HTTP_SEC_GPC'] ?? '') === '1') return true;
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'GET') return true; // Do not count HEAD probes as delivery.
    try {
        $registry = json_decode(@file_get_contents(__DIR__.'/artifacts.json'), true, 16, JSON_THROW_ON_ERROR);
        $known = array_merge(...array_values($registry['aliases']));
        if (!in_array($artifact, $known, true) && !preg_match('/^updates_?\d{2,6}[-_]\d{2,6}$/D', $artifact)) $artifact = 'unknown';
        if (!preg_match('/^(?:unknown|[0-9]{1,3}(?:\.[0-9]{1,4}){0,3}(?:-[a-z0-9]{1,12})?|R[0-9]{4}[ab])$/D', $version)) $version = 'unknown';
        $bytes = random_bytes(16);
        $bytes[6] = chr((ord($bytes[6]) & 0x0f) | 0x40);
        $bytes[8] = chr((ord($bytes[8]) & 0x3f) | 0x80);
        $hex = bin2hex($bytes);
        $id = substr($hex,0,8).'-'.substr($hex,8,4).'-'.substr($hex,12,4).'-'.substr($hex,16,4).'-'.substr($hex,20);
        lead_analytics_collector()->record(['schema'=>1,'event_id'=>$id,'kind'=>'download','item'=>$artifact,
          'app_version'=>$version,'outcome'=>$outcome], $_SERVER['REMOTE_ADDR'] ?? '', $_SERVER['HTTP_USER_AGENT'] ?? '');
        return true;
    } catch (Throwable $e) {
        error_log('Lead download analytics failed.');
        return false; // Analytics failure must not break a download or redirect.
    }
}
