# GitHub repo for collaboration on developing a semantic version for ISO 14224 

## Goals

1. Build and publish a machine-readable version of definitions and concepts in ISO 14224 :2016 (version reconfirmed in 2022). This will encourage shared use of the IRIs provided for the terms. This version will NOT be aligned to any top level ontology. This work is well underway and the results contained in this repo.

2. Publish machine-interpretable versions of the .ttl files in 1. aligned to each of the top level ontologies: IDO, BFO/IDO and DOLCE. This is future work.

## What is ISO 14224?

ISO 14224:2016 is a standard for the collection of reliability and maintenance (RM) data in a standard format for equipment in all facilities and operations. ISO 14224:2016 is widely used within the petroleum, natural gas and petrochemical industries during the operational life cycle of equipment and has also seen adoption in the mining industry.

ISO 14224 provides definitions that constitute a "reliability language" that can be useful for communicating operational experience. The failure modes defined in the normative part of this International Standard can be used as a "reliability thesaurus" for various quantitative as well as qualitative applications.

Standardization of data collection practices facilitates the exchange of information between parties, e.g. plants, owners, manufacturers and contractors. Controlled vocabularies and consistent interpretation of codes is increasingly recognized as a necessary foundation for enterprise generative AU models.

ISO 14224 provides tables for the following data:

a) equipment data, e.g. equipment taxonomy, equipment attributes;

b) failure data, e.g. failure cause, failure consequence;

c) maintenance data, e.g. maintenance action, resources used, maintenance consequence, down time.

There data are used for tracking and investigating reliability issues, calculating equipment and system availability, maintenance management metrics, and events with safety and environmental impacts.

## Motivations

*What is the problem*

Tables capturing failure-related data are often created and maintained ad hoc across teams, departments and organisations. Manual handling of large, unstandardised spreadsheets is time-consuming and error-prone, prompting interest from organisations in using automated and AI-based systems for querying this data.

*What is the opportunity*

There are several opportunities for a shared industry project to improve machine readability of FMEA and maintenance work order data that reference the ISO 14224 standard. In order of technical complexity from technically simple to complex these are

*What's the Value*
The business value of this step is that every organisation (and even engineers within an organisation) keep their own versions of ISO 14424 in database tables and Excel spreadsheets with their own entity type labels and column headings, as well as codes resulting in challenges for humans, let alone AI to determine if the terms are semantically the same.

*Why Linked data?*: this would be a major step forward in providing a shared, open, stable and managed resource, such as a GitHub page that engineers could reference to ensure a shared interpretation of a term. Challenges include where to host it (neither ISO or IEC provide suitable namespaces and IRI hosting capabilities at present) and how to provide trust for enterprises on how it will be maintained, and how updates will be managed.

*Why RDF triple stores?*

The ability to have data in the form of RDF triple stores allows for SHACL to be used for data quality checks. SPARQL can also be used to find and retrieve data with greater precision.

## Purpose of this repo

The purposes of this repo are:

1. to provide **stable** Linked Data and IRIs for:

- 53 terms used in the Terms and Definitions (Clause 3) section of ISO 14224, and 
- Text in tables relating to the classification of failure modes, failure mechanisms and failure causes contained in Appendix B, of the ISO 14224:2016 standard. 
- All the Level 6 and 7 Equipment Classes in Appendix A.
- Cross references for the information in Appendix B Tables B6-B10 on which Failure Mode Codes can be used for which Equipment Classes.

The namespace iso14224.org has been purchased by the GitHub repo owner for this purpose.

2. to provide example data and competency questions from FMEA and Maintenance work order tables from industry that include concepts represented in ISO 14224.

3.  Develop models based on 1. and 2. aligned to different top level ontologies - IDO, IOF and DOLCE. Use the examples in 2. to understand the impact of modelling decisions.

4. Present the outcomes of experiments using ChatGPT (LLMs) to see how the LLMs perform with and without the i14224.ttl files. 


## Outputs
The current RDL files are available in ttl format in the \inDevelopment subdirectory. When they are final they will be moved to the \ontology subdirectory.

The experiment files are in the \experiment subdirectory. Please read the readme for a summary of the results


## Namespace and file names

*i14224_clause3.ttl* Terms and definitions  - modelled as OWL classes, object properties and annotation properties. Contains the `https://iso14224.org/ontology/i14224/ont/clause3` ontology.

*i14224_appendixA.ttl* - data from Appendix A on all the Level 6 and 7 Equipment Class and categories

*i14224_appendixB.ttl* - data from tables in ISO 14224 Annex B for example on Failure modes and Mechanisms - modelled as OWL classes and named individuals. Contains the `https://iso14224.org/ontology/i14224/ont/appendixB` ontology

*i14224_appendixB_allowed_failure_modes.ttl* - as the name suggests these are lists of the allowable failure modes for each Equipment Class.

*i14224_failure_mode_validation_shape.ttl* - SHACL shape code to constraint check if valid equipment class and failure mode codes have been used.

The iso14224.org namespace was purchased to enable future resolvable IRIs.

All terms in the .ttl files have the same root namespace
`<https://iso14224.org/ontology/i14224/rdl/>` and use the prefix *i14224:* 

## Modelling approach

The *i14224_clause3.ttl* file is used to capture information about the  terms from the `Terms and Definitions' clause of ISO 14224:2016 modelled as either OWL classes or as named individuals. 

In the `Terms and Definitions' clause there are many terms that can be grouped. For example: Maintenance Data, Failure Data, Equipment Data are all types of data. Rather than make each of these terms an OWL class, a new OWL class 'TypeData' was created and these terms were created as instances of OWL class 'TypeData'. Similar decisions were made for TypeFailureEvent, TypeMaintenanceStrategy, TypeMaterialState, TypeReliabilityMeasure and TypeTest.

