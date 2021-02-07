from api import getRouteNames
from api import getSchedules
from api import getStops
from assumptions import salesOverTime
from openpyxl import load_workbook

import pandas as pd

relevant_stops = [ '70007', '70240', '70087', '70265', '70154', '70258', '70271', '70091', '70252', '70104', '70067',
                   '70199', '70032', '70030', '70024', '70063', '70029', '70027', '70267', '70177', '70274', '70158',
                   '70009', '70096', '70076', '70257', '70266', '70015', '70057', '70044', '70164', '70100', '70251',
                   '70245', '70273', '70183', '70075', '70156', '70050', '70247', '70083', '70092', '70086', '70167',
                   '70239', '70170', '70066', '70035', '70003', '70008', '70102', '70173', '70041', '70242', '70033',
                   '70042', '70074', '70203', '70017', '70098', '70055', '70165', '70054', '70005', '70002', '70244',
                   '70172', '70186', '70198', '70016', '70254', '70264', '70014', '70039', '70045', '70278', '70175',
                   '70081', '70058', '70077', '70090', '70048', '70268', '70022', '70010', '70182', '70025', '70034',
                   '70187', '70026', '70088', '70082', '70004', '70168', '70021', '70006', '70180', '70162', '70073',
                   '70069', '70023', '70243', '70046', '70011', '70250', '70255', '70279', '70079', '70181', '70169',
                   '70201', '70246', '70072', '70179', '70256', '70166', '70084', '70089', '70269', '70080', '70047',
                   '70019', '70200', '70078', '70064', '70049', '70020', '70053', '70065', '70028', '70031', '70241',
                   '70178', '70068', '70248', '70253', '70176', '70085', '70171', '70040', '70272', '70071', '70163',
                   '70070', '70043', '70174', '70018', '70056', '70051', '70013', '70270', '70249', '70263', '70052',
                   '70012' ]

relevant_stops_set = set(relevant_stops)


# Perform API request for MBTA Routes of type 0,1
# Print long_name of each route
# Return list of ids for routes to be used in other API requests
def sortSubList(list):
    list.sort(key=lambda x: x[ 1 ])
    return list


def routeIdList():
    response = getRouteNames()

    json_resp = response.json()
    resp_data = json_resp[ "data" ]

    route_id_list = [ ]
    route_long_names = [ ]
    print('\n')
    print("MBTA Train Routes:")
    for data in resp_data:
        id = data[ 'id' ]
        name = data[ 'attributes' ][ 'long_name' ]
        route_id_list.append(id)
        print(name)
    print('\n')
    # return list of route ids to be used in other queries
    return ','.join(map(str, route_id_list))


def routeStops():
    routeIds = routeIdList()
    stops_id_list = [ ]
    response = getStops(routeIds)
    json_resp = response.json()
    resp_data2 = json_resp[ "data" ]
    for stops in resp_data2:
        stop_id = stops[ 'id' ]
        stops_id_list.append(stop_id)
    print('\n')
    return ','.join(map(str, stops_id_list))


def busyHr():
    stopIds = routeStops()
    stop_ids = stopIds.split(",")
    arrival_time_list = [ ]
    max_arrive_time_list = [ ]
    busy_hr_list = [ ]
    station_list = [ ]
    max_trains = [ ]
    for ids in stop_ids:
        arrival_time_list.clear()
        response = getSchedules(ids)
        json_resp = response.json()
        resp_data3 = json_resp[ "data" ]
        for scheds in resp_data3:
            platform_id = scheds[ 'relationships' ][ 'stop' ][ 'data' ][ 'id' ]
            if platform_id in relevant_stops_set:
                flag_append = True
                arrival_time = scheds[ 'attributes' ][ 'arrival_time' ]
                if arrival_time != None:
                    arrival_time = int(arrival_time[ 11:13 ]) * 60 + int(arrival_time[ 14:16 ])
                else:
                    arrival_time = 0
                arrival_time_list.append(arrival_time)
        if not arrival_time_list:
            pass
        else:

            max_arrive_time_list.clear()
            arrival_time_list.sort()
            max_arrive_time_list = maxArrive(arrival_time_list)
            max_val = max(max_arrive_time_list)
            index_val = max_arrive_time_list.index(max_val)
            busy_hr_start = arrival_time_list[ index_val ]
            max_trains.append(max_val)
            busy_hr_list.append(busy_hr_start)
            if flag_append:
                station_list.append(ids)
            flag_append = False
    print('\n')
    # df_busy_hr = pd.DataFrame(list(zip(station_list, busy_hr_list, max_trains)),columns = ['stations','busy_hrs','max_trains'])
    busy_hr_zip = list([ station_list, busy_hr_list, max_trains ])
    return busy_hr_zip


