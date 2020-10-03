# stdlib
import datetime
from typing import Dict

# 3rd party
import pytest

# this package
from octo_api.api import OctoAPI
from octo_api.consumption import Consumption
from octo_api.pagination import PaginatedResponse
from octo_api.products import DetailedProduct, Product, RegionalTariffs, Tariff, _parse_tariffs
from octo_api.utils import bst, gmt


def test_get_consumption(api: OctoAPI):
	consumption = api.get_consumption(
			mpan="2000024512368",
			serial_number="-------------",
			fuel="electricity",
			)

	assert isinstance(consumption, PaginatedResponse)
	assert len(consumption) == 2496
	assert consumption[0] == Consumption(
			consumption=0.313,
			interval_start="2020-10-03T00:00:00+01:00",
			interval_end="2020-10-03T00:30:00+01:00",
			)
	assert consumption[115] == Consumption(
			consumption=0.409,
			interval_start="2020-09-30T14:30:00+01:00",
			interval_end="2020-09-30T15:00:00+01:00",
			)

	assert consumption[115:116] == [
			Consumption(
					consumption=0.409,
					interval_start="2020-09-30T14:30:00+01:00",
					interval_end="2020-09-30T15:00:00+01:00",
					),
			Consumption(
					consumption=0.421,
					interval_start="2020-09-30T14:00:00+01:00",
					interval_end="2020-09-30T14:30:00+01:00",
					),
			]

	with pytest.raises(IndexError, match="index out of range"):
		consumption[2496]

	with pytest.raises(IndexError, match="index out of range"):
		consumption[2497]

	with pytest.raises(ValueError, match="'page_size' may not be greater than 25,000"):
		api.get_consumption(
				mpan="2000024512368", serial_number="-------------", fuel="electricity", page_size=10000000
				)


@pytest.mark.parametrize(
		"key, value",
		[
				("consumption", 1.234),
				("interval_start", "2020-09-29T14:30:00+01:00"),
				("interval_end", "2020-09-28T15:00:00+01:00"),
				]
		)
def test_consumption_equality(key, value):
	consumption = Consumption(
			consumption=0.409,
			interval_start=datetime.datetime(year=2020, month=9, day=30, hour=14, minute=30, second=0, tzinfo=bst),
			interval_end=datetime.datetime(year=2020, month=9, day=30, hour=15, minute=00, second=0, tzinfo=bst),
			)

	data = dict(
			consumption=0.409,
			interval_start="2020-09-30T14:30:00+01:00",
			interval_end="2020-09-30T15:00:00+01:00",
			)

	assert consumption == Consumption(**data)  # type: ignore

	data[key] = value
	assert consumption != Consumption(**data)  # type: ignore


def test_get_consumption_for_period(api: OctoAPI):
	consumption = api.get_consumption(
			mpan="2000024512368",
			serial_number="-------------",
			fuel="electricity",
			period_from=datetime.datetime(2020, 8, 3, 0, 0, 0, tzinfo=bst),
			period_to=datetime.datetime(2020, 9, 3, 0, 0, 0, tzinfo=bst),
			)

	assert isinstance(consumption, PaginatedResponse)
	assert len(consumption) == 1058
	assert consumption[0] == Consumption(
			consumption=0.263,
			interval_start="2020-09-03T01:00:00+01:00",
			interval_end="2020-09-03T01:30:00+01:00",
			)
	assert consumption[30] == Consumption(
			consumption=0.418,
			interval_start="2020-09-02T10:00:00+01:00",
			interval_end="2020-09-02T10:30:00+01:00",
			)


def test_get_consumption_reverse(api: OctoAPI):
	consumption = api.get_consumption(
			mpan="2000024512368", serial_number="-------------", fuel="electricity", reverse=True
			)

	assert len(consumption) == 2496

	for idx, val in enumerate(consumption):
		if idx == 117:
			break

	assert consumption[0] == Consumption(
			consumption=0,
			interval_start="2020-08-12T00:30:00+01:00",
			interval_end="2020-08-12T01:00:00+01:00",
			)
	assert consumption[115] == Consumption(
			consumption=0.295,
			interval_start="2020-08-14T10:00:00+01:00",
			interval_end="2020-08-14T10:30:00+01:00",
			)


def test_get_consumption_grouping(api: OctoAPI):
	consumption = api.get_consumption(
			mpan="2000024512368", serial_number="-------------", fuel="electricity", group_by="week"
			)

	assert len(consumption) == 8

	assert consumption[0] == Consumption(
			consumption=114.734,
			interval_start="2020-09-28T00:00:00+01:00",
			interval_end="2020-10-03T00:30:00+01:00",
			)
	assert consumption[5] == Consumption(
			consumption=185.26,
			interval_start="2020-08-24T00:00:00+01:00",
			interval_end="2020-08-31T00:00:00+01:00",
			)
