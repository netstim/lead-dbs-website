<?php
declare(strict_types=1);
namespace LeadAnalytics;

use DateTimeImmutable;
use DateTimeZone;
use InvalidArgumentException;
use PDO;
use PDOException;
use RuntimeException;

/**
 * The private SQLite store: schema, rate buckets, retention, health and aggregate export.
 * It needs no HMAC key, country database or Composer dependency, so retention keeps
 * working when collection cannot.
 */
final class Storage
{
    public const RATE_LIMIT_PER_MINUTE = 60;
    public const DEFAULT_MAX_DATABASE_BYTES = 268435456; // 256 MiB
    public const DEFAULT_MIN_FREE_BYTES = 536870912; // 512 MiB
    public const MAINTENANCE_BUSY_TIMEOUT_MS = 3000;

    /** Days of state kept, by table; boundaries are UTC dates. */
    private const RETENTION_DAYS = ['events' => 31, 'buckets' => 2, 'metrics' => 90];

    private const EVENT_COLUMNS = [
        'event_id', 'day', 'hour', 'subject', 'kind', 'item',
        'app_version', 'runtime_version', 'country', 'outcome', 'traffic',
    ];

    private PDO $db;
    private string $database;
    private int $maxDatabaseBytes;
    private int $minFreeBytes;

