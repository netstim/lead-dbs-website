<?php
declare(strict_types=1);

namespace LeadForms;

use InvalidArgumentException;
use RuntimeException;

/** A field of a submission that is missing or not valid: names the field, so the reply can say what to fix. */
final class FieldError extends InvalidArgumentException
{
    /** @param string $problem 'missing' or 'invalid' */
    public function __construct(public readonly string $field, public readonly string $problem)
    {
        parent::__construct("Field {$field} is {$problem}.");
    }
}

/**
 * Checks one submission of the contact or FOCUS form and turns it into a plain-text email to a fixed
 * address. No other form is accepted; the newsletter is not handled here.
 *
 * The fields below are the server's own list. They must match data/forms.yaml (tests/test_forms_http.py
 * checks that): the website only draws the form, this file decides what is accepted.
 */
final class FormHandler
{
    /** form id => [field => [label, required, max length, kind]] (kind: text, email, multiline, check) */
    public const FORMS = [
        'contact' => [
            'subject' => 'contact form',
            'fields' => [
                'name' => ['Name', true, 200, 'text'],
                'email' => ['Email', true, 254, 'email'],
                'message' => ['Message', true, 5000, 'multiline'],
            ],
        ],
        'downloadfocus' => [
            'subject' => 'FOCUS request form',
            'fields' => [
                'first_name' => ['First name', false, 200, 'text'],
                'last_name' => ['Last name', false, 200, 'text'],
                'institution' => ['Institution', false, 200, 'text'],
                'email' => ['Email', true, 254, 'email'],
                'academic' => ['Academic research only', true, 3, 'check'],
                'newsletter' => ['Also wants the newsletter', false, 3, 'check'],
            ],
        ],
    ];

    /** the hidden field people never see; a value in it marks a bot */
    public const TRAP = 'website';
    /** the hidden field that names the form */
    public const FORM_FIELD = 'form';
    /** largest request body accepted, in bytes: room for every field at its longest in 4-byte characters, percent-encoded (no-script forms) */
    public const MAX_BODY = 131072;
    /** config.example.json's rate_key, which must never be used as the real one */
    public const EXAMPLE_KEY = 'replace with a long random string generated on the server';
    /** the rate-limit files are deleted this long after their last change (they must outlive a day plus the window) */
    public const RATE_FILE_AGE = 2 * 86400;

