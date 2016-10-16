#!/usr/bin/env python
import datetime
import cPickle
import numpy as np
import pandas as pd
import scipy.optimize as optimize
from scipy.special import erf
from matplotlib import pyplot as plt
from files import data, bs_period, last_halving_day, last_halving_reward, mcap_ntep_factor

gm=pd.read_pickle("txnrate_growthmodels.pickle")

# assume miner fees at 2ct (low) or $50 (high)
low_fee=0.02
high_fee=50.0

days50years=np.arange(365*50, dtype=float)
fifty_years=[data.index[0]+datetime.timedelta(days=d) for d in range(365*50)]

# calculate reward per day (approximately!), taking _last halving_ as
# reference and assume 10min blocks into both time directions. Inaccurate for
# the beginning of Bitcoin, but the best guess for the future.
reward=144*np.array([last_halving_reward*(.5**x) for x in np.floor((days50years-last_halving_day)/(4*365.))])

# calculate coins in circulation
coins=np.cumsum(reward)

# correct for partial 50BTC due to shift (again inaccurate for earlier times)
coins+=(4*365.0 - (abs(reward/144-25.)<1e-3).argmax()) * 144 * 50.0

# coin price estimates - estimate market cap from txn rate ("Metcalfe's law") and divide by coins issued

price_loglin_till2015=(gm["txn_loglin_till2015"]**mcap_ntep_factor) / coins
price_loglin_2013till2015=(gm["txn_loglin_2013till2015"]**mcap_ntep_factor) / coins

# fix flat model to include real data in earlier times
# this avoids the odd looking (and widly wrong) extrapolation to earlier times
gm["txn_flat"][:len(data)]=data["n-transactions-excluding-popular"]

price_flat  =(gm["txn_flat"]**mcap_ntep_factor) / coins

print "Eventual price $/BTC for flat model:", price_flat[-1]


# total miner income for 2ct/txn or 5ct/txn
income_flat_low=(gm["txn_flat"] * low_fee) + reward * price_flat
income_flat_high=(gm["txn_flat"] * high_fee) + reward * price_flat

# miner income for very optimistic exponential model fit genesis..2015
income_loglin_till2015=(gm["txn_loglin_till2015"] * low_fee) + reward * price_loglin_till2015

# miner income for optimistc exponential model fit 2013..2015
income_loglin_2013till2015=(gm["txn_loglin_2013till2015"] * low_fee) + reward * price_loglin_2013till2015

plt.plot_date(data.index, data["market-price"]*(reward[:len(data)]+data["transaction-fees"]), markersize=0, linewidth=2, linestyle="-", color="blue", label="Fees plus approx. miner reward")
plt.plot_date(fifty_years, income_flat_low, markersize=0, linewidth=2, linestyle="-", color="red", label="Flat txn rate and price, 2ct/txn")
plt.plot_date(fifty_years, income_flat_high, markersize=0, linewidth=2, linestyle="-", color="#ff8080", label="Flat txn rate and price, 50$/txn")
plt.plot_date(fifty_years, income_loglin_till2015, markersize=0, linewidth=2, linestyle="-", color="green", label="Exponential model genesis .. 2015")
plt.plot_date(fifty_years, income_loglin_2013till2015, markersize=0, linewidth=2, linestyle="-", color="black", label="Exponential model 2013 .. 2015")

plt.title("Fee income models")
plt.ylabel("Daily fee income including reward [$/day]")
plt.xlabel("Time")
plt.legend(loc="lower right")
plt.xlim(data.index[0], data.index[0]+datetime.timedelta(days=20*365))
plt.ylim(1e0, 1e13)
plt.axes().set_yscale("log")
plt.grid()
plt.savefig("fee-income-models.pdf")
