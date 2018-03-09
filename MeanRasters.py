#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:38:14 2018

@author: wellenbu
"""

from osgeo import gdal, osr
import numpy as np
import glob
import sys
import urllib2
import ast
import pandas as pd

dir = '/Users/wellenbu/Documents/HKH/ESI/Afghanistan/NDJ1617/'
outTif = 'ND16min'

# Function to read tiff projection:
def GetGeoInfo(FileName):
    SourceDS = gdal.Open(FileName, gdal.GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataType = gdal.GetDataTypeName(DataType)
    return NDV, xsize, ysize, GeoT, Projection, DataType

# Function to write a new file.
def CreateGeoTiff(Name, Array, driver,
                  xsize, ysize, GeoT, Projection, DataType):
    if DataType == 'Float32':
        DataType = gdal.GDT_Float32
    NewFileName = Name+'.tif'
    # Set up the dataset
    DataSet = driver.Create( NewFileName, xsize, ysize, 1, DataType )
            # the '1' is for band 1.
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection( Projection.ExportToWkt() )
    # Write the array
    DataSet.GetRasterBand(1).WriteArray( Array )
    return NewFileName


dl = False

datatype='29'
begintime='01/01/2016'
endtime='02/01/2018'
intervaltype='0'

#5 is mean, 6 is download 
operationtype='5%20'

#Default Params keep as is:
dateType_Category='default'
isZip_CurrentDataType='false'

layerid='country'
featureids='2'

req = 'datatype={0}&begintime={1}&endtime={2}&intervaltype={3}&operationtype={4}&dateType_Category={5}&isZip_CurrentDataType={6}&layerid={7}&featureids={8}'.format(datatype,begintime,endtime,intervaltype,operationtype,dateType_Category,isZip_CurrentDataType,layerid,featureids)

   
req_url1 = 'https://climateserv.servirglobal.net/chirps/submitDataRequest/?'+req

task = urllib2.urlopen(req_url1).read()[2:-2]
print task
#sys.exit() 
 
if dl:
    req_url2 = 'https://climateserv.servirglobal.net/chirps/getFileForJobID/?id={0}'.format(task)
else:
    req_url2 = 'https://climateserv.servirglobal.net/chirps/getDataFromRequest/?id={0}'.format(task)
    response = urllib2.urlopen(req_url2)
    data = ast.literal_eval(response.read())
    data = pd.DataFrame(data['data'])
    for i in data['value'].iteritems():
        i[1]['avg']
    
sys.exit()
tifs = glob.glob(dir+'*.tif')
tifs = tifs[:-4]

#sys.exit()

NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(tifs[0])

b = []

for i in tifs:
    a = gdal.Open(i, gdal.GA_ReadOnly)
    a = a.GetRasterBand(1).ReadAsArray()
    a[a==-9999] = np.nan
    
    b.append(a)
    
b = np.nanmin(np.array(b),0)

driver = gdal.GetDriverByName('GTiff')

CreateGeoTiff(outTif, b, driver, xsize, ysize, GeoT, Projection, DataType)

    
