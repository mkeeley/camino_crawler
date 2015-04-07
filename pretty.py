import re

# given list of names or files, replace and remove characters to make them readable
def pretty(names):
	for i in range(len(names)): 
		names[i] = names[i].replace(' ', '').lower()
		names[i] = re.sub(r'\[.*?\]', '', names[i])
		names[i] = re.sub(r'\(.*?\)', '', names[i])
		names[i] = re.sub('[^a-z0-9-.]', '', names[i])
	return names
