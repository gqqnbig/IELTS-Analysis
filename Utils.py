


def countWords(doc):
	d = dict()
	for token in doc:
		if token.pos_ in ['SPACE', 'PUNCT', 'X', 'SYM']:
			continue

		if token.lemma_ in d:
			# Increment count of word by 1
			d[token.lemma_] = d[token.lemma_] + 1
		else:
			# Add the word to dictionary with count 1
			d[token.lemma_] = 1

	return (dict(sorted(d.items(), key=lambda item: item[1], reverse=True)))
