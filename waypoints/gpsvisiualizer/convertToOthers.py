#/bin/python3
import argparse
import json
import requests
import re

format_json = open('formats.json').read()
values = json.loads(format_json)
choices = [type['input'] for type in values]
specials = dict([(type['input'], type.get('special')) for type in values])
suffixes = dict([(type['input'], type.get('suffix', type['input'])) for type in values])
parser = argparse.ArgumentParser(description = 'Converts the given file to all other file formats')
parser.add_argument('--type', required=True, metavar='FILETYPE', type=str, action='store', dest='fileType', choices=choices, help = 'type of input')
parser.add_argument('--file', required=True, metavar='FILE', type=open, action='store', dest='file', help = 'File to convert')

args = parser.parse_args()
url = 'https://www.gpsvisualizer.com/gpsbabel/gpsbabel_convert'
download_prefix = '/download/gpsbabel/'
filenameForUpload = args.file.name.rsplit('/')[-1]
fileToUpload = args.file.read()
fails = []
for outtype in [v for v in choices if v != args.fileType]:
  data = {
    'lang': '',
    'type': 'w',
    'intype': args.fileType,
    'outtype': outtype,
    'zip_output': '0',
    'all_types': '1',
    'submit': 'Convert the file'
  }
  specialOutput = specials[outtype]
  if specialOutput is not None:
     data.update(specialOutput)
  files = {
    'uploaded_file': (filenameForUpload, fileToUpload)
  }
  
  response = requests.post(url, data=data, files=files)
  if (response.status_code == 200):
    matcher = re.search('href="/download/gpsbabel/(.*)"', response.text)
    if matcher != None:
       suffix = matcher.group(1)
       fileContents = requests.get('https://www.gpsvisualizer.com/download/gpsbabel/%s' % suffix)
       name, dot, extension = filenameForUpload.rpartition('.')
       fileNameSuffix = suffixes[outtype]
       newName = (filenameForUpload, fileNameSuffix)
       if name:
          newName = (name, fileNameSuffix)
       outputFile = open('%s.%s' % newName, 'w+b')
       outputFile.write(fileContents.content)
       print('Successfully converted to %s' % outtype)
    else:
       fails.append(outtype)
print('Failed to convert: %s' % fails)

