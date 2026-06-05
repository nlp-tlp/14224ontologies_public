# ISO 14224 FMEA Conversion and Failure Mode Validation

This folder contains a small workflow for converting an Autoclave Control Loop FMEA spreadsheet into RDF/Turtle and checking the ISO 14224 failure mode codes against the equipment-class-specific allowed failure modes.

The work supports two main tasks:

1. Convert each FMEA worksheet row into RDF named individuals.
2. Summarise ISO 14224 failure mode code quality and equipment-class compliance in CSV reports.

## Files in this folder

| File | Purpose |
|---|---|
| `fmea_csv_to_ttl.py` | Converts `AutoclaveControlLoopFMEA.csv` into RDF/Turtle. It maps ISO 14224 equipment class codes, failure mode codes, and failure mechanisms using the ISO 14224 ontology files. |
| `AutoclaveControlLoopFMEA_instances.ttl` | Generated RDF/Turtle file containing one `fmea:FMEAEntry` individual per FMEA worksheet row, plus assets, components, functional locations, failure mechanisms, maintenance strategies, control measures, and ISO 14224 links. |
| `AutoclaveControlLoopFMEA_warnings.csv` | Generated warning file from the conversion step. It lists rows where the equipment class code or failure mode code was blank or could not be mapped to the ISO 14224 ontology files. |
| `summarise_fmea_shacl_results.py` | Checks the generated RDF against `i14224_appendixB_allowed_failure_modes.ttl` and produces summary and row-level CSV validation reports. This version performs the check directly using RDF triples and does not require `pyshacl`. |
| `ISO14224_FM_Code_Check_report_completed.csv` | Generated summary report with one row per validation category and a list of worksheet rows in each category. |
| `ISO14224_FM_Code_Check_row_details.csv` | Generated row-by-row details report showing the category, FM code literal, mapped ISO 14224 failure mode, equipment class used, and FMEA entry URI. |
| `powershell script for running SHACL check.md` | PowerShell command example for running the validation summary script. |

## Expected repository layout

The scripts assume the following repository layout:

```text
14224ontologies_public/
  inDevelopment/
    i14224_appendixA.ttl
    i14224_appendixB.ttl
    i14224_clause3.ttl
    i14224_appendixB_allowed_failure_modes.ttl
  experiments/
    experiment2/
      AutoclaveControlLoopFMEA.csv
      fmea_csv_to_ttl.py
      summarise_fmea_shacl_results.py
```

The conversion script is designed to be run from:

```text
14224ontologies_public/experiments/experiment2
```

## Dependencies

Install the required Python packages in your virtual environment:

```powershell
pip install pandas rdflib
```

No `pyshacl` installation is required for the current validation summary script.

## Step 1: Convert the FMEA CSV to RDF/Turtle

From the `experiments/experiment2` directory, run:

```powershell
python .\fmea_csv_to_ttl.py
```

This creates:

```text
AutoclaveControlLoopFMEA_instances.ttl
AutoclaveControlLoopFMEA_warnings.csv
```

You can also override paths manually:

```powershell
python .\fmea_csv_to_ttl.py `
  --csv ".\AutoclaveControlLoopFMEA.csv" `
  --iso-a "..\..\inDevelopment\i14224_appendixA.ttl" `
  --iso-b "..\..\inDevelopment\i14224_appendixB.ttl" `
  --iso-c "..\..\inDevelopment\i14224_clause3.ttl" `
  --out ".\AutoclaveControlLoopFMEA_instances.ttl" `
  --warnings ".\AutoclaveControlLoopFMEA_warnings.csv"
```

## What the conversion does

The conversion script creates RDF individuals for the FMEA data, including:

- `fmea:FMEAEntry` individuals for each worksheet row.
- Asset individuals typed as `i14224:EquipmentUnit`.
- Component individuals typed as `i14224:MaintainableItem`.
- Functional locations typed as both `fmea:FunctionalLocation` and `i14224:TagNumber`.
- Links from each row to the original asset, component, functional location, maintenance strategy, control measure, and control group.
- ISO 14224 failure mode links using `i14224:hasFailureMode` where the FM code can be resolved.
- ISO 14224 equipment class links using `i14224:hasEquipmentClass` where the equipment class code can be resolved.
- Literal preservation of original source values such as failure effect, failure mechanism text, consequence note, hidden failure, and control frequency.

