import requests
import os
import PyPDF2

#Holdings file
payload = {'format':'VOP', 'itemId':'FS3RE050996'}

#Fact sheet file

url = 'https://secure05.principal.com/document-download/api/v1/public/document'
response = requests.get(url,stream=True,params=payload)
filename = "fact_sheet.pdf"

#with open(f'file/{filename}', 'wb') as fd:
#    for chunk in r.iter_content(chunk_size=128):
#        fd.write(chunk)

with open(f'file/{filename}', 'wb') as pdf_file:
  pdf_file.write(response.content)

pdfFileObj = open(f'file/{filename}', 'rb')

pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 

num_of_pages = pdfReader.getNumPages()
print(f'\nNumber of Pages found: {num_of_pages}\n\n')

if pdfReader.isEncrypted:
  pdfReader.decrypt("")
  print(pdfReader.getPage(0).extractText())
#pages = pdfReader.pages
#print(f'\nPages found: {pages}\n\n')

else:
    print(pdfReader.getPage(0).extractText())

#pageObj = pdfReader.getPage(0)

#print('\n\nExtract Text:\n')
#print(pageObj.extractText())

#print('\n\nExtract Contents:\n')
#print(pageObj.getContents())
#print(pageObj.getContents()[0])
#print(pageObj.getContents()[0])
#print(pageObj.getContents()[2])
#print(pageObj.getContents()[3])

pdfFileObj.close()
