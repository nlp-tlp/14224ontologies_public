# GitHub repo for collaboration on developing a semantic version for ISO 14224 

Building a machine-readable version of ISO 14224 :2016 (version reconfirmed in 2022)

## Purpose

The purpose of this repo is to provide Linked Data and IRIs for 1) the 53 terms used in the Terms and Definitions section of ISO 14224, and 2) Appendix B, of the ISO 14224:2016 standard. Appendix B contains text and tables relating to the classification of failure modes, failure mechanisms and failure causes. The namespace iso14224.org has been purchased by the GitHub repo owner for this purpose.

## Output
The standard is available in ttl format

**Files**

vocab14224_skos_basic.ttl Terms and definitions - modelled as SKOS concepts

vocab14224_basic.ttl Terms and definitions  - modelled as OWL classes

vocab14224_extended.ttl - data from Annex B such as Failure modes and Mechanisms - modelled as OWL classes and instances - this file is temporary and likely to be superceded.

## What is ISO 14224?

ISO 14224:2016 is a standard for the collection of reliability and maintenance (RM) data in a standard format for equipment in all facilities and operations. ISO 14224:2016 is widely used within the petroleum, natural gas and petrochemical industries during the operational life cycle of equipment and has also seen adoption in the mining industry.

ISO 14224 provides definitions that constitute a "reliability language" that can be useful for communicating operational experience. The failure modes defined in the normative part of this International Standard can be used as a "reliability thesaurus" for various quantitative as well as qualitative applications.

Standardization of data collection practices facilitates the exchange of information between parties, e.g. plants, owners, manufacturers and contractors. Controlled vocabularies and consistent interpretation of codes is increasingly recognized as a necessary foundation for enterprise generative AU models.

ISO 14224 provides categories for the following data:

a) equipment data, e.g. equipment taxonomy, equipment attributes;

b) failure data, e.g. failure cause, failure consequence;

c) maintenance data, e.g. maintenance action, resources used, maintenance consequence, down time.

There data are used for tracking and investigating reliability issues, calculating equipment and system availability, maintenance management metrics, and events with safety and environmental impacts.


## Namespace and file names

The iso14224.org namespace was purchased to enable future resolvable IRIs.

**Prefix and namespaces for IRIs**

@prefix iso14224 https://iso14224.org/skos/ - for terms represented as SKOS concepts

@prefix voc https://iso14224.org/vocab - for terms represented as OWL classes

## Approach

The first step was to make the vocab14224_basic.ttl file with some terms modelled as OWL classes and others as named individuals.


## OWL Data modelling approach

In this initial phase some concepts have been modelled as classes and others as individuals, examples below. 
Model as a class if:

- there are likely to be a need to create subclasses at a future modelling stage e.g. EquipmentType
- data we wish to model usually contains instances of the class

Model as an instance if:

- the information we seek to model is usually present as a string or code e.g WO10101010 hasTypeMaintenanceStrategy voc:preventative_maintenance

Annotations -  Where the term also appears in EN13306:2017 Maintenance terminology and IEC60812:2018 FMEA, definitions from these standards are also provided.

**These modelling decisions are still being explored and some changes are likely the next phase. The next phase of work will consider how to create lists containing individuals - such as found in tables such as list of maintenance strategies. The goal is to enable queries from e.g. a list.**

### Example of a class

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

### Example if an individual
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
