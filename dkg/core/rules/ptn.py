from binascii import hexlify
from typing import Set, Tuple

from core.db.triplet import Triplet
from dkg.core.content import Content
from dkg.core.rules.rule import Rule

import PTN


class PTNRule(Rule):
    RULE_NAME = "PTN"

    def apply_rule(self, content: Content) -> Set[Triplet]:
        metadata = PTN.parse(content.data.decode())
        triplets = set()
        for relation, tail in metadata.items():
            if not tail:
                continue
            if relation == "excess":
                continue

            relation = Rule.convert_to_bytes(relation)

            # Some items can be a list and we have to add multiple triplets
            if isinstance(tail, list):
                for tail_item in tail:
                    triplets.add(Triplet(hexlify(content.identifier), relation, Rule.convert_to_bytes(tail_item)))
            else:
                triplets.add(Triplet(hexlify(content.identifier), relation, Rule.convert_to_bytes(tail)))
        return triplets
