# QUDT

Another issue is the widely used Quantities and units of measure (qudt) ontology https://github.com/qudt/qudt-public-repo

*The problem is that units of measure such as quantitykind:Pressure are modelled as an individual of qudt:QuantityKind and not as an owl Class*

Having a concept as a named individual (in rdf) rather than a class can cause issues if you want to make subclasses. In QUDT quantitykind:AmbientPressure is a peer to pressure and also quantitykind:AmbientPressure a qudt:QuantityKind ; rather than a subclass (as we might model it in IDO).


The file at https://github.com/qudt/qudt-public-repo/blob/main/src/main/rdf/vocab/quantitykinds/VOCAB_QUDT-QUANTITY-KINDS-ALL.ttl  has definitions for each unit of measure, for example:

```

quantitykind:Pressure
  a qudt:QuantityKind ;
  dcterms:description """Pressure is an effect which occurs when a force is applied on a surface. Pressure is the amount of force
    acting on a unit area. Pressure is distinct from stress, as the former is the ratio of the component of force normal to a
    surface to the surface area. Stress is a tensor that relates the vector force to the vector area.
  """^^qudt:LatexString ;
  qudt:dbpediaMatch "http://dbpedia.org/resource/Pressure"^^xsd:anyURI ;
  qudt:hasDimensionVector qkdv:A0E0L-1I0M1H0T-2D0 ;
  qudt:iec61360Code "0112/2///62720#UAD142" ;
  qudt:informativeReference "https://en.wikipedia.org/wiki/Pressure"^^xsd:anyURI ;
  qudt:isoNormativeReference "http://www.iso.org/iso/catalogue_detail?csnumber=31889"^^xsd:anyURI ;
  qudt:latexDefinition "$p = \\frac{dF}{dA}$, where $dF$ is the force component perpendicular to the surface element of area $dA$."^^qudt:LatexString ;
  qudt:plainTextDescription """Pressure is an effect which occurs when a force is applied on a surface. Pressure is the amount of
    force acting on a unit area. Pressure is distinct from stress, as the former is the ratio of the component of force normal to
    a surface to the surface area. Stress is a tensor that relates the vector force to the vector area.
  """ ;
  qudt:siExactMatch si-quantity:PRES ;
  qudt:specializationOf quantitykind:ForcePerArea ;
  qudt:wikidataMatch <http://www.wikidata.org/entity/Q39552> ;
  rdfs:isDefinedBy <http://qudt.org/$$QUDT_VERSION$$/vocab/quantitykind> ;
  rdfs:label "Druck"@de ;
  rdfs:label "Pressure"@en ;
  rdfs:label "Tekanan"@ms ;
  rdfs:label "Tlak"@cs ;
  rdfs:label "basınç"@tr ;
  rdfs:label "ciśnienie"@pl ;
  rdfs:label "nyomás"@hu ;
  rdfs:label "presiune"@ro ;
  rdfs:label "presión"@es ;
  rdfs:label "pressio"@la ;
  rdfs:label "pression"@fr ;
  rdfs:label "pressione"@it ;
  rdfs:label "pressão"@pt ;
  rdfs:label "tlak"@sl ;
  rdfs:label "Πίεση - τάση"@el ;
  rdfs:label "Давление"@ru ;
  rdfs:label "Налягане"@bg ;
  rdfs:label "לחץ"@he ;
  rdfs:label "الضغط أو الإجهاد"@ar ;
  rdfs:label "فشار، تنش"@fa ;
  rdfs:label "दबाव"@hi ;
  rdfs:label "压强、压力"@zh ;
  rdfs:label "圧力"@ja ;
  skos:altLabel "naprężenie"@pl ;
  skos:altLabel "pritisk"@sl ;
  skos:altLabel "tegasan"@ms ;
  skos:altLabel "tensione meccanica"@it ;
  skos:altLabel "tensiune mecanică"@ro ;
  skos:altLabel "tensão"@pt ;
  skos:altLabel "механично напрежение"@bg ;
  skos:altLabel "दाब"@hi .
  ```

In the https://github.com/qudt/qudt-public-repo/blob/main/src/main/rdf/schema/SCHEMA_QUDT.ttl

qudt:QuantityKind is an owl:Class

