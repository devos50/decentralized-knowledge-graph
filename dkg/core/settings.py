from dataclasses import dataclass


@dataclass
class DKGSettings:
    edge_exchange_interval = 5
    edge_batch_size = 1
