import re, string, sys 

"""
Usage: 
python parser.py <Filename>

"""

def parser(): 
  filepath = sys.argv[1]
  wiki_file = open(filepath)
  lines = wiki_file.readlines() # list of each line in the file as a string

  for line in lines: 
    title_obj = re.search('<title>.*</title>' , line)
    if title_obj != None: 
      break

  title = title_obj.group(0)
  title = title[7 : (title.find("Wikipedia, the free encyclopedia")-3)]

  json_file_name = title + '.json'

  json_file = open(json_file_name, 'w') # json file to write to

  json_file.write('{\n  ')
  json_file.write('"title" : ' + '"' + title + '",\n  ')
  links = find_links(lines)
  write_links_to_json(json_file, links)
  json_file.write(',\n  ')

  json_file.write('}')

  json_file.close()
  wiki_file.close()

def write_links_to_json(json_file, links):
  json_file.write('"links" : [')
  for i in range(len(links)):
    json_file.write('"')
    json_file.write(links[i])
    json_file.write('"')
    if i != len(links) - 1:
      json_file.write(',')
  json_file.write(']')

def find_links(lines):
  links = []
  for line in lines:
    link_obj = re.search('<a href="/wiki/.*" title=".*">', line)
    if link_obj != None:
      link = link_obj.group(0)
      link_obj = re.search('title=".*"', link)
      link = link_obj.group(0)
      link_obj = re.search('"[^"]*"', link)
      link = link_obj.group(0)
      link = link[1:-1]
      links.append(link)
  return links

parser()
