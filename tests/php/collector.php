<?php
declare(strict_types=1);
// Standalone collector checks. Needs PHP with pdo_sqlite only: no Composer dependencies.
$collectorDir = is_dir(__DIR__ . '/../../collector') ? __DIR__ . '/../../collector' : __DIR__ . '/../../server/analytics';
require $collectorDir . '/Collector.php';

use LeadAnalytics\Collector;
use LeadAnalytics\Storage;

function check(bool $ok, string $why): void
{
    if (!$ok) {
        throw new RuntimeException($why);
    }
}

function event(int $i, string $kind = 'access', string $item = 'dbs'): array
{
    return [
        'schema' => 1,
        'event_id' => sprintf('12345678-1234-4234-8234-%012d', $i),
        'kind' => $kind,
        'item' => $item,
        'app_version' => '3.2.1',
        'runtime_version' => 'R2024b',
        'outcome' => $kind === 'access' ? 'request' : 'redirect',
        'consent' => true,
    ];
}

function rejects(callable $call, string $why): void
{
    try {
        $call();
    } catch (InvalidArgumentException $e) {
        return;
    }
    throw new RuntimeException($why);
}

function count_events(string $path): int
{
    return (int) (new PDO('sqlite:' . $path))->query('SELECT COUNT(*) FROM events')->fetchColumn();
}

