import re

# given list of names or files, replace and remove characters to make them readable
def pretty(name):
	name = name.lower()
	name = re.sub(r'\[.*?\]|\(.*?\)' or '|[^a-z0-9-.]', '', name)
	name = re.split("[(--)|_]", name)
	name = '_'.join(filter(lambda a: not (a.isdigit() or not a), name))
	name = name.replace(' ', '')
	return name
