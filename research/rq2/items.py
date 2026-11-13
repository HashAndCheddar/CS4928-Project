"""Reproducible synthetic information items and review queries.

The review data has no text, so every participant gets one generated note. Notes are
built from a topic, a component of that topic, a fact and a reason, and drawn without
replacement, so all notes are distinct. Each review gets a query about one member's
topic. Everything is a pure function of the seed and the ids.
"""
from itertools import product
import zlib

import numpy as np

TOPICS = {
    'authentication': ['the login flow', 'token refresh', 'password reset', 'session handling', 'single sign-on'],
    'caching': ['the search result cache', 'the CDN layer', 'cache invalidation', 'the price cache', 'cache warm-up'],
    'database': ['the bookings schema', 'the migration scripts', 'the read replicas', 'connection pooling', 'the hotel table indexes'],
    'search': ['the ranking model', 'query parsing', 'the autocomplete service', 'filter handling', 'the search index'],
    'deployment': ['the release pipeline', 'the canary rollout', 'the Kubernetes manifests', 'environment config', 'rollback scripts'],
    'logging': ['request tracing', 'the error reporter', 'log retention', 'the metrics exporter', 'alert rules'],
    'api': ['the public REST API', 'API versioning', 'rate limiting', 'the GraphQL gateway', 'request validation'],
    'frontend': ['the date picker', 'the results page', 'the map view', 'the CSS build', 'client-side routing'],
    'testing': ['the integration test suite', 'test fixtures', 'flaky end-to-end tests', 'the mocking library', 'coverage gates'],
    'localisation': ['currency formatting', 'translation files', 'right-to-left layouts', 'date formats', 'the locale fallback'],
    'performance': ['image loading', 'the hot path in pricing', 'memory usage of workers', 'database query batching', 'page load budget'],
    'security': ['input sanitising', 'secret rotation', 'the dependency scanner', 'CSRF protection', 'access control checks'],
}
FACTS = [
    'was moved behind a feature flag',
    'now retries failed calls three times',
    'no longer accepts empty input',
    'must be changed together with its config file',
    'has a known race condition under load',
    'was rewritten to use the shared client',
]
REASONS = [
    'after an incident last quarter',
    'to cut response time',
    'because the old behaviour broke clients',
    'to match the new API contract',
    'as agreed in the architecture review',
    'because of a security finding',
]
NOTES = [
    (topic, f'{topic.capitalize()}: {component} {fact} {reason}.')
    for topic, components in TOPICS.items()
    for component, fact, reason in product(components, FACTS, REASONS)
]


def make_items(participants, seed):
    """One distinct note per participant; returns (texts, topics) aligned with participants."""
    if len(participants) > len(NOTES):
        raise ValueError(f'{len(participants)} participants but only {len(NOTES)} distinct notes')
    order = np.random.default_rng(seed).permutation(len(NOTES))[:len(participants)]
    topics = [NOTES[i][0] for i in order]
    texts = [NOTES[i][1] for i in order]
    return texts, topics


def make_query(review, member_topics, seed):
    """The query for a review is about a component in the topic of one of its members."""
    rng = np.random.default_rng([seed, zlib.crc32(review.encode())])
    topic = member_topics[rng.integers(len(member_topics))]
    component = TOPICS[topic][rng.integers(len(TOPICS[topic]))]
    return f'Code review of a change to {component} in the {topic} area.'
