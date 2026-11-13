"""RQ2: perfect memory vs bounded (top-k) retrieval-augmented memory on the same review network.

    python -m research.rq2.run                 # perfect, random-k control, RAG retrieval
    python -m research.rq2.run --generate      # also RAG + LLM generation (needs OPENROUTER_API_KEY)

Embeddings use OpenRouter when a key is available, otherwise local TF-IDF (or force one with --embedder).
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from research.rq1.run import compute_ranges
from research.rq2 import diffusion, embeddings, items
from research.rq2.generation import Generator
from research.rq2.openrouter import OpenRouter, api_key
from simulation.model import CommunicationNetwork

ROOT = Path(__file__).resolve().parents[2]
RQ2 = ROOT / 'research/rq2'
RQ1_RESULT = ROOT / 'research/rq1/results/normalized_ranges.csv'
PERCENTILES = (0.7, 0.5, 0.3, 0.1)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--network', default='trivago', choices=('trivago', 'spotify', 'microsoft'))
    parser.add_argument('--k', type=int, default=5, help='items each participant can retrieve per review')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--embedder', default='auto', choices=('auto', 'openrouter', 'tfidf'))
    parser.add_argument('--embedding-model', default='openai/text-embedding-3-small')
    parser.add_argument('--dimensions', type=int, default=256)
    parser.add_argument('--generate', action='store_true', help='add the RAG + LLM generation condition')
    parser.add_argument('--chat-model', default='openai/gpt-4.1-nano')
    parser.add_argument('--max-cost', type=float, default=1.0, help='USD cap on reported OpenRouter cost per run')
    return parser.parse_args()


def summarise(name, coverage):
    """Max/median plus the paper's Table 5 rows: the largest observed coverage v such that at
    least a fraction q of items reach more than v (gives 0.67/0.72/0.81/0.83 for Trivago)."""
    row = {'condition': name, 'max': coverage.max(), 'median': coverage.median(), 'mean': coverage.mean()}
    values = np.unique(coverage)
    for q in PERCENTILES:
        row[f'top_{q:g}'] = max((v for v in values if (coverage > v).mean() >= q), default=values[0])
    return row


def main():
    args = parse_args()
    key = api_key()
    client = OpenRouter(key, args.max_cost) if key else None
    embedder = args.embedder if args.embedder != 'auto' else ('openrouter' if key else 'tfidf')
    if embedder == 'openrouter' and args.embedder == 'auto':
        print('Using OpenRouter embeddings (key found).')
    elif embedder == 'tfidf':
        print('Using local TF-IDF embeddings.' + ('' if key else ' No OPENROUTER_API_KEY found.'))

    network = CommunicationNetwork.from_json(ROOT / f'data/networks/{args.network}.json.bz2', name=args.network)
    participants = tuple(sorted(network.participants()))
    index = {p: i for i, p in enumerate(participants)}
    texts, topics = items.make_items(participants, args.seed)
    reviews = sorted(network.channels())
    queries = {
        r: items.make_query(r, sorted(topics[index[p]] for p in network.participants(r)), args.seed)
        for r in reviews
    }
    print(f'{args.network}: {len(participants)} participants, {len(reviews)} reviews, k={args.k}.')

    corpus = texts + [queries[r] for r in reviews]
    if embedder == 'openrouter':
        cache = RQ2 / f'cache/embeddings-{args.embedding_model.replace("/", "_")}-{args.dimensions}.npz'
        vectors = embeddings.openrouter(corpus, client, args.embedding_model, args.dimensions, cache)
    else:
        vectors = embeddings.tfidf(corpus)
    item_vectors, query_vectors = vectors[:len(texts)], vectors[len(texts):]
    similarity = dict(zip(reviews, query_vectors @ item_vectors.T))

    retrieve = diffusion.retrieval(similarity, args.k)
    conditions = {
        'perfect': diffusion.perfect,
        f'random_{args.k}': diffusion.random_k(args.k, args.seed),
        f'rag_{args.k}': retrieve,
    }
    generator = None
    if args.generate:
        generator = Generator(client, args.chat_model, RQ2 / f'cache/generation-{args.chat_model.replace("/", "_")}.jsonl')
        progress = tqdm(total=len(reviews), desc='RAG + generation', unit='review')

        generation_share = diffusion.generated(
            retrieve, lambda review, candidates: generator.cite(queries[review], candidates, texts))

        def with_progress(review, members, memory):
            progress.update()
            return generation_share(review, members, memory)

        conditions[f'rag_{args.k}_generation'] = with_progress

    memories = {}
    for name, share in conditions.items():
        memories[name] = diffusion.diffuse(network, share)[1]
        print(f'  {name}: done')
    if generator:
        progress.close()

    # Perfect memory must reproduce the RQ1 range distribution; otherwise the comparison is meaningless.
    perfect_ranges = compute_ranges(diffusion.to_minimal_distances(participants, memories['perfect']), 'perfect', True)
    if args.network == 'trivago':
        expected = pd.read_csv(RQ1_RESULT, index_col='index')['Trivago']
        matches = np.allclose(perfect_ranges.to_numpy(), expected.to_numpy(), atol=1e-6) and len(expected) == len(perfect_ranges)
        if not matches:
            raise SystemExit('Perfect memory does not reproduce research/rq1/results/normalized_ranges.csv')
        print('Perfect memory reproduces the RQ1 Trivago range distribution exactly.')

    results = RQ2 / 'results' / args.network
    results.mkdir(parents=True, exist_ok=True)
    coverage = pd.DataFrame({name: diffusion.coverage(participants, m) for name, m in memories.items()})
    coverage.index.name = 'participant'
    coverage.to_csv(results / 'coverage.csv', float_format='%g')
    for normalize, output in ((True, 'normalized_ranges.csv'), (False, 'ranges.csv')):
        ranges = pd.concat([
            compute_ranges(diffusion.to_minimal_distances(participants, m), name, normalize)
            for name, m in memories.items()
        ], axis=1).fillna(1)
        ranges.to_csv(results / output, index_label='index', float_format='%g')
    summary = pd.DataFrame([summarise(name, coverage[name].round(2)) for name in coverage]).set_index('condition')
    summary.to_csv(results / 'summary.csv', float_format='%.4g')

    run = {
        'network': args.network, 'participants': len(participants), 'reviews': len(reviews),
        'k': args.k, 'seed': args.seed, 'embedder': embedder,
        'embedding_model': args.embedding_model if embedder == 'openrouter' else None,
        'dimensions': args.dimensions if embedder == 'openrouter' else None,
        'chat_model': args.chat_model if generator else None,
        'generation': generator.stats if generator else None,
        'openrouter_calls': client.calls if client else 0,
        'openrouter_reported_cost_usd': round(client.spent, 6) if client else 0,
        'rag_within_perfect': bool((coverage.drop(columns='perfect').le(coverage['perfect'], axis=0)).all().all()),
    }
    (results / 'run.json').write_text(json.dumps(run, indent=2) + '\n')

    print(summary.round(2).to_string())
    print(f'Results written to {results.relative_to(ROOT)}.')


if __name__ == '__main__':
    main()
