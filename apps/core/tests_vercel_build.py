"""Vercel collectstatic must import settings without SECRET_KEY."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2]


class VercelCollectstaticTests(SimpleTestCase):
    def test_collectstatic_without_runtime_secrets(self):
        env = {
            key: value
            for key, value in os.environ.items()
            if key
            not in {
                'SECRET_KEY',
                'CSRF_TRUSTED_ORIGINS',
                'DATABASE_URL',
            }
        }
        env['DEBUG'] = 'False'
        env['VERCEL'] = '1'
        env['DJANGO_SETTINGS_MODULE'] = 'config.settings'
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / 'manage.py'),
                'collectstatic',
                '--noinput',
                '--dry-run',
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('ImproperlyConfigured', result.stderr)
