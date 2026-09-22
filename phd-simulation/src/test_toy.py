import unittest
import numpy as np
from toy_qaoa import costs, probabilities

class ToyChecks(unittest.TestCase):
    def test_independent_feasible_optimum(self):
        _, demand, unserved = costs()
        # Manually enumerated feasible load sets: {}, {0}, {1}, {2}, {0,1}.
        self.assertEqual(sorted(unserved[demand <= 5].tolist()), [6, 8, 9, 11, 14])

    def test_unitary_normalization_and_zero_phase(self):
        for gamma in [0, 0.3, 2]:
            p = probabilities(np.arange(8), gamma, .7)
            self.assertAlmostEqual(float(p.sum()), 1)
            self.assertTrue(np.all(p >= 0))
        np.testing.assert_allclose(probabilities(np.arange(8), 0, .7), np.ones(8)/8)

    def test_single_qubit_rotation_analytic_oracle(self):
        # Energy depends only on bit zero: p(bit0=1)=(1+sin(2b)*sin(g))/2.
        g,b = .4,.2
        energy = np.arange(8) % 2
        p = probabilities(energy,g,b)
        self.assertAlmostEqual(float(p[1::2].sum()), (1+np.sin(2*b)*np.sin(g))/2)

if __name__ == '__main__':
    unittest.main()
