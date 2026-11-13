<?php
declare(strict_types=1);

namespace LeadForms;

use InvalidArgumentException;
use RuntimeException;

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
    /** largest request body accepted, in bytes */
    public const MAX_BODY = 16384;

    /**
     * The checked values of a submission, in the form's field order.
     * @param array<string, mixed> $post
     * @return array<string, string>
     * @throws InvalidArgumentException when the form or a field is missing, unknown or invalid
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
            if (!is_string($value)) throw new InvalidArgumentException('Invalid field.');
            if (!mb_check_encoding($value, 'UTF-8')) throw new InvalidArgumentException('Invalid encoding.');
            $value = $kind === 'multiline'
                ? trim(str_replace(["\r\n", "\r"], "\n", $value))
                : trim(preg_replace('/\s+/u', ' ', $value) ?? '');
            // control characters other than line breaks in a message have no business in a form
            $value = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $value) ?? '';
            if (mb_strlen($value) > $max) throw new InvalidArgumentException('Field too long.');
            if ($kind === 'check') {
                if ($value !== '' && $value !== 'yes') throw new InvalidArgumentException('Invalid choice.');
            }
            if ($kind === 'email' && $value !== '' && !self::isEmail($value)) {
                throw new InvalidArgumentException('Invalid email address.');
            }
            if ($required && $value === '') throw new InvalidArgumentException('Missing field.');
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
     * keyed hash that changes every day; nothing else of the sender is stored.
     */
    public static function overLimit(string $dir, string $key, string $address, int $limit, int $window, ?int $now = null): bool
    {
        $now ??= time();
        $id = hash_hmac('sha256', gmdate('Y-m-d', $now) . '|' . $address, $key);
        $path = rtrim($dir, '/') . '/' . $id;
        $handle = @fopen($path, 'c+');
        if ($handle === false) throw new RuntimeException('Rate limit storage unavailable.');
        try {
            flock($handle, LOCK_EX);
            $times = array_filter(array_map('intval', explode("\n", stream_get_contents($handle) ?: '')),
                static fn(int $t) => $t > $now - $window);
            $over = count($times) >= $limit;
            if (!$over) $times[] = $now;
            ftruncate($handle, 0);
            rewind($handle);
            fwrite($handle, implode("\n", $times));
            return $over;
        } finally {
            flock($handle, LOCK_UN);
            fclose($handle);
        }
    }

    /** removes the rate-limit files of earlier days */
    public static function sweep(string $dir, int $maxAge = 2 * 86400, ?int $now = null): void
    {
        $now ??= time();
        foreach (glob(rtrim($dir, '/') . '/*') ?: [] as $file) {
            if (preg_match('/\/[0-9a-f]{64}$/', $file) && @filemtime($file) < $now - $maxAge) @unlink($file);
        }
    }
}
