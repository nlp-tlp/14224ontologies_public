# GitHub repo for collaboration on developing a semantic version for ISO 14224 

A public repo for shared development of controlled vocabulary, linked data and ontologies for ISO 14224 users

## Purpose

The purpose of this repo is to provide a shared space for work on semantic representation of knowledge held in industry data in in 1) failure modes and effects analysis tables, and 2) maintenance work order databases that reference failure descriptors (failure mode, failure mechanism) and the asset taxonomic structures codified in the ISO 14224:2016 standard.

## What is ISO 14224?

ISO 14224:2016 is a standard for the collection of reliability and maintenance (RM) data in a standard format for equipment in all facilities and operations. ISO 14224:2016 is widely used within the petroleum, natural gas and petrochemical industries during the operational life cycle of equipment and has also seen adoption in the mining industry.

ISO 14224 provides definitions that constitute a "reliability language" that can be useful for communicating operational experience. The failure modes defined in the normative part of this International Standard can be used as a "reliability thesaurus" for various quantitative as well as qualitative applications.

Standardization of data collection practices facilitates the exchange of information between parties, e.g. plants, owners, manufacturers and contractors. Controlled vocabularies and consistent interpretation of codes is increasingly recognized as a necessary foundation for enterprise generative AU models.

ISO 14224 provides categories for the following data:

a) equipment data, e.g. equipment taxonomy, equipment attributes;

b) failure data, e.g. failure cause, failure consequence;

c) maintenance data, e.g. maintenance action, resources used, maintenance consequence, down time.

There data are used for tracking and investigating reliability issues, calculating equipment and system availability, maintenance management metrics, and events with safety and environmental impacts.

## What is the opportunity?

There are several opportunities for a shared industry project to improve machine readability of FMEA and maintenance data. In order of technical complexity from technically simple to complex these are

**Controlled vocabulary**: while some terms are provided in the terms and definitions section of the ISO 14224:2016: https://www.iso.org/obp/ui/en/#iso:std:iso:14224:ed-3:v2:en the standard lacks robust definitions for terms inside the document e.g. in the tables in Appendix B that describe failure modes and mechanisms. A mapping also needs to be done between terms that are common to ISO 14224:2016 and IEC 60812 IEC 60812:2018 Failure modes and effects analysis (FMEA and FMECA) and to document the differences.

Example
label:failure effect
natural language definition: process that is the consequence of failure, within or beyond the boundary of the failed item
example: leaking pipe, erratic operation, equipment does not run

Value
The business value of this step is that every organisation (and even engineers within an organisation) keep their own versions of ISO 14424 in database tables and Excel spreadsheets with their own entity type labels and column headings, as well as codes resulting in challenges for humans, let alone AI to determine if the terms are semantically the same.

**Linked data**: this would be a major step forward in providing a shared, open, stable and managed resource, such as a GitHub page that engineers could reference to ensure a shared interpretation of a term. Challenges include where to host it (neither ISO or IEC provide suitable namespaces and IRI hosting capabilities at present) and how to provide trust for enterprises on how it will be maintained, and how updates will be managed.

Example
Linked data for the term 'failure effect' https://spec.industrialontologies.org/iof/ontology/maintenance/Maintenance/FailureEffect

**Lightweight schemas based on semi-structured definitions**: providing semi-formal definitions based on a list of controlled terms (nodes and edges/ classes and object properties) clarifies the meaning of each term moving away from the ambiguity of natural language and towards machine interpretability. It provides the basis for a common schema.

Example
if x is a 'failure effect' then x is a 'process' that is 'preceded by' some 'failure event' or 'failure process'

In this example, the schema would need to contain concepts for 'process', 'failure event', 'failure process' and 'preceded by'

**Ontology modules**:

Ontologies go beyond schemas and provide a principled approach to defining concepts and their relations. To domain practitioners (such as the author of this readme) this can be achieved by alignment to a top-level ontology either directly or via ontology modules that are also aligned to a top-level ontology.

In the opinion of this author, in engineering domain there are four ontologies to be considered as follows
- Basic Formal Ontology
- Industrial Data Ontology
- DOLCE
- Unified Foundational Ontology

It should be possible to represent ISO 14224 in each of these frameworks.

A key step in ontology development and in assessing fitness for purpose is to have data and competency questions. One of the goals of this repo is to provide these. 

Ontologies are very expensive to develop and maintain and if they cannot demonstrate business value, that is a problem.




