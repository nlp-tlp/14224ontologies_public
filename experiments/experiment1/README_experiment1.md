# Experiment 1: ISO 14224 FMEA failure-mode code checking with LLMs

## Purpose

This experiment evaluates how well large language models can check failure-mode codes in an FMEA spreadsheet against ISO 14224 Annex B failure-mode rules.

The task is to review each FMEA row and classify the ISO 14224 failure mode (FM) code as:

1. blank or missing,
2. not present in the ISO 14224 Annex B failure-mode code list,
3. present in ISO 14224 but not allowed for the row's equipment class,
4. present in ISO 14224 but not checkable because the equipment class is blank or unresolved,
5. compliant because the code is valid and allowed for the resolved equipment class, or
6. part of the total worksheet rows checked.

The experiment compares report outputs produced from two different ways of providing the ISO 14224 reference information to an LLM:

- **PDF-based prompt**: the LLM is given the FMEA spreadsheet and the ISO 14224 Annex B PDF tables.
- **TTL-based prompt**: the LLM is given the FMEA spreadsheet and ontology/Turtle files containing equipment class codes, failure mode codes, and class-specific allowed failure modes.

## Repository contents

| File | Description |
| --- | --- |
| `Experiment_PDF_LLM_prompt.docx` | Prompt used for the PDF-based experiment. It instructs the LLM to use `ISO14224_ApB.pdf` and `AutoclaveControlLoopFMEA.xlsx` to produce a validation report. |
| `Experiment_TTL_LLM_prompt.docx` | Prompt used for the TTL-based experiment. It instructs the LLM to use the FMEA workbook plus ISO 14224 ontology files: `i14224_appendixA.ttl`, `i14224_appendixB.ttl`, `i14224_appendixB_allowed_failure_modes.ttl`, and `i14224_clause3.ttl`. |
| `ISO14224_FMEA_FM_Check_Report_PDF_ChatGPT_Computer1.xlsx` | PDF-based result report generated with ChatGPT on Computer 1. Includes summary, row detail, and reference sheets. |
| `ISO14224_FMEA_FM_Check_Report_PDF_ChatGPT_Computer2.xlsx` | PDF-based result report generated with ChatGPT on Computer 2. Includes summary, row detail, and ISO reference sheets. |
| `ISO14224_FM_Code_Check_PDF_Claude_Computer2.xlsx` | PDF-based result report generated with Claude on Computer 2. Includes summary and row-level detail. |
| `ISO14224_FM_Code_Check_Report_TTL_ChatGPT_Computer1.xlsx` | TTL-based result report generated with ChatGPT on Computer 1. Includes summary, row detail, and validation-basis sheets. |
| `ISO14224_FM_Code_Check_report_TTL_ChatGPT_Paul.xlsx` | TTL-based result report generated with another user's ChatGPT account. Contains a compact summary table. |
| `readme.md` | Earlier README draft used as a starting point for this Experiment 1 documentation. |

## Input data and reference sources

The experiment assumes the following source files were supplied to the LLM during the validation runs:

- `AutoclaveControlLoopFMEA.xlsx` — the FMEA worksheet to be checked.
- `ISO14224_ApB.pdf` — ISO 14224 Annex B failure-mode tables used in the PDF-based experiment.
- `i14224_appendixA.ttl` — ISO 14224 equipment class vocabulary.
- `i14224_appendixB.ttl` — ISO 14224 failure mode vocabulary.
- `i14224_appendixB_allowed_failure_modes.ttl` — class-specific allowed failure-mode mappings.
- `i14224_clause3.ttl` — additional ISO 14224 vocabulary definitions.

The uploaded result workbooks record that 66 non-empty FMEA worksheet rows were checked.

## Validation logic

For each FMEA row, the checking process needs to use the row's equipment class and failure-mode code.

The validation procedure is:

