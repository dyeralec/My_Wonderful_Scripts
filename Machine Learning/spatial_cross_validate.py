"""
Evaluate metric(s) by sptial cross-validation by splitting data set into clusters
using coordinate fields (latitude & longitude).

Created by Alec Dyer
4/8/2022
"""

import numpy as np
from sklearn.model_selection import cross_validate, GroupKFold
from sklearn.cluster import KMeans

def spatial_cross_validate(
    estimator,
    X,
    lat,
    lon,
    n_clusters=5,
    random_state=None,
    y=None,
    scoring=None,
    n_jobs=None,
    verbose=0,
    fit_params=None,
    pre_dispatch="2*n_jobs",
    return_train_score=False,
    return_estimator=False,
    error_score=np.nan,
    ):

    """Evaluate metric(s) by sptial cross-validation using k-means clustering
    of latitude and longitude coordinates. This code builds off the sklearn
    function, cross_validate.
    Read more in the :ref:`User Guide <multimetric_cross_validation>`.
    Parameters
    ----------
    estimator : estimator object implementing 'fit'
        The object to use to fit the data.
    X : pandas DataFrame (n_samples, n_features)
        The data to fit. Can be for example a list, or an array.
    lat: str, name of latitude field in X.
    lon: str, name of longitude field in X.
    n_clusters: int, default=5. Number of clusters to be used in
        cross validation.
    random_state: int, RandomState instance or None, default=None
    y : array-like of shape (n_samples,) or (n_samples, n_outputs), \
            default=None
        The target variable to try to predict in the case of
        supervised learning.
    scoring : str, callable, list, tuple, or dict, default=None
        Strategy to evaluate the performance of the cross-validated model on
        the test set.
        If `scoring` represents a single score, one can use:
        - a single string (see :ref:`scoring_parameter`);
        - a callable (see :ref:`scoring`) that returns a single value.
        If `scoring` represents multiple scores, one can use:
        - a list or tuple of unique strings;
        - a callable returning a dictionary where the keys are the metric
          names and the values are the metric scores;
        - a dictionary with metric names as keys and callables a values.
        See :ref:`multimetric_grid_search` for an example.
    n_jobs : int, default=None
        Number of jobs to run in parallel. Training the estimator and computing
        the score are parallelized over the cross-validation splits.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.
    verbose : int, default=0
        The verbosity level.
    fit_params : dict, default=None
        Parameters to pass to the fit method of the estimator.
    pre_dispatch : int or str, default='2*n_jobs'
        Controls the number of jobs that get dispatched during parallel
        execution. Reducing this number can be useful to avoid an
        explosion of memory consumption when more jobs get dispatched
        than CPUs can process. This parameter can be:
            - None, in which case all the jobs are immediately
              created and spawned. Use this for lightweight and
              fast-running jobs, to avoid delays due to on-demand
              spawning of the jobs
            - An int, giving the exact number of total jobs that are
              spawned
            - A str, giving an expression as a function of n_jobs,
              as in '2*n_jobs'
    return_train_score : bool, default=False
        Whether to include train scores.
        Computing training scores is used to get insights on how different
        parameter settings impact the overfitting/underfitting trade-off.
        However computing the scores on the training set can be computationally
        expensive and is not strictly required to select the parameters that
        yield the best generalization performance.
        .. versionadded:: 0.19
        .. versionchanged:: 0.21
            Default value was changed from ``True`` to ``False``
    return_estimator : bool, default=False
        Whether to return the estimators fitted on each split.
        .. versionadded:: 0.20
    error_score : 'raise' or numeric, default=np.nan
        Value to assign to the score if an error occurs in estimator fitting.
        If set to 'raise', the error is raised.
        If a numeric value is given, FitFailedWarning is raised.
        .. versionadded:: 0.20
    Returns
    -------
    scores : dict of float arrays of shape (n_splits,)
        Array of scores of the estimator for each run of the cross validation.
        A dict of arrays containing the score/time arrays for each scorer is
        returned. The possible keys for this ``dict`` are:
            ``test_score``
                The score array for test scores on each cv split.
                Suffix ``_score`` in ``test_score`` changes to a specific
                metric like ``test_r2`` or ``test_auc`` if there are
                multiple scoring metrics in the scoring parameter.
            ``train_score``
                The score array for train scores on each cv split.
                Suffix ``_score`` in ``train_score`` changes to a specific
                metric like ``train_r2`` or ``train_auc`` if there are
                multiple scoring metrics in the scoring parameter.
                This is available only if ``return_train_score`` parameter
                is ``True``.
            ``fit_time``
                The time for fitting the estimator on the train
                set for each cv split.
            ``score_time``
                The time for scoring the estimator on the test set for each
                cv split. (Note time for scoring on the train set is not
                included even if ``return_train_score`` is set to ``True``
            ``estimator``
                The estimator objects for each cv split.
                This is available only if ``return_estimator`` parameter
                is set to ``True``.

    """

    # create list of coordinates (lat/lon)
    coors = [[i[lon], i[lat]] for v, i in X.iterrows()]

    # group points with KMeans clustering using the coordinates
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(coors)
    groups = kmeans.labels_

    cv = GroupKFold(n_clusters)

    # run cross_validate with the cluster groups
    results = cross_validate(estimator, X, y=y, groups=groups, scoring=scoring, cv=cv, n_jobs=n_jobs, verbose=verbose, fit_params=fit_params, pre_dispatch=pre_dispatch, return_train_score=return_train_score, return_estimator=return_estimator, error_score=error_score)

    return results