"""Model layer: out-of-distribution detection for the quantile offset models."""
import numpy as np

from agroforestry.models import QuantileModel


def test_ood_score_flags_out_of_range():
    rng = np.random.default_rng(0)
    X = rng.uniform(0.0, 1.0, size=(200, 4))
    y = X[:, 0] + rng.normal(0, 0.05, 200)
    qm = QuantileModel().fit(X, y, feature_names=list("abcd"))
    # a point inside the training cloud -> 0 OOD; a point far outside -> all features OOD
    assert qm.ood_score(np.array([[0.5, 0.5, 0.5, 0.5]]))[0] == 0.0
    assert qm.ood_score(np.array([[9.0, 9.0, 9.0, 9.0]]))[0] == 1.0
