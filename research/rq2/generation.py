"""Grounded generation: an LLM writes the review comment from the retrieved notes.

Only notes the model cites, and that were actually offered to it, are passed on. Responses
are cached by prompt in a JSONL file, so a rerun makes no calls and gives the same result.
"""
import hashlib
import json
import re

import numpy as np

SYSTEM = 'You are a code reviewer. Use only the numbered notes you are given. Reply with JSON only.'


def build_prompt(query, notes):
    listed = '\n'.join(f'[{n}] {text}' for n, text in enumerate(notes, start=1))
    return (
        f'Change under review: {query}\n\n'
        f'Notes the reviewers retrieved from memory:\n{listed}\n\n'
        'Write a review comment of at most three sentences that uses the notes relevant to this change. '
        'Reply as {"comment": "...", "cited": [numbers of the notes you used]}. '
        'Cite only numbers from the list above; cite none if no note is relevant.'
    )


def parse_cited(content, count):
    """Returns (valid 1-based note numbers, number of invalid citations), or None if unparseable."""
    match = re.search(r'\{.*\}', content or '', re.DOTALL)
    try:
        cited = json.loads(match.group(0))['cited']
    except (AttributeError, ValueError, KeyError, TypeError):
        return None
    if not isinstance(cited, list):
        return None
    is_valid = [isinstance(c, int) and not isinstance(c, bool) and 1 <= c <= count for c in cited]
    valid = {c for c, ok in zip(cited, is_valid) if ok}
    return valid, is_valid.count(False)


class Generator:
    def __init__(self, client, model, cache_path):
        self.client = client
        self.model = model
        self.cache_path = cache_path
        self.cache = {}
        if cache_path.exists():
            for line in cache_path.read_text().splitlines():
                entry = json.loads(line)
                self.cache[entry['key']] = entry['content']
        self.stats = {'reviews': 0, 'cache_hits': 0, 'unparseable': 0, 'invalid_citations': 0, 'offered': 0, 'cited': 0}

    def complete(self, prompt):
        key = hashlib.sha256(f'{self.model}|{SYSTEM}|{prompt}'.encode()).hexdigest()
        if key in self.cache:
            self.stats['cache_hits'] += 1
            return self.cache[key]
        if self.client is None:
            raise RuntimeError('A generation response is not cached and no OPENROUTER_API_KEY is set')
        data = self.client.post('/chat/completions', {
            'model': self.model,
            'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': prompt}],
            'temperature': 0,
            'seed': 0,
            'max_tokens': 300,
            'response_format': {'type': 'json_object'},
        })
        content = data['choices'][0]['message'].get('content') or ''
        self.cache[key] = content
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_path.open('a') as file:
            file.write(json.dumps({'key': key, 'model': self.model, 'prompt': prompt, 'content': content}) + '\n')
        return content

    def cite(self, query, candidates, texts):
        """Return the candidate item indices the model validly cited (empty if unparseable)."""
        candidates = np.asarray(candidates)
        content = self.complete(build_prompt(query, [texts[i] for i in candidates]))
        parsed = parse_cited(content, len(candidates))
        self.stats['reviews'] += 1
        self.stats['offered'] += len(candidates)
        if parsed is None:
            self.stats['unparseable'] += 1
            return candidates[:0]
        valid, invalid = parsed
        self.stats['invalid_citations'] += invalid
        self.stats['cited'] += len(valid)
        return np.sort(candidates[[n - 1 for n in valid]]) if valid else candidates[:0]
