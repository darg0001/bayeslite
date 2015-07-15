# -*- coding: utf-8 -*-

#   Copyright (c) 2010-2014, MIT Probabilistic Computing Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Miscellaneous statistics utilities."""

import math

from bayeslite.util import float_sum

def arithmetic_mean(array):
    """Arithmetic mean of elements of `array`.

    :param list<float> array: List of floats to compute arithmetic mean.

    :return: Arithmetic mean of `array`.
    :rtype: float
    """
    return float_sum(array) / len(array)

def pearsonr(a0, a1):
    """Pearson r correlation coefficient of two samples.

    For random variables X, Y:

                 cov(X, Y)
    r(X, Y) = ---------------,
              sigma_X sigma_Y

    where

      cov(X, Y) = E[(X - E[X]) (Y - E[Y])],
    {sigma_X}^2 = E[(X - E[X])^2], and
    {sigma_Y}^2 = E[(Y - E[Y])^2]

    For a sample a0, we take the mean of a0 instead of E[X], and the
    variance of a0 instead of E[(X - E[X])^2].

    https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient

    :param list<float> a0: Observations of the first random variable.
    :param list<float> a1: Observations of the second random variable.

    :return: Pearson r correlation coefficient of samples `a0` and `a1`.
    :rtype: float
    """
    n = len(a0)
    assert n == len(a1)
    if n == 0:
        # No data, so no notion of correlation.
        return float('NaN')
    m0 = arithmetic_mean(a0)
    m1 = arithmetic_mean(a1)
    num = float_sum((x0 - m0)*(x1 - m1) for x0, x1 in zip(a0, a1))
    den0_sq = float_sum((x0 - m0)**2 for x0 in a0)
    den1_sq = float_sum((x1 - m1)**2 for x1 in a1)
    den = math.sqrt(den0_sq*den1_sq)
    if den == 0.0:
        # No variation in at least one column, so no notion of
        # correlation.
        return float('NaN')
    r = num / den
    # Clamp r in [-1, +1] in case of floating-point error.
    r = min(r, +1.0)
    r = max(r, -1.0)
    return r

def signum(x):
    """Sign of `x`.

    :param float x: Argument to signum.

    :return: Sign of `x`: ``-1 if x<0, 0 if x=0, +1 if x>0``.
    :rtype: int
    """
    if x < 0:
        return -1
    elif 0 < x:
        return +1
    else:
        return 0

def chi2_contingency(contingency, correction=None):
    """Pearson chi^2 statistic for test of independence on contingency table.

    https://en.wikipedia.org/wiki/Pearson%27s_chi-squared_test#Test_of_independence

    :param list<list> contingency: Table counting values of two random
    variables X, Y in a population sample: for each pair of values
    x_i, y_j that X, Y can take, contingency[i][j] is the number of
    occurrences of that pair.

    :param boolean correction: If ``True``, move each observation
    count in the direction of the expectation by 1/2.

    :return: Observed Pearson chi^2 test statistic on `contingency`.
    :rtype: float
    """
    if correction is None:
        correction = False
    assert 0 < len(contingency)
    assert all(all(isinstance(v, int) for v in row) for row in contingency)
    n = float(sum(sum(row) for row in contingency))
    n0 = len(contingency)
    n1 = len(contingency[0])
    assert all(n1 == len(row) for row in contingency)
    p0 = [float_sum(contingency[i0][i1]/n for i1 in range(n1))
        for i0 in range(n0)]
    p1 = [float_sum(contingency[i0][i1]/n for i0 in range(n0))
        for i1 in range(n1)]
    def q(i0, i1):
        O = contingency[i0][i1]
        E = n*p0[i0]*p1[i1]
        if correction:
            O += 0.5*signum(E - O)
        return ((O - E)**2)/E
    return float_sum(q(i0, i1) for i0 in range(n0) for i1 in range(n1))

