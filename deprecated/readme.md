# Readme for file sin the deprecated folder

## i14224_clause.ttl file

Original file of all the terms in clause 3 of ISO 14224 modelling terms as rdf classes and some rdf individuals

Uses @prefix i14224: <https://iso14224.org/ontology/i14224/rdl/> .

Example of terms modelled as classes (may be needed to support individuals)

###  https://iso14224.org/ontology/i14224/rdl/Boundary
i14224:Boundary rdf:type owl:Class ;
                rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/clause3> ;
                rdfs:label "Boundary"@en ;
                rdfs:seeAlso ""@en ;
                skos:altLabel ""@en ;
                skos:definition "interface between an item and its surroundings"@en ;
                skos:example ""@en ;
                skos:scopeNote ""@en ;
                i14224:en13306:definition "n/a"@en ;
                i14224:iec60812:definition "n/a"@en ;
                cmnsav:adaptedFrom ""@en ;
                cmnsav:directSource "ISO 14224:2023 Terms and Definitions"@en ;
                cmnsav:explanatoryNote ""@en ;
                cmnsav:usageNote ""@en .

With the addition of some owl:ObjectProperty to support grouping of terms e.g.

###  https://iso14224.org/ontology/i14224/rdl/hasFailureEventByType
i14224:hasFailureEventByType rdf:type owl:ObjectProperty ;
                             rdfs:domain i14224:Failure ;
                             rdfs:range i14224:FailureEventByType ;
                             rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/clause3> ;
                             rdfs:label "hasFailureEventByType" ;
                           skos:definition "identifies the type of failure event" .

Examples of terms modelled as owl:NamedIndividual

###  https://iso14224.org/ontology/i14224/rdl/random_failure
i14224:random_failure rdf:type owl:NamedIndividual ,
                               i14224:FailureEventByType ;
                      rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/clause3> ;
                      rdfs:label "random failure"@en ;
                      rdfs:seeAlso ""@en ;
                      skos:altLabel "PDM"@en ;
                      skos:definition "failure occurring in a random way"@en ;
                      skos:example ""@en ;
                      skos:scopeNote ""@en ;
                      i14224:en13306:definition "n/a"@en ;
                      i14224:iec60812:definition "n/a"@en ;
                      cmnsav:adaptedFrom ""@en ;
                      cmnsav:directSource "ISO 14224:2016 Terms and Definitions"@en ;
                      cmnsav:explanatoryNote ""@en ;
                      cmnsav:usageNote ""@en .

# i14224_appendixA.ttl file

Original file for equipment class terms in Appendix A.

Uses @prefix i14224: <https://iso14224.org/ontology/i14224/rdl/> 

Examples of terms modelled as owl:Class

i14224:EquipmentCode rdf:type owl:Class ;
    rdfs:label "Equipment code"@en ;
    rdfs:seeAlso ""@en ;
    skos:altLabel ""@en ;
    skos:definition "class of codes used to identify ISO 14224 equipment classes and equipment types"@en ;
    skos:example ""@en ;
    rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/appendixA> ;
    cmnsav:directSource "ISO 14224:2023 Appendix A"@en .

Includes all the Level 6 Equipment class entries 

###  https://iso14224.org/ontology/i14224/rdl/CombustionEngine
i14224:CombustionEngine
    rdf:type owl:Class ;
    rdfs:subClassOf i14224:EquipmentClass ;
    rdfs:label "Combustion engine"@en ;
    i14224:equipment_category "rotating equipment"@en ;
    i14224:equipment_class_level "Level 6"@en ;
    i14224:hasEquipmentCode i14224:CE ;
    rdfs:seeAlso ""@en ;
    skos:altLabel ""@en ;
    skos:definition "class of combustion engines"@en ;
    skos:example ""@en ;
    rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/appendixA> ;
    cmnsav:directSource "ISO 14224:2023 Appendix A"@en .

and Level 7 Equipment 

###  https://iso14224.org/ontology/i14224/rdl/DieselEngine
i14224:DieselEngine
    rdf:type owl:Class ;
    rdfs:subClassOf i14224:CombustionEngine , i14224:EquipmentByType ;
    rdfs:label "Diesel engine"@en ;
    i14224:equipment_category "rotating equipment"@en ;
    i14224:equipment_class_level "Level 7"@en ;
    i14224:hasEquipmentCode i14224:DE ;
    rdfs:seeAlso ""@en ;
    skos:altLabel ""@en ;
    skos:definition "class of diesel engines"@en ;
    skos:example ""@en ;
    rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/appendixA> ;
    cmnsav:directSource "ISO 14224:2023 Appendix A"@en .

Equipment codes are modelled as individuals

i14224:AB
    rdf:type owl:NamedIndividual , i14224:EquipmentCode ;
    rdfs:isDefinedBy <https://iso14224.org/ontology/i14224/ont/appendixA> ;
    rdfs:label "AB"@en ;
    skos:definition "equipment code AB"@en ;
    cmnsav:directSource "ISO 14224:2023 Appendix A"@en .