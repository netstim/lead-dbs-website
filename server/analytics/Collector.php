<?php
declare(strict_types=1);
namespace LeadAnalytics;

use DateTimeImmutable;
use DateTimeZone;
use InvalidArgumentException;
use PDO;
use RuntimeException;

/** Private state only: no raw address, user agent, path or patient field is stored. */
final class Collector
{
    private PDO $db;
    private string $key;
    private $countryLookup;

    public function __construct(string $database, string $key, callable $countryLookup)
    {
        if (strlen($key) < 32) throw new InvalidArgumentException('Key must have at least 32 random bytes.');
        if (!is_dir(dirname($database))) throw new RuntimeException('Private storage is missing.');
        $this->key = $key;
        $this->countryLookup = $countryLookup;
        $previousMask = umask(0077);
        try {
        $this->db = new PDO('sqlite:' . $database, null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
        $this->db->exec('PRAGMA busy_timeout=3000; PRAGMA secure_delete=ON;');
        $this->db->exec('CREATE TABLE IF NOT EXISTS events (
          event_id TEXT PRIMARY KEY, day TEXT NOT NULL, hour INTEGER NOT NULL,
          subject TEXT NOT NULL, kind TEXT NOT NULL, item TEXT NOT NULL,
          app_version TEXT NOT NULL, runtime_version TEXT NOT NULL,
          country TEXT NOT NULL, outcome TEXT NOT NULL, traffic TEXT NOT NULL
        ); CREATE INDEX IF NOT EXISTS events_day ON events(day);
        CREATE TABLE IF NOT EXISTS buckets (bucket TEXT PRIMARY KEY, day TEXT NOT NULL, n INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS metrics (day TEXT NOT NULL, name TEXT NOT NULL, n INTEGER NOT NULL, PRIMARY KEY(day,name));');
        } finally { umask($previousMask); }
    }

    public static function validate(array $event): array
    {
        $allowed = ['schema','event_id','kind','item','app_version','runtime_version','outcome','consent'];
        if (array_diff(array_keys($event), $allowed)) throw new InvalidArgumentException('Unsupported fields.');
        foreach (['schema','event_id','kind','item','outcome'] as $field) {
            if (!array_key_exists($field, $event)) throw new InvalidArgumentException('Missing required field.');
        }
        if ($event['schema'] !== 1) throw new InvalidArgumentException('Invalid schema.');
        if (($event['kind'] ?? '') === 'access' && ($event['consent'] ?? false) !== true) throw new InvalidArgumentException('App analytics requires opt-in.');
        if (!is_string($event['event_id']) || !preg_match('/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/D', $event['event_id'])) throw new InvalidArgumentException('Invalid event ID.');
        if (!in_array($event['kind'], ['access','download'], true)) throw new InvalidArgumentException('Invalid event kind.');
        if (!is_string($event['item']) || !preg_match('/^[A-Za-z0-9_.-]{1,100}$/D', $event['item'])) throw new InvalidArgumentException('Invalid item.');
        if ($event['kind'] === 'access' && !in_array($event['item'], ['dbs','group','connectome','anatomy','other'], true)) throw new InvalidArgumentException('Invalid tool.');
        $outcomes = $event['kind'] === 'access' ? ['request'] : ['request','redirect','file_response','not_found'];
        if (!in_array($event['outcome'], $outcomes, true)) throw new InvalidArgumentException('Invalid outcome.');
        foreach (['app_version','runtime_version'] as $field) {
            $event[$field] = $event[$field] ?? 'unknown';
            if (!is_string($event[$field]) || !preg_match('/^(?:unknown|[0-9]{1,3}(?:\.[0-9]{1,4}){0,3}(?:-[a-z0-9]{1,12})?|R[0-9]{4}[ab])$/D', $event[$field])) throw new InvalidArgumentException('Invalid version.');
        }
        return $event;
    }

    private function metric(string $day, string $name): void
    {
        $stmt = $this->db->prepare('INSERT INTO metrics(day,name,n) VALUES(?,?,1) ON CONFLICT(day,name) DO UPDATE SET n=n+1');
        $stmt->execute([$day,$name]);
    }

    public function record(array $event, string $address, string $agent, ?DateTimeImmutable $now = null): string
    {
        $event = self::validate($event);
        if (filter_var($address, FILTER_VALIDATE_IP) === false) throw new InvalidArgumentException('Invalid remote address.');
        $now = ($now ?? new DateTimeImmutable('now', new DateTimeZone('UTC')))->setTimezone(new DateTimeZone('UTC'));
        $day = $now->format('Y-m-d');
        $subject = hash_hmac('sha256', $day . ':' . bin2hex(inet_pton($address)), $this->key);
        $bucket = hash_hmac('sha256', $now->format('Y-m-d H:i') . ':' . $subject, $this->key);
        // This is a user-agent declaration, not independently verified bot identity.
        $traffic = preg_match('/bot|crawler|spider|headless/i', substr($agent,0,512)) ? 'declared_automation' : 'unclassified';
        $country = ($this->countryLookup)($address);
        if (!is_string($country) || !preg_match('/^[A-Z]{2}$/D', $country)) $country = 'ZZ';
        $this->db->exec('BEGIN IMMEDIATE');
        try {
            $this->metric($day, 'received');
            $stmt = $this->db->prepare('INSERT INTO buckets(bucket,day,n) VALUES(?,?,1) ON CONFLICT(bucket) DO UPDATE SET n=n+1 RETURNING n');
            $stmt->execute([$bucket,$day]);
            $requests = (int)$stmt->fetchColumn();
            $stmt->closeCursor();
            if ($requests > 60) {
                $this->metric($day, 'rate_limited');
                $this->db->exec('COMMIT');
                return 'rate_limited';
            }
            $stmt = $this->db->prepare('INSERT OR IGNORE INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?)');
            $stmt->execute([$event['event_id'],$day,(int)$now->format('H'),$subject,$event['kind'],$event['item'],$event['app_version'],$event['runtime_version'],$country,$event['outcome'],$traffic]);
            $result = $stmt->rowCount() ? 'accepted' : 'duplicate';
            $this->metric($day, $result);
            $this->db->exec('COMMIT');
            return $result;
        } catch (\Throwable $e) {
            $this->db->exec('ROLLBACK');
            throw $e;
        }
    }

    /** Erases pseudonymous event state beyond retention; keep aggregate health counters for 90 days. */
    public function retain(?DateTimeImmutable $now = null): array
    {
        $now = ($now ?? new DateTimeImmutable('now', new DateTimeZone('UTC')))->setTimezone(new DateTimeZone('UTC'));
        $counts = [];
        $this->db->beginTransaction();
        try {
            foreach (['events'=>31,'buckets'=>2,'metrics'=>90] as $table=>$days) {
                $stmt = $this->db->prepare("DELETE FROM $table WHERE day < ?");
                $stmt->execute([$now->modify("-$days days")->format('Y-m-d')]);
                $counts[$table] = $stmt->rowCount();
            }
            $this->db->commit();
        } catch (\Throwable $e) { $this->db->rollBack(); throw $e; }
        return $counts;
    }

    /** Private operational summary: no tokens, addresses or event IDs. */
    public function health(): array
    {
        return ['schema'=>1, 'last_event_day'=>$this->db->query('SELECT MAX(day) FROM events')->fetchColumn() ?: null,
          'events_retained'=>(int)$this->db->query('SELECT COUNT(*) FROM events')->fetchColumn(),
          'counters'=>$this->db->query('SELECT day,name,n FROM metrics ORDER BY day,name')->fetchAll(PDO::FETCH_ASSOC)];
    }

    /** Export closed UTC days only. Separate series from legacy server-clock data. */
    public function aggregate(string $cutoff): array
    {
        $date = DateTimeImmutable::createFromFormat('!Y-m-d', $cutoff, new DateTimeZone('UTC'));
        if (!$date || $date->format('Y-m-d') !== $cutoff || $cutoff >= gmdate('Y-m-d')) throw new InvalidArgumentException('Cutoff must be a completed UTC day.');
        $queries = [
          'access' => "SELECT day,country,COUNT(*) AS n FROM (SELECT day,hour,subject,MIN(country) AS country FROM events WHERE kind='access' AND day<=? GROUP BY day,hour,subject) GROUP BY day,country ORDER BY day,country",
          'tools' => "SELECT day,item,COUNT(*) AS n FROM (SELECT DISTINCT day,hour,subject,item FROM events WHERE kind='access' AND day<=?) GROUP BY day,item ORDER BY day,item",
          'download_requests' => "SELECT day,item,country,COUNT(*) AS n FROM (SELECT day,subject,item,MIN(country) AS country FROM events WHERE kind='download' AND outcome IN ('redirect','file_response') AND traffic='unclassified' AND day<=? GROUP BY day,subject,item) GROUP BY day,item,country ORDER BY day,item,country",
          'outcomes' => "SELECT day,kind,outcome,traffic,COUNT(*) AS n FROM events WHERE day<=? GROUP BY day,kind,outcome,traffic ORDER BY day,kind,outcome,traffic"
        ];
        $out = ['schema'=>1,'timezone'=>'UTC','cutoff'=>$cutoff,'series'=>[]];
        foreach ($queries as $name=>$query) {
            $stmt=$this->db->prepare($query);$stmt->execute([$cutoff]);$out['series'][$name]=$stmt->fetchAll(PDO::FETCH_ASSOC);
        }
        return $out;
    }
}
