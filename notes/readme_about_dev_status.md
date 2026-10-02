# Status of the skos version

Current active file is iso14224_skos_ApA_level7_updated.ttl

1. This file is the result of a conversion from the i14224.ttl RDF file. There have been some issues with this.
2. The Level 6 concepts need to be checked as there may be some concepts e.g XmasTree that are there that shouldn't be. Check against original standard. Also check to see if they are in the RDF file (maybe result of hallucination when file created using LLM).
3. The  i14224skos:hasEquipmentCode objects need to be finished. Many did not transfer through
4. Do a check against the number of Level 6 and 7 concepts vs the standard.
5. Decide which of the python scripts used to prepare this need to be preserved. 




Some things to note.

The original i14224_appendixA.ttl file was made with an LLM. Manual checking revealed several errors as follows

- The LLM failed to identify the following Level 6 classes: Centrifuge, ConveyorAndElevator, FilterAndStrainer, PressureVessel and Silo.

- It added a class and plausible predicates for XmasTreeTopsideOffshore in the MechanicalEngineering section (also Vessel)

- In Electrical Equipment the entry for Switchgear was written as "SwitchgearSwitchboardAnd DistributionBoard"

- In the Level 7 entries. 
1. It added Blower Fan under Compressor (there is no Blower Fan)
2. It completely missed all the Switchgear and Frequency Converter Equipment Types and Storage Tanks.

- Many equipment codes were wrong.

2/10/25  - ran the SKOS https://skos-play.sparna.fr/ tool. Identified a duplicate class (2nd EquipmentUnit should have been SubUnit). Also some opportunities to the improve the graph captured here https://chatgpt.com/share/6abf4eb9-cce0-83ec-a804-9f6bfb4f1a0d . Actioned these changes manually.

Also all the Level 7 concepts were incorrectly given  i14224skos:taxonomicClassificationLevel i14224skos:EquipmentUnit ; instead of     i14224skos:taxonomicClassificationLevel i14224skos:SubUnit ; - this has been corrected. 

Changed all the equipment class codes from skos:Concept to skos:notation and defined a i14224skos:Allowed

i14224skos:TitaniumPiping
    skos:notation "TI"^^i14224skos:ISO14224EquipmentCode .

i14224skos:AllowedISO14224EquipmentCode
    a rdfs:Datatype ;
    rdfs:label "ISO 14224 equipment code"@en .

and created an         


i14224skos:AllowedISO14224EquipmentCode 
    rdf:value (
        "AB"^^i14224skos:ISO14224EquipmentCode
        "AC"^^i14224skos:ISO14224EquipmentCode


Created lists for L6 and L7 terms

FOund the following conflicts when running the SKOS checker

Notation: DI, conflicting resources: https://iso14224.org/skos/DiaphragmValve, https://iso14224.org/skos/DisplacementInputDevice, https://iso14224.org/skos/DiscValve
Notation: SS, conflicting resources: https://iso14224.org/skos/SolidStateControlUnit, https://iso14224.org/skos/SingleStageSteamTurbine
Notation: AD, conflicting resources: https://iso14224.org/skos/AeroDerivativeGasTurbine, https://iso14224.org/skos/AdsorberPressureVessel
Notation: GA, conflicting resources: https://iso14224.org/skos/GaseousNozzle, https://iso14224.org/skos/GateValve
Notation: LV, conflicting resources: https://iso14224.org/skos/LowVoltageSwitchgear, https://iso14224.org/skos/LowVoltageFrequencyConverter
Notation: DT, conflicting resources: https://iso14224.org/skos/DisconnectableTurret, https://iso14224.org/skos/DryPowerTransformer
Notation: OT, conflicting resources: https://iso14224.org/skos/OilImmersedPowerTransformer, https://iso14224.org/skos/OtherInputDevice
Notation: ES, conflicting resources: https://iso14224.org/skos/ElectricSignalSwivel, https://iso14224.org/skos/ExternalSleeveValve
Notation: IF, conflicting resources: https://iso14224.org/skos/FixedRoofWithInternalFloatingRoofStorageTank, https://iso14224.org/skos/IndirectHGFiredHeater
Notation: SD, conflicting resources: https://iso14224.org/skos/SteamTurbineDrivenElectricGenerator, https://iso14224.org/skos/SurgeDrumPressureVessel
Notation: DP, conflicting resources: https://iso14224.org/skos/DoublePipeHeatExchanger, https://iso14224.org/skos/DiaphragmStorageTank
Notation: CO, conflicting resources: https://iso14224.org/skos/CorrosionInputDevice, https://iso14224.org/skos/ContactorPressureVessel
Notation: AC, conflicting resources: https://iso14224.org/skos/AirCooledHeatExchanger, https://iso14224.org/skos/AlternatingCurrentElectricMotor
Notation: AX, conflicting resources: https://iso14224.org/skos/AxialTurboexpander, https://iso14224.org/skos/AxialSwivel, https://iso14224.org/skos/AxialCompressor
Notation: RL, conflicting resources: https://iso14224.org/skos/RelayControlUnit, https://iso14224.org/skos/RooflessStorageTank
Notation: CA, conflicting resources: https://iso14224.org/skos/CarbonSteelPiping, https://iso14224.org/skos/CoalescerPressureVessel
Notation: RE, conflicting resources: https://iso14224.org/skos/ReactorPressureVessel, https://iso14224.org/skos/ReciprocatingCompressor, https://iso14224.org/skos/ReciprocatingPump
Notation: BA, conflicting resources: https://iso14224.org/skos/BallValve, https://iso14224.org/skos/OtherFireDetector
Notation: PT, conflicting resources: https://iso14224.org/skos/PigTrapPressureVessel, https://iso14224.org/skos/PermanentTurret
Notation: SB, conflicting resources: https://iso14224.org/skos/PSVConventionalWithBellowValve, https://iso14224.org/skos/ScrubberPressureVessel
Notation: PC, conflicting resources: https://iso14224.org/skos/PlugAndCageValve, https://iso14224.org/skos/ComputerControlUnit, https://iso14224.org/skos/PrintedCircuitHeatExchanger
Notation: CE, conflicting resources: https://iso14224.org/skos/CentrifugalTurboexpander, https://iso14224.org/skos/CentrifugalPump, https://iso14224.org/skos/CentrifugalCompressor
Notation: DC, conflicting resources: https://iso14224.org/skos/DistillationColumnPressureVessel, https://iso14224.org/skos/DirectCurrentElectricMotor, https://iso14224.org/skos/DistributedControlUnit
Notation: SC, conflicting resources: https://iso14224.org/skos/PSVConventionalValve, https://iso14224.org/skos/ScrewCompressor, https://iso14224.org/skos/SlugCatcherPressureVessel
Notation: SP, conflicting resources: https://iso14224.org/skos/StripperPressureVessel, https://iso14224.org/skos/PSVPilotOperatedValve, https://iso14224.org/skos/SpeedInputDevice
Notation: ST, conflicting resources: https://iso14224.org/skos/ShellAndTubeHeatExchanger, https://iso14224.org/skos/StainlessSteelPiping

