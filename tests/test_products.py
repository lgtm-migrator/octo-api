# stdlib
import json
from typing import Dict

# 3rd party
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from octo_api.api import OctoAPI
from octo_api.pagination import PaginatedResponse
from octo_api.products import DetailedProduct, Product, RegionalTariffs, Tariff, _parse_tariffs


def test_get_products(api: OctoAPI):
	assert isinstance(api.get_products(), PaginatedResponse)
	assert api.get_products()[0] == Product(
			code="1201",
			direction="IMPORT",
			full_name="Affect Standard Tariff",
			display_name="Affect Standard Tariff",
			description="Affect Standard Tariff",
			is_variable=True,
			is_green=False,
			is_tracker=False,
			is_prepay=False,
			is_business=False,
			is_restricted=False,
			term=None,
			available_from="2016-01-01T00:00:00Z",
			available_to=None,
			brand="AFFECT_ENERGY",
			links=[{
					"href": "https://api.octopus.energy/v1/products/1201/",
					"rel": "self",
					"method": "GET",
					}]
			)

	assert api.get_products(is_green=True)[0] == Product(
			code="AGILE-18-02-21",
			direction="IMPORT",
			full_name="Agile Octopus February 2018",
			display_name="Agile Octopus",
			description='',
			is_variable=True,
			is_green=True,
			is_tracker=False,
			is_prepay=False,
			is_business=False,
			is_restricted=False,
			term=12,
			available_from="2017-01-01T00:00:00Z",
			available_to=None,
			brand="OCTOPUS_ENERGY",
			links=[{
					"href": "https://api.octopus.energy/v1/products/AGILE-18-02-21/",
					"rel": "self",
					"method": "GET",
					}]
			)

	assert not api.get_products(is_tracker=True)
	assert not api.get_products(is_prepay=True, is_variable=False)


def test_get_product_info(api, datadir):
	dual_register_electricity_tariffs = json.loads((datadir / "get_product_info_dual_register_tariffs.json").read_text())
	single_register_gas_tariffs = json.loads((datadir / "get_product_info_single_register_gas_tariffs.json").read_text())
	sample_quotes = json.loads((datadir / "get_product_info_sample_quotes.json").read_text())
	single_register_electricity_tariffs = json.loads((datadir / "single_register_electricity_tariffs.json").read_text())

	product = DetailedProduct(
			code="VAR-17-01-11",
			full_name="Flexible Octopus January 2017 v1",
			display_name="Flexible Octopus",
			description="This variable tariff always offers great value - driven by our belief that prices should be fair for the long term, not just a fixed term. We aim for 50% renewable electricity on this tariff.",
			is_variable=True,
			is_green=False,
			is_tracker=False,
			is_prepay=False,
			is_business=False,
			is_restricted=False,
			term=None,
			available_from="2017-01-11T10:00:00Z",
			available_to="2018-02-15T00:00:00Z",
			tariffs_active_at="2020-09-27T21:12:33.228811Z",
			single_register_electricity_tariffs=single_register_electricity_tariffs,
			dual_register_electricity_tariffs=dual_register_electricity_tariffs,
			single_register_gas_tariffs=single_register_gas_tariffs,
			sample_quotes=sample_quotes,
			sample_consumption={
					"electricity_single_rate": {"electricity_standard": 2900},
					"electricity_dual_rate": {"electricity_day": 2436, "electricity_night": 1764},
					"dual_fuel_single_rate": {"electricity_standard": 2900, "gas_standard": 12000},
					"dual_fuel_dual_rate": {
							"electricity_day": 2436, "electricity_night": 1764, "gas_standard": 12000
							}
					},
			brand="OCTOPUS_ENERGY",
			links=[{
					"href": "https://api.octopus.energy/v1/products/VAR-17-01-11/",
					"rel": "self",
					"method": "GET",
					}]
			)
	assert api.get_product_info("VAR-17-01-11") == product


def test_parse_tariffs(file_regression: FileRegressionFixture, datadir):
	single_register_electricity_tariffs = json.loads((datadir / "single_register_electricity_tariffs.json").read_text())

	assert isinstance(_parse_tariffs(single_register_electricity_tariffs), RegionalTariffs)
	assert str(_parse_tariffs(single_register_electricity_tariffs)) == "RegionalTariffs(['direct_debit_monthly'])"

	file_regression.check(
			repr(_parse_tariffs(single_register_electricity_tariffs)), encoding="UTF-8", extension=".json"
			)

	tariffs: Dict[str, Dict[str, Tariff]] = {}

	for gsp, payment_methods in single_register_electricity_tariffs.items():
		tariffs[gsp] = {}

		for method, tariff in payment_methods.items():
			tariffs[gsp][method] = Tariff(**tariff)

	assert repr(_parse_tariffs(single_register_electricity_tariffs)) == str(tariffs)
	assert repr(_parse_tariffs(single_register_electricity_tariffs)) == repr(tariffs)