def maxArrive(arr_time):
    max_list = [ ]
    for time in arr_time:
        counter = 0
        temp_var = time + 60
        time_sub = time
        index = arr_time.index(time)
        while time_sub < temp_var:
            if (index + counter) == len(arr_time) - 1:
                break
            counter = counter + 1
            time_sub = arr_time[ index + counter ]
        max_list.append(counter)

    return max_list


def getBusyStation():
    list_df_busy_hr = busyHr()
    stations = list_df_busy_hr[ 0 ]
    hours = list_df_busy_hr[ 1 ]
    max_frequency = max(list_df_busy_hr[ 2 ])
    max_index = list_df_busy_hr[ 2 ].index(max_frequency)
    station_name = stations[ max_index ]
    busy_hour = hours[ max_index ]
    return list([ station_name, busy_hour // 60, busy_hour % 60, max_frequency ])

def busyStationSchedule(data):
    arg_list = [ data[ 0 ], '&filter[min_time]=', data[ 1 ], ':', data[ 2 ], '&filter[max_time]=', data[ 1 ] + 1, ':',
                 data[ 2 ] ]
    df = "".join(map(str, arg_list))
    arrival_list = [ ]
    departure_list = [ ]
    platform_id_list = [ ]
    response = getSchedules(df)
    json_resp = response.json()
    resp_data3 = json_resp[ "data" ]
    for scheds in resp_data3:
        arrival_time = scheds[ 'attributes' ][ 'arrival_time' ]
        departure_time = scheds[ 'attributes' ][ 'departure_time' ]
        platform_id = scheds[ 'relationships' ][ 'stop' ][ 'data' ][ 'id' ]
        if arrival_time != None:
            arrival_time = int(arrival_time[ 11:13 ]) * 60 + int(arrival_time[ 14:16 ])
        else:
            arrival_time = 0
        departure_time = scheds[ 'attributes' ][ 'departure_time' ]
        if departure_time != None:
            departure_time = int(departure_time[ 11:13 ]) * 60 + int(departure_time[ 14:16 ])
        else:
            departure_time = 0
        arrival_list.append(arrival_time)
        departure_list.append(departure_time)
        platform_id_list.append(platform_id)

    station_data = sortSubList(list(zip(platform_id_list, arrival_list, departure_list)))

    return station_data


def getSalesStrategy(data):
    sales_list = [ ]
    sales_platform = [ ]
    platform_time = [ ]
    time_counter = 3600;
    skip_index = 0
    for index, elem in enumerate(data):
        if index < skip_index:
            pass
        else:
            if (index + 1 < len(data) and index - 1 >= 0):
                if data[ index - 1 ][ 1 ] == 0:
                    pass
                else:
                    temp_station = data[ index - 1 ][ 0 ]
                    temp_arrival = data[ index - 1 ][ 1 ]
                    sales_list.append(salesOverTime(60))
                    sales_platform.append(temp_station)
                    current_time = temp_arrival + 1
                    platform_time.append(temp_arrival)
                    time_counter = time_counter - 60 - 45
                    while data[ index - 1 ][ 1 ] <= current_time:
                        index = index + 1
                        if index == len(data) - 1:
                            break
                    skip_index = index
    print('Time remaining {}s'.format(time_counter))
    return list(zip(sales_platform, platform_time, sales_list))


def displaySales(sales_strat):
    for data in sales_strat:
            print('Platform:{} ArrTime:{}:{} DepTime:{}:{} #Sales:{}'.format(data[ 0 ], int(data[ 1 ])//60, int(data[ 1 ])%60,
                                                                             int(data[ 1 ])//60, int(data[ 1 ])%60 + 1,
                                                                             data[ 2 ]))
