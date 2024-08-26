# fairpair

Create and evaluate pairwise comparison graphs considering accuracy and fairness.

Install the Python package with
```
pip install git+https://github.com/wanLo/fairpair
```

Experiments we conducted can be found a [separate repository](https://github.com/wanLo/fairpair_notebooks).

This repository also includes the [appendix](./appendix.pdf) to our [pre-print](https://arxiv.org/abs/2408.13034). Cite us:

```
Georg Ahnert, Antonio Ferrara, and Claudia Wagner (2024). Fair Pairs: Fairness-Aware Ranking Recovery from Pairwise Comparisons. arXiv preprint arXiv:2408.13034
```

## Overview

See [examples/example.ipynb](examples/example.ipynb) for a general overview of the available functionality, [examples/sampling.ipynb](examples/sampling.ipynb) for a comparison of proposed sampling strategies, and [examples/ranking.ipynb](examples/ranking.ipynb) for how to generate and evaluate rankings.

The package itself consists of the following parts:
- [fairgraph.py](fairpair/fairgraph.py) implements `FairPairGraph` as a subclass of networkx.DiGraph with functions required for generating a graph with two classes and scores for each node, as well as an implementation of the BTL-model for comparing pairs.
- [distributions.py](fairpair/distributions.py) supplies usefull wrappers to sample scores.
- [sampling.py](fairpair/sampling.py) implements a general `Sampling` class which is able to generate statistics while sampling is applied, and supplies implementations for the following sampling methods: `RandomSampling`, and `Oversampling`, and `RankSampling`.
- [rank_recovery.py](fairpair/rank_recovery.py) supplies a wrapper for ranking recovery algorithms.
- [recovery_baselines.py](fairpair/recovery_baselines.py) contains implementations of ranking recovery methods.
- [metrics.py](fairpair/metrics.py) supplies measures of accuracy and fairness for rankings recovered from pairwise comparisons.