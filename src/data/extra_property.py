import dataclasses
import datetime
from collections import defaultdict
from re import Pattern
from typing import Literal, Union

import pywikibot

from ..constants import retrieved_prop, site, url_prop
from ..pywikibot_stub_types import WikidataReference


@dataclasses.dataclass
class ExtraQualifier:
    claim: pywikibot.Claim
    skip_if_conflicting_exists: bool = False
    skip_if_conflicting_language_exists: bool = False
    reference_only: bool = False


@dataclasses.dataclass
class ExtraReference:
    match_property_values: dict[str, pywikibot.Claim] = dataclasses.field(
        default_factory=dict
    )
    url_match_pattern: Pattern[Union[str], None] = None
    new_reference_props: dict[str, pywikibot.Claim] = dataclasses.field(
        default_factory=dict
    )
    retrieved: dataclasses.InitVar[Union[pywikibot.WbTime, Literal[False], None]] = None

    def __post_init__(self, retrieved: Union[pywikibot.WbTime, Literal[False], None]):
        if retrieved is None:
            now = pywikibot.Timestamp.now(tz=datetime.timezone.utc)
            retrieved = pywikibot.WbTime(year=now.year, month=now.month, day=now.day)
        if retrieved:
            retrieved_claim = pywikibot.Claim(site, retrieved_prop)
            retrieved_claim.setTarget(retrieved)
            self.new_reference_props[retrieved_prop] = retrieved_claim

    def is_compatible_reference(self, reference: WikidataReference) -> bool:
        if self.url_match_pattern and url_prop in reference:
            for claim in reference[url_prop]:
                if self.url_match_pattern.match(claim.getTarget()):  # type: ignore
                    return True
        for prop, claim in self.match_property_values.items():
            if prop not in reference:
                continue
            for ref_claim in reference[prop]:
                if ref_claim.getTarget() == claim.getTarget():
                    return True
        return False


@dataclasses.dataclass
class ExtraProperty:
    claim: pywikibot.Claim
    skip_if_conflicting_exists: bool = False
    skip_if_conflicting_language_exists: bool = False
    reference_only: bool = False
    qualifiers: defaultdict[str, list[ExtraQualifier]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )
    extra_references: list[ExtraReference] = dataclasses.field(default_factory=list)
