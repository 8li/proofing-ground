import json
import numpy as np
import pandas as pd
from balances import Balances, random_value, random_int
from parse_config import ConfigDict

# simulation object

# default configuration parameters
try:
    config = ConfigDict().parse()
except OSError:
    print("Can't import parameters")

DEFAULT_KWARGS = { 'n_sims' : int(config['default']['n_sims']),
                   'n_blocks' : int(config['default']['n_blocks']),
                   'n_tx_max' : int(config['default']['n_tx_max']),
                   'tx_max' : float(config['default']['tx_max'])}

class Simulation:

    def __init__(self, balances=None, **kwargs):

        if balances:
            self.balances = balances
        else:
            self.balances = Balances(**kwargs)

        self.n_sims = int(kwargs.get('n_sims', DEFAULT_KWARGS['n_sims']))
        self.n_blocks = int(kwargs.get('n_blocks', DEFAULT_KWARGS['n_blocks']))
        self.n_tx_max = int(kwargs.get('n_tx_max', DEFAULT_KWARGS['n_tx_max']))
        self.tx_max = float(kwargs.get('tx_max', DEFAULT_KWARGS['tx_max']))
        self.n_users = self.balances.n_users

        self.tx_data = pd.DataFrame()
        self.gini = np.empty(self.n_sims)

    def params(self):
        return { 'n_sims' : self.n_sims,
                 'n_blocks' : self.n_blocks,
                 'n_tx_max' : self.n_tx_max,
                 'tx_max' : self.tx_max }

    def simulate(self):
        for sim in range(self.n_sims):
            # print(sim)
            for block in range(self.n_blocks):

                # transactions per block
                n_tx = random_int(self.n_tx_max)

                for _ in range(n_tx):
                    # select a sender and a receiver
                    from_ind = to_ind = random_int(self.n_users)
                    if self.balances.greed_factor:
                        while from_ind in self.balances.greedy_list:
                            from_ind = random_int(self.n_users)
                    while from_ind == to_ind:
                        to_ind = random_int(self.n_users)

                    # transaction amount
                    val = random_value(self.tx_max)

                    self.balances.transaction(from_ind, to_ind, val)

                # reward a miner
                to_ind = np.random.choice(self.balances.miner_list)
                self.balances.transaction(None, to_ind, self.balances.reward)

                # record balance state
                if block % 1000 == 0:
                    self.tx_data = self.tx_data.append(self.balances.data['values'])

            # record gini coefficient
            self.gini[sim] = self.balances.gini()

        return self.tx_data, self.gini