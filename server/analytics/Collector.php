<?php
declare(strict_types=1);
namespace LeadAnalytics;

use Closure;
use DateTimeImmutable;
use InvalidArgumentException;

require_once __DIR__ . '/Storage.php';

/** Private state only: no raw address, user agent, path or patient field is stored. */
final class Collector
{
    private Storage $storage;
    private string $key;
    private Closure $countryLookup;

    public function __construct(Storage $storage, string $key, callable $countryLookup)
    {
        if (strlen($key) < 32) throw new InvalidArgumentException('Key must have at least 32 random bytes.');
        $this->storage = $storage;
        $this->key = $key;
        $this->countryLookup = Closure::fromCallable($countryLookup);
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

    /**
     * Returns accepted, duplicate, rate_limited or over_capacity. The two rejections that need no
     * write are decided before the country lookup and without the SQLite write lock; they are not
     * counted in the metrics table, which would otherwise grow under the load being shed.
     */
    public function record(array $event, string $address, string $agent, ?DateTimeImmutable $now = null): string
    {
        $event = self::validate($event);
        if (filter_var($address, FILTER_VALIDATE_IP) === false) throw new InvalidArgumentException('Invalid remote address.');
        if ($this->storage->overCapacity()) {
            return 'over_capacity';
        }
        $now = Storage::utc($now);
        $day = $now->format('Y-m-d');
        $subject = hash_hmac('sha256', $day . ':' . bin2hex(inet_pton($address)), $this->key);
        $bucket = hash_hmac('sha256', $now->format('Y-m-d H:i') . ':' . $subject, $this->key);
        if ($this->storage->requestsInBucket($bucket) >= Storage::RATE_LIMIT_PER_MINUTE) {
            return 'rate_limited';
        }
        // This is a user-agent declaration, not independently verified bot identity.
        $traffic = preg_match('/bot|crawler|spider|headless/i', substr($agent, 0, 512)) ? 'declared_automation' : 'unclassified';
        $country = ($this->countryLookup)($address);
        if (!is_string($country) || !preg_match('/^[A-Z]{2}$/D', $country)) $country = 'ZZ';
        return $this->storage->record([
            'event_id' => $event['event_id'],
            'day' => $day,
            'hour' => (int) $now->format('H'),
            'subject' => $subject,
            'kind' => $event['kind'],
            'item' => $event['item'],
            'app_version' => $event['app_version'],
            'runtime_version' => $event['runtime_version'],
            'country' => $country,
            'outcome' => $event['outcome'],
            'traffic' => $traffic,
        ], $bucket);
    }
}
