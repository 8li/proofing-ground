#from balances import Balances
import json
import numpy as np
import pandas as pd
from balances import generate_random_value
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

    def __init__(self, balances, **kwargs):

        self.balances = balances

        self.n_sims = int(kwargs.get('n_sims', DEFAULT_KWARGS['n_sims']))
        self.n_blocks = int(kwargs.get('n_blocks', DEFAULT_KWARGS['n_blocks']))
        self.n_tx_max = int(kwargs.get('n_tx_max', DEFAULT_KWARGS['n_tx_max']))
        self.tx_max = float(kwargs.get('tx_max', DEFAULT_KWARGS['tx_max']))
        self.n_users = self.balances.n_users

        self.tx_data = pd.DataFrame()
        self.gini_data = np.empty(self.n_sims)

        print(json.dumps(kwargs, indent=2))


    def simulate(self):
        for sim in range(self.n_sims):
            for block in range(self.n_blocks):

                n_tx = np.random.randint(0, self.n_tx_max)

                for _ in range(n_tx):
                    to_ind = from_ind = np.random.randint(0, self.n_users)
                    while from_ind == to_ind:
                        from_ind = np.random.randint(0, self.n_users)

                    val = generate_random_value(self.tx_max)

                    self.balances.transaction(to_ind, from_ind, val)

                #self.txdata = self.txdata.append(self.balances.data['values'], ignore_index=True)

            #self.gini.append(self.balances.gini())
            self.gini_data[sim] = self.balances.gini()


        return self.gini_data