    public function __construct(
        string $database,
        int $busyTimeoutMs = self::MAINTENANCE_BUSY_TIMEOUT_MS,
        int $maxDatabaseBytes = self::DEFAULT_MAX_DATABASE_BYTES,
        int $minFreeBytes = self::DEFAULT_MIN_FREE_BYTES
    ) {
        if ($busyTimeoutMs < 1 || $maxDatabaseBytes < 1 || $minFreeBytes < 1) {
            throw new InvalidArgumentException('Storage limits must be positive.');
        }
        if (!is_dir(dirname($database))) {
            throw new RuntimeException('Private storage is missing.');
        }
        $this->database = $database;
        $this->maxDatabaseBytes = $maxDatabaseBytes;
        $this->minFreeBytes = $minFreeBytes;

        $previousMask = umask(0077);
        try {
            $this->db = new PDO('sqlite:' . $database, null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
            $this->db->exec('PRAGMA busy_timeout=' . $busyTimeoutMs);
            $this->db->exec('PRAGMA secure_delete=ON');
            // Lets retain() give freed pages back to the filesystem. Only a new, empty database can
            // switch mode, and setting it on an existing one would wait for the write lock.
            if ((int) $this->db->query('PRAGMA page_count')->fetchColumn() === 0) {
                $this->db->exec('PRAGMA auto_vacuum=INCREMENTAL');
            }
            $this->db->exec('CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY, day TEXT NOT NULL, hour INTEGER NOT NULL,
                subject TEXT NOT NULL, kind TEXT NOT NULL, item TEXT NOT NULL,
                app_version TEXT NOT NULL, runtime_version TEXT NOT NULL,
                country TEXT NOT NULL, outcome TEXT NOT NULL, traffic TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS events_day ON events(day);
            CREATE TABLE IF NOT EXISTS buckets (bucket TEXT PRIMARY KEY, day TEXT NOT NULL, n INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS metrics (day TEXT NOT NULL, name TEXT NOT NULL, n INTEGER NOT NULL, PRIMARY KEY(day, name));
            CREATE TABLE IF NOT EXISTS state (name TEXT PRIMARY KEY, value TEXT NOT NULL);');
        } finally {
            umask($previousMask);
        }
    }

    public static function utc(?DateTimeImmutable $time = null): DateTimeImmutable
    {
        $utc = new DateTimeZone('UTC');
        return ($time ?? new DateTimeImmutable('now', $utc))->setTimezone($utc);
    }

    /** File-system use only (no SQL), so it is safe to call before any lock. */
    public function usage(): array
    {
        $bytes = 0;
        foreach (['', '-journal', '-wal'] as $suffix) {
            $path = $this->database . $suffix;
            clearstatcache(true, $path);
            $size = @filesize($path);
            if ($size !== false) {
                $bytes += $size;
            }
        }
        // Filesystem free space, not a hosting quota. Unknown (e.g. a disabled function) counts as too little.
        $free = function_exists('disk_free_space') ? @disk_free_space(dirname($this->database)) : false;
        return [
            'database_bytes' => $bytes,
            'free_bytes' => $free === false ? null : (int) $free,
            'max_database_bytes' => $this->maxDatabaseBytes,
            'min_free_bytes' => $this->minFreeBytes,
        ];
    }

    public function overCapacity(): bool
    {
        $usage = $this->usage();
        return $usage['database_bytes'] >= $this->maxDatabaseBytes
            || $usage['free_bytes'] === null
            || $usage['free_bytes'] < $this->minFreeBytes;
    }

    /** A plain read: in rollback-journal mode it does not wait for another connection's write transaction. */
    public function requestsInBucket(string $bucket): int
    {
        $stmt = $this->db->prepare('SELECT n FROM buckets WHERE bucket = ?');
        $stmt->execute([$bucket]);
        $requests = $stmt->fetchColumn();
        $stmt->closeCursor();
        return $requests === false ? 0 : (int) $requests;
    }

    /**
     * Counts the request in its bucket and stores the event unless that bucket is over the limit.
     * Returns accepted, duplicate or rate_limited.
     */
    public function record(array $row, string $bucket): string
    {
        $columns = array_keys($row);
        sort($columns);
        $expected = self::EVENT_COLUMNS;
        sort($expected);
        if ($columns !== $expected) {
            throw new InvalidArgumentException('Unexpected event columns.');
        }

        $this->db->exec('BEGIN IMMEDIATE');
        try {
            $this->metric($row['day'], 'received');
            $stmt = $this->db->prepare('INSERT INTO buckets(bucket, day, n) VALUES(?, ?, 1)
                ON CONFLICT(bucket) DO UPDATE SET n = n + 1 RETURNING n');
            $stmt->execute([$bucket, $row['day']]);
            $requests = (int) $stmt->fetchColumn();
            $stmt->closeCursor();
            // Rechecked under the write lock: concurrent requests may all have passed the early read.
            if ($requests > self::RATE_LIMIT_PER_MINUTE) {
                $this->metric($row['day'], 'rate_limited');
                $this->db->exec('COMMIT');
                return 'rate_limited';
            }

            $names = implode(', ', self::EVENT_COLUMNS);
            $placeholders = ':' . implode(', :', self::EVENT_COLUMNS);
            $stmt = $this->db->prepare("INSERT OR IGNORE INTO events($names) VALUES($placeholders)");
            $stmt->execute($row);
            $result = $stmt->rowCount() > 0 ? 'accepted' : 'duplicate';
            $this->metric($row['day'], $result);
            $this->db->exec('COMMIT');
            return $result;
        } catch (\Throwable $e) {
            $this->rollBack();
            throw $e;
        }
    }

    /**
     * Erases pseudonymous event state beyond retention and keeps aggregate health counters for 90 days.
     * The completion time is stored in the same transaction, so a failed run leaves no success record.
     */
    public function retain(?DateTimeImmutable $now = null): array
    {
        $today = self::utc($now);
        $this->db->exec('BEGIN IMMEDIATE');
        try {
            $deleted = [];
            foreach (self::RETENTION_DAYS as $table => $days) {
                $stmt = $this->db->prepare("DELETE FROM $table WHERE day < ?");
                $stmt->execute([$today->modify("-$days days")->format('Y-m-d')]);
                $deleted[$table] = $stmt->rowCount();
            }
            $this->db->exec('PRAGMA incremental_vacuum');
            $completedAt = self::utc()->format(DATE_ATOM);
            $stmt = $this->db->prepare("INSERT INTO state(name, value) VALUES('last_retention_at', ?)
                ON CONFLICT(name) DO UPDATE SET value = excluded.value");
            $stmt->execute([$completedAt]);
            $this->db->exec('COMMIT');
        } catch (\Throwable $e) {
            $this->rollBack();
            throw $e;
        }
        return $deleted + ['completed_at' => $completedAt];
    }

    /** Private operational summary: no tokens, addresses or event IDs. */
    public function health(): array
    {
        $stmt = $this->db->prepare('SELECT value FROM state WHERE name = ?');
        $stmt->execute(['last_retention_at']);
        $lastRetention = $stmt->fetchColumn();
        $stmt->closeCursor();
        return [
            'schema' => 1,
            'last_event_day' => $this->db->query('SELECT MAX(day) FROM events')->fetchColumn() ?: null,
            'events_retained' => (int) $this->db->query('SELECT COUNT(*) FROM events')->fetchColumn(),
            'last_retention_at' => $lastRetention === false ? null : $lastRetention,
            'storage' => $this->usage(),
            'counters' => $this->db->query('SELECT day, name, n FROM metrics ORDER BY day, name')->fetchAll(PDO::FETCH_ASSOC),
        ];
    }

    /** Export closed UTC days only. Separate series from legacy server-clock data. */
    public function aggregate(string $cutoff): array
    {
        $date = DateTimeImmutable::createFromFormat('!Y-m-d', $cutoff, new DateTimeZone('UTC'));
        if (!$date || $date->format('Y-m-d') !== $cutoff || $cutoff >= gmdate('Y-m-d')) {
            throw new InvalidArgumentException('Cutoff must be a completed UTC day.');
        }
        $queries = [
            'access' => "SELECT day,country,COUNT(*) AS n FROM (SELECT day,hour,subject,MIN(country) AS country FROM events WHERE kind='access' AND day<=? GROUP BY day,hour,subject) GROUP BY day,country ORDER BY day,country",
            'tools' => "SELECT day,item,COUNT(*) AS n FROM (SELECT DISTINCT day,hour,subject,item FROM events WHERE kind='access' AND day<=?) GROUP BY day,item ORDER BY day,item",
            'download_requests' => "SELECT day,item,country,COUNT(*) AS n FROM (SELECT day,subject,item,MIN(country) AS country FROM events WHERE kind='download' AND outcome IN ('redirect','file_response') AND traffic='unclassified' AND day<=? GROUP BY day,subject,item) GROUP BY day,item,country ORDER BY day,item,country",
            'outcomes' => "SELECT day,kind,outcome,traffic,COUNT(*) AS n FROM events WHERE day<=? GROUP BY day,kind,outcome,traffic ORDER BY day,kind,outcome,traffic",
        ];
        $out = ['schema' => 1, 'timezone' => 'UTC', 'cutoff' => $cutoff, 'series' => []];
        foreach ($queries as $name => $query) {
            $stmt = $this->db->prepare($query);
            $stmt->execute([$cutoff]);
            $out['series'][$name] = $stmt->fetchAll(PDO::FETCH_ASSOC);
        }
        return $out;
    }

    private function metric(string $day, string $name): void
    {
        $stmt = $this->db->prepare('INSERT INTO metrics(day, name, n) VALUES(?, ?, 1)
            ON CONFLICT(day, name) DO UPDATE SET n = n + 1');
        $stmt->execute([$day, $name]);
    }

    private function rollBack(): void
    {
        try {
            $this->db->exec('ROLLBACK');
        } catch (PDOException $e) {
            // SQLite may already have ended the transaction (e.g. after an I/O error); keep the original error.
        }
    }
}
