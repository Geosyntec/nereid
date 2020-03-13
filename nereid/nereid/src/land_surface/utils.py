from typing import Union, Sequence, Mapping

import numpy


## PMH: AFAICT, this isn't used outside of conftest. Is that right?
def make_fake_land_surface_requests(
    n_rows: int,
    n_nodes: int,
    surface_ids: str,
    min_acres: float = 0,
    max_acres: float = 10,
    pct_imp_min: float = 0,
    pct_imp_max: float = 1,
    seed: int = 42,
) -> Sequence[Mapping[str, Union[str, int, float]]]:

    land_surfaces = []

    numpy.random.seed(seed)
    nodes = numpy.random.choice(range(n_nodes))

    for i in range(n_rows):
        land_surface = {}
        land_surface["node_id"] = str(numpy.random.choice(nodes))
        land_surface["surface_key"] = numpy.random.choice(surface_ids)
        land_surface["area_acres"] = numpy.random.uniform(min_acres, max_acres)
        land_surface["imp_area_acres"] = (
            numpy.random.uniform(pct_imp_min, pct_imp_max) * land_surface["area_acres"]
        )

        land_surfaces.append(land_surface)

    return land_surfaces
