# SalesforceFlowAnalysis
A collection of scripts and rulesets to use over Salesforce Flow XML Metadata to identify flows that are not following various best practices.

## March 2022: Initial Stage ##  
Starting with something simple, that is often a go-to manual check in an org review or an analysis of current state of scalability. 

**Unscalable Flow Identifier: SOQL or DML inside of Loops**  
Currently we can identify Get Records, Create Records, Update Records, and Delete Records elements inside of Loops based on an explicit reference to the Loop item inside of the element

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

Example of a Get Records (SOQL) referencing a Loop item (with invalid replaced names):
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

**Future Additions:**  
- Another way to identify if an element is in a Loop is to follow the elements from the start of the Loop to then end of the Loop using the targetReference values within the nextValueConnector at the start, the Connector tags in the subsequent elements. This will catch any elements within the Loop that don't explicitly reference the Loop itself or the Loop item variable.  
- SOQL/DML Elements that use a loop item reference inside a Formula variable, which would require checking for variable names in potential elements, checking <formulas> for those names and checking loop item name in the expression.
