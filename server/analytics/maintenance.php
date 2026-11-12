<?php
declare(strict_types=1);
// CLI only. Never expose health data or exports as an unauthenticated HTTP endpoint.
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require_once __DIR__ . '/bootstrap.php';
try {
    $collector = lead_analytics_collector();
    $command = $argv[1] ?? '';
    $result = match ($command) {
        'health' => $collector->health(),
        'retain' => $collector->retain(),
        'export' => $collector->aggregate($argv[2] ?? ''),
        default => throw new InvalidArgumentException('Use health, retain, or export YYYY-MM-DD.')
    };
    echo json_encode($result, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES) . "\n";
} catch (Throwable $e) { fwrite(STDERR, "Analytics maintenance failed. Check private configuration and storage.\n"); exit(1); }
