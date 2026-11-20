"""Replay the committed OpenRouter experiment without API calls or result overwrites.

Run from the repository root: python -m research.rq2.replay
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pandas as pd

from research.rq2 import run


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='new directory inside the repository; must not exist')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    source = root / 'research/rq2'
    reference = source / 'results/trivago'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = (args.output or root / '_reproduction' / ('rq2-' + stamp)).resolve()
    if not output.is_relative_to(root):
        parser.error('--output must be inside the repository')
    if output.exists():
        parser.error('output directory already exists; choose a new directory')

    caches = [source / 'cache/embeddings-openai_text-embedding-3-small-256.npz',
              source / 'cache/generation-openai_gpt-4.1-nano.jsonl']
    required = caches + sorted(reference.glob('*.csv')) + [reference / 'run.json']
    for path in required:
        if not path.is_file():
            raise SystemExit(f'Missing committed input: {path.relative_to(root)}')
    original_hashes = {str(path.relative_to(root)): digest(path) for path in required}
    (output / 'cache').mkdir(parents=True)
    for path in caches:
        shutil.copy2(path, output / 'cache' / path.name)

    # Use the existing engine and isolated copies of the caches. Ignoring api_key()
    # also ignores any OPENROUTER_API_KEY in the environment or repository .env.
    # With client=None, an uncached embedding/response fails instead of using HTTP.
    old_rq2, old_key, old_argv = run.RQ2, run.api_key, sys.argv
    try:
        run.RQ2 = output
        run.api_key = lambda: None
        sys.argv = ['research.rq2.run', '--embedder', 'openrouter', '--generate', '--max-cost', '0']
        run.main()
    finally:
        run.RQ2, run.api_key, sys.argv = old_rq2, old_key, old_argv
        changed = [str(path.relative_to(root)) for path in required
                   if digest(path) != original_hashes[str(path.relative_to(root))]]
        if changed:
            raise RuntimeError(f'Committed inputs changed: {changed}')

    replay = output / 'results/trivago'
    compared = []
    for expected in sorted(reference.glob('*.csv')):
        actual = replay / expected.name
        pd.testing.assert_frame_equal(pd.read_csv(expected), pd.read_csv(actual), check_exact=True)
        compared.append(expected.name)
    original_run = json.loads((reference / 'run.json').read_text())
    replay_run = json.loads((replay / 'run.json').read_text())
    for field in ['network', 'participants', 'reviews', 'k', 'seed', 'embedder',
                  'embedding_model', 'dimensions', 'chat_model']:
        if original_run[field] != replay_run[field]:
            raise RuntimeError(f'Configuration differs: {field}')
    if replay_run['openrouter_calls'] != 0 or replay_run['openrouter_reported_cost_usd'] != 0:
        raise RuntimeError('Replay unexpectedly made API calls')
    if replay_run['generation']['cache_hits'] != replay_run['generation']['reviews']:
        raise RuntimeError('Replay did not use only cached generation responses')
    result = {'passed': True, 'parsed_csvs_identical': compared,
              'committed_inputs_unchanged': True, 'input_sha256': original_hashes,
              'original_run_metadata': original_run, 'replay_metadata': replay_run}
    (output / 'verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS: all saved CSV values matched; no API calls; committed inputs unchanged.')
    print(f'Verification: {(output / "verification.json").relative_to(root)}')


if __name__ == '__main__':
    main()
