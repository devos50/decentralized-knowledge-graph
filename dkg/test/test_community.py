from dkg.core.settings import DKGSettings
from dkg.core.community import DKGCommunity

from ipv8.test.base import TestBase
from ipv8.test.mocking.ipv8 import MockIPv8


class TestDKGCommunity(TestBase):
    NUM_NODES = 2

    def create_node(self, *args, **kwargs):
        return MockIPv8("curve25519", self.overlay_class, *args, **kwargs)

    def setUp(self):
        super().setUp()
        self.initialize(DKGCommunity, self.NUM_NODES, settings=DKGSettings())

        for node in self.nodes:
            node.overlay.start_rule_execution_engine()

    async def test_kg_gossip(self):
        self.nodes[0].overlay.gossip_kg_edges()
        await self.deliver_messages()
