# Status of the skos version

Current active file is iso14224_skos-ApA_level7_updated.ttl

1. This file is the result of a conversion from the i14224.ttl RDF file. There have been some issues with this.
2. The Level 6 concepts need to be checked as there may be some concepts e.g XmasTree that are there that shouldn't be. Check against original standard. Also check to see if they are in the RDF file (maybe result of hallination when file created using LLM).
3. The  i14224skos:hasEquipmentCode objects need to be finished. Many did not transfer through
4. Do a check against the number of Level 6 and 7 concepts vs the standard.
5. Decide which of the python scripts used to prepare this need to be preserved. 




Some things to note.

The original i14224_appendixA.ttl file was made with an LLM. Manual checking revealed several errors as follows

The LLM failed to identify the following Level 6 classes: Centrifuge, ConveyorAndElevator, FilterAndStrainer, PressureVessel and Silo.

It added a class and plausible predicates for XmasTreeTopsideOffshore in the MechanicalEngineering section (also Vessel)

In Electrical Equipment the entry for Switchgear was written as "SwitchgearSwitchboardAnd DistributionBoard"

In the Level 7 entries. 
1. It added Blower Fan under Compressor (there is no Blower Fan)
2. It completely missed all the Switchgear and Frequency Converter Equipment Types and Storage Tanks.

Many codes were wrong.