def f_oneway(groups):
    """F-test statistic for one-way analysis of variance (ANOVA).

    https://en.wikipedia.org/wiki/F-test#Multiple-comparison_ANOVA_problems

    :param list<list> groups: List of lists of the observed values of
        each group.  The outer list must length equal to the number of
        groups.

    :return: Observed F test statistic on `groups`.
    :rtype: float
    """
    K = len(groups)
    N = sum(len(group) for group in groups)
    means = [arithmetic_mean(group) for group in groups]
    overall_mean = float_sum(x for group in groups for x in group) / N
    bgv = float_sum(len(group) * (mean - overall_mean)**2 / (K - 1)
        for group, mean in zip(groups, means))
    wgv = float_sum(float((x - mean)**2)/float(N - K)
        for group, mean in zip(groups, means)
        for x in group)
    if wgv == 0.0:
        if bgv == 0.0:
            # No variation between or within groups, so we cannot
            # ascertain any correlation between them -- it is as if we
            # had no data about the groups: every value in every group
            # is the same.
            return float('NaN')
        else:
            # Within-group variability is zero, meaning for each
            # group, each value is the same; between-group variability
            # is nonzero, meaning there is variation between the
            # groups.  So if there were zero correlation we could not
            # possibly observe this, whereas all finite F statistics
            # could be observed with zero correlation.
            return float('+inf')
    return bgv / wgv

def t_cdf(x, df):
    """Approximate CDF for Student's t distribution.

    ``t_cdf(x,df) = P(T_df < x)``
    Values are tested to within 0.5% of values returned by the
    Cephes C library for numerical integration.

    :param float x: Argument to the survival function, must be positive.
    :param float df: Degrees of freedom of the chi^2 distribution.

    :return: Area from negative infinity to `x` under t distribution
        with degrees of freedom `df`.
    :rtype: float
    """
    import numpy

    if df <= 0:
        raise ValueError('Degrees of freedom must be positive.')
    if x == 0:
        return 0.5

    MONTE_CARLO_SAMPLES = 1e5
    random = numpy.random.RandomState(seed=0)
    T = random.standard_t(df, size=MONTE_CARLO_SAMPLES)
    p = numpy.sum(T < x) / MONTE_CARLO_SAMPLES
    return p

def chi2_sf(x, df):
    """Approximate survival function for chi^2 distribution.

    ``chi2_sf(x, df) = P(CHI > x)``
    Values are tested to within 0.5% of values returned by the
    Cephes C library for numerical integration.

    :param float x: Argument to the survival function, must be positive.
    :param float df: Degrees of freedom of the chi^2 distribution.

    :return: Area from `x` to infinity under the chi^2 distribution
        with degrees of freedom `df`.
    :rtype: float
    """
    import numpy

    if df <= 0:
        raise ValueError('Degrees of freedom must be positive.')
    if x <= 0:
        return 1.0

    MONTE_CARLO_SAMPLES = 5e5
    random = numpy.random.RandomState(seed=0)
    CHI = random.chisquare(df, size=MONTE_CARLO_SAMPLES)
    p = numpy.sum(CHI > x) / MONTE_CARLO_SAMPLES
    return p

def f_sf(x, df_num, df_den):
    """Approximate survival function for the F distribution.

    ``f_sf(x, df_num, df_den) = P(F > x)``
    Values are tested to within 1% of values returned by the
    Cephes C library for numerical integration.

    :param float x: Argument to the survival function, must be positive.
    :param float df_num: Degrees of freedom of the numerator.
    :param float df_den: Degrees of freedom of the denominator.

    :return: Area from negative infinity to `x` under F distribution
        with degrees of freedom `df`.
    :rtype: float
    """
    import numpy

    if df_num <= 0 or df_den <= 0:
        raise ValueError('Degrees of freedom must be positive.')
    if x <= 0:
        return 1.0

    MONTE_CARLO_SAMPLES = 1e5
    random = numpy.random.RandomState(seed=0)
    F = random.f(df_num, df_den, size=MONTE_CARLO_SAMPLES)
    p = numpy.sum(F > x) / MONTE_CARLO_SAMPLES
    return p