$dir = sys_get_temp_dir() . '/lead-collector-' . bin2hex(random_bytes(8));
mkdir($dir, 0700);
$path = $dir . '/events.sqlite';
try {
    $mask = umask();
    $storage = new Storage($path);
    $lookups = 0;
    $collector = new Collector($storage, random_bytes(32), function (string $ip) use (&$lookups): string {
        $lookups++;
        return 'DE';
    });
    check(umask() === $mask, 'constructor restores process umask');
    check((fileperms($path) & 0777) === 0600, 'database private mode');

    $now = new DateTimeImmutable('2026-01-02T12:00:00Z');
    check($collector->record(event(1), '192.0.2.1', 'MATLAB', $now) === 'accepted', 'accept event');
    check($collector->record(event(1), '192.0.2.1', 'MATLAB', $now) === 'duplicate', 'idempotent event');
    $collector->record(event(2), '192.0.2.1', 'MATLAB', $now);
    $collector->record(event(3, 'access', 'group'), '192.0.2.1', 'MATLAB', $now);
    $collector->record(event(4, 'download', 'latest'), '192.0.2.1', 'MATLAB', $now);
    $collector->record(event(5, 'download', 'latest'), '192.0.2.1', 'SomeBot', $now);
    $notFound = event(6, 'download', 'latest');
    $notFound['outcome'] = 'not_found';
    $collector->record($notFound, '192.0.2.2', 'Browser', $now);
    $collector->record(event(7, 'download', 'latest'), '192.0.2.3', 'SomeBot', $now);

    $export = $storage->aggregate('2026-01-02');
    check($export['series']['access'][0]['n'] === 1, 'address/hour dedup');
    check(count($export['series']['tools']) === 2, 'tool counts independent');
    check(array_sum(array_column($export['series']['download_requests'], 'n')) === 1,
        'response requests deduped; failures and declared automation excluded');
    check(count($export['series']['outcomes']) === 4, 'outcomes retain failure and automation diagnostics');

    foreach (['patient', 'filename', 'path', 'ip'] as $field) {
        rejects(fn() => Collector::validate(event(9) + [$field => 'forbidden']), 'accepted extra field');
    }
    foreach ([false, null, 'true'] as $consent) {
        $notOptedIn = event(9);
        $notOptedIn['consent'] = $consent;
        rejects(fn() => Collector::validate($notOptedIn), 'accepted non-opted-in client');
    }
    $arbitraryTool = event(9);
    $arbitraryTool['item'] = 'patient_name';
    rejects(fn() => Collector::validate($arbitraryTool), 'accepted arbitrary tool');

    // Rate-limit saturation: 192.0.2.1 has used 6 of its 60 requests in this minute.
    for ($i = 10; $i < 64; $i++) {
        $collector->record(event($i), '192.0.2.1', 'MATLAB', $now);
    }
    $lookupsAtLimit = $lookups;
    $eventsAtLimit = count_events($path);
    $writer = new PDO('sqlite:' . $path, null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
    $writer->exec('BEGIN IMMEDIATE');
    $started = microtime(true);
    for ($i = 64; $i < 80; $i++) {
        check($collector->record(event($i), '192.0.2.1', 'MATLAB', $now) === 'rate_limited', 'bounded per-minute requests');
    }
    $elapsed = microtime(true) - $started;
    $writer->exec('ROLLBACK');
    check($elapsed < 0.5, 'over-limit requests are rejected without waiting for the write lock');
    check($lookups === $lookupsAtLimit, 'over-limit requests skip the country lookup');
    check(count_events($path) === $eventsAtLimit, 'over-limit requests store nothing');

    $collector->record(event(100), '192.0.2.1', 'MATLAB', $now->modify('+1 day'));
    $db = new PDO('sqlite:' . $path);
    $tokens = $db->query('SELECT DISTINCT subject FROM events')->fetchAll(PDO::FETCH_COLUMN);
    check(count($tokens) === 4, 'daily identity rotates');
    check(!str_contains(file_get_contents($path), '192.0.2.1'), 'raw address not stored');
    check(!str_contains(json_encode($export), 'subject'), 'export has no token');

    // Storage ceiling: shed before the lookup and without writing.
    $lookupsBefore = $lookups;
    $eventsBefore = count_events($path);
    $ceilings = [
        'database size' => new Storage($path, 3000, 1, 1),
        'free space' => new Storage($path, 3000, PHP_INT_MAX, PHP_INT_MAX),
    ];
    foreach ($ceilings as $name => $limited) {
        $shedding = new Collector($limited, random_bytes(32), function (string $ip) use (&$lookups): string {
            $lookups++;
            return 'DE';
        });
        check($limited->overCapacity(), "$name ceiling detected");
        check($shedding->record(event(200), '192.0.2.9', 'MATLAB', $now) === 'over_capacity', "$name ceiling sheds");
    }
    check($lookups === $lookupsBefore, 'shed requests skip the country lookup');
    check(count_events($path) === $eventsBefore, 'shed requests store nothing');
    $usage = $storage->health()['storage'];
    check($usage['database_bytes'] === filesize($path), 'health reports the database size');
    check($usage['max_database_bytes'] === Storage::DEFAULT_MAX_DATABASE_BYTES, 'health reports the ceiling');

    // Retention: a failed run leaves no completion record; a successful one records it and returns space.
    check($storage->health()['last_retention_at'] === null, 'no retention recorded yet');
    $writer->exec('BEGIN IMMEDIATE');
    try {
        (new Storage($path, 50))->retain(new DateTimeImmutable('2026-03-01T00:00:00Z'));
        throw new RuntimeException('retention succeeded while the database was locked');
    } catch (PDOException $e) {
    } finally {
        $writer->exec('ROLLBACK');
    }
    check($storage->health()['last_retention_at'] === null, 'failed retention records no completion');
    check(count_events($path) === $eventsBefore, 'failed retention deletes nothing');

    for ($i = 1000; $i < 3000; $i++) {
        $address = '198.51.100.' . ($i % 250);
        $collector->record(event($i), $address, 'MATLAB', $now->modify('+' . intdiv($i, 250) . ' minutes'));
    }
    clearstatcache();
    $sizeBefore = filesize($path);
    $retained = $storage->retain(new DateTimeImmutable('2026-03-01T00:00:00Z'));
    clearstatcache();
    $health = $storage->health();
    check($retained['events'] > 0 && $health['events_retained'] === 0, 'retention enforced');
    check($health['last_retention_at'] === $retained['completed_at'], 'retention completion recorded');
    $completedAt = new DateTimeImmutable($health['last_retention_at']);
    check($completedAt->getOffset() === 0 && abs($completedAt->getTimestamp() - time()) < 60,
        'retention completion is the current UTC time, not the retention cutoff');
    check(filesize($path) < $sizeBefore / 2, 'retention returns freed pages to the filesystem');

    echo "Collector validation, consent, idempotency, deduplication, rates, storage ceiling, privacy and retention passed.\n";
} finally {
    foreach (glob($dir . '/*') as $file) {
        unlink($file);
    }
    rmdir($dir);
}
