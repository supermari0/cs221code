import re, string, sys 

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

	json_file.write('{\n')

	json_file.write('}')


	json_file.close()

	wiki_file.close()

parser()