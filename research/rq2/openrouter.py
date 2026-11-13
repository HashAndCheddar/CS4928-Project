"""Minimal OpenRouter client: key from the environment, bounded retries, and a spending cap.

The key is read from OPENROUTER_API_KEY, or from that line in a repo-root .env file (.env
is gitignored). It is only ever sent in the Authorization header and is never printed.
"""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

API = 'https://openrouter.ai/api/v1'
ROOT = Path(__file__).resolve().parents[2]
RETRY_CODES = {408, 429, 500, 502, 503, 504, 524, 529}


class BudgetExceeded(RuntimeError):
    pass


def api_key():
    key = os.environ.get('OPENROUTER_API_KEY')
    env_file = ROOT / '.env'
    if not key and env_file.exists():
        for line in env_file.read_text().splitlines():
            name, _, value = line.partition('=')
            if name.strip() == 'OPENROUTER_API_KEY':
                key = value.strip().strip('"\'')
    return key or None


class OpenRouter:
    def __init__(self, key, max_cost, retries=3, timeout=60):
        self._key = key
        self.max_cost = max_cost
        self.retries = retries
        self.timeout = timeout
        self.spent = 0.0
        self.calls = 0

    def post(self, path, body):
        if self.spent >= self.max_cost:
            raise BudgetExceeded(f'Spent ${self.spent:.4f} of the ${self.max_cost:.2f} cap')
        request = urllib.request.Request(
            API + path,
            data=json.dumps(body).encode(),
            headers={'Authorization': f'Bearer {self._key}', 'Content-Type': 'application/json'},
        )
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data = json.load(response)
                break
            except urllib.error.HTTPError as error:
                if error.code not in RETRY_CODES or attempt == self.retries:
                    detail = error.read()[:300].decode(errors='replace')
                    raise RuntimeError(f'OpenRouter {path} failed with HTTP {error.code}: {detail}') from None
            except OSError as error:  # URLError, timeouts, dropped connections (RemoteDisconnected)
                if attempt == self.retries:
                    raise RuntimeError(f'OpenRouter {path} unreachable: {error}') from None
            time.sleep(2 ** attempt)

        if 'error' in data:
            raise RuntimeError(f'OpenRouter {path} returned an error: {str(data["error"])[:300]}')
        self.calls += 1
        self.spent += float((data.get('usage') or {}).get('cost') or 0)
        return data
