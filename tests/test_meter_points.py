# this package
from octo_api.api import OctoAPI
from octo_api.utils import MeterPointDetails, Region


def test_get_meter_point_details(api: OctoAPI):

	assert api.get_meter_point_details("2000024512368") == MeterPointDetails(
			mpan="2000024512368",
			gsp=Region.Southern,
			profile_class=1,
			)

	assert isinstance(api.get_meter_point_details("2000024512368"), MeterPointDetails)
