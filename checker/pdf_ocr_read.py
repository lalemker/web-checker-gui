import requests
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import shutil




processing_path = 'file_ocr_processing_path'
os.mkdir(processing_path)

#Holdings file
# payload = {'format':'VOP', 'itemId':'FS3RE050996'}
# FS1SABPX
payload = {'format': 'VOP', 'itemId':'FS1SABPX'}

#Fact sheet file
fileNameFinal = payload['itemId']
print(f'fileNameFinal: {fileNameFinal}')
url = 'https://secure05.principal.com/document-download/api/v1/public/document'
response = requests.get(url,stream=True,params=payload)
filename = f'{fileNameFinal}.pdf'

#with open(f'{processing_path}/{filename}', 'wb') as fd:
#    for chunk in r.iter_content(chunk_size=128):
#        fd.write(chunk)

with open(f'{processing_path}/{filename}', 'wb') as pdf_file:
  pdf_file.write(response.content)

filePath = f'{processing_path}/{fileNameFinal}.pdf'
doc = convert_from_path(filePath)
path, fileName = os.path.split(filePath)
fileBaseName, fileExtension = os.path.splitext(fileName)
print(f'information about doc - {doc}')

image_counter = 1
print('save images of each page in PDF')
for page in doc:
  
  filename = f'{processing_path}/page_{str(image_counter)}.jpg'
      
  # Save the image of the page in system
  page.save(filename, 'JPEG')

  # Increment the counter to update filename
  image_counter = image_counter + 1

# Variable to get count of total number of pages
filelimit = image_counter-1
  
# Creating a text file to write the output
outfile = "out_text.txt"
  
# Open the file in append mode so that 
# All contents of all images are added to the same file
# f = open(outfile, "a")

text = ''
# Iterate from 1 to total number of pages
for i in range(1, filelimit + 1):
  
  # Set filename to recognize text from
  # Again, these files will be:
  # page_1.jpg
  # page_2.jpg
  # ....
  # page_n.jpg
  filename = f'{processing_path}/page_{str(i)}.jpg'

  # Recognize the text as string in image using pytesserct
  text = text + str(pytesseract.image_to_string(Image.open(filename))) + f'\n\n --------- End of page {str(i)} --------- \n\n'

  # Finally, write the processed text to the file.
  # f.write(text)

# Close the file after writing all the text.
# f.close()

# The recognized text is stored in variable text
# Any string processing may be applied on text
# Here, basic formatting has been done:
# In many PDFs, at line ending, if a word can't
# be written fully, a 'hyphen' is added.
# The rest of the word is written in the next line
# Eg: This is a sample text this word here GeeksF-
# orGeeks is half on first line, remaining on next.
# To remove this, we replace every '-\n' to ''.
text = text.replace('-\n', '')

# print(text)

searchTextList = ['as of 09/30/2021','09/30/2021']

for searchText in searchTextList:
  result = text.find(searchText)

  if (result != -1):
    print(f'text found - {searchText}')
    break
  else:
    print(f'text not found - {searchText}')
    continue

shutil.rmtree(processing_path)

# for f in os.listdir('file_ocr_processing_path'):
#     os.remove(os.path.join(dir, f))



