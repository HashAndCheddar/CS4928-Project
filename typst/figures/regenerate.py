from pathlib import Path
import csv
import json
import hashlib

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
FIG = HERE
DATA = FIG / 'data'
DATA.mkdir(parents=True, exist_ok=True)
SHA = '40f8c8556f11cbc9d8e38a7cd3aac6b12a0adb20'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 8,
    'axes.titlesize': 8.5, 'axes.labelsize': 8,
    'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5,
    'svg.fonttype': 'path', 'pdf.fonttype': 42,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#777777', 'axes.linewidth': .6,
})

sources = [
    'research/event_a/results/turnover.csv',
    'research/event_a/results/split_sensitivity.csv',
    'research/rq2/results/trivago/coverage.csv',
    'research/rq2/results/trivago/summary.csv',
]
manifest = []
for path in sources:
    target = DATA / ('event_a_' + Path(path).name if 'event_a' in path else 'rq2_' + Path(path).name)
    if not target.is_file():
        raise FileNotFoundError(f'Missing figure input: {target}')
    manifest.append({'file': str(target.relative_to(FIG)).replace('\\', '/'),
                     'source_url': f'https://github.com/HashAndCheddar/CS4928-Project/blob/{SHA}/{path}',
                     'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})

def read(name):
    with (DATA / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

turnover = {r['cohort']: r for r in read('event_a_turnover.csv')}
split = next(r for r in read('event_a_split_sensitivity.csv') if r['split'] == '2020-02-17')
fig, axes = plt.subplots(2, 1, figsize=(3.5, 2.7))
panels = [
    ('a) Window medians',
     [f"Early (n = {int(split['early_participants']):,})\n{int(split['early_reviews']):,} reviews",
      f"Late (n = {int(split['late_participants']):,})\n{int(split['late_reviews']):,} reviews"],
     [float(turnover['all']['early_median']), float(turnover['all']['late_median'])]),
    ('b) Late-window cohorts',
     [f"Continuing\nn = {int(turnover['continuing']['participants']):,}",
      f"Joined (late only)\nn = {int(turnover['joined']['participants']):,}"],
     [float(turnover['continuing']['late_median']), float(turnover['joined']['late_median'])]),
]
for ax, (title, labels, values) in zip(axes, panels):
    ax.barh([1, 0], values, height=.48, color=['#909090', '#2166ac'])
    ax.set_yticks([1, 0], labels)
    ax.set_xlim(0, 1)
    ax.set_ylim(-.55, 1.6)
    ax.set_xticks([0, .5, 1])
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_title(title, loc='left', pad=6)
    ax.grid(axis='x', color='#dddddd', linewidth=.5)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', length=0)
    for y, value in zip([1, 0], values):
        ax.text(value + .025, y, f'{value:.2f}', va='center', fontsize=8, weight='bold')
axes[-1].set_xlabel('Coverage (active population)')
fig.subplots_adjust(left=.43, right=.97, top=.92, bottom=.15, hspace=.85)
for ext in ('svg', 'png'):
    fig.savefig(FIG / f'event-a-coverage.{ext}', dpi=240, facecolor='white', bbox_inches='tight', pad_inches=.04)
plt.close(fig)

coverage = read('rq2_coverage.csv')
assert len(coverage) == 364
styles = [
    ('perfect', 'Perfect memory', '#333333', '-'),
    ('random_5', 'Random-5', '#7570b3', '--'),
    ('rag_5', 'Semantic top-5', '#2166ac', '-.'),
    ('rag_5_generation', 'Top-5 + generation', '#a6611a', ':'),
]
fig, ax = plt.subplots(figsize=(3.5, 2.3))
for condition, label, color, style in styles:
    values = np.array([float(r[condition]) for r in coverage])
    assert np.all((values >= 0) & (values <= 1))
    x, counts = np.unique(values, return_counts=True)
    y = np.cumsum(counts) / len(values)
    ax.step(np.r_[0, x, 1], np.r_[0, y, 1], where='post',
            label=label, color=color, linestyle=style, linewidth=1.6)
ax.set(xlim=(0, 1), ylim=(0, 1.025), xlabel='Coverage: fraction of the 364-person network',
       ylabel='Fraction of notes at or below coverage')
ax.set_xticks(np.linspace(0, 1, 6))
ax.set_yticks(np.linspace(0, 1, 5))
ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.grid(color='#dddddd', linewidth=.5)
ax.legend(loc='lower right', frameon=True, framealpha=1, facecolor='white', edgecolor='none', fontsize=7)
fig.subplots_adjust(left=.18, right=.97, top=.96, bottom=.22)
for ext in ('svg', 'png'):
    fig.savefig(FIG / f'rq2-distributions.{ext}', dpi=240, facecolor='white', bbox_inches='tight', pad_inches=.04)
plt.close(fig)

(FIG / 'sources.json').write_text(json.dumps({'repository_commit': SHA, 'sources': manifest,
    'notes': ['Graphs are derived from saved outputs; no new experiment was performed.',
              'Event A cohorts measure review activity, not employment.',
              'RQ2 ECDF uses all 364 saved per-note coverage rows, not confidence intervals.']},
    indent=2), encoding='utf-8')
(FIG / 'requirements.txt').write_text(
    'matplotlib==3.11.2\nnumpy==2.5.5\ncontourpy==1.4.0\ncycler==0.12.1\n'
    'fonttools==4.68.0\nkiwisolver==1.5.1\npackaging==26.3\npillow==13.0.0\n'
    'pyparsing==3.3.3\npython-dateutil==4.0.0\ntzdata==2026.6\n', encoding='utf-8')
print('Created Event A and RQ2 SVG/PNG figures from saved CSV evidence.')