```
qudt:QuantityKind  rdf:type        owl:Class;
        rdfs:isDefinedBy           <http://qudt.org/$$QUDT_VERSION$$/schema/qudt>;
        rdfs:label                 "Quantity Kind";
        rdfs:subClassOf            qudt:AbstractQuantityKind , qudt:Verifiable;
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:Unit;
                                     owl:onProperty     qudt:applicableCGSUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:qkdvNumerator
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:hasDimensionVector
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  xsd:string;
                                     owl:onProperty     qudt:eclassCode
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  xsd:string;
                                     owl:onProperty     qudt:mathMLdefinition
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:minCardinality  "0"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:applicableUnit
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:Unit;
                                     owl:onProperty     qudt:applicableImperialUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:latexDefinition
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:minCardinality  "0"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:applicableISOUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:baseImperialUnitDimensions
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:QuantityKindDimensionVector;
                                     owl:onProperty     qudt:hasDimensionVector
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:Unit;
                                     owl:onProperty     qudt:applicableSIUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:minCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:hasDimensionVector
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:dimensionVectorForSI
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:minCardinality  "0"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:applicableSIUnit
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:Unit;
                                     owl:onProperty     qudt:applicableISOUnit
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:Unit;
                                     owl:onProperty     qudt:applicableUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:minCardinality  "0"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:applicableCGSUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:baseUSCustomaryUnitDimensions
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:mathMLdefinition
                                   ];
        rdfs:subClassOf            [ rdf:type         owl:Restriction;
                                     owl:cardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty   qudt:hasDimensionVector
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:QuantityKindDimensionVector;
                                     owl:onProperty     qudt:qkdvDenominator
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  xsd:string;
                                     owl:onProperty     qudt:iec61360Code
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:QuantityKindDimensionVector;
                                     owl:onProperty     qudt:qkdvNumerator
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:SystemOfQuantityKinds;
                                     owl:onProperty     qudt:belongsToSystemOfQuantities
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:qkdvDenominator
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:minCardinality  "0"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:applicableImperialUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:minCardinality  "0"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:applicableUSCustomaryUnit
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:Unit;
                                     owl:onProperty     qudt:applicableUSCustomaryUnit
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:baseSIUnitDimensions
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:baseCGSUnitDimensions
                                   ];
        rdfs:subClassOf            [ rdf:type            owl:Restriction;
                                     owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                                     owl:onProperty      qudt:baseISOUnitDimensions
                                   ];
        rdfs:subClassOf            [ rdf:type           owl:Restriction;
                                     owl:allValuesFrom  qudt:QuantityKindDimensionVector_SI;
                                     owl:onProperty     qudt:dimensionVectorForSI
                                   ];
        dcterms:description        "\n  <p>A <em>Quantity Kind</em> is any observable property that can be  measured and quantified numerically. \n  Familiar examples include physical properties such as length, mass, time, force, energy, power, electric charge, etc. \n  Less familiar examples include currency, interest rate, price to earning ratio, and information capacity.\n  </p>"^^rdf:HTML;
        qudt:informativeReference  "http://www.electropedia.org/iev/iev.nsf/display?openform&ievref=112-01-04"^^xsd:anyURI .
    ```

    and qudt:QuantityValue

    ```
    qudt:QuantityValue  rdf:type  owl:Class;
        rdfs:isDefinedBy     <http://qudt.org/$$QUDT_VERSION$$/schema/qudt>;
        rdfs:label           "Quantity value";
        rdfs:subClassOf      qudt:Verifiable , qudt:Concept , qudt:Quantifiable;
        dcterms:description  "\n  <p>A <em>Quantity Value</em> \n  </p>"^^rdf:HTML .
    ```

    With object property
    ```
    qudt:quantityValue  rdf:type  owl:ObjectProperty;
        rdfs:isDefinedBy  <http://qudt.org/$$QUDT_VERSION$$/schema/qudt>;
        rdfs:label        "quantity value";
        rdfs:range        qudt:QuantityValue .
    ```

    and Quantity class
    ```
    qudt:Quantity  rdf:type      owl:Class;
        rdfs:isDefinedBy     <http://qudt.org/$$QUDT_VERSION$$/schema/qudt>;
        rdfs:label           "Quantity";
        rdfs:subClassOf      qudt:Quantifiable , qudt:Concept , qudt:Verifiable;
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  qudt:QuantityKind;
                               owl:onProperty     qudt:hasQuantityKind
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  qudt:QuantityValue;
                               owl:onProperty     qudt:quantityValue
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  xsd:boolean;
                               owl:onProperty     qudt:isDeltaQuantity
                             ];
        rdfs:subClassOf      [ rdf:type            owl:Restriction;
                               owl:minCardinality  "0"^^xsd:nonNegativeInteger;
                               owl:onProperty      qudt:hasQuantityKind
                             ];
        dcterms:description  "\n  <p>A <b>Quantity</b> is the measurement of an observable property of a particular object, event, or physical system. \n  A quantity is always associated with the context of measurement (i.e. the thing measured, the measured value, the accuracy of measurement, etc.) whereas the \n  underlying <b>quantity kind</b> is independent of any particular measurement. Thus, length is a quantity kind while the height of a rocket is a specific \n  quantity of length; its magnitude that may be expressed in meters, feet, inches, etc. Examples of physical quantities include physical constants, such as \n  the speed of light in a vacuum, Planck's constant, the electric permittivity of free space, and the fine structure constant. </p>\n<p>In other words, quantities are quantifiable aspects of the world, such as the duration of a movie, the distance between two points, \nvelocity of a car, the pressure of the atmosphere, and a person's weight; and units are used to describe their numerical measure.</p> \n<p>Many <b>quantity kinds</b> are related to each other by various physical laws, and as a result, the associated units of some quantity \nkinds can be expressed as products (or ratios) of powers of other quantity kinds (e.g., momentum is mass times velocity and velocity is defined as distance \ndivided by time). In this way, some quantities can be calculated from other measured quantities using their associations to the quantity kinds in these \nexpressions. These quantity kind relationships are also discussed in dimensional analysis. Those that cannot be so expressed can be regarded \nas \"fundamental\" in this sense.</p>\n<p>A quantity is distinguished from a \"quantity kind\" in that the former carries a value and the latter is a type specifier.\n</p>"^^rdf:HTML;
        qudt:dbpediaMatch    "http://dbpedia.org/resource/Quantity"^^xsd:anyURI .
```
and quantity object property
```
qudt:quantity  rdf:type      owl:FunctionalProperty , owl:ObjectProperty;
        rdfs:isDefinedBy     <http://qudt.org/$$QUDT_VERSION$$/schema/qudt>;
        rdfs:label           "quantity";
        rdfs:range           qudt:Quantity;
        dcterms:description  "a property to relate an observable thing with a quantity (qud:Quantity)" .
```

