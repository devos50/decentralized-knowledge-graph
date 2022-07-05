from typing import List, Tuple

from ipv8.messaging.payload_dataclass import dataclass


@dataclass(msg_id=10)
class TripletsMessage:

    @dataclass
    class Triplet:
        head: bytes
        relation: bytes
        tail: bytes
        signatures: List[Tuple[bytes, bytes]]

    triplets: [Triplet]
