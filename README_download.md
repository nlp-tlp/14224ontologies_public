# ISO 14224 Semantic Collaboration Repository

This repository develops a machine-readable semantic version of ISO 14224, with example data, validation workflows, and experiments using LLMs and RDF.

## Goals

1. Build and publish a stable, machine-readable RDF/Turtle representation of key ISO 14224 concepts, including:
   - terms and definitions from Clause 3,
   - failure mode data from Appendix B,
   - equipment classes from Appendix A,
   - allowed failure-mode mappings by equipment class.
2. Provide example data, validation workflows, and experiments that show how FMEA and maintenance data can be linked to ISO 14224.
3. Explore ontology modelling choices aligned to top-level ontologies such as IDO, IOF, and DOLCE.
4. Demonstrate the value of explicit ontology/TTL reference data for LLM-assisted validation and automated checks.

## What is ISO 14224?

ISO 14224 is the international standard for reliability and maintenance data collection. It is widely used in industries such as petroleum, natural gas, petrochemical, and mining.

The standard defines:

- equipment data (taxonomy, attributes);
- failure data (failure causes, consequences);
- maintenance data (actions, resources, downtime).

A machine-readable ISO 14224 vocabulary can help organisations share, validate, and analyse FMEA and work order data more consistently.

## Why this repository exists

Manual FMEA and maintenance tables are often inconsistent and hard to automate. This repository is intended to:

- reduce ambiguity in failure mode and equipment class usage,
- make ISO 14224 concepts available as Linked Data,
- support data quality checks with SHACL-style validation,
- demonstrate how LLMs perform with and without explicit ontology data,
- provide reproducible examples and scripts for engineers and researchers.

## Repository structure

- `catalog-v001.xml`, `LICENSE`, `README.md` — root metadata and documentation
- `imports/` — source RDF/TTL imports and external ontology material
- `inDevelopment/` — working TTL files for ISO 14224 concepts and allowed failure mode mappings
- `experiments/experiment1/` — LLM experiment documentation, prompts, and generated reports
- `experiments/experiment2/` — FMEA-to-RDF conversion and validation scripts, data, and outputs

## Experiments

This repo contains two linked experiments:

### Experiment 1: LLM-assisted failure mode validation

See `experiments/experiment1/README_experiment1.md`.

This experiment compares two approaches for validating an FMEA spreadsheet against ISO 14224:

- a **PDF-based prompt** that gives the model the FMEA workbook plus ISO 14224 Annex B PDF tables,
- a **TTL-based prompt** that gives the model the FMEA workbook plus RDF/Turtle files for equipment classes and allowed failure modes.

The key insight is that TTL-based reference data can reduce ambiguity and improve model reliability compared to raw PDF reference material.

### Experiment 2: FMEA conversion and failure mode compliance

See `experiments/experiment2/README_experiment2.md`.

This experiment converts an FMEA spreadsheet into RDF/Turtle and then checks failure mode codes against ISO 14224 equipment-class-specific allowed failure modes.

The workflow includes:

- `fmea_csv_to_ttl.py` — converts FMEA rows into RDF individuals,
- `summarise_fmea_shacl_results.py` — summarises validation results in CSV reports,
- generated outputs such as `AutoclaveControlLoopFMEA_instances.ttl`, warning files, and validation reports.

## Key files and outputs

### ISO 14224 ontology files in `inDevelopment/`

- `i14224_clause3.ttl` — Clause 3 terms and definitions
- `i14224_appendixA.ttl` — equipment classes from Appendix A
- `i14224_appendixB.ttl` — failure modes and mechanisms from Appendix B
- `i14224_appendixB_allowed_failure_modes.ttl` — allowed failure modes by equipment class
- `i14224_failure_mode_validation_shape.ttl` — validation shape for equipment-class/failure-mode checks

### Experiment files

- `experiments/experiment1/README_experiment1.md` — details of the LLM validation experiment
- `experiments/experiment2/README_experiment2.md` — details of the FMEA conversion and validation workflow
- `experiments/experiment2/fmea_csv_to_ttl.py` — converter script
- `experiments/experiment2/summarise_fmea_shacl_results.py` — validation summary script
- `experiments/experiment2/AutoclaveControlLoopFMEA.csv` — input FMEA data
- generated reports and result workbooks in experiment directories

## How to run the main workflow

From `experiments/experiment2`:

```powershell
python .\fmea_csv_to_ttl.py \
  --csv .\AutoclaveControlLoopFMEA.csv \
  --iso-a ..\..\inDevelopment\i14224_appendixA.ttl \
  --iso-b ..\..\inDevelopment\i14224_appendixB.ttl \
  --iso-c ..\..\inDevelopment\i14224_clause3.ttl \
  --out .\AutoclaveControlLoopFMEA_instances.ttl \
  --warnings .\AutoclaveControlLoopFMEA_warnings.csv

python .\summarise_fmea_shacl_results.py \
  --data .\AutoclaveControlLoopFMEA_instances.ttl \
  --allowed ..\..\inDevelopment\i14224_appendixB_allowed_failure_modes.ttl \
  --out .\ISO14224_FM_Code_Check_report_completed.csv
```

## Notes on modelling

- The current TTL files capture ISO 14224 concepts as OWL classes and named individuals.
- The repository is intentionally not yet aligned to a single top-level ontology; future work can add explicit alignments to IDO, IOF, or DOLCE.
- The namespace `https://iso14224.org/ontology/i14224/rdl/` is used consistently for current terms.

## Disclaimer

This repository contains an original academic interpretation of ISO 14224 concepts.

- It is not a substitute for the official ISO standard.
- It is not endorsed by ISO or IEC.
- Consult the official ISO/IEC publications for authoritative definitions and requirements.
