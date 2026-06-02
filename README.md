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

## Purpose of this repo

The purposes of this repo are:

1. to provide **stable** Linked Data and IRIs for:

- 53 terms used in the Terms and Definitions (Clause 3) section of ISO 14224, and 
- Text in tables relating to the classification of failure modes, failure mechanisms and failure causes contained in Appendix B, of the ISO 14224:2016 standard. 

The namespace iso14224.org has been purchased by the GitHub repo owner for this purpose.

2. to provide example data and competency questions from FMEA and Maintenance work order tables from industry that include concepts represented in ISO 14224.

3.  Develop models based on 1. and 2. aligned to different top level ontologies - IDO, IOF and DOLCE. Use the examples in 2. to understand the impact of modelling decisions.


## Outputs
The current files are available in ttl format in the \inDevelopment subdirectory. When they are final they will be moved to the \ontology subdirectory.

**Files**
*i14224_clause3.ttl* Terms and definitions  - modelled as OWL classes, object properties and annotation properties. Contains the `https://iso14224.org/ontology/i14224/ont/clause3` ontology.

*vocab14224_appendixB.ttl* - data from tables in ISO 14224 Annex B for example on Failure modes and Mechanisms - modelled as OWL classes and named individuals. Contains the `https://iso14224.org/ontology/i14224/ont/appendixB` ontology




## Namespace and file names

The iso14224.org namespace was purchased to enable future resolvable IRIs.

**Prefix and namespaces for IRIs**

@prefix iso14224 https://iso14224.org/skos/ - for terms represented as SKOS concepts

@prefix voc https://iso14224.org/vocab - for terms represented as OWL classes

## Approach

The first step was to make the *vocab14224_basic.ttl* file with terms from the Terms and Definitions clause of ISO 14224:2016 modelled as either OWL classes or as named individuals. In the Terms and Definitions clause there are many terms that can be grouped. For example: Maintenance Data, Failure Data, Equipment Data are all types of data. Rather than make each of these terms an OWL class, a new OWL class 'TypeData' was created and these terms were created as instances of OWL class 'TypeData'. Similar decisions were made for TypeFailureEvent, TypeMaintenanceStrategy, TypeMaterialState, TypeReliabilityMeasure and TypeTest.

Python code (*owl_to_skos.py*) was created to convert the *vocab14224_basic.ttl* file to *vocab14224_skos_basic.ttl* file. Concepts in the *vocab14224_skos_basic.ttl* file have a separate namespace @prefix iso14224 https://iso14224.org/skos/. 

### What does the *owl_to_skos.py* file do?

