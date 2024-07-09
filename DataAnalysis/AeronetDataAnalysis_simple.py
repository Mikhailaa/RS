'''
Developed by Anthony Castillo
Under Supervision of Professor Wing To
Created: 02/23/2023
Last Modified: 02/13/2023
Description: A simplified program/script used to create plots of, and to analyze, Aeronet Data.
Data is initially collected from: 
    https://aeronet.gsfc.nasa.gov/
    https://aeronet.gsfc.nasa.gov/cgi-bin/webtool_aod_v3
    https://aeronet.gsfc.nasa.gov/new_web/data_usage.html - Additional Citation information
'''
# First we set the path of the current working directory
import os
import pathlib
currentPath = pathlib.Path(__file__).parent.resolve() # Gets this python script file's current location
os.chdir(currentPath) # Sets the working directory to the current file's location

# Second we import the list of libraries we are going to use
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import time
import datetime

# PHASE 1: Reading in all of the data available 

rawData = [] # Initialize an empty list for holding the data
formattedData = []
headers = []
filename = '20220101_20221231_Modesto.tot_lev20' # The default file location
with open(filename, 'r') as datafile: # Opening the file as the object "datafile"
    for line in datafile: # Iterating thru the date file line by line
        if line != '': # If the line from the file is not empty then we will append that line to the list of usable data
            keys = []
            key = ''
            for character in line: # We'll iterate thru each line looking for commas, since those are what separate every data point
                if character != ',':
                    key += character
                else:
                    keys.append(key) # Appends the key to the list of keys
                    key = '' # Empties the key for the next iteration
            keys.append(key) # Appends the very last data point to keys
            formattedData.append(keys)
            #rawData.append(line) # Debugging
#rpint(formattedData[0], '\n', formattedData[1], '\n', formattedData[2], '\n', formattedData[3], '\n', formattedData[4], '\n', formattedData[5], '\n', formattedData[6], '\n', formattedData[7]) # Debugging
#formattedData[6] is the headers # Information
#formattedData[7] is the start of the actual data # Information
for index, value in enumerate(formattedData):
    if headers == []:
        for i, j in enumerate(formattedData[index]):
            if 'dd:mm:yyyy' in j:
                headers = formattedData[index]
                break
    #for iterator in range(7, len(formattedData)): # Debugging
        #print(value, formattedData[iterator][index]) # Debugging
#print(headers) # Debugging

# PHASE 2: Select which Data the user wants to display

for i in headers:
    print(i)
userInput = ''
while userInput == '': # Having the user select a header
    #userTest = input('Which header would you like to process? ')
    userTest = 'aod_870nm-total' # Default for debugging purposes
    userTest = 'aod_1640nm-total'
    for i in headers:
        if userTest.lower() == i.lower():
            userInput = i
            break
    if userInput == '':
        print('Please enter a valid selection.')

selectedData, selectedDates, selectedTimes = [], [], []
for index, value in enumerate(headers):
    if value == userInput:
        for i, v in enumerate(formattedData):
            if i >= 7:
                selectedTimes.append(v[1])
                selectedDates.append(v[0])
                selectedData.append(float(v[index])) # convert to floating point integers
        break
#print(selectedDates) # Debugging
#print(selectedTimes) # Debugging
#print(selectedData) # Debugging

# PHASE 3: Convert all data points into PST/GMT+7