    /**
     * The checked values of a submission, in the form's field order.
     * @param array<string, mixed> $post
     * @return array<string, string>
     * @throws FieldError when a field of the form is missing or not valid
     * @throws InvalidArgumentException when the form is unknown or the submission has fields it shouldn't
     */
    public static function validate(string $form, array $post): array
    {
        $spec = self::FORMS[$form] ?? null;
        if ($spec === null) throw new InvalidArgumentException('Unknown form.');
        $allowed = array_merge(array_keys($spec['fields']), [self::TRAP, self::FORM_FIELD]);
        foreach (array_keys($post) as $key) {
            if (!in_array($key, $allowed, true)) throw new InvalidArgumentException('Unexpected field.');
        }
        $clean = [];
        foreach ($spec['fields'] as $name => [$label, $required, $max, $kind]) {
            $value = $post[$name] ?? '';
            if (!is_string($value) || !mb_check_encoding($value, 'UTF-8')) throw new FieldError($name, 'invalid');
            $value = $kind === 'multiline'
                ? trim(str_replace(["\r\n", "\r"], "\n", $value))
                : trim(preg_replace('/\s+/u', ' ', $value) ?? '');
            // control characters other than line breaks in a message have no business in a form
            $value = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $value) ?? '';
            if (mb_strlen($value) > $max) throw new FieldError($name, 'invalid');
            if ($kind === 'check' && $value !== '' && $value !== 'yes') throw new FieldError($name, 'invalid');
            if ($kind === 'email' && $value !== '' && !self::isEmail($value)) throw new FieldError($name, 'invalid');
            if ($required && $value === '') throw new FieldError($name, 'missing');
            $clean[$name] = $value;
        }
        return $clean;
    }

    public static function isEmail(string $value): bool
    {
        return strlen($value) <= 254 && filter_var($value, FILTER_VALIDATE_EMAIL) !== false
            && !preg_match('/[\r\n,;<>"]/', $value);
    }

    /**
     * The email for a checked submission.
     * @param array<string, string> $clean the result of validate()
     * @return array{to: string, subject: string, body: string, headers: array<string, string>}
     */
    public static function message(string $form, array $clean, string $to, string $from, string $site): array
    {
        $spec = self::FORMS[$form];
        $who = $clean['name'] ?? trim(($clean['first_name'] ?? '') . ' ' . ($clean['last_name'] ?? ''));
        $subject = ucfirst($spec['subject']) . ($who !== '' ? ': ' . $who : '');
        $lines = ["Sent from the {$spec['subject']} on {$site}.", ''];
        foreach ($spec['fields'] as $name => [$label, , , $kind]) {
            $value = $clean[$name];
            if ($kind === 'check') $value = $value === 'yes' ? 'yes' : 'no';
            if ($kind === 'multiline') {
                $lines[] = "{$label}:";
                $lines[] = $value;
            } else {
                $lines[] = "{$label}: " . ($value === '' ? '-' : $value);
            }
        }
        $lines[] = '';
        $lines[] = 'Reply to this email to answer the sender.';
        return [
            'to' => $to,
            'subject' => self::header(mb_substr($subject, 0, 150)),
            'body' => implode("\r\n", array_map(static fn(string $l) => str_replace("\n", "\r\n", $l), $lines)) . "\r\n",
            'headers' => [
                'From' => self::header('Lead-DBS website') . " <{$from}>",
                'Reply-To' => $clean['email'],
                'MIME-Version' => '1.0',
                'Content-Type' => 'text/plain; charset=UTF-8',
                'Content-Transfer-Encoding' => '8bit',
                'Auto-Submitted' => 'auto-generated',
            ],
        ];
    }

    /** a header value: one line, encoded when it is not plain ASCII */
    public static function header(string $value): string
    {
        $value = trim(preg_replace('/[\r\n\t]+/', ' ', $value) ?? '');
        return preg_match('/[^\x20-\x7E]/', $value) ? mb_encode_mimeheader($value, 'UTF-8', 'Q', "\r\n") : $value;
    }

    /**
     * Counts a submission from an address and says whether it is over the limit. The address is kept only as a
     * keyed hash that changes every day (UTC); nothing else of the sender is stored. Submissions of the day before
     * count too while they are inside the window, so the limit does not start afresh at midnight. When the count
     * cannot be read or written it throws: the form then answers 503 rather than sending without a limit.
     */
    public static function overLimit(string $dir, string $key, string $address, int $limit, int $window, ?int $now = null): bool
    {
        $now ??= time();
        $file = static fn(int $day) => rtrim($dir, '/') . '/' . hash_hmac('sha256', gmdate('Y-m-d', $day) . '|' . $address, $key);
        $recent = static fn(string $text) => array_values(array_filter(array_map('intval', preg_split('/\n/', $text, -1, PREG_SPLIT_NO_EMPTY)),
            static fn(int $t) => $t > $now - $window && $t <= $now));
        $earlier = 0;
        if (gmdate('Y-m-d', $now - $window) !== gmdate('Y-m-d', $now)) {
            $yesterday = $file($now - 86400);
            if (is_file($yesterday)) {
                $text = @file_get_contents($yesterday);
                if ($text === false) throw new RuntimeException('Rate limit storage unreadable.');
                $earlier = count($recent($text));
            }
        }
        $previousMask = umask(0077);     // a new file is the server's alone (0600)
        try {
            $handle = @fopen($file($now), 'c+');
        } finally {
            umask($previousMask);
        }
        if ($handle === false) throw new RuntimeException('Rate limit storage unavailable.');
        try {
            if (!flock($handle, LOCK_EX)) throw new RuntimeException('Rate limit storage cannot be locked.');
            $text = stream_get_contents($handle);
            if ($text === false) throw new RuntimeException('Rate limit storage unreadable.');
            $times = $recent($text);
            $over = count($times) + $earlier >= $limit;
            if (!$over) $times[] = $now;
            $data = implode("\n", $times) . "\n";
            if (!ftruncate($handle, 0) || !rewind($handle) || fwrite($handle, $data) !== strlen($data) || !fflush($handle)) {
                throw new RuntimeException('Rate limit storage cannot be written.');
            }
            return $over;
        } finally {
            flock($handle, LOCK_UN);
            fclose($handle);
        }
    }

    /**
     * Removes the rate-limit files not changed for $maxAge seconds, and returns how many it removed.
     * @throws RuntimeException when the folder can't be read or a file can't be removed
     */
    public static function sweep(string $dir, int $maxAge = self::RATE_FILE_AGE, ?int $now = null): int
    {
        $now ??= time();
        $names = @scandir($dir);
        if ($names === false) throw new RuntimeException('Rate limit storage unreadable.');
        $removed = 0;
        clearstatcache();
        foreach ($names as $name) {
            if (!preg_match('/^[0-9a-f]{64}$/D', $name)) continue;
            $file = rtrim($dir, '/') . '/' . $name;
            $changed = @filemtime($file);
            if ($changed === false || $changed >= $now - $maxAge) continue;
            if (!@unlink($file)) throw new RuntimeException('Rate limit file cannot be removed.');
            $removed++;
        }
        return $removed;
    }

    /**
     * The private configuration (README.md describes its fields), checked.
     * @param ?string $documentRoot the web root, when known: no private file may be inside it
     * @throws RuntimeException naming what is wrong, never a value of it
     */
    public static function config(string $path, ?string $documentRoot): array
    {
        if (!is_readable($path)) throw new RuntimeException('Forms configuration unavailable.');
        $config = json_decode((string) file_get_contents($path), true, 8, JSON_THROW_ON_ERROR);
        if (!is_array($config)) throw new RuntimeException('Forms configuration is not an object.');
        foreach (array_keys(self::FORMS) as $id) {
            if (!self::isEmail($config['recipients'][$id] ?? '')) throw new RuntimeException('Forms recipient missing.');
        }
        if (!self::isEmail($config['from'] ?? '')) throw new RuntimeException('Forms sender missing.');
        foreach (['rate_dir', 'rate_key', 'site'] as $key) {
            if (!is_string($config[$key] ?? null) || $config[$key] === '') throw new RuntimeException('Forms configuration incomplete.');
        }
        if (strlen($config['rate_key']) < 32 || $config['rate_key'] === self::EXAMPLE_KEY) {
            throw new RuntimeException('Forms rate_key must be a random string of at least 32 characters.');
        }
        $config['limit'] ??= 5;
        $config['window'] ??= 600;
        if (!is_int($config['limit']) || $config['limit'] < 1 || $config['limit'] > 100) {
            throw new RuntimeException('Forms limit must be a whole number from 1 to 100.');
        }
        // a window longer than a day would need the files of more than one earlier day
        if (!is_int($config['window']) || $config['window'] < 60 || $config['window'] > 86400) {
            throw new RuntimeException('Forms window must be a whole number of seconds from 60 to 86400.');
        }
        $root = $documentRoot !== null ? (realpath($documentRoot) ?: null) : null;
        $private = [$path, $config['rate_dir']];
        if (($config['delivery'] ?? 'mail') === 'outbox') $private[] = $config['outbox'] ?? '';
        foreach ($private as $p) {
            $resolved = realpath($p) ?: '';
            if ($resolved === '' || $resolved[0] !== '/') throw new RuntimeException('Forms private path missing.');
            if ($root && ($resolved === $root || str_starts_with($resolved, $root . '/'))) {
                throw new RuntimeException('Forms private files must be outside the document root.');
            }
        }
        if (!is_dir($config['rate_dir'])) throw new RuntimeException('Forms rate_dir is not a folder.');
        return $config;
    }
}
