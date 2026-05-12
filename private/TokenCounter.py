# Token counter
"""
# For PDF

from pypdf import PdfReader

reader = PdfReader("ISO14224_ApB.pdf")

text = ""
for page in reader.pages:
    text += page.extract_text() or ""

print(len(text))


import tiktoken

enc = tiktoken.encoding_for_model("gpt-5")

tokens = enc.encode(text)

print(len(tokens))

"""
# For Excel

import pandas as pd
import tiktoken

xls = pd.ExcelFile("INPUT.xlsx")

combined = ""

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet)
    combined += df.to_csv(index=False)

enc = tiktoken.encoding_for_model("gpt-5")

tokens = len(enc.encode(combined))

print(tokens)

