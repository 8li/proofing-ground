import os
import numpy as np
import pandas as pd
import binascii, hashlib, base58
from parse_config import ConfigDict

# balance sheet object and functions

# default configuration parameters
try:
    config = ConfigDict().parse()
except OSError:
    print("Can't import parameters")

DEFAULT_KWARGS = { 'n_users' : int(config['default']['n_users']),
                   'init_issue' : config['default']['init_issue'],
                   'reward_dist' : config['default']['reward_dist'],
                   'reward' : config['default']['reward'] }


def generate_random_key():
    # inspiration: https://www.reddit.com/r/Bitcoin/comments/7tzq3w/generate_your_own_private_key_5_lines_of_python/
    # inspiration: https://codereview.stackexchange.com/questions/185106/bitcoin-wallet-address-and-private-key-generator

    fullkey = "80" + binascii.hexlify(os.urandom(32)).decode()
    sha256a = hashlib.sha256(binascii.unhexlify(fullkey)).hexdigest()
    sha256b = hashlib.sha256(binascii.unhexlify(sha256a)).hexdigest()
    return base58.b58encode(binascii.unhexlify(fullkey + sha256b[:8]))


def generate_random_value(max_val):
    return max_val * np.random.random()


class Balances:
    def __init__(self, **kwargs):

        self.n_users = int(kwargs.get('n_users', DEFAULT_KWARGS['n_users']))
        self.init_issue = kwargs.get('init_issue', DEFAULT_KWARGS['init_issue'])
        self.reward_dist = kwargs.get('reward_dist', DEFAULT_KWARGS['reward_dist'])
        self.reward = float(kwargs.get('reward', DEFAULT_KWARGS['reward']))

        if self.init_issue:
            self.init_issue_max = float(kwargs['init_issue_max'])
            self.init_issue_perc = float(kwargs['init_issue_perc'])

        # generate set of addresses
        self.keys = [ generate_random_key().decode('utf-8')
                      for _ in range(self.n_users) ]

        # generate initial balance values
        if self.init_issue:
            self.init_values = [ generate_random_value(self.init_issue_max)
                                 for i in range(self.n_users)]
        else:
            self.init_values = [0.0] * self.n_users

        self.data = pd.DataFrame(data = { 'address': self.keys,
                                          'values': self.init_values })

    def transaction(self, from_ind, to_ind, val):
        self.data.at[from_ind, 'values'] -= val
        self.data.at[to_ind, 'values'] += val


    def gini(self):
        vals = self.data['values'].values
        zero_area = 1e-100

        if np.amin(vals) < 0:
            vals -= np.amin(vals)

        vals = np.sort(vals)

        n = len(vals)
        total = np.sum(vals)

        equality_area = total * n / 2. or zero_area
        lorenz_area = np.sum(np.cumsum(vals) - vals / 2.) or zero_area

        return (equality_area - lorenz_area) / equality_area