import hashlib
from typing import List, Tuple

from core.payloads import TripletsMessage


class Triplet:

    def __init__(self, head: bytes, relation: bytes, tail: bytes):
        self.head: bytes = head
        self.relation: bytes = relation
        self.tail: bytes = tail
        self.signatures: List[Tuple[bytes, bytes]] = []

    def add_signature(self, public_key: bytes, signature: bytes) -> None:
        self.signatures.append((public_key, signature))

    def to_payload(self) -> TripletsMessage.Triplet:
        payload = TripletsMessage.Triplet(self.head, self.relation, self.tail, self.signatures)
        return payload

    @staticmethod
    def from_payload(payload: TripletsMessage.Triplet):
        triplet = Triplet(payload.head, payload.relation, payload.tail)
        triplet.signatures = payload.signatures
        return triplet

    def get_hash(self) -> bytes:
        m = hashlib.md5()
        m.update(b"%s" % self.head)
        m.update(b"%s" % self.relation)
        m.update(b"%s" % self.tail)
        return m.digest()
