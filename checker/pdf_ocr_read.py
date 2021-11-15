import requests
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import shutil
import csv

#add inbound file with Ticker collection
scantype='fact-sheet'
#scantype='monthly-holdings'
search_text_date = '09/30/2021'
search_text_list = [f'as of {search_text_date}', search_text_date, '9/30/2021']
search_text_list_output = ' OR '.join(search_text_list)

source_list_file = f'input/{scantype}.txt'

print(f'-------------- {scantype} scan started! --------------')
print(f'INFO -- Searching files for: {search_text_list_output}')

my_file = open(source_list_file, "r")
check_list = my_file.readlines()

results_list = []

for itm in check_list:
  data_row = {}
  check_item = itm.replace('\n','')

  print(f'INFO -- ####### Performing check for {scantype} on Item: {check_item} #######')

  processing_path = 'file_ocr_processing_path'

  if (os.path.exists(processing_path)):
    shutil.rmtree(processing_path)

  os.mkdir(processing_path)

  #Holdings file
  # holdings_identifier = '0996'
  # file_prefix = 'FS3'
  # holdings_type = 'RE'
  # month_to_check = '05'
  # item_id = f'{file_prefix}{holdings_type}{month_to_check}{holdings_identifier}'

  # Fact Sheet
  file_prefix = 'FS1'
  item_id = f'{file_prefix}{check_item}'


  payload = {'format': 'VOP', 'itemId': item_id}

  fileNameFinal = payload['itemId']
  url = 'https://secure05.principal.com/document-download/api/v1/public/document'

  print('INFO -- Get PDF by requesting from URL...')
  response = requests.get(url,stream=True,params=payload)
  url_output = response.url
  filename = f'{fileNameFinal}.pdf'
  print(f'INFO -- URL Requested: {url_output}')

  print(f'INFO -- {scantype} PDF URL Request Status Code: {response.status_code}')

  # if PDF URL request does not result in a 200 or success state
  # capture result and continue to next ticker
  if (response.status_code != 200):
    print(f'ERROR -- !!!!!!! PDF was not found at URL. !!!!!!!')

    print(f'INFO -- Clean up processing folder.')
    shutil.rmtree(processing_path)
    
    print(f'INFO -- >>>>>>> Capture results for {check_item}. <<<<<<<')
    data_row['CheckItem'] = check_item
    data_row['FileURL'] = url_output
    data_row['SearchText'] = search_text_list_output
    data_row['Status'] = 'PDF not found by URL'
    results_list.append(data_row)
    
    continue

  with open(f'{processing_path}/{filename}', 'wb') as pdf_file:
    pdf_file.write(response.content)
  # set processing path to file
  filePath = f'{processing_path}/{fileNameFinal}.pdf'

  #validate file is not empty
  if os.stat(filePath).st_size == 0:
    print('ERROR -- File is empty')
    print(f'INFO -- >>>>>>> Capture results for {check_item}. <<<<<<<')
    data_row['CheckItem'] = check_item
    data_row['FileURL'] = url_output
    data_row['SearchText'] = search_text_list_output
    data_row['Status'] = 'PDF file is empty or erring out'
    results_list.append(data_row)
    continue
  else:
    print('INFO -- File is not empty, continue processing.')
  
  print(f'INFO -- Set up PDF Reader.')
  # Windows requires setting poppler_path if you don't add poppler to PATH environment variable
  doc = convert_from_path(pdf_path=filePath, poppler_path="C:/poppler-0.68.0_x86/poppler-0.68.0/bin")
  # if poppler is installed and available in Path or environment settings, use this
  # doc = convert_from_path(pdf_path=filePath)

  path, fileName = os.path.split(filePath)
  fileBaseName, fileExtension = os.path.splitext(fileName)
  # print(f'information about doc - {doc}')

  image_counter = 1
  print('INFO -- Convert PDF Pages to images to prep for OCR scans.')
  for page in doc:
    
    filename = f'{processing_path}/page_{str(image_counter)}.jpg'
        
    # Save the image of the page in system
    page.save(filename, 'JPEG')

    # Increment the counter to update filename
    image_counter = image_counter + 1

  # Variable to get count of total number of pages
  filelimit = image_counter-1

  print(f'INFO -- Begin OCR scans for PDF pages and extract all text.')
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

  
  print(f'INFO -- Perform scan for searchText: {search_text_list_output}')

  # default status is fail
  status = 'Fail'
  for search_text in search_text_list:
    result = text.find(search_text)

    if (result != -1):
      print(f'INFO -- text found: {search_text}')
      status = 'Pass'
      break

    else:
      print(f'INFO -- text not found: {search_text}')
      status = 'Fail'

  print(f'INFO -- Clean up processing path.')
  shutil.rmtree(processing_path)

  print(f'INFO -- >>>>>>> Capture results for {check_item}. <<<<<<<')
  data_row['CheckItem'] = check_item
  data_row['FileURL'] = url_output
  data_row['SearchText'] = search_text_list_output
  data_row['Status'] = status
  results_list.append(data_row)

csv_output_columns = ['CheckItem', 'Status', 'FileURL', 'SearchText']
csv_file = f'output/{scantype}-output-summary.csv'

print(f'INFO -- Clear Output directory before writing results.')
if (os.path.exists('output') == False):
  os.mkdir('output')
else:
  shutil.rmtree('output')
  os.mkdir('output')

print(f'INFO -- Write Results for Scan - {csv_file}')
with open(csv_file, 'w',newline='') as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=csv_output_columns, quoting=csv.QUOTE_ALL)
  writer.writeheader()
  for data in results_list:
      writer.writerow(data)

print(f'-------------- {scantype} scan completed! --------------')


