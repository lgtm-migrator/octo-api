# stdlib
import json
import os
import pathlib
from typing import Callable
from urllib.parse import quote

# 3rd party
import pytest
from apeye.url import SlumberURL
from pytest_httpserver import HTTPServer  # type: ignore
from pytest_httpserver.pytest_plugin import Plugin, PluginHTTPServer, get_httpserver_listen_address  # type: ignore

# this package
import octo_api.api


@pytest.fixture(scope="session")
def httpserver_listen_address():
	return get_httpserver_listen_address()


@pytest.fixture(scope="session")
def httpserver(httpserver_listen_address):
	if Plugin.SERVER:
		Plugin.SERVER.clear()
		yield Plugin.SERVER
		return

	host, port = httpserver_listen_address
	if not host:
		host = HTTPServer.DEFAULT_LISTEN_HOST
	if not port:
		port = HTTPServer.DEFAULT_LISTEN_PORT

	server = PluginHTTPServer(host=host, port=port)
	server.start()
	yield server


responses = pathlib.Path(__file__).parent / "responses"


@pytest.fixture(scope="session")
def api(httpserver: HTTPServer):
	a = octo_api.api.OctoAPI("token")
	assert a.API_KEY.value == "token"

	def respond(url, **params):

		query_params = "&".join(
				f"{name}={quote(str(value)).replace('%20', '+')}" for name, value in params.items()
				)
		if not url.endswith("/"):
			url = f"{url}/"

		def deco(f: Callable) -> Callable:
			httpserver.expect_request(url, query_string=query_params).respond_with_json(f())
			return f

		return deco

	def respond_from_file(filename: pathlib.Path, url: str, **params):

		@respond(url, **params)
		def func():
			return json.loads(filename.read_text())

	def null_response(url: str, **params):

		@respond(url, **params)
		def func():
			return {"count": 0, "next": None, "previous": None, "results": []}

	def respond_404(url: str, **params):

		@respond(url, **params)
		def func():
			return {"detail": "Not found."}

	respond_404("/v1")

	respond_from_file(responses / "products_business_false.json", "/v1/products/", is_business=False)
	respond_from_file(responses / "products_green.json", "/v1/products/", is_green=True, is_business=False)
	respond_from_file(responses / "products_tracker.json", "/v1/products/", is_tracker=True, is_business=False)
	respond_from_file(
			responses / "products_tracker.json",
			"/v1/products/",
			is_variable=False,
			is_prepay=True,
			is_business=False
			)

	respond_from_file(responses / "products_VAR-17-01-11.json", "/v1/products/VAR-17-01-11")
	respond_from_file(
			responses / "standard_unit_rates.json",
			"/v1/products/VAR-17-01-11/electricity-tariffs/E-1R-VAR-17-01-11-A/standard-unit-rates",
			page_size=100
			)

	unit_rates_endpount = "/v1/products/AGILE-18-02-21/electricity-tariffs/E-1R-AGILE-18-02-21-C/standard-unit-rates"
	respond_from_file(responses / "agile_unit_rates.json", unit_rates_endpount, page_size=100)
	respond_from_file(responses / "agile_unit_rates.json", unit_rates_endpount, page=1, page_size=100)
	respond_from_file(responses / "agile_unit_rates_page2.json", unit_rates_endpount, page=2, page_size=100)

	httpserver.expect_request("/v1/electricity-meter-points/2000024512368/").respond_with_json({
			"gsp": "_H", "mpan": "2000024512368", "profile_class": 1
			})

	@respond("/v1/industry/grid-supply-points/", postcode="SW1A 1AA")
	@respond("/v1/industry/grid-supply-points/", postcode="SW1A1AA")
	def grid_supply_point():
		return {"count": 1, "next": None, "previous": None, "results": [{"group_id": "_C"}]}

	null_response("/v1/industry/grid-supply-points/", postcode=12345)

	# Invalid
	respond_404("/v1/electricity-meter-points/2000024512368/meters/12345/consumption/", postcode=12345)

	# Valid
	consumption_endpoint = "/v1/electricity-meter-points/2000024512368/meters/-------------/consumption"
	respond_from_file(responses / "consumption.json", consumption_endpoint, page_size=100)
	respond_from_file(responses / "consumption.json", consumption_endpoint, page=1, page_size=100)
	respond_from_file(responses / "consumption_page2.json", consumption_endpoint, page=2, page_size=100)

	respond_from_file(
			responses / "consumption_august.json",
			consumption_endpoint,
			period_from="2020-08-03T00:00:00+01:00",
			period_to="2020-09-03T00:00:00+01:00",
			page_size=100
			)
	respond_from_file(
			responses / "consumption_august.json",
			consumption_endpoint,
			period_from="2020-08-03T00:00:00+01:00",
			period_to="2020-09-03T00:00:00+01:00",
			page=1,
			page_size=100
			)

	respond_from_file(
			responses / "consumption_reversed.json",
			consumption_endpoint,
			page_size=100,
			order_by="period",
			)
	respond_from_file(
			responses / "consumption_reversed.json",
			consumption_endpoint,
			page=1,
			page_size=100,
			order_by="period",
			)
	respond_from_file(
			responses / "consumption_reversed_page2.json",
			consumption_endpoint,
			page=2,
			page_size=100,
			order_by="period",
			)

	respond_from_file(
			responses / "consumption_weekly.json",
			consumption_endpoint,
			page_size=100,
			group_by="week",
			)

	a.API_BASE = SlumberURL(httpserver.url_for("/v1"), auth=('', ''))

	return a


@pytest.fixture
def original_datadir(request):
	# Work around pycharm confusing datadir with test file.
	return pathlib.Path(os.path.splitext(request.module.__file__)[0] + "_")
