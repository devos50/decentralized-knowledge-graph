class SimulationSettings:

    def __init__(self):
        self.duration: int = 3600
        self.peers: int = 10
        self.torrents_per_user = 10
        self.data_filename = "torrents_1000.txt"
