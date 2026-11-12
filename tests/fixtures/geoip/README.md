# Offline test fixture

`GeoIP2-Country-Test.mmdb` is MaxMind's synthetic country test database, copied
from [MaxMind-DB at d12e37856df12a62bb4647da66d20feddb8783a6](https://github.com/maxmind/MaxMind-DB/tree/d12e37856df12a62bb4647da66d20feddb8783a6/test-data).
It is not the production country database or user logs.

SHA-256: `fc12d6470b35b70bd3e4534dd433d3e262a6c73f7682f85c344e832d4190f02b`.
Copyright 2013–2026 MaxMind, Inc. Licensed under Apache-2.0 or MIT at your
option; both upstream license texts are included here.

Tests exercise the locked `maxmind-db/reader` 1.14.0: fixture addresses
81.2.69.160 → GB, 2001:218:: → JP, and 127.0.0.1 → no record. No lookup leaves
the machine. Run Composer install before the collector tests.
