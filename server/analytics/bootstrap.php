<?php
declare(strict_types=1);
require_once __DIR__ . '/Collector.php';

use LeadAnalytics\Collector;
use LeadAnalytics\Storage;

/** Optional positive-integer settings and their defaults (bytes and milliseconds). */
const LEAD_ANALYTICS_LIMITS = [
    'max_database_bytes' => Storage::DEFAULT_MAX_DATABASE_BYTES,
    'min_free_bytes' => Storage::DEFAULT_MIN_FREE_BYTES,
    // The download hook runs before the download response, so it waits for the database lock only briefly.
    'hook_busy_timeout_ms' => 200,
    'collect_busy_timeout_ms' => 1000,
];

/**
 * Reads the private JSON configuration and validates only the path and limit keys the caller uses,
 * so that, for example, retention never depends on collection-only settings.
 */
function lead_analytics_config(array $paths, array $limits = []): array {
    $file = getenv('LEAD_ANALYTICS_CONFIG');
    if (!$file || !is_readable($file)) throw new RuntimeException('Analytics configuration unavailable.');
    $config = json_decode((string) @file_get_contents($file), true, 8, JSON_THROW_ON_ERROR);
    if (!is_array($config)) throw new RuntimeException('Analytics configuration must be an object.');

    foreach ($paths as $key) {
        if (!isset($config[$key]) || !is_string($config[$key]) || !str_starts_with($config[$key], '/')) {
            throw new RuntimeException('Analytics paths must be absolute.');
        }
    }
    // An empty DOCUMENT_ROOT (the CLI) must not fall back to the working directory, which realpath('') returns.
    $documentRoot = $_SERVER['DOCUMENT_ROOT'] ?? '';
    $root = is_string($documentRoot) && $documentRoot !== '' ? realpath($documentRoot) : false;
    if ($root !== false) {
        $private = [$file];
        foreach ($paths as $key) {
            $private[] = $config[$key];
        }
        foreach ($private as $path) {
            $resolved = realpath($path) ?: (realpath(dirname($path)) . '/' . basename($path));
            if ($resolved === $root || str_starts_with($resolved, $root . '/')) {
                throw new RuntimeException('Analytics private files must be outside the document root.');
            }
        }
    }

    foreach ($limits as $key) {
        $value = $config[$key] ?? LEAD_ANALYTICS_LIMITS[$key];
        if (!is_int($value) || $value < 1) throw new RuntimeException('Analytics limits must be positive integers.');
        $config[$key] = $value;
    }
    return $config;
}

/** The private database alone: no Composer dependencies, key or country database. */
function lead_analytics_storage(bool $withLimits = false): Storage {
    $limits = $withLimits ? ['max_database_bytes', 'min_free_bytes'] : [];
    $config = lead_analytics_config(['database'], $limits);
    if (!$withLimits) {
        return new Storage($config['database']);
    }
    return new Storage($config['database'], Storage::MAINTENANCE_BUSY_TIMEOUT_MS,
        $config['max_database_bytes'], $config['min_free_bytes']);
}

/** $caller is 'collect' or 'hook' and selects that caller's lock wait budget. */
function lead_analytics_collector(string $caller = 'collect'): Collector {
    $busyTimeout = match ($caller) {
        'collect' => 'collect_busy_timeout_ms',
        'hook' => 'hook_busy_timeout_ms',
    };
    $paths = ['database', 'key_file', 'country_database'];
    $config = lead_analytics_config($paths, array_keys(LEAD_ANALYTICS_LIMITS));
    if (array_diff(array_keys($config), [...$paths, ...array_keys(LEAD_ANALYTICS_LIMITS)])) {
        throw new RuntimeException('Unknown analytics setting.');
    }
    if (!is_file(__DIR__ . '/vendor/autoload.php')) throw new RuntimeException('Collector dependencies unavailable.');
    require_once __DIR__ . '/vendor/autoload.php';
    $key = @file_get_contents($config['key_file']);
    if ($key === false) throw new RuntimeException('Analytics key unavailable.');

    $storage = new Storage($config['database'], $config[$busyTimeout],
        $config['max_database_bytes'], $config['min_free_bytes']);
    // Opened on the first lookup only, so requests rejected before it never read the country database.
    $countryDatabase = $config['country_database'];
    $reader = null;
    $lookup = static function (string $ip) use (&$reader, $countryDatabase) {
        if ($reader === null) {
            $reader = new MaxMind\Db\Reader($countryDatabase);
        }
        return $reader->get($ip)['country']['iso_code'] ?? 'ZZ';
    };
    return new Collector($storage, $key, $lookup);
}
