import re, string, sys, os, random

"""
Usage: 
python parser.py <Filename>

"""

DELIMITER = '%%%'

def parser():
  directory = sys.argv[1]
  wikiFiles = os.listdir(directory)
  #json_file_name = 'wiki.json'
  #json_file = open(json_file_name, 'w')
  for filepath in wikiFiles:
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

      json_file.write('{\n  ')
      json_file.write('"title" : ' + '"' + title + '",\n')

      links = find_links(lines)
      cat_and_index = parse_section_headers(lines, json_file)
      article_text_index = cat_and_index[1]
      entire_article_text = parse_article_text(lines, json_file, article_text_index)
      write_links_to_json(json_file, links, entire_article_text, cat_and_index[0])


      parse_edits(edits_lines, json_file)

      most_frequent_users = find_most_frequent_users(edits_lines)
      write_users_to_json(json_file, most_frequent_users)

      json_file.write('}\n' + DELIMITER + '\n')
      wiki_file.close()
      json_file.close()
  #json_file.close()

def parse_edits(edits_lines, json_file):

  json_file.write('"edits" : {\n')
  edits_line = ""
  cont = 0

  for index, line in enumerate(edits_lines): 
    obj = re.search('<h2>[0-9]+ edits on article.*', line)
    if obj != None: 
      edits_line = line
      cont = index
      break

  start_index = edits_line.find('<h2>') + 4
  end_index = edits_line.find('edits')

  num_edits = edits_line[start_index : end_index]
  json_file.write('     "total" : ' + num_edits + ',\n')

  for line in edits_lines[cont : len(edits_lines)]: 
    obj = re.search('<li>Anonymous user edited [0-9]+ times</li>', line)
    if obj != None: 
      edits_line = line
      break

  start_index = edits_line.find('edited')
  end_index = edits_line.find('times')

  anon_edits = edits_line[(start_index + 7) : end_index]
  json_file.write('    "anonymous" : ' + anon_edits + ',\n')

  for line in edits_lines[cont : len(edits_lines)]: 
    obj = re.search('<li>Edit count of the top .*', line)
    if obj != None:
      edits_line = line
      break

  start_index = edits_line.find("users:")
  edits_line = edits_line[start_index : len(edits_line)]
  end_index = edits_line.find('<')
  top_10_percent = edits_line[7 : end_index]

  json_file.write('    "top_10_percent" : ' + top_10_percent + ',\n')


  for line in edits_lines:
    freq_line_obj = re.search('One edit par .* days', line)
    if freq_line_obj != None:
      freq_line = freq_line_obj.group(0)
      frequency_obj = re.search('[0-9]*\.[0-9]*', freq_line)
      frequency = frequency_obj.group(0)
      json_file.write('    "frequency" : ' + frequency + '\n')


  json_file.write('  },\n')

"""
Arguments: 
1) lines - list of strings from the file
2) json_file - json_file to write to
3) article_text_index - index in lines of where the actual article text starts

Returns the entire article text as a string
"""

def parse_article_text(lines, json_file, article_text_index): 

  entire_article_text = ""

  dab = ""  # disambiguation line
  for line in lines: 
    obj = re.search('.*div class="dablink">.*', line)
    if obj != None: 
      dab = line
      break

  start_index = (dab.find("<div class=\"dablink\">") + 21)
  dab_text = dab[start_index : len(dab)]
  end_index = dab_text.find(">.<")
  dab_text = dab_text[0 : end_index+1]

  dab_text = dab_text.replace("\n", "")

  entire_article_text += dab_text.replace('"', '\\"')

  end_article_index = 0

  for line in lines[article_text_index : len(lines)]: 
    if "<h2> <span class=\"mw-headline\" id=\"See_also\">See also</span></h2>" in line: 
      break
    else: 
      entire_article_text += line.replace('"', '\\"')

  entire_article_text = entire_article_text.replace("\n", "")
  
  json_file.write('  "text" : ' + '"' + entire_article_text + '"' + ',\n')
  json_file.write('  "length" : ' + str(len(entire_article_text)) + '\n')
  json_file.write('  },\n')

  return entire_article_text


