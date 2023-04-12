import numpy as np

class Distributions:

    @staticmethod
    def uniform_distr(*, n: int, low=0.000001, high=1, seed: int | None = None):
        '''Draw scores from a uniform distribution using np.random.Generator.uniform'''
        rng = np.random.default_rng(seed=seed)
        return rng.uniform(low=low, high=high, size=n)

    @staticmethod
    def normal_distr(*, n: int, loc=0.5, scale=0.25, min_val=0.0001, max_val=0.9999, seed: int | None = None):
        '''Draw scores from a normal distribution using np.random.Generator.normal, limit to [min_val, max_val]'''
        rng = np.random.default_rng(seed=seed)
        scores = rng.normal(loc=loc, scale=scale, size=n)
        scores = [max(min_val, min(max_val, x)) for x in scores]
        return np.array(scores)