from asyncio import ensure_future

from dkg.core.settings import DKGSettings

from ipv8.configuration import ConfigBuilder

from simulations.settings import SimulationSettings
from simulations.simulation import DKGSimulation


class BasicDKGSimulation(DKGSimulation):

    def get_ipv8_builder(self, peer_id: int) -> ConfigBuilder:
        builder = super().get_ipv8_builder(peer_id)
        settings = DKGSettings()
        builder.add_overlay("DKGCommunity", "my peer", [], [], {"settings": settings}, [])
        return builder


if __name__ == "__main__":
    settings = SimulationSettings()
    simulation = BasicDKGSimulation(settings)
    ensure_future(simulation.run())

    simulation.loop.run_forever()
