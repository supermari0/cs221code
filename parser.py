import re, string, sys, os, random

"""
Usage: 
python parser.py <Filename>

"""

DELIMITER = '%%%'

def parser():
  directory = sys.argv[1]
  wikiFiles = os.listdir(directory)
  article_count = 0
  for filepath in wikiFiles:
    if article_count > 500:
      break
    # Randomly select whether to add this file to training or test set
    if random.random() < 0.5:
      json_file_name = 'train.json'
    else:
      json_file_name = 'test.json'
    json_file = open(json_file_name, 'a') # json file to write to
    if re.search('^index\.html.*', filepath) == None:
      try:
        wiki_file = open(directory + filepath)
        edits_file = open(directory + 'index.html?a=' + filepath)
      except IOError:
        print("could not open file " + filepath)
        continue

      edits_lines = edits_file.readlines()
      lines = wiki_file.readlines() # list of each line in the file as a string

      for line in lines: 
        title_obj = re.search('<title>.*</title>' , line)
        if title_obj != None: 
          break

      title = title_obj.group(0)
      title = title[7 : (title.find("Wikipedia, the free encyclopedia")-3)]
      title = title.replace('"', '\\"')

      json_file.write('{\n  ')
      json_file.write('"title" : ' + '"' + title + '",\n')

      links = find_links(lines)
      articleTextIndex = parseSectionHeaders(lines, json_file)
      parseArticleText(lines, json_file, articleTextIndex)
      write_links_to_json(json_file, links)


      parseEdits(edits_lines, json_file)

      most_frequent_users = find_most_frequent_users(edits_lines)
      write_users_to_json(json_file, most_frequent_users)

      json_file.write('}\n' + DELIMITER + '\n')
      wiki_file.close()
      json_file.close()
      article_count += 1

def parseEdits(edits_lines, json_file):

  json_file.write('"edits" : {\n')
  edits_line = ""
  cont = 0

  # Number of edits
  found_num_edits = False
  for index, line in enumerate(edits_lines): 
    obj = re.search('<h2>[0-9]+ edits on article.*', line)
    if obj != None: 
      edits_line = line
      cont = index
      startIndex = edits_line.find('<h2>') + 4
      endIndex = edits_line.find('edits')
      numEdits = edits_line[startIndex : endIndex]
      json_file.write('     "total" : ' + numEdits + ',\n')
      found_num_edits = True
      break
    
  if not found_num_edits:
    json_file.write('     "total" : 0,\n')

  # Number of anonymous edits
  found_anonymous_edits = False
  for line in edits_lines[cont : len(edits_lines)]: 
    obj = re.search('<li>Anonymous user edited [0-9]+ times</li>', line)
    if obj != None: 
      edits_line = line
      startIndex = edits_line.find('edited')
      endIndex = edits_line.find('times')
      anon_edits = edits_line[(startIndex + 7) : endIndex]
      json_file.write('    "anonymous" : ' + anon_edits + ',\n')
      found_anonymous_edits = True
      break

  if not found_anonymous_edits:
    json_file.write('    "anonymous" : 0,\n')

  found_edit_count = False 
  for line in edits_lines[cont : len(edits_lines)]: 
    obj = re.search('<li>Edit count of the top .*', line)
    if obj != None:
      edits_line = line
      startIndex = edits_line.find("users:")
      edits_line = edits_line[startIndex : len(edits_line)]
      endIndex = edits_line.find('<')
      top_10_percent = edits_line[7 : endIndex]
      json_file.write('    "top_10_percent" : ' + top_10_percent + ',\n')
      found_edit_count = True
      break

  if not found_edit_count:
     json_file.write('    "top_10_percent" : 0,\n')


  found_frequency = False
  for line in edits_lines:
    freq_line_obj = re.search('One edit par .* days', line)
    if freq_line_obj != None:
      freq_line = freq_line_obj.group(0)
      frequency_obj = re.search('[0-9]*\.[0-9]*', freq_line)
      frequency = frequency_obj.group(0)
      json_file.write('    "frequency" : ' + frequency + '\n')
      found_frequency = True
      break

  if not found_frequency:
    json_file.write('    "frequency": 0\n') 

  json_file.write('  },\n')

"""
Returns an array of strings
"""
def tokenize_text(json_file, entireArticleText): 
  all_words = string.split(entireArticleText)
  json_file.write('  "tokens": [\n')
  for i in range(0, len(all_words) - 1):
    json_file.write('    "' + all_words[i] + '",\n')
  json_file.write('    "' + all_words[len(all_words)-1] + '" ]\n')



