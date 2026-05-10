"""Multi-objective performance metrics (pure Python, 2-objective focus).

The metrics implemented match those covered in BAO chapter 6.2:

- hypervolume_2d -- HV (combined convergence + diversity)
- inverted_generational_distance -- IGD (diversity / convergence)
- delta_spread -- Delta diversity metric (Deb)
- schott_spacing -- legacy spacing metric, kept for backward compatibility
"""

from diet_bao.metrics.hypervolume import hypervolume_2d
from diet_bao.metrics.igd import inverted_generational_distance
from diet_bao.metrics.spread import delta_spread, schott_spacing

__all__ = [
    "hypervolume_2d",
    "inverted_generational_distance",
    "delta_spread",
    "schott_spacing",
]
