import re
import time
import numpy as np
import pynmea2
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr 

dataUrl = 'geo_data.nmea'
pattern = r'GPGGA'

def parseNMEA(data):
    output = []
    [output.append(data[i]) for i in range(len(data)) if re.search(pattern, data[i])]
    return(output)

def parseGPS(data):
    output = []
    for i in range(len(data)):
        if data[i].find('GGA') > 0:
            output.append(pynmea2.parse(data[i]))
    return(output)

def dmsToDD(d,m,s):
    dd = d + float(m)/60 + float(s)/3600
    return dd

def ddToDms(dms):
    d = int(dms)
    md = abs(dms - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def cordinateToDD(data):
    dd_lat, dd_lon = [], []
    for i in range(len(data)):
        
        lat_d = float(('%02d' % data[i].latitude))
        lat_m = ('%02d' % data[i].latitude_minutes)
        lat_s = ('%07.4f' % data[i].latitude_seconds)
        dd_lat.append(dmsToDD(lat_d,lat_m,lat_s))

        lon_d = float(('%02d' % data[i].longitude))
        lon_m = ('%02d' % data[i].longitude_minutes)
        lon_s = ('%07.4f' % data[i].longitude_seconds)
        dd_lon.append(dmsToDD(lon_d, lon_m, lon_s))

    return {'latitude':dd_lat, 'longitude':dd_lon}

def viewAllData(data, cordinates, La, Fi):
    for i in range(len(data)):
        print('\nTime: '+str(data[i].timestamp))
        print('%02d°%02d′%07.4f″%s' %   
            ( 
                data[i].latitude, 
                data[i].latitude_minutes, 
                data[i].latitude_seconds, 
                data[i].lat_dir
            )
        )
        print("%s: %f" % 
            (
                data[i].lat_dir, 
                cordinates['latitude'][i]
            )
        )
        print('%02d°%02d′%07.4f″%s' % 
            (
                data[i].longitude, 
                data[i].longitude_minutes, 
                data[i].longitude_seconds, 
                data[i].lon_dir
            )
        )
        print("%s: %f" % 
            (
                data[i].lon_dir, 
                cordinates['longitude'][i]
            )
        )
        print("Współczynnik La: %f" % La[i])
        print("Współczynnik Fi: %f" % Fi[i])

def generateLaFi(data):
    La, Fi = [], []
    
    for item in range(len(data)):
        i_column = float(data[item].horizontal_dil)
        h_column = float(data[item].num_sats)

        La.append(float((i_column * 6378137 * np.cos(h_column * np.pi / 180)*np.pi/180)/np.sqrt(1-0.00669438*np.power(np.sin(h_column*np.pi/180),2))-968010))
        Fi.append(float((h_column*6335439.327*np.pi/180)*np.power(np.sqrt(1-0.00669438*np.power(np.sin(h_column*np.pi/180),2)),3)-5946350))
    
    return(La,Fi)

def mseCordinates(data, average):
    mse = 0
    for i in range(len(data)):
        mse = mse + ((data[i] - average)**2)
    return (mse/len(data))

def avgCordinates(data):
    sumOfElements = 0
    for i in range(len(data)):
        sumOfElements = sumOfElements + data[i]
    return(sumOfElements/len(data))
def viewSummary(countInputLines, countOutputLines, avgLatitudeDMS, avgLongitudeDMS, mseLatitude, mseLongitude,bladKolowy,corelation):
    print()
    print("Liczba wynikow przed obrobka: %d \nLiczba wynikow po obrobce: % d" % (countInputLines,countOutputLines))
    print()
    print("Średnia szerokość: %02d°%02d′%07.4f″ \nŚrednia długość: %02d°%02d′%07.4f″" % 
    (
        avgLatitudeDMS[0], 
        avgLatitudeDMS[1], 
        avgLatitudeDMS[2],
        avgLongitudeDMS[0],
        avgLongitudeDMS[1],
        avgLongitudeDMS[2]
    ))
    print()
    print("Błąd szerokości: " + str(mseLatitude))
    print("Błąd długości: " + str(mseLongitude))
    print()
    print("Błąd średni kołowy: " + str(bladKolowy))
    print()
    print("Współczynnik korelacji jest równy: " + str(corelation))
    print()

def viewPlotPosition(X,Y):
    fig, ax1 = plt.subplots()

    plt.title("Pozycja geograficzna")
    plt.plot(X,Y,'rx')

    ax1.set_xlabel('Latitude')
    ax1.set_ylabel('Longitude')

    plt.savefig('position.png')
    # plt.show()

def viewPlotLatitude(X,Y):
    fig, ax1 = plt.subplots()

    plt.title("Szerokość geograficzna")
    plt.plot(X,Y,'gx')

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Latitude')

    plt.savefig('latitude.png')
    # plt.show()

def viewPlotLongitude(X,Y):
    fig, ax1 = plt.subplots()
    
    plt.title("Długość geograficzna")
    plt.plot(X,Y,'bx')
    
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Longitude')
    
    plt.savefig('longitude.png')
    # plt.show()

def viewPlotCorelation(X,Y1,Y2):
    fig, ax1 = plt.subplots()

    plt.title("Korelacja długość i szerokość")

    ax2 = ax1.twinx()
    ax1.plot(X,Y1, 'rx')
    ax2.plot(X,Y2, 'b-')

    ax1.set_xlabel('Time')
    ax1.set_ylabel('Latitude', color='r')
    ax2.set_ylabel('Longitude', color='b')

    plt.savefig('corelation.png')
    # plt.show()

def main():
    file = open(dataUrl, 'r')

    if file.mode == 'r':

        contents = file.readlines()
        dataToAnalist = parseGPS(parseNMEA(contents)) # contents: List[String]
        cordinates = cordinateToDD(dataToAnalist)
        La, Fi = generateLaFi(dataToAnalist)
        
        # viewAllData(dataToAnalist, cordinates, La, Fi)

        avgLatitudeDD = avgCordinates(cordinates['latitude'])
        avgLongitudeDD = avgCordinates(cordinates['longitude'])

        avgLatitudeDMS = ddToDms(avgLatitudeDD)
        avgLongitudeDMS = ddToDms(avgLongitudeDD)

        mseLatitude = mseCordinates(cordinates['latitude'], avgLatitudeDD)
        mseLongitude = mseCordinates(cordinates['longitude'], avgLongitudeDD)

        bladKolowy = np.sqrt((avgLatitudeDD**2)+(avgLongitudeDD**2))

        countInputLines = len(contents)
        countOutputLines = len(dataToAnalist)

        corelation = pearsonr(cordinates['latitude'], cordinates['longitude'])[0]

        measureTime = [dataToAnalist[i].timestamp for i in range(len(dataToAnalist))]

        timeCollection = [dmsToDD(measureTime[i].hour, measureTime[i].minute, measureTime[i].second) for i in range(len(measureTime))]

    # viewSummary(countInputLines, countOutputLines, avgLatitudeDMS, avgLongitudeDMS, mseLatitude, mseLongitude,bladKolowy,corelation)

    viewPlotPosition(cordinates['latitude'], cordinates['longitude'])
    viewPlotLatitude(timeCollection, cordinates['latitude'])
    viewPlotLongitude(timeCollection, cordinates['longitude'])
    viewPlotCorelation(timeCollection, cordinates['latitude'], cordinates['longitude'])

    file.close()

if __name__=='__main__':
    main()
