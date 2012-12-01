import re, string, sys 

"""
Usage: 
python parser.py <Filename>

"""

def parser(): 

	print("HELLO")
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

	json_file.write('{\n\t')
	json_file.write('"title" : ' + '"' + title + '",\n')

	links = find_links(lines)
	write_links_to_json(json_file, links)
	articleTextIndex = parseSectionHeaders(lines, json_file)
	#parseArticleText(lines, json_file, articleTextIndex)

	json_file.write('}')

	json_file.close()

	wiki_file.close()


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


	
	json_file.write('\t\t"text" : ' + '"' + entireArticleText + '"' + ',\n')
	json_file.write('\t\t"length" : ' + str(len(entireArticleText)) + '\n')
	json_file.write('\t},\n')


"""
Arguments: 
1) lines - list of strings from the file
2) json_file - json_file to write to

Returns the index of lines where the article text starts

"""

def parseSectionHeaders(lines, json_file): 
	
	json_file.write('\t"body" : {\n')

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
			#print(line)
			startIndex = line.find("<span class=\"toctext\">")
			line = line[(startIndex + 22) : len(line)]
			endIndex = line.find('<')
			line = line[0 : endIndex]
			categories.append(line)

		
	json_file.write('\t\t"headings" : [\n')
	json_file.write('\t\t\t"' + categories[0] + '"')
	for cat in categories[1 : len(categories)]: 
		json_file.write(',\n\t\t\t"' + cat + '"')

	json_file.write('\n\t\t],\n')


	return contentsEnd + 1

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
