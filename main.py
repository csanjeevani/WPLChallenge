
from data import getBusyStation
from data import busyStationSchedule
from data import getSalesStrategy
from data import displaySales
import sys


def main(argv):
    date = input('Enter date in YYYY-MM-DD format')
    df = getBusyStation(date)
    print('Station:{} Start Time:{}:{} Arrival Frequency:{}'.format(df[0],df[1],df[2],df[3]))
    station_data_list = busyStationSchedule(df)
    sales_strat = getSalesStrategy(station_data_list)
    displaySales(sales_strat )



    print('\n')
    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
