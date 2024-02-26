# SalesforceFlowAnalysis
A collection of scripts and rulesets to use over Salesforce Flow XML Metadata to identify flows that are not following various best practices.

## March 2022: Initial Stage ##  
Starting with something simple, that is often a go-to manual check in an org review or an analysis of current state of scalability. 

## Feb 2024: Loop Finder 2.0 and Missing Entry Criteria Finder ##  
Fixed the narrow version of the loop finder to account for more accurate scenarios such as referencing the Loop directly in input values in DML elements, as opposed to just filter values, and referencing loop single variables in input and filter elements. This still does not identify loop name or loop single variable references inside of flow formulas. 

Missing Entry Criteria class added to output a list of record-triggered flows that don't have entry critera as another starting point for improving an org's process automation performance or assessing quality and efficiency.

**Unscalable Flow Identifier: SOQL or DML inside of Loops**  
Currently we can identify Get Records, Create Records, Update Records, and Delete Records elements inside of Loops based on an explicit reference to the Loop or Loop item inside of the element

Example of a Loop tag within a Flow XML file (with invalid replaced names):
```
<Flow .....
    <loops>
        <name>Loop Name</name>
        <label>Loop Name</label>
        <locationX>176</locationX>
        <locationY>278</locationY>
        <collectionReference>Collection Variable</collectionReference>
        <iterationOrder>Asc</iterationOrder>
        <nextValueConnector>
            <targetReference>Next Element Name</targetReference>
        </nextValueConnector>
        <noMoreValuesConnector>
            <targetReference>The Next Element after the Last Item</targetReference>
        </noMoreValuesConnector>
    </loops>
```

Example of a Get Records (SOQL) referencing a Loop item (with invalid replaced names) in Filters:
```
<Flow ...    
    <recordLookups>
        <name>Element Name</name>
        <label>Element Name</label>
        <locationX>264</locationX>
        <locationY>854</locationY>
        <assignNullValuesIfNoRecordsFound>false</assignNullValuesIfNoRecordsFound>
        <connector>
            <targetReference>Next Element Name</targetReference>
        </connector>
        <filterLogic>and</filterLogic>
        <filters>
            <field>Id</field>
            <operator>EqualTo</operator>
            <value>
                <elementReference>Loop Name</elementReference>
            </value>
        </filters>
        <object>Object API Name</object>
        <outputAssignments>
            <assignToReference>Variable Name</assignToReference>
            <field>Field API Name</field>
        </outputAssignments>
    </recordLookups>
```
Example of a Loop defining a single variable and a Create Records (DML) referencing that loop's single variable (with invalid replaced names) in Values:
```
<loops>
        <name>Loop_Accounts</name>
        <label>Loop Accounts</label>
        <locationX>1969</locationX>
        <locationY>1156</locationY>
        <assignNextValueToReference>singleLoopVariable</assignNextValueToReference>
        <collectionReference>get_accounts</collectionReference>
        <iterationOrder>Asc</iterationOrder>
        <nextValueConnector>
            <targetReference>get_contacts</targetReference>
        </nextValueConnector>
        <noMoreValuesConnector>
            <targetReference>update_flow_stage</targetReference>
        </noMoreValuesConnector>
    </loops>
……
<recordCreates>
        <name>Create_Contact</name>
        <label>Create Contact</label>
        <locationX>2094</locationX>
        <locationY>1340</locationY>
        <connector>
            <targetReference>Loop_Accounts</targetReference>
        </connector>
        <inputAssignments>
            <field>OwnerId</field>
            <value>
                <elementReference>singleLoopVariable.OwnerId</elementReference>
            </value>
        </inputAssignments>
        <inputAssignments>
            <field>Type</field>
            <value>
                <elementReference>AccountOwner</elementReference>
            </value>
        </inputAssignments>
        <object>Contact</object>
        <storeOutputAutomatically>true</storeOutputAutomatically>
    </recordCreates>
```

**Future Additions:**  
- Another way to identify if an element is in a Loop is to follow the elements from the start of the Loop to then end of the Loop using the targetReference values within the nextValueConnector at the start, the Connector tags in the subsequent elements. This will catch any elements within the Loop that don't explicitly reference the Loop itself or the Loop item variable.  
- SOQL/DML Elements that use a loop item reference inside a Formula variable, which would require checking for variable names in potential elements, checking <formulas> for those names and checking loop item name in the expression.
