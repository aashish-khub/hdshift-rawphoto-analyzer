#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 16:55:35 2022

@author: aashishk29
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import rawpy
from matplotlib.widgets import TextBox


def getPhoto(filePath, savePath):
    raw = rawpy.imread(filePath)
    print("Loaded up Photo. Post-processed image looks like:")
    plt.figure()
    plt.imshow(raw.postprocess(use_camera_wb=True))
    plt.show()
    plt.savefig(savePath)
    return raw

def splitToRGB(raw):
    rawimg = raw.raw_image
    bayer = raw.raw_colors
    rows = len(rawimg)
    cols = len(rawimg[0])
    print("Rows, Cols respectively are:")
    print(rows,cols) 
    Rarr = np.zeros((rows//2, cols//2),dtype=rawimg.dtype) #one quarter: upper l
    Garr = np.zeros((rows//2, cols),dtype=rawimg.dtype) #two quarters: upper r, lower l
    Barr = np.zeros((rows//2, cols//2),dtype=rawimg.dtype) #one quarter: lower r
    
    flatRaw = rawimg.flatten()
    flatBayer = bayer.flatten()

    flatRarr = Rarr.flatten()
    flatGarr = Garr.flatten()
    flatBarr = Barr.flatten()
    
    assert(len(flatRaw)==len(flatBayer))

    #keep these moving pointers to show where we are:
    rP = 0
    gP = 0
    bP = 0

    for i in range(len(flatRaw)):
        iVal = flatRaw[i]
        color = flatBayer[i]
        if color==0:
            flatRarr[rP] = iVal
            rP +=1
        elif color==1:
            flatGarr[gP] = iVal
            gP +=1
        elif color==2:
            flatBarr[bP] = iVal
            bP +=1
        else:
            print(color)
            raise Exception("Invalid Color Error!")
            
    Rarr = np.flip(np.reshape(flatRarr,Rarr.shape),1)
    Garr = np.flip(np.reshape(flatGarr,Garr.shape),1)
    Barr = np.flip(np.reshape(flatBarr,Barr.shape),1)
    
    return(Rarr,Garr,Barr)


def refMaxPlot(Rarr,Garr,Barr,fig=None):
    '''
        Plot the max by column approach (for reference only!)
    '''
    maxRbr = np.amax(Rarr,axis=1)
    maxGbr = np.amax(Garr,axis=1)
    maxBbr = np.amax(Barr,axis=1)
    plt.figure()
    plt.plot(maxRbr,'r')
    plt.plot(maxGbr,'g')
    plt.plot(maxBbr,'b')
    return 1

def submitColorChoice(text):
    print("Received Text: "+ text)
    global colorChoice
    if text in ['r','g','b']:
        colorChoice = text

def submitDataExtractRequest(text):
    print("Received Text: "+ text)
    global extractStatus 
    if(text[0] == 'b'): #"bye" command!
        global nextPhotoGo
        nextPhotoGo = True
    if(text[0] == 'p'):
        xLims = ax.get_xlim()
        print("Fetched xLims: "+str(xLims))
        yLims = ax.get_ylim()
        print("Fetched yLims: "+str(yLims))
        xMin = int(xLims[0])
        xMax = int(xLims[1])
        yMin = int(yLims[1])
        yMax = int(yLims[0])
        global arr
        subset = arr[yMin:yMax, xMin:xMax]
        mu = np.mean(subset)
        sd = np.std(subset)
        print("Mean = " + str(mu))
        print("StDv = " + str(sd))
        global logWriter
        logWriter.write("Comment: " + text[1:] + "\n")
        logWriter.write("Mean = " + str(mu) + "\n")
        logWriter.write("StDv = " + str(sd) + "\n")
        logWriter.write("\n")


## BEGIN SCRIPT ###
RAWIMAGEPATH = "./images/"
NEWPHOTOPATH = "./processed/"
LOGFILE = "./log.txt"
files = [f for f in os.listdir(RAWIMAGEPATH)]
files.sort()
files = files

for fileName in files:
    plt.close('all')
    logWriter = open(LOGFILE, "a")
    processedFilePath = NEWPHOTOPATH + fileName.split(".")[0]+".jpg"
    raw = getPhoto(RAWIMAGEPATH + fileName, processedFilePath) 
    logWriter.write("Opening File: "+ fileName + "\n")
    r,g,b = splitToRGB(raw)
    print("RGB Arrays produced.")
    refMaxPlot(r,g,b)
    plt.subplots_adjust(bottom=0.2)
    colorChoice = "unchosen"
    axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
    text_box = TextBox(axbox, 'Choose Focus Plot: ', initial="[r], [g], or [b]")
    text_box.on_submit(submitColorChoice)
    plt.show()
    while colorChoice == "unchosen":
        print("Please choose a color!")
        plt.pause(5)
    plt.close() #choice is complete! 
    letterMap = {'r': r, 'g': g, 'b': b}
    arr = letterMap[colorChoice]
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)
    plt.imshow(arr,cmap='hot')
    nextPhotoGo = False
    axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
    text_box = TextBox(axbox, 'Type p, hit enter', initial="[p]")
    text_box.on_submit(submitDataExtractRequest)
    plt.show()
    while not nextPhotoGo:
        plt.pause(5)
    logWriter.close()


#pickPlotToStudy('a')

