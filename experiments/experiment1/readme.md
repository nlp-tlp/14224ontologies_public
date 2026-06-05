
ISO 14224 FMEA failure-mode code compliance checker

# Purpose
-------
Checks an Excel FMEA worksheet for rows where the ISO 14224 failure mode (FM) code is:
  1. is the FM code missing,
  2. not in the ISO 14224 Annex B failure-mode code list, or
  3. a valid ISO 14224 code, but not allowed for the row's equipment class.

### The FMEA Excel spreadsheet

The spreadsheet contains FMEA data from an actual plant. The table has inconsistent use of colour and formats. An extract is shown below.

![Diagram](../fmeaTableImage.JPG)

## Summary of results in all 5 experiments
- Experiment 1 - Computer 1 + PDF + ChatGPT
- Experiment 2 - Computer 1 + TTL files + ChatGPT
- Experiment 3 - Computer 2 + PDF + ChatGPT
- Experiment 4 - Computer 2 + TTL + ChatGPT
 -Experiment 5 - Computer 2 + PDF + Claude

All experiments gave the same results

| Experiment                                                                                         | 1  | 2  | 3  |
|-----|----|----|----|
| No. of rows analysed         66 | 66 | 66 |
| Rows with missing/non-compliant/unsupported code    | 33 | 33 |    |
| Rows with FMEA FM code provided      |    |    | 54 |
| Non-compliant rows      |    |    | 25 |
| FM code not in the ISO 14224 FM code list           | 2  | 2  | 2  |
| FM code not permitted for resolved equipment class       | 19 | 19 | 5  |
| Missing ISO 14224 failure mode code        | 12 | 12 | 12 |
| Missing/ unrecognised ISO equipment class           |    |    | 18 |
| FM code is valid in ISO 14224 but not shown for equipment class 'Control logic units' in Table B.9 | 2  | 2  |    |
| FM code is valid in ISO 14224 but not shown for equipment class 'Input devices' in Table B.9       | 14 | 14 |    |
| FM code is valid in ISO 14224 but not shown for equipment class 'Valves' in Table B.9   | 3  | 3  | 3  |

## Prompt
The prompt codes are in the folder



