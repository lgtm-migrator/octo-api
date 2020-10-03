# stdlib
import sys
from typing import Any, Dict, NamedTuple, Optional, Union

# 3rd party
from enum_tools import StrEnum

__all__ = ["from_iso_zulu", "RateType", "Region", "MeterPointDetails"]

# stdlib
from datetime import datetime, timedelta, timezone

if sys.version_info[:2] < (3, 7):
	# 3rd party
	from backports.datetime_fromisoformat import MonkeyPatch
	MonkeyPatch.patch_fromisoformat()

#
# def format_datetime(dt: datetime) -> str:
# 	"""
# 	Format a :class:`datetime.datetime` object to a string in
# 	`ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ format.
#
# 	:param dt:
# 	"""
#
# 	return dt.strftime("%Y-%m-%dT:")


def from_iso_zulu(the_datetime: Union[str, datetime, None]) -> Optional[datetime]:
	"""
	Constructs a :class:`datetime.datetime` object from an
	`ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ format string.

	This function understands the character ``Z`` as meaning Zulu time (GMT/UTC).

	:param the_datetime:
	"""

	if the_datetime is None:
		return the_datetime
	elif isinstance(the_datetime, datetime):
		return the_datetime
	else:
		return datetime.fromisoformat(  # type: ignore
				the_datetime.replace("Z", "+00:00"),
				)


class RateType(StrEnum):
	"""
	Enumeration of different rate types.
	"""

	StandingCharge = "standing-charges"
	StandardUnitRate = "standard-unit-rates"
	DayUnitRate = "day-unit-rates"
	NightUnitRate = "night-unit-rates"


class Region(StrEnum):
	"""
	Enumeration of different electricity supply regions.
	"""

	Eastern = "_A"  # Eastern Electricity
	EastMidlands = "_B"  # East Midlands Electricity
	London = "_C"  # London Electricity
	Merseyside = "_D"  # Merseyside and North Wales Electricity Board
	NorthWales = "_D"  # Merseyside and North Wales Electricity Board
	Midlands = "_E"  # Midlands Electricity
	NorthEastern = "_F"  # North Eastern Electricity Board
	NorthWestern = "_G"  # North Western Electricity Board
	Southern = "_H"  # Southern Electric
	SouthEastern = "_J"  # South Eastern Electricity Board
	SouthWales = "_K"  # South Wales Electricity
	SouthWestern = "_L"  # South Western Electricity
	Yorkshire = "_M"  # Yorkshire Electricity
	SouthScotland = "_N"  # South of Scotland Electricity Board
	NorthScotland = "_P"  # North of Scotland Hydro Board


# @prettify_docstrings
class MeterPointDetails(NamedTuple):
	"""
	Information about a meter point.

	:param mpan: The meter point access number.
	:param gsp: The grid supply point/region that the meter point is located in.
	:param profile_class: The profile class of the meter point.

	* **Profile Class 1** –- Domestic Unrestricted Customers
	* **Profile Class 2** –- Domestic Economy 7 Customers
	* **Profile Class 3** –- Non-Domestic Unrestricted Customers
	* **Profile Class 4** –- Non-Domestic Economy 7 Customers
	* **Profile Class 5** –- Non-Domestic Maximum Demand (MD) Customers with a Peak Load Factor (LF) of less than 20%
	* **Profile Class 6** –- Non-Domestic Maximum Demand Customers with a Peak Load Factor between 20% and 30%
	* **Profile Class 7** –- Non-Domestic Maximum Demand Customers with a Peak Load Factor between 30% and 40%
	* **Profile Class 8** –- Non-Domestic Maximum Demand Customers with a Peak Load Factor over 40%

	.. seealso:: `Load Profiles and their use in Electricity Settlement <https://www.elexon.co.uk/documents/training-guidance/bsc-guidance-notes/load-profiles/>`_ by Elexon

	Information from https://www.elexon.co.uk/knowledgebase/profile-classes/

	|
	"""

	mpan: str
	gsp: Region
	profile_class: int

	@classmethod
	def _from_dict(cls, octopus_dict: Dict[str, Any]) -> "MeterPointDetails":
		return MeterPointDetails(
				mpan=str(octopus_dict["mpan"]),
				gsp=Region(octopus_dict["gsp"]),
				profile_class=int(octopus_dict["profile_class"]),
				)


#: The British Summer Time timezone (UTC+1).
bst = timezone(timedelta(seconds=3600))

#: The Greenwich Mean Time timezone (aka UTC).
gmt = timezone.utc

utc = gmt
