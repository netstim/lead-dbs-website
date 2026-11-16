<?php
declare(strict_types=1);
// CLI only. Never expose health data or exports as an unauthenticated HTTP endpoint.
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require_once __DIR__ . '/bootstrap.php';
// Opens the private database only, so a broken key, country database or vendor folder cannot stop retention.
try {
    $command = $argv[1] ?? '';
    if (!in_array($command, ['health', 'retain', 'export'], true)) {
        throw new InvalidArgumentException('Use health, retain, or export YYYY-MM-DD.');
    }
    $storage = lead_analytics_storage($command === 'health');
    $result = match ($command) {
        'health' => $storage->health(),
        'retain' => $storage->retain(),
        'export' => $storage->aggregate($argv[2] ?? ''),
    };
    echo json_encode($result, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES) . "\n";
} catch (Throwable $e) {
    fwrite(STDERR, "Analytics maintenance failed. Check private configuration and storage.\n");
    exit(1);
}
