import math
import re
import sys

import spacy
from spacy.matcher import Matcher

import Utils

nlp = spacy.load("en_core_web_sm")


def removeSectionHeadings(text, mode: int):
	"""
	Remove the Latex section headings
	:param text:
	:return: text without headings, and the number of headings removed
	"""
	count = 0
	if mode == 2:
		text, c = re.subn(r'\\begin{itemize}.+\\end{itemize}', '', text, flags=re.DOTALL)
		if c == 1:
			count = 2
		else:
			raise Exception('Prompt of Part 2 is expected to be in one itemize environment. But we found ' + str(c))

	text = re.sub(r'\\subsection\*?\{.+?\}', '', text)
	text, c = re.subn(r'\\subsubsection\*?\{.+?\}', '', text, flags=re.DOTALL)
	count += c
	return text, count


def checkTenses(doc):
	matcher = Matcher(nlp.vocab)
	# https://universaldependencies.org/u/pos/
	# https://machinelearningknowledge.ai/tutorial-on-spacy-part-of-speech-pos-tagging/

	# ignore Present Simple
	pattern = [{'TEXT': {'in': ['\'m', 'am', 'is', 'are']}}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBG"}]
	matcher.add("Present Continuous", [pattern])

	pattern = [{'TEXT': {'in': ['have', 'has', '\'ve']}}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBN"}]
	matcher.add("Present Perfect", [pattern])

	pattern = [{'TEXT': {'in': ['have', 'has']}}, {'TEXT': 'been'}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBG"}]
	matcher.add("Present Perfect Continuous", [pattern])

	# ignore Past Simple

	pattern = [{'TEXT': {'in': ['was', 'were']}}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBG"}]
	matcher.add("Past Continuous", [pattern])

	pattern = [{'TEXT': 'had'}, {"TAG": "VBN"}]
	matcher.add("Past Perfect", [pattern])

	pattern = [{'TEXT': 'had'}, {'TEXT': 'been'}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBG"}]
	matcher.add("Past Perfect Continuous", [pattern])

	pattern = [{'TEXT': 'will'}, {'TEXT': 'be'}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBG"}]
	matcher.add("Future Continuous", [pattern])

	pattern = [{'TEXT': 'will'}, {'TEXT': 'have'}, {"TAG": "VBN"}]
	matcher.add("Future Perfect", [pattern])

	pattern = [{'TEXT': 'will'}, {'TEXT': 'have'}, {'TEXT': 'been'}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBG"}]
	matcher.add("Future Perfect Continuous", [pattern])

	# for token in doc:
	# 	print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
	# 		  token.shape_, token.is_alpha, token.is_stop)

	matches = matcher(doc)

	nonoverlap = []
	# Matches may have overlaps.
	for m in matches:
		if any(m2[1] < m[1] and m2[2] >= m[2] or m2[1] <= m[1] and m2[2] > m[2] for m2 in matches) == False:
			nonoverlap.append(m)

	tenses = []
	for m in nonoverlap:
		# print("{}:\t{}".format(nlp.vocab.strings[m[0]], doc[m[1]:m[2]]))
		t = nlp.vocab.strings[m[0]]
		if t not in tenses:
			tenses.append(t)

	return tenses


def checkPassive(doc):
	matcher = Matcher(nlp.vocab)
	pattern = [{'LEMMA': 'be'}, {'TAG': 'RB', 'OP': '*'}, {"TAG": "VBN"}]
	matcher.add("Passive voice", [pattern])

	# for token in doc:
	# 	print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
	# 		  token.shape_, token.is_alpha, token.is_stop)

	matches = matcher(doc)
	# for m in matches:
	# 	print("{}:\t{}".format(nlp.vocab.strings[m[0]], doc[m[1]:m[2]]))
	if len(matches) > 0:
		return ["Passive voice"]
	else:
		return []


def checkBlackwords(doc):
	matcher = Matcher(nlp.vocab)
	pattern = [{'TEXT': 'think'}, {'OP': '!', 'TEXT': 'of'}]
	matcher.add("think", [pattern])

	matches = matcher(doc)
	for m in matches:
		raise Exception(f'Words not allowed: {doc[m[1]:m[2]]}')


# print("{}:\t{}".format(nlp.vocab.strings[m[0]], doc[m[1]:m[2]]))



if __name__ == '__main__':
	file = sys.argv[-1]
	if re.search('part\s?1', file, re.IGNORECASE):
		mode = 1
	elif re.search('part\s?2', file, re.IGNORECASE):
		mode = 2
	elif len(sys.argv) >= 2:
		if sys.argv[-2] == '1':
			mode = 1
		elif sys.argv[-2] == '2':
			mode = 2
		else:
			raise Exception('File mode is unknown. It must be Part 1 or Part 2. You provided ' + sys.argv[-2])
	else:
		raise Exception('File mode is unknown. It must be Part 1 or Part 2.')

	with open(file, encoding='utf8') as f:
		lines = f.readlines()
		for i in range(len(lines)):
			# all lines read by readlines() have trailing \n.
			lines[i] = lines[i].rstrip()
			l = lines[i]
			try:
				p = l.index('%')
				l = l[0:p]
				lines[i] = l
			except:
				pass

	for i in range(len(lines)):
		if i > 0:
			s = lines[i].lstrip()
			if s != "" and s[0].islower():
				lines[i - 1] += " " + lines[i]
				lines[i] = ""

	text = '\n'.join(lines)

	(text, questionCount) = removeSectionHeadings(text, mode)
	# remove latex commands, but keep its content
	text = re.sub(r'\\\w+\{(.+)\}', r'\1', text)

	# text = re.sub(r'[,.;!?] ', ' ', text)
	# text = re.sub(r'[,.;!?]($|[\n\r])', '', text)
	# text = re.sub(r'"\s|\s"', '', text)

	doc = nlp(text)
	checkBlackwords(doc)

	tenses = checkTenses(doc)
	passives = checkPassive(doc)
	if len(tenses) + len(passives) <= 2:
		print('Two few tenses (passive): ' + ', '.join(tenses + passives))
		print()

	counts = Utils.countWords(doc)

	# if counts['I'] > 4 * questionCount:
	# 	print(f'I: {counts["I"]} - too many')

	counts.pop('the')

	frequentWords = []
	n = 10
	for key in list(counts.keys()):
		if n == 0 or counts[key] <= math.ceil(questionCount * 1.2):
			break
		if len(key) <= 2:
			continue

		frequentWords.append(key + ": " + str(counts[key]))
		n = n - 1

	if len(frequentWords) > 0:
		print('Frequent words: ' + ', '.join(frequentWords))
		print()
