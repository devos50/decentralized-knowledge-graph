import asyncio
import logging
import os
import random
import shutil
import time
from binascii import unhexlify
from typing import List, Tuple

from dkg.core.content import Content
from dkg.core.community import DKGCommunity
from dkg.core.rules.ptn import PTNRule

from ipv8.configuration import ConfigBuilder
from ipv8_service import IPv8

from simulation.discrete_loop import DiscreteLoop
from simulation.simulation_endpoint import SimulationEndpoint

from simulations.settings import SimulationSettings


class DKGSimulation:

    def __init__(self, settings: SimulationSettings) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = settings
        self.nodes = []
        self.data_dir = os.path.join("data", "n_%d" % self.settings.peers)

        self.loop = DiscreteLoop()
        asyncio.set_event_loop(self.loop)

    def get_ipv8_builder(self, peer_id: int) -> ConfigBuilder:
        builder = ConfigBuilder().clear_keys().clear_overlays()
        builder.add_key("my peer", "curve25519", os.path.join(self.data_dir, f"ec{peer_id}.pem"))
        return builder

    def setup_directories(self) -> None:
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)
        os.makedirs(self.data_dir, exist_ok=True)

    def setup_logger(self) -> None:
        root = logging.getLogger()
        root.handlers[0].setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
        root.setLevel(logging.INFO)

    async def start_ipv8_nodes(self) -> None:
        for peer_id in range(1, self.settings.peers + 1):
            if peer_id % 100 == 0:
                print("Created %d peers..." % peer_id)
            endpoint = SimulationEndpoint()
            instance = IPv8(self.get_ipv8_builder(peer_id).finalize(), endpoint_override=endpoint,
                            extra_communities={'DKGCommunity': DKGCommunity})
            await instance.start()
            self.nodes.append(instance)

    def ipv8_discover_peers(self) -> None:
        for node_a in self.nodes:
            for node_b in self.nodes:
                if node_a == node_b:
                    continue

                node_a.overlays[0].walk_to(node_b.endpoint.wan_address)
        print("IPv8 peer discovery complete")

    def load_data(self) -> None:
        # TODO assume torrent dataset
        torrents: List[Tuple[bytes, bytes]] = []
        with open(os.path.join("data", self.settings.data_filename), "r") as data_file:
            for line in data_file.readlines():
                parts = line.strip().split("\t")
                infohash = unhexlify(parts[0])
                torrent_title = parts[1].encode()
                torrents.append((infohash, torrent_title))

        for ind, node in enumerate(self.nodes):
            torrents_for_node = random.sample(torrents, self.settings.torrents_per_user)
            for torrent in torrents_for_node:
                content = Content(*torrent)
                node.overlays[0].content_db.add_content(content)

            self.logger.info("Node %d has %d torrents", ind, node.overlays[0].content_db.size())

    def on_ipv8_ready(self) -> None:
        """
        This method is called when IPv8 is started and peer discovery is finished.
        """
        pass

    def on_simulation_finished(self) -> None:
        """
        This method is called when the simulations are finished.
        """
        for ind, node in enumerate(self.nodes):
            print("Node %d has %d edges" % (ind, node.overlays[0].knowledge_graph.get_num_edges()))
            print("Node %d - outgoing bytes: %d" % (ind, node.overlays[0].endpoint.bytes_up))

    async def start_simulation(self) -> None:
        print("Starting simulation with %d peers..." % self.settings.peers)
        ptn_rule = PTNRule()
        for node in self.nodes:
            node.overlays[0].rules_db.add_rule(ptn_rule)
            node.overlays[0].start_rule_execution_engine()
            node.overlays[0].start_kg_gossip()

        start_time = time.time()
        await asyncio.sleep(self.settings.duration)
        print("Simulation took %f seconds" % (time.time() - start_time))

        self.loop.stop()

    async def run(self) -> None:
        self.setup_directories()
        await self.start_ipv8_nodes()
        self.setup_logger()
        self.ipv8_discover_peers()
        self.on_ipv8_ready()
        self.load_data()
        await self.start_simulation()
        self.on_simulation_finished()
