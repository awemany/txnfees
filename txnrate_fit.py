#!/usr/bin/env python
import datetime
import cPickle
import numpy as np
import pandas as pd
import scipy.optimize as optimize
from scipy.special import erf
from matplotlib import pyplot as plt
from files import data, bs_period, mcap_ntep_factor

# do calcs in days since beginning of blockchain.info's data - approx. days since genesis block
days=np.arange(len(data), dtype=float)
ntep=np.array(data["n-transactions-excluding-popular"])
lntep=np.log(ntep)
valids=np.isfinite(lntep)

days=days[valids]
lntep=lntep[valids]

lnteptill2015=np.log(np.array(data["n-transactions-excluding-popular"][:bs_period]))
daystill2015=np.arange(bs_period, dtype=float)

valids2015=np.isfinite(lnteptill2015)
lnteptill2015=lnteptill2015[valids2015]
daystill2015=daystill2015[valids2015]

lntep2013till2015=np.log(np.array(data["n-transactions-excluding-popular"][bs_period-2*365:bs_period]))
days2013till2015=np.arange(bs_period-2*365, bs_period, dtype=float)

valids2013till2015=np.isfinite(lntep2013till2015)
lntep2013till2015=lntep2013till2015[valids2013till2015]
days2013till2015=days2013till2015[valids2013till2015]

def txn_loglin_curve(X):
    return X[1]*daystill2015+X[0]

def txn_loglin(X):
    return txn_loglin_curve(X) - lnteptill2015

def txn_loglin_curve2013till2015(X):
    return X[1]*days2013till2015+X[0]

def txn_loglin2013till2015(X):
    return txn_loglin_curve2013till2015(X) - lntep2013till2015

def txn_loglin_extrapolate(X):
    return X[1]*np.arange(365*50, dtype=float)+X[0]

fit_lin_till2015_result=optimize.leastsq(txn_loglin, [1.0, 1.0], full_output=True)

fit_lin_2013till2015_result=optimize.leastsq(txn_loglin2013till2015, [1.0, 1.0], full_output=True)

fifty_years=[data.index[0]+datetime.timedelta(days=d) for d in range(365*50)]

plt.clf()
plt.xlabel("Time")
plt.ylabel("Transactions (excl. popular) [$\mathrm{day}^{-1}$]")

plt.plot_date(fifty_years, [np.exp(lntep.max())]*len(fifty_years), markersize=0, linewidth=2.0, linestyle="-", color="red", label="Saturation (1MB is final)")

plt.plot_date([data.index[0]+datetime.timedelta(days=d) for d in days], np.exp(lntep), markersize=0, linewidth=1, linestyle="-", color="blue", label="Real transaction rate")

plt.plot_date(fifty_years, np.exp(txn_loglin_extrapolate(fit_lin_till2015_result[0])), markersize=0, linewidth=2.0, linestyle="-", color="green", label="Exponential for data genesis .. 2015")
plt.plot_date(fifty_years, np.exp(txn_loglin_extrapolate(fit_lin_2013till2015_result[0])), markersize=0, linewidth=2.0, linestyle="-", color="black", label="Exponential for data 2013 .. 2015")

print "Max daily transactions:", np.exp(lntep.max())
print "Corresponding max Bitcoin market cap at 1MB saturation:", np.exp(mcap_ntep_factor*lntep.max()), "$"

print "Fit linear log(data) parameters 2009-2015:", fit_lin_till2015_result[0]
print "Fit linear log(data) parameters 2013-2015:", fit_lin_2013till2015_result[0]

plt.legend(loc="lower right")
plt.xlim(data.index[0], data.index[0]+datetime.timedelta(days=20*365))
ylow, yhigh=1.0, 1e9
plt.ylim(ylow, yhigh) 
plt.axes().set_yscale("log")
plt.grid()
plt.text(np.mean(plt.xlim()), np.exp(lntep.max()), "1MB limit", color='red')

ax2=plt.twinx()
plt.ylim(ylow ** mcap_ntep_factor, yhigh ** mcap_ntep_factor)
ax2.set_yscale("log")
plt.ylabel("Theoretical market cap (Metcalfe's idea) [\$]")
plt.title("Transaction rate growth")
plt.savefig("txngrowth.pdf")

fits=pd.DataFrame(index=fifty_years,
                  data={
                      "txn_loglin_till2015" : np.exp(txn_loglin_extrapolate(fit_lin_till2015_result[0])),
                      "txn_loglin_2013till2015" : np.exp(txn_loglin_extrapolate(fit_lin_2013till2015_result[0])),
                      "txn_flat"   : [np.exp(lntep.max())]*len(fifty_years)
                      })
                      
fits.to_pickle("txnrate_growthmodels.pickle")
