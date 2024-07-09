'''
Developed by Anthony Castillo
Under Supervision of Professor Wing To
Created: 01/11/2023
Last Modified: 02/13/2023
Description: A program/script used to create plots of, and to analyze, Aeronet Data.
Data is initially collected from: 
    https://aeronet.gsfc.nasa.gov/
    https://aeronet.gsfc.nasa.gov/cgi-bin/webtool_aod_v3
    https://aeronet.gsfc.nasa.gov/new_web/data_usage.html - Additional Citation information
'''

import os
import pathlib
currentPath = pathlib.Path(__file__).parent.resolve() # Gets this python script file's current location
os.chdir(currentPath) # Sets the working directory to the current file's location
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import time
import multiprocessing as mp # not used

class Analysis:
    def __init__(self):
        self.filename = '20220101_20221231_Modesto.tot_lev20' # default file # File needs to be in the same location as this script
        self.aeronetData = dataContainer() # A custom class that is desigend to hold and manage aeronet data specifically

    def __del__(self):
        del self.filename
        del self.aeronetData

    def __len__(self):
        return len(self.aeronetData)

    def __str__(self):
        return str(self.aeronetData)

    def help(self): # WIP
        information = 'This is the help command. (WIP)'
        return information

    def getHeaders(self):
        return self.aeronetData.getFormattedHeader()

    def selectAndReadFile(self, selection): # Lets the user select and load a specified file
        self.filename = selection
        self.readDataFromFile(self.filename)

    def readDataFromDefaultFile(self): # Selects and loads the default file
        self.filename = '20220101_20221231_Modesto.tot_lev20' # The default file we are working with
        self.readDataFromFile(self.filename)

    def readDataFromFile(self, filename): # Reads all data from the aeronet data, separating out the "extra" info from the actual data
        self.aeronetData.clear()
        self.filename = filename
        with open(self.filename, 'r') as dataFile:
            self.aeronetData.setVersion(dataFile.readline())
            self.aeronetData.setLocation(dataFile.readline())
            self.aeronetData.setAODLevel(dataFile.readline())
            self.aeronetData.setDescription(dataFile.readline())
            self.aeronetData.setContactInfo(dataFile.readline())
            self.aeronetData.setReference(dataFile.readline())
            self.aeronetData.setHeader(dataFile.readline())
            for line in dataFile:
                if (line != ''):
                    self.aeronetData.append(line)
        self.aeronetData.formatData()

    def drawAllPlots(self): # Draws all plots
        header = self.aeronetData.getFormattedHeader()
        dateHead = self.aeronetData.getDateHeader()
        headDataArray = []
        xDataArray = []
        yDataArray = []
        yDataError = [] 
        count = 0
        for head in header: # Iterate thru the list of headers
            if 'dd:mm:yyyy' in head or 'hh:mm:ss'  in head or 'day' in head.lower() or 'level' in head.lower() or 'name' in head.lower() or 'processed' in head.lower(): # Do not draw graphs of the dates, times, or anything including the 'day' keyword
                continue # Omit these 'Data_Quality_Level', 'AERONET_Site_Name', 'Last_Date_Processed'
            else:
                #print(head)
                tempX, tempY, tempErr = self._calculatePlot(head, dateHead)
                if tempX.size <= 1: # If the data is empty we won't append its data to the data Arrays
                    pass
                elif tempX.size != 0:
                    headDataArray.append(head)
                    xDataArray.append(tempX)
                    yDataArray.append(tempY)
                    yDataError.append(tempErr)
        for index, value in enumerate(xDataArray):
            if self._drawplot(headDataArray[index], value, yDataArray[index], yDataError[index]):
                count += 1
        return count

    def drawAllPlotsMultProcessor(self): # Draws all plots but utilizing multiprocessing to calculate each plot # WIP
        # Work in progress, not functioning, not used
        header = self.aeronetData.getFormattedHeader()
        dateHead = self.aeronetData.getDateHeader()
        headDataArray = []
        xDataArray = []
        yDataArray = []
        yDataError = [] 
        dateHeadArray = []
        for head in header:
            dateHeadArray.append(dateHead)
        count = 0
        #with multiProcess.Pool(len(os.sched_getaffinity(0))) as pool: # Calculates all plots
        with mp.Pool(os.cpu_count()) as pool:
            print(pool.starmap(self._calculatePlot, zip(header, dateHeadArray))) # Debugging
        for index, value in enumerate(xDataArray): # Draws plots
            if self._drawplot(headDataArray[index], value, yDataArray[index], yDataError[index]):
                count += 1
        return count

    def drawSpecificPlot(self, head, dateHead, gaussianGraph=False, monthStart=None, monthEnd=None): # Draws a specified plot
        xData, yData, yErr = self._calculatePlot(head, dateHead, gaussianGraph, month0=monthStart, month1=monthEnd)
        if xData.size <= 1:
            return False
        return self._drawplot(head, xData, yData, yErr)

    def drawSpecificPlots(self, heads, dateHead, gaussianGraph=False, monthStart=None, monthEnd=None, year=None): # Calculates multiple plot from an array of heads, then draws them
        xDataArray, yDataArray, yErrArray = [], [], []
        acceptableHeads = []
        count = 0
        for index, value in enumerate(heads):
            xData, yData, yErr = self._calculatePlot(value, dateHead, gaussianGraph, month0=monthStart, month1=monthEnd, years=year)
            if xData.size <= 1:
                pass
            elif xData.size != 0:
                acceptableHeads.append(value)
                xDataArray.append(xData)
                yDataArray.append(yData)
                yErrArray.append(yErr)
        for index, head in enumerate(acceptableHeads):
            if self._drawplot(head, xDataArray[index], yDataArray[index], yErrArray[index]):
                count += 1
        return count

    def printSpecificData(self, head):
        data = self.aeronetData.getFormattedData()
        for i in head:
            information = i + ' '
            for j in data:
                information += data[j][i] + ' '
            print(information)
            input('Press any key to continue...')


    def _chiSquared(self, xArray, yArray): # NOT USED # Just use the curve fit function Don't use this
        # Identify the slope of a line and it's y intercept
        # Compute the difference between the theoretical value and experimental value
        # Sum of (y_theory - y_experiment)^2
        # Sum of (mx + b - y)^2
        # slope = (Sum_xy - Sum_x*Sum_y)/()
        # We need to pick our initial value to be as close to our actual min so... np.amin(array) (?)
        sum_x, sum_y, sum_xy, sum_x_squared = 0, 0, 0, 0
        result = 0
        intercept = 0
        if len(xArray) == len(yArray):
            for index, _ in enumerate(xArray):
                sum_x = sum_x + xArray[index]
                sum_y = sum_y + yArray[index]
                sum_x_squared = sum_x_squared + xArray[index]**2
                sum_xy = sum_xy + xArray[index] * yArray[index]
        else: # The arrays are not of equal size
            return False
        sum_x = sum_x / len(xArray)
        sum_x_squared = sum_x_squared / len(xArray)
        sum_y = sum_y / len(xArray)
        sum_xy = sum_xy / len(xArray)
        slope = (sum_xy - sum_x * sum_y)/(sum_x_squared - sum_x**2) # Does not work with non-linear functions/curves
        intercept = (sum_x_squared*sum_y - sum_x*sum_xy)/(sum_x_squared - sum_x**2) # Does not work with non-linear functions/curves
        for x in xArray:
            result = result + (slope*x + intercept - x)**2
        #print(sum_x, sum_x_squared, sum_y, sum_xy)
        #print('SLope: ', slope, 'Intercept: ', intercept)
        #print(result) # Maximum or minimum of the chisquared function
        return result

    def _standardDeviationPerDay(self, intArray, timeArray): # NOT USED # Returns the stdDev of the afternoon and the evening, respectively, utilizing an intArray and a time array
        # Use this for calculating the day by day data
        # 6pm being the "sun down time"
        tempEvening = []
        tempAfternoon = []
        for index, _ in enumerate(timeArray):
            if int(timeArray[index][0]) >= 1 :
                if int(timeArray[index][1]) >= 8: # 6pm being 1800 hours
                    tempEvening.append(intArray[index])
            else:
                tempAfternoon.append(intArray[index])
        sum = 0
        for x in tempAfternoon:
            sum = sum + (x-np.mean(intArray))**2
        afternoon = np.sqrt(sum/len(intArray))
        sum = 0
        for x in tempEvening:
            sum = sum + (x-np.mean(intArray))**2
        evening = np.sqrt(sum/len(intArray))
        return afternoon, evening

    def _myCurve_Polynomial(self, xInput, a, b, c, d): # Polynomial of degree 3
        x = np.array(xInput)
        return a*x + b*x**2 + c*x**3 + d#*x**4 + e*x**5 + f

    def _rootMeanSquare(self, intArray): # NOT USED # Returns almost the stdDev of an array # Not used
        sum = 0
        for i in intArray:
            sum = sum + (i - np.mean(intArray))**2
        return np.sqrt(sum/len(intArray)) 

    def _convertGMTtoPST(self, timeInput, dateInput): # Takes in both the date of the day and the time of the day and converts it into PST; takes leap years into consideration
        # Format: Date(dd:mm:yyyy),Time(hh:mm:ss)
        monthsWith31Days = ['01', '03', '05', '07', '08', '10', '12']
        monthsWith30Days = ['04', '06', '09', '11']
        tempTime = int(timeInput[0] + timeInput[1]) - 8
        tempDate, month = '', ''
        if not tempTime >= 0: # If the new time is less than midnight then the day must be decremented 
            tempTime += 24
            if (int(dateInput[0]) == 0) and (int(dateInput[1]) == 1): # If the date is the first of the month then we will need to decremente the month
                if (int(dateInput[3]) == 0) and (int(dateInput[4] == 1)): # If it is the first of the year, then we must decrement the year too
                    tempDate = '31' + ':' + '12' + str(int(dateInput[5:10])-1) # December, New Year's Day
                else: # Otherwise we just have to decrement the month
                    if (int(dateInput[3] + dateInput[4]) - 1) < 10: # First we check if we need to add a zero infront of the month
                        month = '0' + str(int(dateInput[3] + dateInput[4]) - 1)
                    else: # Here the result is double digit so we don't need to add a zero
                        month = str(int(dateInput[3] + dateInput[4]) - 1)
                    # Check if we need a 0
                    if month in monthsWith31Days:
                        tempDate = '31' + ':' + month + dateInput[5:10]# Changes depending on the month we are now in
                    elif month in monthsWith30Days:
                        tempDate = '30' + ':' + month + dateInput[5:10]
                    elif month == '02': # If the new month is feburary then we need to check for leap year
                        if int(dateInput[6] + dateInput[7] + dateInput[8] + dateInput[9]) % 400 == 0: # End of centuries evenly divisible by 400 are leap years, others are not leap years
                            tempDate = '29' + ':' + month + dateInput[5:10]
                        elif int(dateInput[6:10]) % 4 == 0: # Years that are Evenly divisible 4 are leap years 
                            tempDate = '29' + ':' + month + dateInput[5:10]
                        else: # Non-leap years only have 28 days in february
                            tempDate = '28' + ':' + month + dateInput[5:10]
                    else:
                        tempDate = 'ERROR' + month
            else: # Here we're just decrementing the day
                if int(dateInput[0] + dateInput[1]) - 1 < 10:
                    tempDate = '0' + str(int(dateInput[0] + dateInput[1]) -1) + dateInput[2:10]
                else:
                    tempDate = str(int(dateInput[0] + dateInput[1]) -1) + dateInput[2:10]
        else: # We are not crossing midnight
            tempDate = dateInput
        tempTimeStr = ''
        if tempTime < 10:
            tempTimeStr = '0' + str(tempTime)
        else:
            tempTimeStr = str(tempTime)
        returnTime = tempTimeStr + timeInput[2:10]
        returnDate = tempDate
        #print(returnDate, returnTime)
        if returnDate != dateInput:
            print(dateInput, returnDate)
        return returnTime, returnDate

    def _standardDeviation(self, intArray): # Returns the stdDev of an array
        # This is the root mean square formula
        sum = 0
        for x in intArray:
            sum = sum + (x-np.mean(intArray))**2
        return (np.sqrt(sum/len(intArray)) * np.sqrt(2)) # Adding in sqrt(2) to cancel out a log 2

    def _gaussian(self, intArray, dateArray=None, timeArray=None, graph=False): # returns an array of acceptable values within a gaussian "range"
        xpoints = []
        ypoints = []
        Amplitude = np.amax(intArray)
        sigma = self._standardDeviation(intArray)
        '''
        if dateArray == None: # Not used and redundant
            for x in intArray:
                xpoints.append(x)
                ypoints.append(Amplitude*np.exp(-(x-np.mean(intArray))**2 / (2*sigma**2))) # Taken from Professor To's Lecture4 ~ 19minutes 20seconds
            results = []
            for y in ypoints:
                if y >= np.mean(ypoints)-2*sigma or y <= np.mean(ypoints)+2*sigma: # if x is within two standard deviations away from the mean, then we'll keep the x, otherwise we won't keep it
                    results.append(x)
            return 
        '''
        if dateArray != None:
            resultsData, resultsDate, resultsTime = [], [], []# The results which fall within two standard deviations of the peak of the Gaussian curve
            if (2*sigma**2) == 0: # Can't divide by zero, and therefore we'll omit the data
                    return None, None, None
            for x in intArray:
                xpoints.append(x)
                ypoints.append(Amplitude*np.exp(-(x-np.mean(intArray))**2 / (2*sigma**2)))
            if graph: # If graph is true then we'll graph a gaussian curve
                xpointsNp, ypointsNp = np.array(xpoints), np.array(ypoints)
                title = 'Amplitude=' + str(Amplitude) + ' Sigma=' + str(sigma)
                self._graphGaussian(xpointsNp, ypointsNp, title) # Will display a Gaussian curve of the data
            for index, value in enumerate(ypoints): # Should be the same length as intArray, dateArray, and timeArray
                if value < Amplitude+(sigma*2): # If the y value is within two standard deviations from the peak of the Gaussian curve then we will keep that data point
                    if value > Amplitude-(sigma*2):
                        if intArray[index] == 0 or intArray[index] == -999: # Omitting data that is zero or -999
                            continue
                        resultsData.append(intArray[index])
                        resultsDate.append(dateArray[index])
                        resultsTime.append(timeArray[index])
            return resultsData, resultsDate, timeArray
        else:
            return None, None, None

    def _calculatePlot(self, head, dateHead, gaussianGraph=False, month0=None, month1=None, years=None): # Calculates the data for the plots but does not draw out the graphs, useful for calculating multiple graphs before displaying the data
        # TO DO list:
        # Convert Time to PST from GMT
        # Makes an empty tail end for some reason (What does that mean?)
        data = self.aeronetData.getFormattedData() # Acquire the data # Focus on just January to March
        timeHead = self.aeronetData.getTimeHeader()
        dataTemp, dataDate, dataTime = [], [], []
        for i in data: # Gaussian
            dataTemp.append(float(data[i][head])) # header 39, 41 from the tail
            #newTime, newDate = self._convertGMTtoPST(data[i][timeHead], data[i][dateHead])
            #dataDate.append(newDate)
            #dataTime.append(newTime)
            dataDate.append(data[i][dateHead])
            dataTime.append(data[i][timeHead])
        #print('Data: ', dataTemp, '\nDates: ', dataDate, '\nTimes: ', dataTime)
        #print(dataDate)
        tempData, tempDates, tempTime = self._gaussian(dataTemp, dataDate, dataTime, gaussianGraph) # Gives three outputs
        #currentDate = ''
        #evening = False # NOT USED
        xdata = [] # This will be dates
        ydata = [] # This will be the average of value for each day
        yDayMin = [] # This will be the minimum value for each day
        yDayMax = [] # This will be the maximum value for each day
        #dayRange = [] # The range of values for the day
        #timeOfDay = [] # The time range that corresponds to the day's range values
        dataRange = [] # The range of data from the day/night time
        nightTime = True # For time between 6pm and 6am, otherwise daytime is between 6am to 6pm
        if tempData == None: # Temporary(?) Bug Fix, Creating Dummy Arrays with bogus data
            xdata.append('01:01:1970')
            ydata.append(0)
            yDayMin.append(0)
            yDayMax.append(0)
            tempNpx = np.array(xdata)
            tempNpy = np.array(ydata)
            tempNpYerr = np.array([yDayMin, yDayMax])
            return tempNpx, tempNpy, tempNpYerr # Returning the dummy values since no real data was available
        
        for index, value in enumerate(tempData): # Compiling add data for mornings/evenings into a concise format
            #print(dataRange)
            #print(tempTime[index])
            if years != None:
                if int(tempDates[index][6:10]) < int(years):
                    continue
                elif int(tempDates[index][6:10]) > int(years):
                    break
            if month0 != None: # Checks to see if we are before the requested start month
                if int(tempDates[index][3] + tempDates[index][4]) < int(month0): # Skip data for months prior to month0
                    continue
            if month1 != None: # Checks to see if we have gone beyond the requested end month
                #print(int(tempDates[index][3] + tempDates[index][4]), int(month1))
                if int(tempDates[index][3] + tempDates[index][4]) > int(month1): # End data calculations after month1
                    break
                '''
                if years == None:
                    if int(tempDates[index][3] + tempDates[index][4]) < int(month0): # Skip data for months prior to month0
                        continue
                    elif int(tempDates[index][3] + tempDates[index][4]) > int(month1): # End data calculations after month1
                        break
                else:
                    if int(tempDates[index][7:10]) < int(years):
                        continue
                    elif int(tempDates[index][7:10]) > int(years):
                        break
                    if int(tempDates[index][3] + tempDates[index][4]) < int(month0): # Skip data for months prior to month0
                        continue
                    elif int(tempDates[index][3] + tempDates[index][4]) > int(month1): # End data calculations after month1
                        break
                '''
            #print('Acceptable: ', tempDates[index])
            # Check if the data is within a 2 day range
            '''
            if int(tempDate[index][0] + tempDate[index][1]) == tempDate[index-1]
            '''
            if nightTime: # If it was night time
                if int(tempTime[index][0]) == 0 and int(tempTime[index][1]) <= 5 or int(tempTime[index][0]) >= 1 and int(tempTime[index][1]) >= 8: # It is still night time
                        dataRange.append(tempData[index])
                else: # It is no longer night time
                    if np.sum(dataRange) != 0.0:
                        xdata.append(tempDates[index] + '_night')
                        ydata.append(np.sum(dataRange)/len(dataRange))
                        yDayMin.append(self._standardDeviation(dataRange))
                        yDayMax.append(self._standardDeviation(dataRange))
                    dataRange.clear()
                    nightTime = False
            else: # If it was day time
                if int(tempTime[index][0]) == 0 and int(tempTime[index][1]) >= 6 or int(tempTime[index][0]) == 1 and int(tempTime[index][1]) <= 7: # It is still day time
                        dataRange.append(tempData[index])
                else: # It is no longer day time
                    if np.sum(dataRange) != 0.0:
                        xdata.append(tempDates[index] + '_day')
                        ydata.append(np.sum(dataRange)/len(dataRange))
                        yDayMin.append(self._standardDeviation(dataRange))
                        yDayMax.append(self._standardDeviation(dataRange))
                    dataRange.clear()
                    nightTime = True
        '''
        for index, value in enumerate(tempData): # Compiling all data for one day into a concicse format
            if currentDate == '': # If this is the first item of data
                currentDate = tempDates[index]
                currentTime = tempTime[index]
                xdata.append(tempDates[index])
                dayRange.append(value)
                timeOfDay.append(tempTime[index])
                #if int(tempTime[index][0]) >= 1 and int(tempTime[index][1]) >= 8: # NOT USED
                    #evening = True
                #elif int(tempTime[index][0]) <= 0 and int(tempTime[index][1]) <= 5: # NOT USED
                    #evening = False
            elif tempDates[index] == currentDate: # For all cases with a date that matches the previous date
                dayRange.append(value)
                timeOfDay.append(tempTime[index])
                #if int(tempTime[index][0]) >= 1 and int(tempTime[index][1]) >= 8: # If time is greater than 6pm (18:00 military time)
                    #print(tempTime[index], ' is after 6pm.')
                    #evening = True
                #elif int(tempTime[index][0]) <= 0 and int(tempTime[index][1]) <= 5: # If time is not greater than 6pm
                    #print(tempTime[index], ' is before 6am.')
                    #evening = False
            elif tempDates[index] != currentDate: # For all new dates
                morning, evening = [], []
                for i, v in enumerate(dayRange): # Split's the day's values into two separate data points
                    if int(timeOfDay[i][0]) == 1 and int(timeOfDay[i][1]) >= 8: # This is evening
                        evening.append(v)
                    else: # All else is morning
                        morning.append(v)
                #print('Length of Morning Data: ', len(morning), 'Length of Evening Data: ',len(evening))
                if len(morning) != 0: # If the length of the data is 0 we don't need to calculate it
                    meanMorn = np.sum(morning) / len(morning)
                    ydata.append(meanMorn)
                    low = self._standardDeviation(morning)
                    yDayMin.append(low)
                    yDayMax.append(low)
                if len(evening) != 0: # If the length of the data is 0 we don't need to calculate it
                    meanEven = np.sum(evening) / len(evening)
                    ydata.append(meanEven)
                    low = self._standardDeviation(evening)
                    yDayMin.append(low)
                    yDayMax.append(low)
                if len(morning) != 0 and len(evening) != 0: # If we are adding both morning and evening calculations then we need another xdata, otherwise just the initial xdata will work
                    xdata.append(xdata[-1] + '_2')
                #mean = np.sum(dayRange) / len(dayRange)
                #ydata.append(mean)
                #low = self._standardDeviation(dayRange) #self._standardDeviationPerDay(dayRange, timeOfDay) , high
                #high = low
                #yDayMin.append(low)#(self._standardDeviation(dayRange))#(self._rootMeanSquare(dayRange))#(-0.5+np.sqrt(np.sum(dayRange)+0.25)) #(abs(np.amin(dayRange))) # -0.5+sqrt(dayRange+0.25) # Lecture 6 at 35:00 minute mark
                #yDayMax.append(high)#(self._standardDeviation(dayRange))#(self._rootMeanSquare(dayRange))#(0.5+np.sqrt(np.sum(dayRange)+0.25)) #(abs(np.amax(dayRange))) # 0.5+sqrt(dayRange+0.25) # Lecture 6 at 35:00 minute mark
                dayRange.clear()
                timeOfDay.clear()
                if int(tempDates[index][3]) == 1 or int(tempDates[index][4]) >= 4: # Restricts the range of months; WIll not calcualate for data beyond march #This should be temporary
                    #print('Breaking at: ', tempDates[index])
                    break
                xdata.append(tempDates[index]) # Adding the new day to the list of days
                currentDate = tempDates[index]
                if index == len(tempData)-1: # Special Case, if this is the last entry of the array and it is a different day than the previous day
                    ydata.append(value)
                    yDayMin.append(abs(value)) # Essentially there is no min/max
                    yDayMax.append(abs(value)) # Essentially there is no min/max
                    break
                else:
                    dayRange.append(value)
                    timeOfDay.append(tempTime[index])
            if index == len(tempData)-1: # If this is the last entry of the array and it is the same day as the previous day; Note: The entry's value has already been appended to the day's range
                mean = np.sum(dayRange) / len(dayRange)
                ydata.append(mean)
                low, high = self._standardDeviationPerDay(dayRange, timeOfDay) 
                yDayMin.append(low)#(self._standardDeviation(dayRange))#(self._rootMeanSquare(dayRange))#(-0.5+np.sqrt(np.sum(dayRange)+0.25)) #(abs(np.amin(dayRange))) # -0.5+sqrt(dayRange+0.25) # Lecture 6 at 35:00 minute mark
                yDayMax.append(high)#(self._standardDeviation(dayRange))#(self._rootMeanSquare(dayRange))#(0.5+np.sqrt(np.sum(dayRange)+0.25)) #(abs(np.amax(dayRange))) # 0.5+sqrt(dayRange+0.25) # Lecture 6 at 35:00 minute mark
                dayRange.clear()
        '''
        #print('Length of x: ', len(xdata), 'Length of y: ', len(ydata))
        #print(len(xdata), len(ydata))
        tempNpx = np.array(xdata) # The xData for the plot
        tempNpy = np.array(ydata) # The yData for the plot
        tempNpYerr = np.array([yDayMin, yDayMax]) # The yError Range for the plot
        return tempNpx, tempNpy, tempNpYerr

    def _graphGaussian(self, xpointsNp, ypointsNp, title): # Graphs a Gaussian curve
        plt.plot(xpointsNp, ypointsNp,'ko')
        plt.title(title)
        plt.get_current_fig_manager().set_window_title(title)
        plt.show()

    def _drawplot(self, head, xData, yData, tempNpYerr):
        # To-Do: (DONE)
            # Place horizontal bars on the error bars too
            # Place tick marks at the 1st and 15th of each month # Use the numerical day of the year
            # Use the root mean square to calculate the average for each day, use Gaussian for the overall data
        if len(xData) == 0: # If there is no xData, we will not attempt to create a graph
            return False
        months = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May.', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.'] # Used for tick labels
        count = 0
        previousCount = 1 # Start off with zero since we will be subtracting 1 from this at each new tickRange/Label and we want to include the first day
        tickRange = [] # The break points for our xaxis
        tickLabels = [] # The months that the break points will be using
        years = [] # A list of years that the data covers
        currentMonth = str(xData[0][3]) + str(xData[0][4])
        for index, day in enumerate(xData): # To make the break points (tickRange) for the months
            count += 1
            if day[4] != currentMonth[1]: # Any day where the month changes
                tickRange.append(previousCount-1) # Start of the month
                tickRange.append(previousCount + ((count - previousCount)/2)) # Middle of the month
                if currentMonth[0] == '0':
                    tickLabels.append(months[eval(currentMonth[1])-1] + str(xData[previousCount-1][0]) + str(xData[previousCount-1][1])) # Start of the month
                    tickLabels.append(months[eval(currentMonth[1])-1] + str(xData[previousCount + ((count - previousCount)//2)][0]) + str(xData[previousCount + ((count - previousCount)//2)][1])) # Middle of the month
                else:
                    tickLabels.append(months[eval(currentMonth[1])-1] + str(xData[previousCount-1][0]) + str(xData[previousCount-1][1])) # Start of the month
                    tickLabels.append(months[eval(currentMonth)-1] + str(xData[previousCount + ((count - previousCount)//2)][0]) + str(xData[previousCount + ((count - previousCount)//2)][1])) # Middle of the month
                currentMonth = str(day[3] + day[4])
                previousCount = count
            if index == len(xData) - 1: # The last day in the data list
                tickRange.append(previousCount-1) # Start of the month
                tickRange.append(previousCount + ((count - previousCount)/2)) # Middle of the month
                if currentMonth[0] == '0':
                    tickLabels.append(months[eval(currentMonth[1])-1] + str(xData[previousCount-1][0]) + str(xData[previousCount-1][1])) # Start of the month
                    tickLabels.append(months[eval(currentMonth[1])-1] + str(xData[previousCount + (len(xData) - previousCount) // 2][0]) + str(xData[previousCount + (len(xData) - previousCount) // 2][1])) # Middle of the month
                else:
                    tickLabels.append(months[eval(currentMonth[1])-1] + str(xData[previousCount-1][0]) + str(xData[previousCount-1][1])) # Start of the month
                    tickLabels.append(months[eval(currentMonth)-1] + str(xData[previousCount + (len(xData) - previousCount) // 2][0]) + str(xData[previousCount + (len(xData) - previousCount) // 2][1])) # Middle of the month
                previousCount = count
            if str(day[6] + day[7] + day[8] + day[9]) not in years:
                years.append(str(day[6] + day[7] + day[8] + day[9]))
        windowTitle = head + ' with ' + str(len(xData)) + ' data points'
        xaxisName = 'Months' #'Date dd:mm:yyyy'
        if 'nm' in head:
            yaxisName = 'Wavelength(nm)'
        elif 'µm' in head:
            yaxisName = 'Wavelength(µm)'
        elif 'cm' in head:
            yaxisName = 'Wavelength(cm)'
        elif 'hPa' in head:
            yaxisName = 'Pressure(hPa)'
        elif 'degrees_c' in head.lower():
            yaxisName = 'Celsius(°C)'
        elif 'angle' in head.lower():
            yaxisName = 'Angle(°)'
        elif 'longitude' in head.lower():
            yaxisName = 'Longitude(λ)'
        elif 'latitude' in head.lower():
            yaxisName = 'Latitude(Φ)'
        elif 'wavelength' in head.lower():
            yaxisName = 'Wavelength'
        else:
            yaxisName = ''
        if len(years) == 1: # If only one year was detected
            xaxisName = xaxisName + ' in ' + years[0]
        elif len(years) != 0: # Functionality for data with more than one year
            xaxisName = xaxisName + ' in ('
            for i in years:
                if i != years[-1]:
                    xaxisName = xaxisName + i + ', '
                elif i == years[len(years)-1]:
                    xaxisName = xaxisName + i + ')'
        cap = 2 # used for setting the cap sizes for the error bars
        #yDataFit = self._chiSquared(xData, yData)
        xData_poly = []
        for i, _ in enumerate(xData):
            xData_poly.append(i)
        '''
        degree= 8
        z = np.polynomial.Polynomial.fit(xData_poly, yData, degree)
        print(z)
        f = np.polynomial.Polynomial(z)
        xData_new = np.linspace(xData_poly[0], xData_poly[-1], len(xData))
        yData_new = f(xData_new)
        print('lengths: ', len(xData_new), len(yData_new))
        '''
        coeff, covariance = sp.optimize.curve_fit(self._myCurve_Polynomial, xData_poly, yData)
        '''
        print(coeff)
        yFit = self._myCurve_Polynomial(xData_poly, coeff[0], coeff[1], coeff[2], coeff[3], coeff[4], coeff[5])
        ssTot = np.sum((yData - np.mean(yData))**2)
        ssRes = np.sum((yData - yFit)**2)
        r2 = 1 - (ssRes/ssTot)
        print("R Squared: ", r2)
        '''
        #plt.plot(xData, yData, 'o', xData_new, yData_new)
        #print('lengths: ', len(xData_new), len(yData_new))
        #plt.errorbar(xData_new, yData_new, yerr=tempNpYerr, fmt='o', color='black', capsize=cap)
        #print(xData, '\n', yData, '\n', tickRange, '\n', tickLabels, '\n', len(xData), len(yData), len(tickRange), len(tickLabels))
        #plt.subplot(2,1)
        plt.errorbar(xData_poly, self._myCurve_Polynomial(xData_poly, coeff[0], coeff[1], coeff[2], coeff[3]), yerr=tempNpYerr, fmt='o', color='black', capsize=cap, markersize=3)
        plt.title(head)
        plt.xlabel(xaxisName)
        plt.ylabel(yaxisName)
        if len(tickRange) == len(tickLabels): # If for some reason the range is not in equal length to the labels, we won't do anything special to them
            plt.xticks(ticks = tickRange, labels = tickLabels, minor=False)
        plt.get_current_fig_manager().set_window_title(windowTitle)
        plt.get_current_fig_manager().resize(1280, 720)
        plt.show()
        return True # Successfully drawn
# end Analysis

class dataContainer:
    def __init__(self):
        self.version = ''
        self.location = ''
        self.AODLevel = ''
        self.description = ''
        self.contactInfo = ''
        self.reference = ''
        self.header = ''
        self.dateHeader = ''
        self.timeHeader = ''
        self.rawData = []
        self.dataLength = 0
        self.constructedData = {}
        self.formattedHeader = []
    
    def __del__(self):
        self.clear()
        del self.version
        del self.location
        del self.AODLevel
        del self.description
        del self.contactInfo
        del self.reference
        del self.header
        del self.dateHeader
        del self.timeHeader
        del self.rawData
        del self.dataLength
        del self.constructedData
        del self.formattedHeader

    def __len__(self):
        return self.dataLength

    def __str__(self):
        information = ''
        information += self.version + '\n'
        information += self.location + '\n'
        information += self.AODLevel + '\n'
        information += self.description + '\n'
        information += self.contactInfo + '\n'
        information += self.reference + '\n'
        information += self.header + '\n'
        #information += 'Quantity of data: ' + str(self.dataLength) + '\n' # Not a part of the original data
        for i in range(0, self.dataLength):
            if i == self.dataLength:
                information += self.rawData[i] # change to formatted data
            else:
                information += self.rawData[i] + '\n' # change to formatted data
        return information

    def __getitem__(self): # Not Implemented, Might not need
        pass

    def __setitem__(self): # Not Implemented, Might not need
        pass

    def setVersion(self, inputInfo):
        self.version = inputInfo

    def setLocation(self, inputInfo):
        self.location = inputInfo

    def setAODLevel(self, inputInfo):
        self.AODLevel = inputInfo

    def setDescription(self, inputInfo):
        self.description = inputInfo

    def setContactInfo(self, inputInfo):
        self.contactInfo = inputInfo

    def setReference(self, inputInfo):
        self.reference = inputInfo

    def setHeader(self, inputInfo):
        self.header = inputInfo

    def append(self, inputInfo):
        self.rawData.append(inputInfo)
        self.dataLength += 1

    def formatData(self):
        keys = []
        key = ''
        count = 0
        for c in self.header: # Parse header first
            if c != ',':
                key += c
            else:
                keys.append(key)
                key = ''
        keys.append(key) # Append the last key
        key = ''
        self.formattedHeader = keys
        for data in self.rawData: # Parse thru the list of data
            temp = {}
            values = []
            value = ''
            for c in data: # Parse thru each string of data
                if c != ',':
                    value += c
                else:
                    values.append(value)
                    value = ''
            values.append(value) # Append the last value
            value = ''
            for i in keys:
                for k in values:
                    temp[i] = k
                    values.remove(k)
                    break
            self.constructedData[count] = temp
            count += 1
        for head in self.formattedHeader: # Acquire the date and time header for future and easier acquisition
            if 'dd:mm:yyyy' in head:
                self.dateHeader = head
            elif 'hh:mm:ss' in head:
                self.timeHeader = head
            if self.dateHeader != '' and self.timeHeader != '':
                break

    def remove(self, line): # Not Implemented, Might not need
        pass

    def getFormattedHeader(self):
        return self.formattedHeader

    def getFormattedData(self):
        return self.constructedData

    def getDateHeader(self):
        return self.dateHeader
    
    def getTimeHeader(self):
        return self.timeHeader

    def clear(self):
        self.version = ''
        self.location = ''
        self.AODLevel = ''
        self.description = ''
        self.contactInfo = ''
        self.reference = ''
        self.header = ''
        self.dateHeader = ''
        self.timeHeader = ''
        self.rawData.clear()
        self.dataLength = 0
        self.constructedData.clear()
        self.formattedHeader.clear()
# end dataInformation

class Interface:
    @staticmethod
    def printMainMenu():
        print('\n')
        print('***************************************************',
        '\n',
        'Welcome to the Aeronet Data Analysis Program',
        '\n',
        '***************************************************',
        '\n',
        '[0] - Exit Program',
        '\n',
        '[1] - Help',
        '\n',
        '[2] - Load default file',
        '\n',
        '[3] - Select and load File',
        '\n',
        '[4] - Draw all plots',
        '\n',
        '[5] - Draw a specific plot of data',
        '\n',
        '[6] - Draw specific plots of data that contain a keyword',
        '\n',
        '[7] - Print Data',
        '\n')
    # end printMainMenu

    @staticmethod
    def analyticInterface():
        aeronetAnalyzer = Analysis()
        userInput = ''
        affirmativeAnswers = ['y', 'yes']
        months = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May.', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
        monthsLong = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
        
        while (userInput != 0): # If input is 0 the program will close.
            Interface.printMainMenu()
            userPrecheck = input('Option: ')
            userInput = ''
            userChoice, userChoice2, userChoice3, userChoice4 = '', '', '', ''
            userChoice5 = ''
            range0, range1 = None, None
            if (userPrecheck.isdigit()):
                userInput = int(userPrecheck)
            else:
                print('Invalid option selected.')
            
            if (userInput == 1): # help
                print(aeronetAnalyzer.help())
            elif (userInput == 2): # load default
                aeronetAnalyzer.readDataFromDefaultFile()
                print('Imported ', len(aeronetAnalyzer), ' lines of data.')
            elif (userInput == 3): # load requested
                fileLocation = input('What is the filename you wish to select? ')
                aeronetAnalyzer.selectAndReadFile(fileLocation)
                print('Imported ', len(aeronetAnalyzer), ' lines of data.')
            elif (userInput == 4): # draw all plots
                print('Calculating...')
                print('Successfully drew ', aeronetAnalyzer.drawAllPlots(), ' plots')
                #print('Successfully drew ', aeronetAnalyzer.drawAllPlotsMultProcessor(), ' plots') # WIP
            elif (userInput == 5): # draw graph of specific data
                listOfHeaders = aeronetAnalyzer.getHeaders()
                for i in listOfHeaders: # Printing options
                    if 'dd:mm:yyyy' in i:
                        dateHeader = i
                    elif 'hh:mm:ss' in i or 'day' in i.lower():
                        continue
                    else:
                        print(i)
                userChoice = input('What data would you like to plot? ')
                userChoice2 = input('Would you like to see the Gaussian Curve plot? ')
                userChoice3 = input('What starting month are you looking for? ')
                userChoice4 = input('What ending month are you looking for? ')
                #userChoice5 = input('For which years?? ')
                if userChoice == '':
                    print('Please make a selection.')
                    continue
                print('Calculating...')
                drawn = False
                for i in listOfHeaders: # Drawing the user's choices
                    if 'dd:mm:yyyy' in i or 'hh:mm:ss' in i or 'day' in i.lower(): # Skipping these three since we don't want to use them for drawing plots
                        continue
                    elif userChoice.lower() == i.lower():
                        if userChoice2.lower() in affirmativeAnswers: # If the user wants to see the gaussian curves
                            if userChoice3.lower() in monthsLong and userChoice4.lower() in monthsLong:
                                for index, value in enumerate(monthsLong):
                                    if userChoice3.lower() == value:
                                        range0 = index+1
                                    if userChoice4.lower() == value:
                                        range1 = index+1
                            elif userChoice3.lower() in months and userChoice4.lower() in months:
                                for index, value in enumerate(months):
                                    if userChoice3.lower() == value:
                                        range0 = index+1
                                    if userChoice4.lower() == value:
                                        range1 = index+1
                            if aeronetAnalyzer.drawSpecificPlot(i, dateHeader, True, monthStart=range0, monthEnd=range1):
                                drawn = True
                                break
                        elif aeronetAnalyzer.drawSpecificPlot(i, dateHeader, monthStart=range0, monthEnd=range1):
                            drawn = True
                            break
                if drawn:
                    print('Successfully drew 1 plot.')
                else:
                    print('Invalid data choice.')
            elif (userInput == 6): # draw graphs of data that contain the keyword
                listOfHeaders = aeronetAnalyzer.getHeaders()
                for i in listOfHeaders: # Printing options
                    if 'dd:mm:yyyy' in i:
                        dateHeader = i
                    elif 'hh:mm:ss' in i or 'day' in i.lower():
                        continue
                    else:
                        print(i)
                userChoice = input('What data would you like to plot? ')
                userChoice2 = input ('Would you like to see the Gaussian Curve plots? ')
                userChoice3 = input('What starting month are you looking for? ')
                userChoice4 = input('What ending month are you looking for? ')
                userChoice5 = input('What year do you want to see? ')
                if userChoice == '':
                    print('Please make a selection.')
                    continue
                print('Calculating...')
                heads = []
                for i in listOfHeaders: # Drawing the user's choices
                    if 'dd:mm:yyyy' in i or 'hh:mm:ss' in i or 'day' in i.lower(): # Skipping these three since we don't want to use them for drawing plots
                        continue
                    elif userChoice.lower() in i.lower():
                        heads.append(i)
                count = 0
                if len(heads) != 0:
                    if userChoice2.lower() in affirmativeAnswers: # If the user wants to see the gaussian curves
                        if userChoice3.lower() in monthsLong and userChoice4.lower() in monthsLong:
                            for index, value in enumerate(monthsLong):
                                if userChoice3.lower() == value:
                                    range0 = index+1
                                if userChoice4.lower() == value:
                                    range1 = index+1
                        elif userChoice3.lower() in months and userChoice4.lower() in months:
                            for index, value in enumerate(months):
                                if userChoice3.lower() == value:
                                    range0 = index+1
                                if userChoice4.lower() == value:
                                    range1 = index+1
                        if userChoice5 == '':
                            count = aeronetAnalyzer.drawSpecificPlots(heads, dateHeader, True, monthStart=range0, monthEnd=range1)
                        else:
                            count = aeronetAnalyzer.drawSpecificPlots(heads, dateHeader, True, monthStart=range0, monthEnd=range1, year=userChoice5)
                    else:
                        if userChoice3.lower() in monthsLong and userChoice4.lower() in monthsLong:
                            for index, value in enumerate(monthsLong):
                                if userChoice3.lower() == value:
                                    range0 = index+1
                                if userChoice4.lower() == value:
                                    range1 = index+1
                        elif userChoice3.lower() in months and userChoice4.lower() in months:
                            for index, value in enumerate(months):
                                if userChoice3.lower() == value:
                                    range0 = index+1
                                if userChoice4.lower() == value:
                                    range1 = index+1
                        if userChoice5 == '':
                            count = aeronetAnalyzer.drawSpecificPlots(heads, dateHeader, monthStart=range0, monthEnd=range1)
                        else:
                            count = aeronetAnalyzer.drawSpecificPlots(heads, dateHeader, monthStart=range0, monthEnd=range1, year=userChoice5)  
                if count != 0:
                    print('Successfully drew ', count, ' plots.')
                else:
                    print('Invalid data choice.')
            elif (userInput == 7): # print the raw data
                print(aeronetAnalyzer)
                print(len(aeronetAnalyzer), ' lines of data are loaded.')
            elif (userInput == 8): # WIP, print only the most recent month
                currentMonth = time.localtime(time.time()).tm_mon
                currentYear = time.localtime(time.time()).tm_year
                listOfHeaders = aeronetAnalyzer.getHeaders()
                for i in listOfHeaders: # Printing options
                    if 'dd:mm:yyyy' in i:
                        dateHeader = i # Not really needed, change in the future
                    elif 'hh:mm:ss' in i or 'day' in i.lower():
                        continue
                    else:
                        print(i)
                print('The current month is ', monthsLong[currentMonth-1], currentMonth, 'And the current year is ', currentYear)
                userChoice = input('What data would you like to plot? ')
                userChoice2 = input ('Would you like to see the Gaussian Curve plots? ')
                if userChoice == '':
                    print('Please make a selection.')
                    continue
                print('Calculating...')
                heads = []
                for i in listOfHeaders: # Drawing the user's choices
                    if 'dd:mm:yyyy' in i or 'hh:mm:ss' in i or 'day' in i.lower(): # Skipping these three since we don't want to use them for drawing plots
                        continue
                    elif userChoice.lower() in i.lower():
                        heads.append(i)
                count = 0
                if len(heads) != 0:
                    if userChoice2.lower() in affirmativeAnswers: # If the user wants to see the gaussian curves
                        count = aeronetAnalyzer.drawSpecificPlots(heads, dateHeader, True, monthStart=currentMonth, monthEnd=currentMonth, year=currentYear)
                    else:
                        count = aeronetAnalyzer.drawSpecificPlots(heads, dateHeader, False, monthStart=currentMonth, monthEnd=currentMonth, year=currentYear)
                if count != 0:
                    print('Successfully drew ', count, ' plots.')
                else:
                    print('Invalid data choice.')
            elif (userInput == 9):
                listOfHeaders = aeronetAnalyzer.getHeaders()
                for i in listOfHeaders: # Printing options
                    if 'dd:mm:yyyy' in i or 'hh:mm:ss' in i or 'day' in i.lower():
                        continue
                    else:
                        print(i)
                userChoice = input('What data would you like to see? ')
                heads = []
                for i in listOfHeaders: # Drawing the user's choices
                    if 'dd:mm:yyyy' in i or 'hh:mm:ss' in i or 'day' in i.lower(): # Skipping these three since we don't want to use them for drawing plots
                        continue
                    elif userChoice.lower() in i.lower():
                        heads.append(i)
                aeronetAnalyzer.printSpecificData(heads)
        print('Exiting Program.')
    # end dataInterface()
# end Interface

if __name__ == "__main__":
    Interface.analyticInterface()
