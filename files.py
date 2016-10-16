#!/usr/bin/env python
import pandas as pd

blockchain_data={"avg-block-size",
                 "market-cap",
                 "market-price",
                 "miners-revenue",
                 "n-transactions",
                 "n-transactions-excluding-popular",
                 "total-bitcoins",
                 "transaction-fees"}

data=None

for bcd in blockchain_data:
    d=pd.read_csv(bcd+".csv", names=["date", bcd], index_col=0, parse_dates=True)
    if data is None:
        data=d
    else:
        data=pd.merge(data, d, left_index=True, right_index=True)

# Assumed beginning of Blockstream's reign (corresponds to 2016-01-01), alternatively _block _saturation
bs_period=2189


# taken from fit in peterr_fit
mcap_ntep_factor=2.03252978217

# last halving (days) and reward now
last_halving_day=2744
last_halving_reward=12.5
