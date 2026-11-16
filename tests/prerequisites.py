"""What the integration tests need, and whether a missing prerequisite skips them or fails them.

On a computer without PHP, Composer's vendor folder, Apache or Hugo, the tests that need them are skipped. The CI
backend job sets LEAD_REQUIRE_INTEGRATION=1: then a missing prerequisite fails the test class instead, so that job
can't pass with the integration tests quietly skipped (.github/workflows/backend.yml).
"""
import os
import unittest

REQUIRED = os.environ.get('LEAD_REQUIRE_INTEGRATION') == '1'


def needs(available, reason):
    """unittest.skipUnless(available, reason), except that with LEAD_REQUIRE_INTEGRATION=1 it fails instead"""
    if available or not REQUIRED:
        return unittest.skipUnless(available, reason)

    def missing(cls):
        def setUpClass(_):
            raise RuntimeError('LEAD_REQUIRE_INTEGRATION=1, but this is missing: ' + reason)
        cls.setUpClass = classmethod(setUpClass)
        return cls
    return missing
