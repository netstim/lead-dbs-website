<?php
declare(strict_types=1);
require_once __DIR__ . '/Collector.php';

function lead_analytics_config(): array {
    $path = getenv('LEAD_ANALYTICS_CONFIG');
    if (!$path || !is_readable($path)) throw new RuntimeException('Analytics configuration unavailable.');
    $config = json_decode(@file_get_contents($path), true, 8, JSON_THROW_ON_ERROR);
    foreach (['database','key_file','country_database'] as $key) {
        if (!isset($config[$key]) || !is_string($config[$key]) || $config[$key][0] !== '/') throw new RuntimeException('Analytics paths must be absolute.');
    }
    $root = realpath($_SERVER['DOCUMENT_ROOT'] ?? '') ?: null;
    foreach ([$path, $config['database'], $config['key_file'], $config['country_database']] as $private) {
        $resolved = realpath($private) ?: (realpath(dirname($private)) . '/' . basename($private));
        if ($root && ($resolved === $root || str_starts_with($resolved, $root . '/'))) throw new RuntimeException('Analytics private files must be outside the document root.');
    }
    return $config;
}

function lead_analytics_collector(): LeadAnalytics\Collector {
    $config = lead_analytics_config();
    if (!is_file(__DIR__ . '/vendor/autoload.php')) throw new RuntimeException('Collector dependencies unavailable.');
    require_once __DIR__ . '/vendor/autoload.php';
    $reader = new MaxMind\Db\Reader($config['country_database']);
    return new LeadAnalytics\Collector($config['database'], @file_get_contents($config['key_file']),
        static fn(string $ip) => ($reader->get($ip)['country']['iso_code'] ?? 'ZZ'));
}
