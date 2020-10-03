#!/usr/bin/env python3
#
#  products.py
"""
Class to model products and tariffs.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, TypeVar

# 3rd party
import attr
from attr_utils.pprinter import pretty_repr
from attr_utils.serialise import serde
from domdf_python_tools.doctools import prettify_docstrings

# this package
from octo_api.utils import from_iso_zulu

__all__ = ["_term_converter", "BaseProduct", "Product", "_parse_tariffs", "DetailedProduct", "Tariff", "RateInfo"]


def _term_converter(term: Optional[int]) -> Optional[int]:
	"""
	Converter function for ``term`` in :class:`~.BaseProduct``.

	:param term: The number of months that a product lasts for if it is fixed length.
	"""

	if term is None:
		return None
	else:
		return int(term)


def _links_converter(iterable: Iterable[MutableMapping[str, Any]]) -> List[MutableMapping[str, Any]]:
	return list(iterable)


@serde
@pretty_repr
@attr.s(slots=True, frozen=True)
class BaseProduct:
	"""
	Represents an Octopus Energy product.
	"""

	#: The date from which the product is available.
	available_from: Optional[datetime] = attr.ib(converter=from_iso_zulu)

	#: The date until which the product is available.
	available_to: Optional[datetime] = attr.ib(converter=from_iso_zulu)

	#: The brand under which the product is sold.
	brand: str = attr.ib(converter=str)

	#: The code of the product.
	code: str = attr.ib(converter=str)

	#: A description of the product.
	description: str = attr.ib(converter=str)

	#: The display name of the product.
	display_name: str = attr.ib(converter=str)

	#: The name of the product.
	full_name: str = attr.ib(converter=str)

	#: Whether the product is for businesses.
	is_business: bool = attr.ib(converter=bool)

	#: Whether the product is green.
	is_green: bool = attr.ib(converter=bool)

	#: Whether the product is prepay.
	is_prepay: bool = attr.ib(converter=bool)

	#: Whether the product is restricted.
	is_restricted: bool = attr.ib(converter=bool)

	#: Whether the product tracks the wholesale electricity rate.
	is_tracker: bool = attr.ib(converter=bool)

	#: Whether the product has a variable tariff.
	is_variable: bool = attr.ib(converter=bool)

	#: Links associated with this product.
	links: List[MutableMapping[str, Any]] = attr.ib(converter=_links_converter)

	#: The number of months that a product lasts for if it is fixed length.
	term: Optional[int] = attr.ib(converter=_term_converter)


@attr.s(slots=True, frozen=True)
class Product(BaseProduct):
	"""
	Represents an Octopus Energy product.
	"""

	#: The direction of the product (supply to the customer or supply to the grid).
	direction: str = attr.ib(converter=str)


def _parse_tariffs(tariffs_dict: Dict[str, Dict[str, Dict[str, Any]]]) -> "RegionalTariffs":
	"""
	Parse tariff data for a :class:`~.DetailedProduct`.

	:param tariffs_dict:
	"""

	tariffs: RegionalTariffs = RegionalTariffs()

	for gsp, payment_methods in tariffs_dict.items():
		tariffs[gsp] = {}

		for method, tariff in payment_methods.items():
			tariffs[gsp][method] = Tariff(**tariff)

	return tariffs


@serde
@pretty_repr
@attr.s(slots=True, frozen=True)
class DetailedProduct(BaseProduct):
	"""
	Represents an Octopus Energy product, with detailed tariff information.

	Each ``*_tariffs`` object will have up to 14 keys; one for each GSP.
	For each GSP the applicable tariffs are listed under their associated payment method, e.g. direct_debit_monthly.

	* The ``standard_unit_rate_*`` values are listed in p/kWh (pence per kilowatt hour).
	* The ``standing_charge_*`` values are listed in p/day (pence per day).
	* The ``annual_cost_*`` values are listed in p (pence).
	"""
	# 	Historical charges can be browsed using the URLs contained under the key links.

	#:
	tariffs_active_at: Optional[datetime] = attr.ib(converter=from_iso_zulu)

	#: Mapping of GSPs to applicable tariffs for each payment method, e.g. direct_debit_monthly.
	single_register_electricity_tariffs: Dict = attr.ib(converter=_parse_tariffs)

	#: Mapping of GSPs to applicable tariffs for each payment method, e.g. direct_debit_monthly.
	dual_register_electricity_tariffs: Dict = attr.ib(converter=_parse_tariffs)

	#: Mapping of GSPs to applicable tariffs for each payment method, e.g. direct_debit_monthly.
	single_register_gas_tariffs: Dict = attr.ib(converter=_parse_tariffs)

	#:
	sample_quotes: Dict = attr.ib()

	#:
	sample_consumption: Dict = attr.ib()


@serde
@pretty_repr
@attr.s(slots=True, frozen=True)
class Tariff:
	"""
	Represents a tariff for a product.
	"""

	#: The tariff code.
	code: str = attr.ib(converter=str)

	#: In p/day (pence per day)
	standing_charge_exc_vat: float = attr.ib(converter=float)

	#: In p/day (pence per day)
	standing_charge_inc_vat: float = attr.ib(converter=float)

	online_discount_exc_vat: int = attr.ib(converter=int)
	online_discount_inc_vat: int = attr.ib(converter=int)
	dual_fuel_discount_exc_vat: int = attr.ib(converter=int)
	dual_fuel_discount_inc_vat: int = attr.ib(converter=int)
	exit_fees_exc_vat: int = attr.ib(converter=int)
	exit_fees_inc_vat: int = attr.ib(converter=int)
	links: List[Dict[str, Any]] = attr.ib(converter=list)

	#: In p/kWh (pence per kilowatt hour)
	standard_unit_rate_exc_vat: Optional[float] = attr.ib(default=None)

	#: In p/kWh (pence per kilowatt hour)
	standard_unit_rate_inc_vat: Optional[float] = attr.ib(default=None)

	#: In p/kWh (pence per kilowatt hour)
	day_unit_rate_exc_vat: Optional[float] = attr.ib(default=None)

	#: In p/kWh (pence per kilowatt hour)
	day_unit_rate_inc_vat: Optional[float] = attr.ib(default=None)

	#: In p/kWh (pence per kilowatt hour)
	night_unit_rate_exc_vat: Optional[float] = attr.ib(default=None)

	#: In p/kWh (pence per kilowatt hour)
	night_unit_rate_inc_vat: Optional[float] = attr.ib(default=None)


@serde
@pretty_repr
@attr.s(slots=True, frozen=True)
class RateInfo:
	"""
	Represents the unit rate of a tariff at a particular period in time.
	"""

	#: In p/kWh (pence per kilowatt hour)
	value_exc_vat: float = attr.ib(converter=float)

	#: In p/kWh (pence per kilowatt hour)
	value_inc_vat: float = attr.ib(converter=float)

	#: The date and time from which this rate is in effect.
	valid_from: datetime = attr.ib(converter=from_iso_zulu)

	#: The date and time until which this rate is in effect, or :py:obj:`None` if this rate continues in perpetuity.
	valid_to: Optional[datetime] = attr.ib(converter=from_iso_zulu)


@prettify_docstrings
class RegionalTariffs(Dict[str, Dict[str, Tariff]]):
	r"""
	Mapping of GSP regions to a mapping of payment methods to :class:`Tariffs <.Tariff>`.

	| **Key Type:** :class:`str`
	| **Value Type:** :class:`~typing.Dict`\[:class:`str`\,  :class:`~.Tariff`\]
	"""

	def __str__(self) -> str:
		return super().__repr__()

	def __repr__(self) -> str:
		return f"{self.__class__.__name__}([{', '.join(self.keys())}])"
