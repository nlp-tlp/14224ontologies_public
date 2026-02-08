# GitHub repo for collaboration on developing a semantic version for ISO 14224 

A private for now repo for shared development of controlled vocabulary, linked data, RDF triple stores, and ontologies for ISO 14224 users

## Purpose

The purpose of this repo is to provide Linked Data and IRIs for 65 terms used in 1) the Terms and Definitions section, and 2) Appendix B, of the ISO 14224:2016 standard. Appendix B contains text and tables relating to the classification of failure modes, failure mechanisms and failure causes.

## Namespace and file names

The iso14224.org namespace was purchased to enable future resolvable IRIs.

Prefix and namespaces for IRIs are as follows

@prefix iso14224 https://iso14224.org/terms - terms and definitions in Section 3 of the standard 
@prefix iso14224fmode https://iso14224.org/failure-mode - failure modes defined in Annex B 
@prefix iso14224fmech https://iso14224.org/failure-mech - failure mechanisms defined in Annex B

For 2023 release these IRIs are also created
@prefix iso142242024 https://iso14224.org/terms/2024 - terms and definitions in Section 3 of the standard 
@prefix iso14224fmode2024 https://iso14224.org/failure-mode/2024 - failure modes defined in Annex B 
@prefix iso14224fmech2024 https://iso14224.org/failure-mech/2024 - failure mechanisms defined in Annex B

Files
iso14224.ttl Terms and definitions  (base scheme and concepts)
iso14224-failure-mode.ttl  Failure modes  (failure mode list)
iso14224-failure-mechanism.ttl Failure mechanism  (failure mechanism list)
local-to-iso14224-mapping.ttl Mapping from local (organisational specific) file to iso using skos:closeMatch and skos:exactMatch 

and corresponding ttl files for 2024 release, for example, iso14224-2024.ttl


TO be rewritten
**********************************************************************

## Linked Data and IRIs

The pidvocab.ttl file contains IRIs and annotations for 65 terms and definitions in the terms and definitions section of ISO 14424:2016. Where the term also appears in EN13306:2017 Maintenance terminology and IEC60812:2018 FMEA, definitions from these standards are also provided.

Need to revise Namespace: https://pid.vocab14224.org/TermsAndDefinitions/

### Example from pidvocab14224.ttl

###  https://pid.vocab14224.org/TermsAndDefinitions/FailureMode

```
voc:FailureMode rdf:type owl:Class ;
                rdfs:label "Failure mode"@en ;
                rdfs:seeAlso ""@en ;
                skos:altLabel ""@en ;
                skos:definition "manner in which failure occurs"@en ;
                voc:en13306:definition "manner in which the inability of an item to perform a required function occurs"@en ;
                voc:iec60812:definition "manner in which failure occurs"@en ;
                skos:example ""@en ;
                skos:scopeNote ""@en ;
                voc:iso14224:section "https://pid.vocab14224.org/TermsAndDefinitions"^^xsd:anyURI ;
                cmns-av:adaptedFrom "IEC 60050-192:2015 notes added"@en ;
                cmns-av:directSource "ISO 14224:2016 Terms and Definitions"@en ;
                cmns-av:explanatoryNote ""@en ;
                cmns-av:usageNote "Tables in B.2.6 in ISO 14224-2023 on relevant failure modes define failure modes to be used for each equipment class"@en ;
                cmns-av:usageNote "analysis might require data collection to be established on different taxonomy levels"@en .
```

Each term is represented in this pidvocab14224.ttl file as an owl:class. 

We are working on alternate representations and alignment with different top level ontologies and will publish these here as they become available. The IRIs will be stable.

## What is ISO 14224?

ISO 14224:2016 is a standard for the collection of reliability and maintenance (RM) data in a standard format for equipment in all facilities and operations. ISO 14224:2016 is widely used within the petroleum, natural gas and petrochemical industries during the operational life cycle of equipment and has also seen adoption in the mining industry.

ISO 14224 provides definitions that constitute a "reliability language" that can be useful for communicating operational experience. The failure modes defined in the normative part of this International Standard can be used as a "reliability thesaurus" for various quantitative as well as qualitative applications.

Standardization of data collection practices facilitates the exchange of information between parties, e.g. plants, owners, manufacturers and contractors. Controlled vocabularies and consistent interpretation of codes is increasingly recognized as a necessary foundation for enterprise generative AU models.

ISO 14224 provides categories for the following data:

a) equipment data, e.g. equipment taxonomy, equipment attributes;

b) failure data, e.g. failure cause, failure consequence;

c) maintenance data, e.g. maintenance action, resources used, maintenance consequence, down time.

There data are used for tracking and investigating reliability issues, calculating equipment and system availability, maintenance management metrics, and events with safety and environmental impacts.

