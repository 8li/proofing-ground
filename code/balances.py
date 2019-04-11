import os
import sys
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
                   'n_miners_max' : int(config['default']['n_miners_max']),
                   'init_issue' : config['default']['init_issue'],
                   'reward_dist' : config['default']['reward_dist'],
                   'reward' : config['default']['reward'] }

def random_key():
    # inspiration: https://www.reddit.com/r/Bitcoin/comments/7tzq3w/generate_your_own_private_key_5_lines_of_python/
    # inspiration: https://codereview.stackexchange.com/questions/185106/bitcoin-wallet-address-and-private-key-generator

    fullkey = "80" + binascii.hexlify(os.urandom(32)).decode()
    sha256a = hashlib.sha256(binascii.unhexlify(fullkey)).hexdigest()
    sha256b = hashlib.sha256(binascii.unhexlify(sha256a)).hexdigest()
    return base58.b58encode(binascii.unhexlify(fullkey + sha256b[:8]))

def random_value(max_val):
    return max_val * np.random.random()

def random_int(max_val):
    return np.random.randint(0, max_val)


class Balances:
    def __init__(self, **kwargs):

        self.n_users = int(kwargs.get('n_users', DEFAULT_KWARGS['n_users']))
        self.n_miners_max = int(kwargs.get('n_miners_max', DEFAULT_KWARGS['n_miners_max']))
        self.init_issue = kwargs.get('init_issue', DEFAULT_KWARGS['init_issue'])
        self.reward_dist = kwargs.get('reward_dist', DEFAULT_KWARGS['reward_dist'])
        self.reward = float(kwargs.get('reward', DEFAULT_KWARGS['reward']))

        if self.init_issue:
            self.init_issue_total = float(kwargs['init_issue_total'])
            self.init_issue_max = float(kwargs['init_issue_max'])
            self.init_issue_users = int(kwargs['init_issue_users'])

            if self.init_issue_max * self.init_issue_users < self.init_issue_total or \
                    self.init_issue_users > self.n_users:
                print("Initial issuance cannot be fulfilled by current parameters")
                sys.exit()

        # generate set of addresses
        self.keys = [random_key().decode('utf-8')
                     for _ in range(self.n_users)]

        # generate initial balance values
        self.init_values = np.zeros(self.n_users, dtype=float)

        if self.init_issue:
            issue_total = 0.0
            issue_remain = self.init_issue_total

            for i in range(self.init_issue_users):
                # select a random user with zero balance
                n = random_int(self.n_users)
                while self.init_values[n]:
                    n = random_int(self.n_users)

                # determine how much to issue
                issue_remain_split = issue_remain / ( self.init_issue_users - i )
                if issue_remain_split > self.init_issue_max:
                    issue = random_value(self.init_issue_max)
                else:
                    issue = random_value(issue_remain_split)

                if issue_total + issue > self.init_issue_total or \
                        i == self.init_issue_users - 1:
                    issue = self.init_issue_total - issue_total

                # update initial value
                self.init_values[n] = issue
                issue_total += issue
                issue_remain -= issue

            assert np.isclose(self.init_issue_total, np.sum(self.init_values)) and np.isclose(self.init_issue_total, issue_total), \
                "Initial issuance total is inconsistent {} != {} != {}".format(issue_total,
                                                                               np.sum(self.init_values),
                                                                               self.init_issue_total)

        # generate miners
        self.miner = np.zeros(self.n_users, dtype=bool)
        for _ in range(self.n_miners_max):
            # select a random user who is not already designated a miner
            n = random_int(self.n_users)
            while self.miner[n]==1:
                n = random_int(self.n_users)

            self.miner[n] = 1

        assert len(self.miner[self.miner==True])==self.n_miners_max, \
            "Number of miners in ledger is different from specified"

        self.data = pd.DataFrame(data = { 'address': self.keys,
                                          'values': self.init_values,
                                          'miner': self.miner })

    def params(self):
        params = { 'n_users' : self.n_users,
                 'n_miners_max' : self.n_miners_max,
                 'init_issue' : self.init_issue,
                 'reward_dist' : self.reward_dist,
                 'reward' : self.reward }

        if self.init_issue:
            params['init_issue_total'] = self.init_issue_total
            params['init_issue_max'] = self.init_issue_max
            params['init_issue_users'] = self.init_issue_users

        return params

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