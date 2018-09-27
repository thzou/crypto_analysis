#Author : Zoumpekas Athanasios
#codename : thzou 

import os
import numpy as np
import pandas as pd
import datetime
import time
import sys
import io
from itertools import product
import warnings
from data_acquisition import *
from data_analysis import *


def main():

	btc_usd_datasets = btc_average_data()
	altcoin_data = get_altcoins_data()
	final_df = convert_and_combine(altcoin_data,btc_usd_datasets)

	correlation_analysis(final_df)
	distribution_analysis(final_df)
	trading_strategies(final_df)




if __name__ == "__main__":
    main()