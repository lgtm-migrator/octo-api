# 3rd party
import pytest

# this package
from octo_api.api import OctoAPI
from octo_api.utils import MeterPointDetails, Region


def test_get_grid_supply_point(api: OctoAPI):

	assert api.get_grid_supply_point("SW1A 1AA") == Region.London
	assert api.get_grid_supply_point("SW1A1AA") == Region.London

	with pytest.raises(ValueError, match="Cannot map the postcode '12345' to a GSP."):
		api.get_grid_supply_point("12345")