"""
Arguments: 
1) lines - list of strings from the file
2) json_file - json_file to write to

Returns a tuple: (categories, the index of lines where the article text starts)

"""

def parse_section_headers(lines, json_file): 
  
  json_file.write('  "body" : {\n')

  contents_start = 0
  for index, line in enumerate(lines): 
    contents_obj = re.search('<h2>Contents</h2>' , line)
    if contents_obj != None: 
      contents_start = index
      break


  contents_end = 0
  counter = contents_start

  for line in lines[contents_start : len(lines)]: 
    if ('</table>' in line): 
      contents_end = counter
      break
    counter += 1

  categories = []
  
  for line in lines[contents_start : contents_end]:  # lines[contents_start : contents_end] contains the HTML of the categories table
    obj = re.search('li class="toclevel-[0-9].*', line)
    if (obj != None): 
      #print(line)
      start_index = line.find("<span class=\"toctext\">")
      line = line[(start_index + 22) : len(line)]
      end_index = line.find('<')
      line = line[0 : end_index]
      categories.append(line)

    
  json_file.write('    "headings" : [\n')
  if len(categories) > 0:
    json_file.write('      "' + categories[0] + '"')
    for cat in categories[1 : len(categories)]: 
      json_file.write(',\n      "' + cat + '"')

  json_file.write('\n    ],\n')




  return (categories, contents_end + 1)

def write_links_to_json(json_file, links, entire_article_text, categories):



  json_file.write('  "links" : [\n')
  
  if len(links) > 0: 
    for i in range(len(links) - 1):
      number_of_mentions = get_number_of_mentions(links[i], entire_article_text, categories)
      json_file.write('    { "name" : ' + '"' + links[i] + '" , ' + '"number_of_mentions": ' + str(number_of_mentions) + '},\n')

    number_of_mentions = get_number_of_mentions(links[len(links) - 1], entire_article_text, categories)
    json_file.write('    { "name" : ' + '"' + links[len(links) - 1] + '" , ' + '"number_of_mentions": ' + str(number_of_mentions) + '}\n')
  

  """number_of_mentions = get_number_of_mentions('Etymology', entire_article_text, categories)
  json_file.write('    { "name" : ' + '"' + 'Etymology' + '" , ' + '"number_of_mentions": ' + str(number_of_mentions) + '}\n')
  """
  json_file.write('  ],\n')


def get_number_of_mentions(link, entire_article_text, categories): 
  curr = entire_article_text
  counter = 0

  while True: 
    index = curr.find(link)
    if index == -1: 
      break
    cmp1 = '\\" title'
    cmp2 = '\\">'

    if curr[index + len(link) : index + len(link) + 8] != cmp1: 
 
      if curr[index + len(link) : index + len(link) + 3] != cmp2:  
        counter += 1

    curr = curr[index + len(link): len(curr)]

  return counter


def find_links(lines):
  links = []
  for line in lines:
    link_obj = re.search('<a href="/wiki/.*" title=".*">[^<]*</a>', line)
    if link_obj != None:
      link = link_obj.group(0)
      rest = link
      while True: 
        end_index = rest.find('</a>')
        start_index = rest.find('<a href')
        curr_link = rest[start_index : end_index]
        link_obj = re.search('title=".*"', curr_link)
        if link_obj != None: 
          curr_link = link_obj.group(0)
          link_obj = re.search('"[^"]*"', curr_link)
          if link_obj != None: 
            curr_link = link_obj.group(0)
            curr_link = curr_link[1:-1]

            if curr_link not in links: 
              links.append(curr_link)

        if end_index == len(rest) - 4: 
          break
        rest = rest[end_index + 4 : len(rest)]

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
      user_number_start = user_name_and_number.find('(') + 1
      user_number_end = user_name_and_number.find(')')
      user_number = user_name_and_number[user_number_start:user_number_end]
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
