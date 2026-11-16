<?php
declare(strict_types=1);

// Deletes the forms' rate-limit files once they are no longer needed, on a schedule (README.md, Deploying):
//   php sweep.php          sweep, and record the time in rate_dir/sweep-status.json; exit 1 when it failed
//   php sweep.php check    exit 1 when the last sweep failed or is older than two hours (for monitoring)
// It reads the config named by LEAD_FORMS_CONFIG. Command line only; the folder's .htaccess serves only send.php.
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
require_once __DIR__ . '/FormHandler.php';

use LeadForms\FormHandler;

const LEAD_FORMS_SWEEP_STATUS = 'sweep-status.json';
const LEAD_FORMS_SWEEP_MAX_AGE = 2 * 3600;   // the schedule is hourly

function writeSweepStatus(string $file, array $status): void
{
    $previousMask = umask(0077);
    $tmp = null;
    try {
        $tmp = tempnam(dirname($file), '.sweep-');
        if ($tmp === false || realpath(dirname($tmp)) !== realpath(dirname($file))
            || @file_put_contents($tmp, json_encode($status), LOCK_EX) === false || !@rename($tmp, $file)) {
            throw new RuntimeException('The sweep status cannot be written.');
        }
    } finally {
        if (is_string($tmp) && is_file($tmp)) @unlink($tmp);
        umask($previousMask);
    }
}

$statusFile = null;
$command = $argv[1] ?? 'sweep';
try {
    $path = getenv('LEAD_FORMS_CONFIG');
    if (!$path) throw new RuntimeException('LEAD_FORMS_CONFIG is not set.');
    $config = FormHandler::config($path, null);
    $statusFile = rtrim($config['rate_dir'], '/') . '/' . LEAD_FORMS_SWEEP_STATUS;
    if ($command === 'sweep') {
        $removed = FormHandler::sweep($config['rate_dir']);
        writeSweepStatus($statusFile, ['ok' => true, 'completed_at' => gmdate('c'), 'removed' => $removed]);
        echo "Forms rate-limit sweep: {$removed} files removed.\n";
    } elseif ($command === 'check') {
        $status = is_readable($statusFile) ? json_decode((string) file_get_contents($statusFile), true) : null;
        $at = is_array($status) && ($status['ok'] ?? false) === true ? strtotime((string) ($status['completed_at'] ?? '')) : false;
        if ($at === false || time() - $at > LEAD_FORMS_SWEEP_MAX_AGE) {
            fwrite(STDERR, "Forms rate-limit sweep needs attention: no successful sweep in the last two hours.\n");
            exit(1);
        }
        echo "Forms rate-limit sweep ran at " . gmdate('c', $at) . ".\n";
    } else {
        throw new InvalidArgumentException('Use: php sweep.php [check]');
    }
} catch (Throwable $e) {
    if ($command === 'sweep' && $statusFile !== null) {
        try {
            writeSweepStatus($statusFile, ['ok' => false, 'completed_at' => gmdate('c')]);
        } catch (Throwable $statusError) {
            // Monitoring must consume this command's exit code if status storage itself fails.
            fwrite(STDERR, "The failed sweep status could not be written.\n");
        }
    }
    // the reason, never a value of the configuration
    fwrite(STDERR, 'Forms rate-limit sweep failed: ' . $e->getMessage() . "\n");
    exit(1);
}
