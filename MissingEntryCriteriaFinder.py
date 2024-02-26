#Find any record-triggered flows without starting entry criteria aka flows that always run without any condition check

#PREP: In Finder, select all returned flows in flows folder and replace .flow with .xml
#To Call in Terminal: python3 MissingEntryCriteriaFinder.py "File Path to Flows" "Output File Label"
#Example file path: /Users/username/Desktop/OrgName/PackageName/flows
#Example outout file name: FlowResults_MissingEntryCriteria-DevSandboxA.txt with DevSandboxA as the provided input


from sys import argv
from pathlib import Path
import xml.etree.ElementTree as ET

NAMESPACE = '{http://soap.sforce.com/2006/04/metadata}'
TRIGGERTYPE_REFERENCE = f'{NAMESPACE}start/{NAMESPACE}recordTriggerType'
FILTER_REFERENCE = f'{NAMESPACE}start/{NAMESPACE}filters'


#Create new file for list of file names of flows missing entry conditions in their start element
def outputToFile(infile, orgName):
    # a = append / Later: Create xlxs file and add counter for each identified issue
    with open(f'FlowResults_MissingEntryCriteria-{orgName}.txt', 'a') as outfile:
        outfile.write(f'{infile}\n')
        print(f'{infile}')

        
def entryFilterCheck(folderPath, infile, orgName):
    root = ET.parse(folderPath / infile).getroot()
    flowFound = False

    if root.find(f'{NAMESPACE}status').text == 'Active' and (root.find(TRIGGERTYPE_REFERENCE) is not None):
       # check for entry criteria
      if root.find(FILTER_REFERENCE) is None:
            outputToFile(infile, orgName)
            flowFound = True
    
    return flowFound


def commandLineParser(flowsPath, orgName):
    overallFlowFound = False
    #iterate directory - go through all the files in the folder above and call the main function
    #only look at xml files
    for filePath in [f for f in flowsPath.iterdir() if f.suffix == '.xml']:
        if entryFilterCheck(flowsPath, filePath.name, orgName):
            overallFlowFound = True
    return overallFlowFound


if __name__ == "__main__":
    overallFlowFound = commandLineParser(Path(argv[1]), argv[2])
    if not overallFlowFound:
        print('No Active Record-Triggered Flows with missing entry criteria.')