timeDifference = datetime.datetime.utcnow() - datetime.datetime.now() # Finding the difference between UTC0 and the local timezone
def gmt0ToLocalTZ_conversion(dateData,timeData): # A function to convert the date and time of a data plot from UTC0 to the local timezone (PST)
    # Date(dd:mm:yyyy),Time(hh:mm:ss)
    oldTime = datetime.datetime.strptime(dateData + ':' + timeData + ':' + 'GMT', '%d:%m:%Y:%H:%M:%S:%Z') #  + ':' + 'GMT' # :%Z
    newTime = oldTime - timeDifference
    newDateData, newTimeData = '', ''
    if len(str(newTime.day)) < 2:
        newDateData = '0' + str(newTime.day) + ':'
    else:
        newDateData = str(newTime.day) + ':'
    if len(str(newTime.month)) < 2:
        newDateData += '0' + str(newTime.month) + ':'
    else:
        newDateData += str(newTime.month) + ':'
    newDateData += str(newTime.year)

    if len(str(newTime.hour)) < 2:
        newTimeData = '0' + str(newTime.hour) + ':'
    else:
        newTimeData = str(newTime.hour) + ':'
    if len(str(newTime.minute)) < 2:
        newTimeData += '0' + str(newTime.minute) + ':'
    else:
        newTimeData += str(newTime.minute) + ':'
    if len(str(newTime.second)) < 2:
        newTimeData += '0' + str(newTime.second)
    else:
        newTimeData += str(newTime.second)
    #if int(newTime.day) != oldTime.day: # Debugging
        #print('Converting: ', dateData, timeData, ' to ', newDateData, newTimeData) # Debugging
    return newDateData, newTimeData

adjustedDates, adjustedTimes = [], []
for i, v in enumerate(selectedDates): # For every datapoint
    adjustedDate, adjustedTime = gmt0ToLocalTZ_conversion(v, selectedTimes[i]) # Convert its date and time to the local timezone
    adjustedDates.append(adjustedDate)
    adjustedTimes.append(adjustedTime)
#print(adjustedDates) # Debugging
#print(adjustedTimes) # Debugging


#for i, v in enumerate(selectedData): # Debugging
    #print(v, adjustedDates[i], adjustedTimes[i]) # Debugging
#print(adjustedDates, '\n', adjustedTimes, '\n') # Debugging
#print(len(selectedData), len(adjustedDates), len(adjustedTimes)) # Debugging

# PHASE 4: Plot on a Gaussian Curve and Remove the outliers from the data set

def standardDeviation(integerArray): # Computes the standard deviation of any given integer array
    sum = 0
    for x in integerArray:
        sum = sum + (x-np.mean(integerArray))**2
    return (np.sqrt(sum/len(integerArray)) * np.sqrt(2))

xpoints, ypoints = [], []
graph = False
Amplitude = np.amax(selectedData)
sigma = standardDeviation(selectedData)
resultsData, resultsDate, resultsTime = [], [], []
if (2*sigma**2) == 0:
    print('Error: Cannot divide by zero.', userInput, ' data is in an invalid format:', selectedData[0])
    raise ZeroDivisionError # division by zero
else:
    for x in selectedData:
        xpoints.append(x)
        ypoints.append(Amplitude*np.exp(-(x-np.mean(selectedData))**2 / (2*sigma**2)))
    if graph:
        xpointsNp, ypointsNp = np.array(xpoints), np.array(ypoints)
        title = 'Amplitude=' + str(Amplitude) + ' Sigma=' + str(sigma)
        plt.plot(xpointsNp, ypointsNp, 'ko')
        plt.title(title)
        plt.get_current_fig_manager().set_window_title(userInput + ' with ' + str(xpointsNp.size) + ' data points.')
        plt.show()
    for index, value in enumerate(ypoints):
        if (Amplitude-(sigma*2)) <= value <= (Amplitude+(sigma*2)):
            if selectedData[index] == 0 or selectedData[index] == -999: # We will omit this type of data
                continue
            resultsData.append(selectedData[index])
            resultsDate.append(adjustedDates[index])
            resultsTime.append(adjustedTimes[index])
print(len(resultsData), len(resultsDate), len(resultsTime)) # Debugging

# PHASE 5: Clumping together datapoints that are within the same 12hrs of eachother, from 6pm to 6am and 6am to 6pm
    # Condensing the values tooooo much, why? It should produce about 300 points instead of 40

