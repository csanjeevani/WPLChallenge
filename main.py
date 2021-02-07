import json
import pandas as pd
from data import getBusyStation
from data import busyStationSchedule
from data import getSalesStrategy
from data import displaySales
import sys


def main(argv):
    df = getBusyStation()
    station_data_list = busyStationSchedule(df)
    sales_strat = getSalesStrategy(station_data_list)
    displaySales(sales_strat )



    print('\n')
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
