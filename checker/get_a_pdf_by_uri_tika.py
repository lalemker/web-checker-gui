import requests
import os
from tika import parser

payload = {'format':'VOP', 'itemId':'FS3RE050996'}
url = 'https://secure05.principal.com/document-download/api/v1/public/document'
response = requests.get(url,stream=True,params=payload)
filename = "fact_sheet.pdf"

raw = parser.from_file(f'file/{filename}')
raw = str(raw)

safe_text = raw.encode('utf-8', errors='ignore')

safe_text = str(safe_text).replace("\n", "").replace("\\", "")
print('--- safe text ---' )
print( safe_text )