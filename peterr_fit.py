#!/usr/bin/env python
import numpy as np
import pandas as pd
import scipy.optimize as optimize
from matplotlib import pyplot as plt
from files import data, bs_period

# First, let's recreate Peter Rizun's plot with current data, showing the enforced saturation
plt.clf()
plt.plot_date(data.index, data["market-cap"], linestyle="-", marker="", label="BTC market cap")
plt.plot_date(data.index, data["n-transactions"]**2, linestyle="-", marker="", color='green', label="No. txn squared")
plt.plot_date(data.index, data["n-transactions-excluding-popular"]**2, linestyle="-", marker="", color='red', label="No. txn. squared, excl. pop.")
plt.axes().set_yscale("log")
plt.legend(loc="lower right")
plt.xlabel("Time")
plt.ylabel("\$, $\mathrm{ntxn}^2$")
plt.title("Market capitalization vs. transactions - updated Oct. 15th 2016")
plt.savefig("mcap-vs-txn-fullrange.pdf")

# Now, lets see how log(market cap) and log(ntep) moved together
lnteptill2015=np.log(np.array(data["n-transactions-excluding-popular"][:bs_period]))
lmcaptill2015=np.log(np.array(data["market-cap"][:bs_period]))

# filter out  where market cap or ntep is zero
valids=np.isfinite(lnteptill2015) & np.isfinite(lmcaptill2015)

lnteptill2015=lnteptill2015[valids]
lmcaptill2015=lmcaptill2015[valids]

plt.clf()
plt.scatter(data["n-transactions-excluding-popular"][:bs_period], data["market-cap"][:bs_period], marker=".", color="green", label="until 2015")
plt.scatter(data["n-transactions-excluding-popular"][bs_period:], data["market-cap"][bs_period:], marker=".", color="red", label="since 2015")
plt.xlabel("Number of transactions excluding popular addresses")
plt.ylabel("Market cap [\$]")
plt.title("Daily market cap vs. TXN volume")

# and fit line to log-log data
fit_result = optimize.leastsq(lambda X: X[0]*lnteptill2015-lmcaptill2015, [1.0], full_output=True)

mcap_ntep_factor = fit_result[0][0]

print "log($) per log(txn):", mcap_ntep_factor

plt.axes().set_yscale("log")
plt.axes().set_xscale("log")
plt.xlim(1e2, 1e6)
plt.ylim(1e5, 1e11)
plt.plot(np.linspace(*plt.xlim()+(10,)), np.exp(mcap_ntep_factor*np.log(np.linspace(*plt.xlim()+(10,)))), label="Fit until 2015")
plt.legend(loc="lower right")
plt.savefig("mcap-vs-txn-scatter-and-fit.pdf")