xdata, ydata, yMinMax, dataRange, nightTime, currentDate = [], [], [], [], False, time.strptime(resultsDate[0] + ':' + resultsTime[0], '%d:%m:%Y:%H:%M:%S')
#datetime.datetime.strptime(resultsDate[0] + ':' + resultsTime[0], '%d:%m:%Y:%H:%M:%S')
if int(resultsTime[0][0]) == 0 and int(resultsTime[0][1]) <=5 or int(resultsTime[0][0]) >= 1 and int(resultsTime[0][1]) >= 8: # Dynamically setting the nightTime boolean
    nightTime = True
else:
    nightTime = False
#print(currentDate) # Debugging
#print(time.gmtime(time.mktime(currentDate)-86400)) # Debugging
for index, value in enumerate(resultsData):
    print(resultsDate[index], resultsTime[index], value)
    if nightTime: # If it was night time
        if int(resultsTime[index][0]) == 0 and int(resultsTime[index][1]) <= 5 or int(resultsTime[index][0]) >= 1 and int(resultsTime[index][1]) >= 8: # It is still night time
                dataRange.append(value)
        else: # It is no longer night time
            if np.sum(dataRange) != 0.0:
                xdata.append(resultsDate[index] + '_night')
                ydata.append(np.sum(dataRange)/len(dataRange))
                yMinMax.append(standardDeviation(dataRange))
            dataRange.clear()
            nightTime = False
    else: # If it was day time
        if int(resultsTime[index][0]) == 0 and int(resultsTime[index][1]) >= 6 or int(resultsTime[index][0]) == 1 and int(resultsTime[index][1]) <= 7: # It is still day time
                dataRange.append(value)
        else: # It is no longer day time
            if np.sum(dataRange) != 0.0:
                xdata.append(resultsDate[index] + '_day')
                ydata.append(np.sum(dataRange)/len(dataRange))
                yMinMax.append(standardDeviation(dataRange))
            dataRange.clear()
            nightTime = True
print(resultsDate)
print(xdata)
xdataNp, ydataNp, yErrNp = np.array(xdata), np.array(ydata), np.array(yMinMax) # Converting our results to numpy arrays for use in the graphing phase
print(len(xdata), len(ydata), len(yMinMax)) # Debugging

# PHASE 6: Calculating the curve/polynomial fit for the data set

def myCurveFit_Polynomial(xInput, a, b, c, d): # A polynomial representation for our curve fit
    x = np.array(xInput)
    return a*x + b*x**2 + c*x**3 + d

xData_poly = []
for i, _ in enumerate(xdataNp): # Createing an array of all the integer indexes of our data
    xData_poly.append(i)
coeff, covariance = sp.optimize.curve_fit(myCurveFit_Polynomial, xData_poly, ydataNp) # Covariances are not used

# PHASE 7: Plot the data on a graph

#print(len(xdataNp), len(xdata), len(xpoints), len(resultsData),len(resultsDate), len(resultsTime)) # Debugging
#print(resultsDate) # Debugging
#print(xdata) # Debugging

months = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May.', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.'] # Used for tick labels
count = 0
previousCount = 1 # Start off with zero since we will be subtracting 1 from this at each new tickRange/Label and we want to include the first day
tickRange = [] # The break points for our xaxis
tickLabels = [] # The months that the break points will be using
years = [] # A list of years that the data covers
currentMonth = str(xdataNp[0][3]) + str(xdataNp[0][4])
for index, day in enumerate(xdataNp): # To make the break points (tickRange) for the months
    count += 1
    if day[4] != currentMonth[1]: # Any day where the month changes
        tickRange.append(previousCount-1) # Start of the month
        tickRange.append(previousCount + ((count - previousCount)/2)) # Middle of the month
        if currentMonth[0] == '0':
            tickLabels.append(months[eval(currentMonth[1])-1] + str(xdataNp[previousCount-1][0]) + str(xdataNp[previousCount-1][1])) # Start of the month
            tickLabels.append(months[eval(currentMonth[1])-1] + str(xdataNp[previousCount + ((count - previousCount)//2)][0]) + str(xdataNp[previousCount + ((count - previousCount)//2)][1])) # Middle of the month
        else:
            tickLabels.append(months[eval(currentMonth[1])-1] + str(xdataNp[previousCount-1][0]) + str(xdataNp[previousCount-1][1])) # Start of the month
            tickLabels.append(months[eval(currentMonth)-1] + str(xdataNp[previousCount + ((count - previousCount)//2)][0]) + str(xdataNp[previousCount + ((count - previousCount)//2)][1])) # Middle of the month
        currentMonth = str(day[3] + day[4])
        previousCount = count
    if index == len(xdataNp) - 1: # The last day in the data list
        tickRange.append(previousCount-1) # Start of the month
        tickRange.append(previousCount + ((count - previousCount)/2)) # Middle of the month
        if currentMonth[0] == '0':
            tickLabels.append(months[eval(currentMonth[1])-1] + str(xdataNp[previousCount-1][0]) + str(xdataNp[previousCount-1][1])) # Start of the month
            tickLabels.append(months[eval(currentMonth[1])-1] + str(xdataNp[previousCount + (len(xdataNp) - previousCount) // 2][0]) + str(xdataNp[previousCount + (len(xdataNp) - previousCount) // 2][1])) # Middle of the month
        else:
            tickLabels.append(months[eval(currentMonth[1])-1] + str(xdataNp[previousCount-1][0]) + str(xdataNp[previousCount-1][1])) # Start of the month
            tickLabels.append(months[eval(currentMonth)-1] + str(xdataNp[previousCount + (len(xdataNp) - previousCount) // 2][0]) + str(xdataNp[previousCount + (len(xdataNp) - previousCount) // 2][1])) # Middle of the month
        previousCount = count
    if str(day[6] + day[7] + day[8] + day[9]) not in years:
        years.append(str(day[6] + day[7] + day[8] + day[9]))
if 'nm' in userInput:
    yaxisName = 'Wavelength(nm)'
elif 'µm' in userInput:
    yaxisName = 'Wavelength(µm)'
elif 'cm' in userInput:
    yaxisName = 'Wavelength(cm)'
elif 'hPa' in userInput:
    yaxisName = 'Pressure(hPa)'
elif 'degrees_c' in userInput.lower():
    yaxisName = 'Celsius(°C)'
elif 'angle' in userInput.lower():
    yaxisName = 'Angle(°)'
elif 'longitude' in userInput.lower():
    yaxisName = 'Longitude(λ)'
elif 'latitude' in userInput.lower():
    yaxisName = 'Latitude(Φ)'
elif 'wavelength' in userInput.lower():
    yaxisName = 'Wavelength'
else:
    yaxisName = ''

windowTitle = userInput + ' with ' + str(len(xdataNp)) + ' data points' # The title of the window
cap = 2 # The cap sizes for the error bars
xaxisName = 'Months' #'Date dd:mm:yyyy'
if len(years) == 1: # If only one year was detected
    xaxisName = xaxisName + ' in ' + years[0]
elif len(years) != 0: # Functionality for data with more than one year
    xaxisName = xaxisName + ' in ('
    for i in years:
        if i != years[-1]:
            xaxisName = xaxisName + i + ', '
        elif i == years[len(years)-1]:
            xaxisName = xaxisName + i + ')'

plt.errorbar(xData_poly, myCurveFit_Polynomial(xData_poly, coeff[0], coeff[1], coeff[2], coeff[3]), yerr=yErrNp, fmt='o', color='black', capsize=cap, markersize=3)
plt.title(userInput)
plt.xlabel(xaxisName)
plt.ylabel(yaxisName)
if len(tickRange) == len(tickLabels): # If for some reason the range is not in equal length to the labels, we won't do anything special to them
    plt.xticks(ticks = tickRange, labels = tickLabels, minor=False)
plt.get_current_fig_manager().set_window_title(windowTitle)
plt.get_current_fig_manager().resize(1280, 720)
plt.show()