Examples:

- TypeData: EquipmentData, FailureData, GenericReliabilityData, MaintenanceData, ReliabilityData
- TypeFailureEvent: CommonCauseFailure, CommonModeFailure, CriticalFailure, DegradedFailure, FailureDueToDemand, FailureOnDemand, HiddenFailure, IncipientFailure, NonCriticalFailure, RandomFailure, SafetyCriticalFailure, SystematicFailure, Trip
- TypeMaintenanceStrategy: ConditionBasedMaintenance, CorrectiveMaintenance, OpportunityMaintenance
- TypeMaterialState: DownState, IdleState, OperatingState, UpState
- TypeReliabilityMeasure: 21 examples, see the file
- TypeTest: PeriodicTest, Demand

The *i14224_appendixB.ttl* file is used to capture information in the tables in Appendix B relating to maintenance activity and failure mechanism as OWL classes or failure modes as named individuals. 

Appendix B was largely built manually but Appendix A was built with assistance from Chat GPT.

### Example of class and its annotations

```
https://iso14224.org/ontology/i14224/rdl/DetectionMethod
i14224:DetectionMethod rdf:type owl:Class ;
rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/clause3> ;
rdfs:label "Detection method"@en ;
rdfs:seeAlso ""@en ;
skos:altLabel ""@en ;
skos:definition "method or activity by which a failure is discovered"@en ;
skos:example ""@en ;
skos:scopeNote ""@en ;
i14224:en13306:definition "n/a"@en ;
i14224:iec60812:definition "n/a"@en ;
cmnsav:adaptedFrom ""@en ;
cmnsav:directSource "ISO 14224:2023 Terms and Definitions"@en ;
cmnsav:explanatoryNote ""@en ;
cmnsav:usageNote "ISO 14224-2023 Table B4 provides a categorization of detection methods (e.g. periodic testing or continuous condition monitoring)"@en .
```

### Example of a named individual and its annotations

```
https://iso14224.org/ontology/i14224/rdl/up_time
i14224:up_time rdf:type owl:NamedIndividual ,
                        i14224:TypeReliabilityMeasure ;
rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/clause3> ;
rdfs:label "up time"@en ;
rdfs:seeAlso ""@en ;
skos:altLabel ""@en ;
skos:definition "time interval during which an item is in an upstate"@en ;
skos:example ""@en ;
skos:scopeNote ""@en ;
i14224:en13306:definition "n/a"@en ;
i14224:iec60812:definition "n/a"@en ;
cmnsav:adaptedFrom ""@en ;
cmnsav:directSource "ISO 14224:2016 Terms and Definitions"@en ;
cmnsav:explanatoryNote ""@en ;
cmnsav:usageNote ""@en .
```

## Examples of competency questions on which to test these ttl models

*FMEA table management*

Organisations have hundreds (if not thousands) of FMEA tables, if these are created and stored in Excel they can have wildly different column labels. Different software packages each have their own labels for terms in FMEA spreadsheets. There is a significant use case in being able to use modern AI tools to map these tables to a common semantic layer so that some of the following tasks can be done.

- Identify and fix inconsistencies - are the same FM codes/ effects/ mechanism descriptors being used for identical equipment?

- Are FM codes/ effects/ mechanism descriptors being used at appropriate levels in equipment class (functional location) hierarchies?

- Map synonyms to agreed controlled vocabulary

- Use Linked Data to reduce ambiguity for AI tools and humans

*Quality control of failure mode assignment in MWOs*

It is common practice to assign a FM code based on ISO 14224 (or a derivative) to each maintenance notification associated with a failure event or observation of failure process. The consistency of application of these FM codes is very difficult in large organisations but it is possible with modern AI tools to post process MWO data and improve the quality of FM code assignment. The effectiveness of these AI tools would be improved, initially through a move to Linked Data, then quality control though SHACL, and in the long term using the reasoning ability of ontologies. 

*Reconciliation of failure mode assignment in MWOs with what is in FMEAs to improve equipment maintenance strategy*

One of the holy grails for Maintenance Managers is to be able to confirm equipment maintenance strategies are correct. Vast sums of money are spent on the execution of maintenance strategies whether they are working or not. Lagging indicators of maintenance strategy effectiveness include equipment availability, unplanned outages, maintenance costs and safety incidents. After unplanned outages it is common for reliability engineers to examine the maintenance strategy to see if the failure event that occurred was a) identified in the FMEA, 2) had a suitable control activity, and 3) if the control activity was actioned. Other actions include trawling through old MWOs to see if similar events had happened in the past. All of these activities could be assisted by AI tools but only if these tools can be certain what data are looking at. Again this will be assisted by a move to Linked Data, then quality control though SHACL, and in the long term using the reasoning ability of ontologies.

## Disclaimer

Important Notice

This taxonomy is an original academic artifact developed as part of scholarly research at the University of Western Australia. It represents the author's interpretation and analysis of concepts from the ISO 14224.

This work:

- Is based on AS ISO 14224:2023 but is not a substitute for those standards
- Does not reproduce the ISO standards verbatim; all definitions are paraphrased interpretations
- Should be viewed as a scholarly analysis and the author's interpretation of information security concepts
- Was created in an academic context and does not offer guarantees as a reference document
- Is not affiliated with, endorsed by, or officially connected to ISO or IEC
- For authoritative definitions and requirements, please consult the official ISO/IEC standards available at iso.org.
