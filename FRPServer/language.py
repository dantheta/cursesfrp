
def nl_join(items):
	if isinstance(items, set):
		lst = list(items)
	else:
		lst = items

	if len(lst) == 1:
		return lst[0]
	return ", ".join(lst[:-1]) + " and " + lst[-1]

def singular(word):
	if word.startswith(('a','e','i','o','h')):
		return "an"
	else:
		return "a"

def pluralize(word):
	if word.endswith('y'):
		return word[:-1] + 'ies'
	if word.endswith('s'):
		return word
	return word + 's'

def to_be_plural(word, pl):
	if pl:
		return "are " + pluralize(word)
	else:
		return "is {0} {1}".format(singular(word), word)
	