1. Read the FM code from the FMEA row.
2. If the FM code cell is blank, classify the row as **FM cell code is blank**.
3. If the FM code is present but not in the ISO 14224 Annex B failure-mode code list, classify the row as **FM code is not in the ISO 14224 Annex B list**.
4. If the FM code is valid but the equipment class is blank or cannot be resolved, classify the row as **class-specific check could not be run**.
5. If the FM code is valid and the equipment class is resolved, check whether that FM code is allowed for that equipment class.
6. If the FM code is not allowed for the resolved equipment class, classify it as **valid but not allowed for that equipment class**.
7. If the FM code is valid and allowed for the resolved equipment class, classify the row as **compliant**.

## Expected summary result

Across the uploaded Experiment 1 report files, the recurring summary result is:

| Check category | Count | Worksheet row numbers |
| --- | ---: | --- |
| FM cell code is blank | 12 | 2, 3, 6, 10, 20, 21, 26, 27, 30, 31, 32, 61 |
| FM code is not in the ISO 14224 Annex B list | 2 | 14, 15 |
| FM code is valid but not allowed for the resolved equipment class | 5 | 7, 38, 39, 45, 63 |
| FM code is valid but class-specific check could not be run because the equipment class was blank or unresolved | 18 | 4, 5, 11, 12, 13, 33, 40, 41, 44, 46, 47, 50, 52, 55, 56, 59, 60, 62 |
| Compliant: FM code is defined and allowed for the resolved equipment class | 29 | — |
| Total worksheet rows checked | 66 | 2–67 |

## Report workbook structure

The generated Excel reports use one or more of the following worksheets:

- **Summary** — aggregate counts for each validation category and the affected worksheet row numbers.
- **Row detail / Row details / Detail** — row-by-row classification showing asset ID, component ID, equipment class, FM code, and validation status.
- **Reference / ISO reference / Validation basis** — source assumptions, valid code lists, equipment-class mappings, and allowed failure-mode sets used by the check.

## How to interpret the output

The most important fields in the result reports are:

- **Worksheet row** — the row number in the original FMEA workbook.
- **Equipment class code** — the ISO 14224 equipment class code used for class-specific checking, for example `CL` or `VA`.
- **FM code** — the ISO 14224 failure-mode code being validated.
- **Validation status / Result** — the classification assigned to the row.
- **Allowed FM codes for resolved class** — the list of failure-mode codes permitted for the row's resolved equipment class.

Rows in categories 1–4 require review or correction before the FMEA data can be treated as ISO 14224-compliant. Rows in category 5 are compliant for the purposes of this check.

## Key observation from Experiment 1

The LLMs were able to produce the required report structure and identify the main categories of failure-mode code problems. However, the experiment also shows why explicit, machine-readable reference data is useful: the TTL-based prompt provides the code list and class-specific allowed-mode mappings directly, reducing the need for the model to interpret PDF tables visually.

## Limitations

This repository contains prompt documents and generated report workbooks. It does not contain an executable Python validation script for Experiment 1.

For repeatable automated validation, the next step would be to implement a script that:

1. reads the FMEA workbook,
2. parses the ISO 14224 TTL files,
3. resolves equipment class codes and failure-mode codes,
4. checks each row against `i14224_appendixB_allowed_failure_modes.ttl`, and
5. writes a summary and row-detail report to Excel or CSV.

## Suggested naming convention for future runs

Use filenames that record the reference source, model, machine or account, and run number, for example:

```text
ISO14224_FM_Check_<PDF-or-TTL>_<Model>_<Computer-or-Account>_<RunNo>.xlsx
```

Example:

```text
ISO14224_FM_Check_TTL_ChatGPT_Computer1_Run01.xlsx
```

## Status

Experiment 1 demonstrates that LLM-assisted ISO 14224 failure-mode code checking is feasible, but the most reliable path is to combine the LLM workflow with explicit ontology-based validation rules and reproducible scripts.