The generated TTL also declares a small local `fmea:` vocabulary for FMEA-specific classes and properties that are not part of ISO 14224.

## Step 2: Run the ISO 14224 failure mode compliance summary

From the `experiments/experiment2` directory, run:

```powershell
python .\summarise_fmea_shacl_results.py `
  --data ".\AutoclaveControlLoopFMEA_instances.ttl" `
  --allowed "..\..\inDevelopment\i14224_appendixB_allowed_failure_modes.ttl" `
  --out ".\ISO14224_FM_Code_Check_report_completed.csv" `
  --details-out ".\ISO14224_FM_Code_Check_row_details.csv"
```

This creates:

```text
ISO14224_FM_Code_Check_report_completed.csv
ISO14224_FM_Code_Check_row_details.csv
```

## What the validation checks

The validation summary checks each FMEA row and classifies it into one of the following categories:

| Category | Meaning |
|---|---|
| `1. FM code blank` | The worksheet row has no ISO 14224 failure mode code. |
| `2. FM code not in ISO 14224 Annex B` | The row has an FM code, but the code could not be mapped to an ISO 14224 Annex B failure mode individual. |
| `3. FM valid but not allowed for equipment class` | The FM code exists in ISO 14224 Annex B, but is not allowed for the row's equipment class according to `i14224_appendixB_allowed_failure_modes.ttl`. |
| `4. FM valid but class-specific check could not run (equipment class blank/unresolved)` | The FM code is valid, but no usable equipment class was available for the row, so the class-specific check could not be completed. |
| `5. Compliant (FM defined and allowed for equipment class)` | The FM code is valid and allowed for the row's equipment class. |
| `6. Total worksheet rows checked` | Total number of FMEA worksheet rows checked. |

The script checks allowed failure modes using `i14224:hasAllowedFailureMode`. It also considers superclass relationships using `rdfs:subClassOf*`, so an allowed failure mode on a superclass can be inherited by a subclass during the check.

## Current validation result

The current completed report contains the following summary:

| Category | Total rows | Worksheet rows |
|---|---:|---|
| FM code blank | 15 | 2, 3, 6, 10, 20, 21, 26, 27, 30, 31, 32, 61, 68, 69, 70 |
| FM code not in ISO 14224 Annex B | 2 | 14, 15 |
| FM valid but not allowed for equipment class | 5 | 7, 38, 39, 45, 63 |
| FM valid but class-specific check could not run | 18 | 4, 5, 11, 12, 13, 33, 40, 41, 44, 46, 47, 50, 52, 55, 56, 59, 60, 62 |
| Compliant | 29 | 8, 9, 16, 17, 18, 19, 22, 23, 24, 25, 28, 29, 34, 35, 36, 37, 42, 43, 48, 49, 51, 53, 54, 57, 58, 64, 65, 66, 67 |
| Total worksheet rows checked | 69 | 2–70 |

## Notes on equipment class mapping

The validation script supports several ways of finding the equipment class for a row:

1. A direct row-level triple:

```turtle
inst:FMEAEntry_row_0004 i14224:hasEquipmentClass i14224:InputDevice .
```

2. A failed equipment individual typed with an ISO 14224 equipment class.

3. An equipment code on the row, mapped in the script to an ISO 14224 class.

4. An optional component type fallback, enabled with:

```powershell
--use-component-type-fallback
```

The current default equipment code mapping in the summary script includes:

```python
DEFAULT_EQUIPMENT_CODE_TO_CLASS = {
    "CL": "ControlUnit",
    "VA": "Valve",
}
```

Add to this dictionary if the FMEA dataset starts using additional ISO 14224 equipment codes that are not already resolved directly in the generated TTL.

## Outputs to commit

For reproducibility, commit the scripts and the generated reports:

```text
fmea_csv_to_ttl.py
summarise_fmea_shacl_results.py
AutoclaveControlLoopFMEA_instances.ttl
AutoclaveControlLoopFMEA_warnings.csv
ISO14224_FM_Code_Check_report_completed.csv
ISO14224_FM_Code_Check_row_details.csv
powershell script for running SHACL check.md
README.md
```

The original source spreadsheet or CSV should also be committed if it is not confidential and the repository is allowed to contain the source FMEA data.
