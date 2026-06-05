## powershell script

python .\summarise_fmea_shacl_results.py `
  --data ".\AutoclaveControlLoopFMEA_instances.ttl" `
  --allowed "..\..\inDevelopment\i14224_appendixB_allowed_failure_modes.ttl" `
  --out ".\ISO14224_FM_Code_Check_report_completed.csv"