1. Each owl:Class becomes a skos:Concept
2. New SKOS concept namespace/prefix: https://iso14224.org/skos/ with prefix iso14224:
3. rdfs:subClassOf → skos:broader
4. rdfs:label (and any existing skos:prefLabel) → skos:prefLabel
5. Created a concept scheme: <https://iso14224.org/skos/scheme/vocab14224_basic> and linked concepts via skos:inScheme, plus skos:hasTopConcept / skos:topConceptOf
6. Format and annotation to ensure all SKOS concepts have common notation (UpperCamelCase)
7. each concept has dcterms:source pointing to the original class IRI (e.g., <https://iso14224.org/vocab/Boundary>)
8. All terms that are instances of an OWL class 'TypeX' (see above) in the OWL file are converted to SKOS concepts with a skos:broader relationship to the 'TypeX' concept.

## SKOS concept model

See *\InDevelopment\vocab14224_skos_basic.ttl*

TypeX concepts 

- TypeData (EquipmentData, FailureData, GenericReliabilityData, MaintenanceData, ReliabilityData)
- TypeFailureEvent (CommonCauseFailure, CommonModeFailure, CriticalFailure, DegradedFailure, FailureDueToDemand, FailureOnDemand, HiddenFailure, IncipientFailure, NonCriticalFailure, RandomFailure, SafetyCriticalFailure, SystematicFailure, Trip)

- TypeMaintenanceStrategy (ConditionBasedMaintenance, CorrectiveMaintenance, OpportunityMaintenance
- TypeMaterialState (DownState, IdleState, OperatingState, UpState)
- TypeReliabilityMeasure(21 examples, see the file) 
- TypeTest (PeriodicTest, Demand)

### Example of a SKOS concept

**https://iso14224.org/skos/EquipmentType**

```
iso14224:EquipmentType a skos:Concept ;
    dcterms:source <https://iso14224.org/vocab/EquipmentType> ;
    skos:altLabel ""@en ;
    skos:definition "particular feature of the design which is significantly different from the other design(s) within the same equipment class"@en ;
    skos:example ""@en ;
    skos:inScheme <https://iso14224.org/skos/scheme/vocab14224_basic> ;
    skos:prefLabel "equipment type"@en ;
    skos:scopeNote ""@en ;
    skos:topConceptOf <https://iso14224.org/skos/scheme/vocab14224_basic> .
```    

### Example of a SKOS:broader concept

**https://iso14224.org/skos/PredictiveMaintenance**

```
iso14224:PredictiveMaintenance a skos:Concept ;
    dcterms:source <https://iso14224.org/vocab/PredictiveMaintenance> ;
    skos:altLabel "pDM"@en,
        "pdM"@en ;
    skos:broader iso14224:TypeMaintenanceStrategy ;
    skos:definition "maintenance based on the prediction of the future condition of an item estimated or calculated from a defined set of historic data and known future operational parameters"@en ;
    skos:example ""@en ;
    skos:inScheme <https://iso14224.org/skos/scheme/vocab14224_basic> ;
    skos:prefLabel "predictive maintenance"@en ;
    skos:scopeNote ""@en .
```


## OWL class model

### Example of an OWL class

**https://iso14224.org/vocab/EquipmentType**
```
voc:EquipmentType rdf:type owl:Class ;
                  rdfs:label "Equipment type"@en ;
                  rdfs:seeAlso ""@en ;
                  skos:altLabel ""@en ;
                  skos:definition "particular feature of the design which is significantly different from the other design(s) within the same equipment class"@en ;
                  skos:example ""@en ;
                  skos:scopeNote ""@en ;
                 rdfs:isDefinedBy <https://iso14224.org/vocab/basic> ;
                  voc:en13306:definition "n/a"@en ;
                  voc:iec60812:definition "n/a"@en ;
                  ;
                  cmns-av:adaptedFrom ""@en ;
                  cmns-av:directSource "ISO 14224:2023 Terms and Definitions"@en ;
                  cmns-av:explanatoryNote ""@en ;
                  cmns-av:usageNote ""@en .
```

### Example if an OWL named individual
```
###  https://iso14224.org/vocab/predictive_maintenance
voc:predictive_maintenance rdf:type owl:NamedIndividual ,
                                    voc:TypeMaintenanceStrategy ;
                           rdfs:label "predictive maintenance"@en ;
                           rdfs:seeAlso ""@en ;
                           skos:altLabel "PDM"@en ,
                                         "PdM"@en ;
                           skos:definition "maintenance based on the prediction of the future condition of an item estimated or calculated from a defined set of historic data and known future operational parameters"@en ;
                           skos:example ""@en ;
                           skos:scopeNote ""@en ;
                 rdfs:isDefinedBy <https://iso14224.org/vocab/basic> ;
                           voc:en13306:definition "condition-based maintenance carried out following a forecast derived from repeated analysis or known characteristics and evaluation of the significant parameters of the degradation of the item"@en ;
                           voc:iec60812:definition "n/a"@en ;
                           ;
                           cmns-av:adaptedFrom ""@en ;
                           cmns-av:directSource "ISO 14224:2016 Terms and Definitions"@en ;
                           cmns-av:explanatoryNote ""@en ;
                           cmns-av:usageNote ""@en .
```

We are working on alternate representations and alignment with different top level ontologies (IDO, IOF_core and IOF_maintenance, DOLCE) and will publish these here as they become available. The IRIs will be stable.

## Disclaimer

Important Notice

This taxonomy is an original academic artifact developed as part of scholarly research at the University of Western Australia. It represents the author's interpretation and analysis of concepts from the ISO 14224.

This work:

Is based on AS ISO 14224:2023 but is not a substitute for those standards
Does not reproduce the ISO standards verbatim; all definitions are paraphrased interpretations
Should be viewed as a scholarly analysis and the author's interpretation of information security concepts
Was created in an academic context and does not offer guarantees as a reference document
Is not affiliated with, endorsed by, or officially connected to ISO or IEC
For authoritative definitions and requirements, please consult the official ISO/IEC standards available at iso.org.
