#!/usr/bin/env python
import os
import requests
import sys

BASE_URL = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/'
STATION = 'GHCND:USW00013891' #'KTYS'

class NOAA(object):
    def __init__(self, token, station = None):
        self.token = token
        # get information for the station
        self.station = {'id':station}
        if station is not None:
            self.station.update(self.get('stations', station))
        if self.station['id'] is None:
            raise RuntimeError('Everything needs a station id')

    def get(self, *args, **kwargs):
        url = os.path.join(BASE_URL, *args)
        req = requests.get(url, headers={'token':self.token}, params=kwargs)
        if req.status_code != requests.codes.OK:
            print(req.text)
            req.raise_for_status()
        return req.json()

    def datacategories(self):
        return self.get('datacategories', stationid=self.station['id'],
                        limit=42) # for KTYS

    def dataset(self, id):
        '''this doesn't work, don't bother'''
        return self.get('datasets')#, datatypeid=id)

    def datatypes(self):
        return self.get('datatypes', stationid=self.station['id'],
                        limit=686) # for KTYS

    def data(self, id):
        return self.get('data', stationid=self.station['id'],
                        datasetid='NORMAL_DLY', #GHCND',
                        datatypeid=id,
                        count=1000,
                        startdate='2017-11-11', enddate='2017-11-11')



if len(sys.argv) < 2:
    print("Supply API token")
    sys.exit(-1)
token = sys.argv[1]
print("using token", token)

noaa = NOAA(token, STATION)
#https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GSOM&stationid=GHCND:USC00010008&units=standard&startdate=2010-05-01&enddate=2010-05-31
#for item in noaa.get('data', datasetid='GSOM', stationid='GHCND:USC00010008',
#         units='standard', startdate='2010-05-01', enddate='2010-05-31')['results']:
#    print(item)
print('==========================')
#https://www.ncdc.noaa.gov/cdo-web/api/v2/datasets?stationid=COOP:310090&stationid=COOP:310184&stationid=COOP:310212
#for item in noaa.get('datasets', stationid='COOP:310090'):#['results']:
#    print(item)

print('========================== datasets')
datasets = []
data = noaa.get('datasets')
print(data['metadata'])
for item in data['results']:
    print(item)
    if 'NEXRAD' in item['id']:
        continue
    datasets.append(item['id'])
print(datasets)

print('========== categories ==========')
data = noaa.datacategories()
print(data['metadata'])
for item in data['results']:
    print(item)
#print(noaa.dataset('ANNTEMP'))
print('========== type ==========')
data = noaa.datatypes()
print(data['metadata'])
for item in data['results']:
    # averages
    if 'Long-term' in item['name']:
        continue
    # data for only one year
    if item['mindate'].split('-')[0] == item['maxdate'].split('-')[0]:
        continue
    print(item)
print('==========================')

for datasetid in datasets:
    print(datasetid, noaa.get('data', #stationid=STATION,
                              datasetid=datasetid, #GHCND',
                              datatypeid='TOBS',
                              #count=1000,
                              startdate='2017-11-11', enddate='2017-11-11'))


#print(noaa.data('TOBS'))#['results']:
#for item in noaa.data('TOBS')['results']:
#    print(item)