"""
Arguments: 
1) lines - list of strings from the file
2) json_file - json_file to write to
3) article_text_index - index in lines of where the actual article text starts
"""

def parseArticleText(lines, json_file, article_text_index): 

  entireArticleText = ""

  dab = ""  # disambiguation line
  for line in lines: 
    obj = re.search('.*div class="dablink">.*', line)
    if obj != None: 
      dab = line
      break

  startIndex = (dab.find("<div class=\"dablink\">") + 21)
  dab_text = dab[startIndex : len(dab)]
  endIndex = dab_text.find(">.<")
  dab_text = dab_text[0 : endIndex+1]

  entireArticleText += dab_text

  end_article_index = 0

  for line in lines[article_text_index : len(lines)]: 
    if "<h2> <span class=\"mw-headline\" id=\"See_also\">See also</span></h2>" in line: 
      break
    else:
     entireArticleText += line

  entireArticleText = entireArticleText.replace("\n", "")
  entireArticleText = entireArticleText.replace('\\', '\\\\')
  entireArticleText = entireArticleText.replace('"', '\\"')

  entireArticleText.rstrip()
  
  #json_file.write('  "text" : ' + '"' + entireArticleText + '"' + ',\n')
  json_file.write('  "length" : ' + str(len(entireArticleText)) + ',\n')
  tokenize_text(json_file, entireArticleText)
  json_file.write('  },\n')


"""
Arguments: 
1) lines - list of strings from the file
2) json_file - json_file to write to

Returns the index of lines where the article text starts

"""

def parseSectionHeaders(lines, json_file): 
  
  json_file.write('  "body" : {\n')

  contentsStart = 0
  for index, line in enumerate(lines): 
    contents_obj = re.search('<h2>Contents</h2>' , line)
    if contents_obj != None: 
      contentsStart = index
      break


  contentsEnd = 0
  counter = contentsStart

  for line in lines[contentsStart : len(lines)]: 
    if ('</table>' in line): 
      contentsEnd = counter
      break
    counter += 1

  categories = []
  
  for line in lines[contentsStart : contentsEnd]:  # lines[contentsStart : contentsEnd] contains the HTML of the categories table
    obj = re.search('li class="toclevel-[0-9].*', line)
    if (obj != None): 
      startIndex = line.find("<span class=\"toctext\">")
      line = line[(startIndex + 22) : len(line)]
      endIndex = line.find('<')
      line = line[0 : endIndex]
      categories.append(line)

    
  json_file.write('    "headings" : [\n')
  if len(categories) > 0:
    categories[0] = categories[0].replace('"','\\"')
    json_file.write('      "' + categories[0] + '"')
    for cat in categories[1 : len(categories)]: 
      cat = cat.replace('"','\\"')
      json_file.write(',\n      "' + cat + '"')

  json_file.write('\n    ],\n')


  return contentsEnd + 1

def write_links_to_json(json_file, links):
  json_file.write('  "links" : [')
  for i in range(len(links)):
    json_file.write('"')
    json_file.write(links[i])
    json_file.write('"')
    if i != len(links) - 1:
      json_file.write(',\n  ')
  json_file.write('],\n  ')

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
      # Escape characters in link
      link = link.replace('\\','\\\\')
      links.append(link)
  return links

def find_most_frequent_users(edits_lines):
  ''' Given list of lines in edits file, return a list of tuples containing the
  top users and their respective edit numbers.'''
  users = []
  for line in edits_lines:
    user_obj = re.search('<a href="\.\./user/\?t=.*', line)
    if user_obj != None:
      user = user_obj.group(0)
      user_obj = re.search('>.*</a>.*', user)
      user_name_and_number = user_obj.group(0)
      user_name_end = user_name_and_number.find('<')
      user_name = user_name_and_number[1:user_name_end]
      string_after_user_name = user_name_and_number[user_name_end + 1:]
      user_number_start = string_after_user_name.find('(') + 1
      user_number_end = string_after_user_name.find(')')
      user_number = string_after_user_name[user_number_start:user_number_end]
      users.append((user_name, user_number))
  return users

def write_users_to_json(json_file, most_frequent_users):
  json_file.write('"top_editors" : [')
  for i in range(len(most_frequent_users)):
    username = most_frequent_users[i][0]
    num_edits = most_frequent_users[i][1]
    json_file.write('{ "username" : "' + username + '",')
    json_file.write('"num_edits" : ' + num_edits + '}')
    if i != len(most_frequent_users) - 1:
      json_file.write(',')
  json_file.write(']')

def main(): 
  parser()

if __name__ == "__main__": 
  main()
