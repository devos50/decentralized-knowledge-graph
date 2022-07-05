from binascii import hexlify
from typing import Set

from dkg.core.content import Content
from dkg.core.rules.rule import Rule
from dkg.core.db.triplet import Triplet


class DummyRule(Rule):
    """
    A dummy rule that generates fixed edges. Useful for testing.
    """
    RULE_NAME = "DUMMY"

    def apply_rule(self, content: Content) -> Set[Triplet]:
        return {Triplet(hexlify(content.identifier), b"a", b"b")}
