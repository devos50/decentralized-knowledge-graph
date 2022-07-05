import random
from asyncio import sleep
from binascii import unhexlify

from core.db.triplet import Triplet
from ipv8.community import Community

from dkg.core.payloads import TripletsMessage
from dkg.core.db.content_database import ContentDatabase
from dkg.core.db.knowledge_graph import KnowledgeGraph
from dkg.core.db.rules_database import RulesDatabase
from dkg.core.rule_execution_engine import RuleExecutionEngine
from dkg.core.settings import DKGSettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.types import Peer


class DKGCommunity(Community):
    community_id = unhexlify('d5889074c1e5b60423cdb6e9307ba0ca5695ead7')

    def __init__(self, *args, **kwargs):
        self.settings: DKGSettings = kwargs.pop("settings")
        super().__init__(*args, **kwargs)
        self.content_db = ContentDatabase()
        self.rules_db = RulesDatabase()
        self.knowledge_graph = KnowledgeGraph()
        self.rule_execution_engine: RuleExecutionEngine = RuleExecutionEngine(self.content_db, self.rules_db,
                                                                              self.knowledge_graph, self.my_peer.key)

        self.add_message_handler(TripletsMessage, self.on_triplet_message)

        self.logger.info("The DKG community started!")

    def start_kg_gossip(self):
        self.register_task("kg_gossip", self.kg_gossip_loop, interval=self.settings.edge_exchange_interval)

    async def kg_gossip_loop(self):
        while True:
            self.gossip_kg_edges()
            await sleep(self.settings.edge_exchange_interval)

    def gossip_kg_edges(self):
        random_peer = random.choice(self.get_peers())
        if not random_peer:
            self.logger.warning("No peer available to gossip DKG edges with!")
            return

        triplets = self.knowledge_graph.get_random_edges(limit=self.settings.edge_batch_size)
        if not triplets:
            return

        self.logger.info("Sending %d triplet(s) to peer %s", len(triplets), random_peer)
        triplet_payloads = [item.to_payload() for item in triplets]
        payload = TripletsMessage(triplet_payloads)
        packet = self.ezr_pack(TripletsMessage.msg_id, payload)
        self.endpoint.send(random_peer.address, packet)

    @lazy_wrapper(TripletsMessage)
    def on_triplet_message(self, _: Peer, payload: TripletsMessage):
        for triplet in payload.triplets:
            self.process_triplet(triplet)

    def process_triplet(self, triplet: Triplet):
        self.knowledge_graph.add_triplet(Triplet.from_payload(triplet))
        if self.content_db.has_content(triplet.head):  # We assume that the triplet head is always the content hash
            # We do have this content - add it to the verification queue
            self.rule_execution_engine.add_to_validation_queue(triplet)

    def start_rule_execution_engine(self):
        self.rule_execution_engine.start()

    async def unload(self):
        self.rule_execution_engine.shutdown()
