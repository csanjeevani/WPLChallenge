import requests

api_url_base = 'https://api-v3.mbta.com/'
headers = {'Content-Type': 'application/json'}

routes_arg = 'routes?fields[route]=long_name,id&filter[type]=0,1'
stops_arg = 'stops?fields[stop]=id&filter[route]='
schedules_arg = 'schedules?filter[stop]='


def getRouteNames():
    resp = requests.get(api_url_base + routes_arg + '&api_key=123bc0c578314f58b65ee18970d537ff', headers=headers)
    if resp.status_code == 200:
        return resp
    print('Error: getRouteNames API endpoint')


def getStops(data):
    resp2 = requests.get(api_url_base + stops_arg + data + '&api_key=123bc0c578314f58b65ee18970d537ff', headers=headers)
    if resp2.status_code == 200:
        return resp2
    print('Error: getStops API endpoint')


def getSchedules(data):
    resp1 = requests.get(api_url_base + schedules_arg + data + '&api_key=123bc0c578314f58b65ee18970d537ff', headers=headers)
    if resp1.status_code == 200:
        return resp1
    print('Error: getSchedules API endpoint')
