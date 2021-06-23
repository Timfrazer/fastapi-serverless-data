from faker import Faker
from typing import List,Dict,Optional,Union,Any
from pydantic import BaseModel


FAKE = Faker(locale="en_US")


class NestedRow(BaseModel):
	visitor_id: Optional[int] = None
	campaign: Optional[str] = None
	date: Optional[str] = None
	# record, not repeated
	totals: Optional[Dict[str, Any]] = None
	# record, repeated
	custom_dimensions: Optional[List[Dict[str, Any]]] = None


def value_or_nothing(fake_value: Any) -> Union[Any, None]:
	return FAKE.random_choices(elements=[None, fake_value], length=1)[0]


synthetic_output = NestedRow(
	visitor_id=str(FAKE.pyint()),
	campaign=value_or_nothing(FAKE.catch_phrase().lower().replace(" ", "-")),
	date=value_or_nothing(FAKE.date_this_month()),
	totals={
		"visits": value_or_nothing(FAKE.pyint()),
		"hits": value_or_nothing(FAKE.pyint()),
	},
	custom_dimensions=[
		{"index": FAKE.pyint(), "value": FAKE.word()}
		for _ in range(FAKE.pyint(min_value=0, max_value=50))
	],)