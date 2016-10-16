#!/bin/bash
for d in market-price total-bitcoins market-cap avg-block-size transaction-fees n-transactions n-transactions-excluding-popular miners-revenue; do
	wget -O $d.csv "https://api.blockchain.info/charts/$d?format=csv&timespan=all"
done