The root of the concepts for qudt:QuantityKind and qudt:Quantity is the owl:Class qudt:Concept.
The restrictions say that a QUDT concept may have a single string abbreviation, identifier, deprecation status and deprecation version; may be associated with QUDT rules; may identify exact matches to other QUDT concepts; and may provide guidance expressed as HTML.


Some more notes at: https://chatgpt.com/share/6a9e0a0d-c8bc-83ec-bd01-44ce4b009106

```
qudt:Concept  rdf:type       owl:Class;
        rdfs:isDefinedBy     <http://qudt.org/$$QUDT_VERSION$$/schema/qudt>;
        rdfs:label           "QUDT Concept";
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  xsd:string;
                               owl:onProperty     qudt:abbreviation
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  qudt:Rule;
                               owl:onProperty     qudt:hasRule
                             ];
        rdfs:subClassOf      [ rdf:type            owl:Restriction;
                               owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                               owl:onProperty      qudt:deprecated
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  xsd:boolean;
                               owl:onProperty     qudt:deprecated
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  xsd:string;
                               owl:onProperty     qudt:deprecatedInVersion
                             ];
        rdfs:subClassOf      [ rdf:type            owl:Restriction;
                               owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                               owl:onProperty      qudt:id
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  xsd:string;
                               owl:onProperty     qudt:id
                             ];
        rdfs:subClassOf      [ rdf:type            owl:Restriction;
                               owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                               owl:onProperty      qudt:deprecatedInVersion
                             ];
        rdfs:subClassOf      [ rdf:type            owl:Restriction;
                               owl:maxCardinality  "1"^^xsd:nonNegativeInteger;
                               owl:onProperty      qudt:abbreviation
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  qudt:Concept;
                               owl:onProperty     qudt:exactMatch
                             ];
        rdfs:subClassOf      [ rdf:type           owl:Restriction;
                               owl:allValuesFrom  rdf:HTML;
                               owl:onProperty     qudt:guidance
                             ];
        dcterms:description  "The root class for all QUDT concepts."^^rdf:HTML .
```




