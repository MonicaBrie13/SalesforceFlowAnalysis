##############################################################################
#Author: Monica Thornton Hill 
#Date: March 2022
#Description: This parses through individual flow xml files from Salesforce locally, creating a new txt file output 
#of all the flows that have SOQL and DML elements adjacent to Loop elements to help identifiy potentially flows that 
#have SOQL or DML inside Loops.
#Disclaimer: I'm not a Python developer. Attempt #1. 
##############################################################################


#PREP: In Finder, select all returned flows in flows folder and replace .flow with .xml
#To Call in Terminal: python3 UnscalableLoopFinder_Broad.py "File Path to Flows" "Output File Name"
#Example file path: /Users/username/Desktop/OrgName/PackageName/flows


import xml.etree.ElementTree as ET
from sys import argv
from pathlib import Path

NAMESPACE = '{http://soap.sforce.com/2006/04/metadata}'
#path to folder with flows
flowsPath = Path(argv[1])


#Get all loop names in a flow XML file
def processRoots(folderPath,infile):
    # ET.parse(infile) is the tree and is uneeded
    root = ET.parse(folderPath / infile).getroot()
    # print(root)
    # "list comprehension" - python list creation in one line
    loopList = [loop.find(f'{NAMESPACE}name').text for loop in root.findall(f'{NAMESPACE}loops')]
    return root, loopList


#Iterate through the loops tags' names to check for any references in record Flow Elements
def processRecordLoop(root, loopList, targetElement):
    for loopName in loopList:
        potentialLoops = root.findall(f'{NAMESPACE}{targetElement}/{NAMESPACE}connector/{NAMESPACE}targetReference')
        for potentialLoop in potentialLoops:
            if potentialLoop.text == loopName:
                return True
    return False


#Create new file for list of file names and identified bad practice
def outputToFile(infile,identifier,orgName):
    # a = append / Later: Create xlxs file and add counter for each identified issue
    with open(f'FlowLoopResults-Broad-{orgName}.txt', 'a') as outfile:
        outfile.write(f'{identifier} : {infile}\n')
        print(f'{identifier} : {infile}')


#main function
def processOutput(folderPath,infile,orgName):
    root, loopList = processRoots(folderPath,infile)
    status = root.find(f'{NAMESPACE}status').text

    flowFound = False

    if status == 'Active':
        #Record Lookups Elements - SOQL Check
        if processRecordLoop(root, loopList, 'recordLookups'):
            flowFound = True
            outputToFile(infile,'SOQL',orgName)
            
        #Record Create Elements - DML Check
        if processRecordLoop(root, loopList, 'recordCreates'):
            flowFound = True
            outputToFile(infile,'DML ',orgName)

        #Record Delete Elements - DML Check
        if processRecordLoop(root, loopList, 'recordDeletes'):
            flowFound = True
            outputToFile(infile,'DML ',orgName)
    
    return flowFound

#iterate directory - go through all the files in the folder above and call the main function
overallFlowFound = False
for filePath in flowsPath.iterdir():
    flowFound = processOutput(flowsPath, filePath.name, argv[2])
    if flowFound:
        overallFlowFound = True
    #print(f'{overallFlowFound} - {flowFound}')
    #Later: Add Count in processOutput for each SOQL and DML found 

if not overallFlowFound:
    print('No Active Flows with identified SOQL or DML statements inside Loops.')
