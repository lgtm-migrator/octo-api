# stdlib
from datetime import datetime, timezone

# 3rd party
import pytest

# this package
from octo_api.api import OctoAPI
from octo_api.products import RateInfo
from octo_api.utils import RateType


def test_get_tariff_charges(api: OctoAPI):
	charges = api.get_tariff_charges(
			product_code="VAR-17-01-11",
			tariff_code="E-1R-VAR-17-01-11-A",
			fuel="electricity",
			rate_type=RateType.StandardUnitRate,
			)
	assert len(charges) == 6
	expected = [
			RateInfo(
					value_exc_vat=15.51,
					value_inc_vat=16.2855,
					valid_from="2020-11-01T00:00:00Z",
					valid_to=None,
					),
			RateInfo(
					value_exc_vat=14.78,
					value_inc_vat=15.519,
					valid_from="2020-01-15T00:00:00Z",
					valid_to="2020-11-01T00:00:00Z",
					),
			RateInfo(
					value_exc_vat=15.07,
					value_inc_vat=15.8235,
					valid_from="2019-04-30T23:00:00Z",
					valid_to="2020-01-15T00:00:00Z",
					),
			RateInfo(
					value_exc_vat=15.62,
					value_inc_vat=16.401,
					valid_from="2018-11-20T00:00:00Z",
					valid_to="2019-04-30T23:00:00Z",
					),
			RateInfo(
					value_exc_vat=13.94,
					value_inc_vat=14.637,
					valid_from="2018-08-05T23:00:00Z",
					valid_to="2018-11-20T00:00:00Z",
					),
			RateInfo(
					value_exc_vat=12.34,
					value_inc_vat=12.957,
					valid_from="2017-01-11T10:00:00Z",
					valid_to="2018-08-05T23:00:00Z",
					),
			]
	assert list(charges) == expected
	assert charges == expected

	with pytest.raises(ValueError, match="'page_size' may not be greater than 1,500"):
		api.get_tariff_charges(
				product_code="VAR-17-01-11",
				tariff_code="E-1R-VAR-17-01-11-A",
				fuel="electricity",
				rate_type=RateType.StandardUnitRate,
				page_size=2000,
				)


def test_get_agile_tariff_charges(api: OctoAPI):
	charges = api.get_tariff_charges(
			product_code="AGILE-18-02-21",
			tariff_code="E-1R-AGILE-18-02-21-C",
			fuel="electricity",
			rate_type=RateType.StandardUnitRate,
			)

	assert len(charges) == 65611
	assert len(charges._results) == 100
	assert charges[100] == RateInfo(
			value_exc_vat=9.76,
			value_inc_vat=10.248,
			valid_from=datetime(2020, 9, 26, 19, 30, tzinfo=timezone.utc),
			valid_to=datetime(2020, 9, 26, 20, 0, tzinfo=timezone.utc),
			)
	assert len(charges._results) == 200
