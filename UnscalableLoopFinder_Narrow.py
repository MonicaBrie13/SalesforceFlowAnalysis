##############################################################################
#Author: Monica Thornton Hill 
#Date: Feb 2024
#Description: Identify SOQL and DML inside of Loops in Salesforce Flows
#Currently this program only identifies SOQL/DML elements that explicity reference a loop, 
#not SOQL/DML inside of loops that don't use the loop item which does seem to happen.
#Disclaimer: I'm not a Python developer. Attempt #2.

#Current State: Get Loop Names and Loop single variables if defined to check against SOQL/DML Elements [elementtype]->filters->value>elementReference 
#Unaccounted for Element in Loop check: Get SOQL/DML Element names to check against Loops->nextValueConnector->targetReference

#TO ADD LATER: To catch elements inside loop not explicitly referencing the Loop -
# For any elements identified from the above's Current State check - get element Name
# Use name to check if there are any subsquent elements (connector->targetReference = [name])
# that are NOT the noMoreValuesConnector->targetReference value in any of the <loops> tags because those elements are outside of the loop

#Other Scenario to consider: SOQL/DML Element that uses a loop item reference inside a formula variable or loop item reference
#which would require checking for variable names in those elements that have loop items
#<assignNextValueToReference> in <loops> for loop item variable name
##############################################################################


#PREP: In Finder, select all returned flows in flows folder and replace .flow with .xml
#To Call in Terminal: python3 UnscalableLoopFinder_Narrow.py "File Path to Flows" "Output File Label"
#Example file path: /Users/username/Desktop/OrgName/PackageName/flows
#Example output file name: FlowLoopResults-Narrow-DevSandboxA.txt


from sys import argv
from pathlib import Path
import xml.etree.ElementTree as ET

NAMESPACE = '{http://soap.sforce.com/2006/04/metadata}'
LOOPS = f'{NAMESPACE}loops'
LOOP_NAME = f'{NAMESPACE}name'
LOOP_VARIABLE = f'{NAMESPACE}assignNextValueToReference'
FILTERS_ELEMENT_REFERENCE = f'/{NAMESPACE}filters/{NAMESPACE}value/{NAMESPACE}elementReference'
INPUTS_ELEMENT_REFERENCE = f'/{NAMESPACE}inputAssignments/{NAMESPACE}value/{NAMESPACE}elementReference'


def findAllLoops(folderPath, infile):
    root = ET.parse(folderPath / infile).getroot()
    # not all loops have assignNextValue aka a single loop variable defined... loop.find will return None if none are found
    loopVariableNames = [loop.find(LOOP_VARIABLE) for loop in root.findall(LOOPS)]
    return root, [loop.find(LOOP_NAME).text for loop in root.findall(LOOPS)] + \
                 [loopVariable.text for loopVariable in loopVariableNames if loopVariable is not None]


def containsCheck(strings, sub):
    # generator to check if string is found in the reference - https://stackoverflow.com/questions/13779526/finding-a-substring-within-a-list-in-python
    return next((s for s in strings if sub in s), None)


#Iterate through the loops tags' names to check for any references in record Flow Elements
def elementCheck(root, loopList, targetElement):
    def elementCheckHelper(elementReferenceType):
        elementReferences = root.findall(f'{NAMESPACE}{targetElement}{elementReferenceType}')
        return [x for x in loopList if containsCheck([potential.text for potential in elementReferences], x)]
    # Filter references are used in SOQL directly in Get Records Elements or as part of DML Elements
    # Input references are used in DML Elements
    bad_filters = elementCheckHelper(FILTERS_ELEMENT_REFERENCE)
    bad_inputs = elementCheckHelper(INPUTS_ELEMENT_REFERENCE)
    return (bad_filters != []) or (bad_inputs != [])


#Create new file for list of file names and identified bad practice
def outputToFile(infile, identifier, orgName):
    # a = append / Later: Create xlxs file and add counter for each identified issue
    with open(f'FlowLoopResults-Narrow-{orgName}.txt', 'a') as outfile:
        outfile.write(f'{identifier} : {infile}\n')
        print(f'{identifier} : {infile}')


def loopCheck(folderPath, infile, orgName):
    root, loopList = findAllLoops(folderPath, infile)
    flowFound = False

    def processToOutput(targetElement, identifier):
        if elementCheck(root, loopList, targetElement):
            outputToFile(infile, identifier, orgName)
            nonlocal flowFound
            flowFound = True

    if root.find(f'{NAMESPACE}status').text == 'Active':
        # check all Get Records elements
        processToOutput('recordLookups', 'SOQL')
        # check all Create/Update/Delete Records elements
        processToOutput('recordCreates', 'DML ')
        processToOutput('recordDeletes', 'DML ')
        processToOutput('recordUpdates', 'DML ')
    
    return flowFound


def commandLineParser(flowsPath, orgName):
    overallFlowFound = False
    #iterate directory - go through all the files in the folder above and call the main function
    #only look at xml files
    for filePath in [f for f in flowsPath.iterdir() if f.suffix == '.xml']:
        if loopCheck(flowsPath, filePath.name, orgName):
            overallFlowFound = True
    return overallFlowFound


if __name__ == "__main__":
    overallFlowFound = commandLineParser(Path(argv[1]), argv[2])
    if not overallFlowFound:
        print('No Active Flows with identified SOQL or DML statements inside Loops.')
