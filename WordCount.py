#!/usr/bin/env python

import glob
import math
import os
import re
import statistics
import sys

import spacy
from spacy.matcher import Matcher, DependencyMatcher

# nlp = spacy.load("en_core_web_sm")
# Large model to deal with "New York's a city."
# Small model thinks 's here is a particle.
nlp = spacy.load("en_core_web_trf")

import Utils


def removeSectionHeadings(text):
	"""
	Remove the Latex section headings
	:param text:
	:return: text without headings, and the number of headings removed
	"""
	text = re.sub(r'\\begin{\w+}.+\\end{\w+}', '', text, flags=re.DOTALL)

	text = re.sub(r'\\subsection\*?\{.+?\}', '', text)
	text = re.sub(r'\\subsubsection\*?\{.+?\}', '', text, flags=re.DOTALL)
	return text


def revealTextInCommands(text):
	# If a command parameter has other latex commands, this function will not reveal the parameter.
	# like \usemore{ ... \textipa{} ... }
	while True:
		text, n1 = re.subn(r'\\(ps|ss|used|usemore|pr|xout)\{([^\\]+?)\}', r'\2', text)
		text, n2 = re.subn(r'\\topicKeyword{.+?}{(.+?)}', r'\1', text)
		if n1 + n2 == 0:
			break
	return text


def removeCommands(text):
	while True:
		# \linebreak[1]
		text, n1 = re.subn(r'\\(linebreak\[\d\]|pause)', r'', text)
		# \footnote{...}
		text, n2 = re.subn(r'\\\w+(\{[^\\]+?\})*', r'', text)
		# {\cjkfont ...}
		if n1 + n2 == 0:
			break
	return text


def loadTextFromLatexFormat(path):
	with open(path, encoding='utf8') as f:
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
	# manual hyphenation
	text = text.replace(r'\-', '')

	try:
		p = text.index(r'\begin{hints}')
		text = text[p:]
	except:
		pass

	text = removeSectionHeadings(text)

	text = revealTextInCommands(text)

	text = removeCommands(text)
	return text


def checkHaveGot(doc):
	matcher = Matcher(nlp.vocab)
	pattern = [{'LEMMA': {'IN': ["have", 'had', "'ve"]}}, {'LEMMA': 'not', 'OP': '?'}, {'TEXT': "got"}]
	matcher.add("have got", [pattern])
	matches = matcher(doc)
	if len(matches) > 0:
		# print('Already have "have got".')
		return

	matcher = Matcher(nlp.vocab)
	pattern = [{'TEXT': {'IN': ["have", 'has', 'had']}}, {'TEXT': 'to'}, {'POS': 'VERB'}]
	matcher.add("have to do", [pattern])

	matches1 = matcher(doc)
	# if len(matches) > 0:
	# 	print("Use contractions in the following:", file=sys.stderr)

	matcher = DependencyMatcher(nlp.vocab)
	# It is not considered correct to say "Last year we had got a house in the city."
	# https://en.wiktionary.org/wiki/have_got
	pattern = [
		{
			"RIGHT_ID": "start",
			"RIGHT_ATTRS": {'TEXT': {'IN': ["have", 'has']}}
		},
		# {
		#     "LEFT_ID": "start",
		#     "REL_OP": ">",
		#     "RIGHT_ID": "founded_subject",
		#     "RIGHT_ATTRS": {"DEP": "nsubj"},
		# },
		{
			"LEFT_ID": "start",
			"REL_OP": ">",
			"RIGHT_ID": "have_object",
			"RIGHT_ATTRS": {"DEP": "dobj"},
		},
		# {
		#     "LEFT_ID": "founded_object",
		#     "REL_OP": ">",
		#     "RIGHT_ID": "founded_object_modifier",
		#     "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "compound"]}},
		# }
	]

	matcher.add("have sth", [pattern])
	matches2 = matcher(doc)

	if len(matches1) + len(matches2) >= 3:
		print('See if you can use "have got". "\'ve" is preferred.', file=sys.stderr)
	else:
		return

	for m in matches1:
		s = m[1] - 2
		if s < 0:
			s = 0
		e = m[2] + 2
		if e > len(doc):
			e = len(doc)
		print("{}:\t{}".format(nlp.vocab.strings[m[0]], str(doc[s:e]).strip()), file=sys.stderr)

	for m in matches2:
		match_id, token_ids = m
		start = min(token_ids)
		end = max(token_ids)
		# for i in range(len(token_ids)):
		# 	print(pattern[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text)
		print("have sth:\t{}".format(doc[start:end + 1]), file=sys.stderr)


def checkContractions(doc):
	matcher = Matcher(nlp.vocab)
	# The short form ’s (= is/has) can be written after nouns (including proper names),
	# question words, "here" and "now" as well as pronouns and unstressed "there".
	pattern = [{'POS': {'in': ['NOUN', 'PROPN']}, 'MORPH': {'IS_SUPERSET': ['Number=Sing']}},
			   {'TEXT': "'s", 'POS': 'AUX'}]
	matcher.add("'s", [pattern])

	pattern = [{'POS': {'in': ['NOUN', 'PROPN']}},
			   {'TEXT': {'in': ["'ll", "'d"]}, 'POS': 'AUX'}]  # 不需要"are"，因为‘re发音是一样的。
	matcher.add("'d-'ll", [pattern])

	matches = matcher(doc)
	if len(matches) > 0:
		# print('Already has contractions')
		return

	pattern = [{'POS': {'in': ['NOUN', 'PROPN']}, 'MORPH': {'IS_SUPERSET': ['Number=Sing']}},
			   {'TEXT': "is"}]
	matcher.add("is", [pattern])

	pattern = [{'POS': {'in': ['NOUN', 'PROPN']}},
			   {'TEXT': "had", 'POS': 'AUX'}]
	matcher.add("had", [pattern])

	pattern = [{'POS': {'in': ['NOUN', 'PROPN']}},
			   {'TEXT': {'in': ["will", "would"]}}]  # 不需要"are"，因为‘re发音是一样的。
	matcher.add("other", [pattern])

	matches = matcher(doc)
	if len(matches)>0:
		print("Use contractions in the following:", file=sys.stderr)
	for m in matches:
		s = m[1] - 2
		if s < 0:
			s = 0
		e = m[2] + 2
		if e > len(doc):
			e = len(doc)
		print("{}:\t{}".format(nlp.vocab.strings[m[0]], str(doc[s:e]).strip()), file=sys.stderr)


def getWords(path):
	text = loadTextFromLatexFormat(path)
	text = text.encode("ascii", "ignore").decode()
	text = re.sub(r'\{\s*\}', r'', text)
	text = re.sub(r'\(\s*\)', r'', text)
	doc = nlp(text)

	# for token in doc:
	# 	print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.morph)

	counts = Utils.countWords(doc)

	# print(text)
	c = sum(counts.values())

	print(f'{path}: {c}')

	# checkContractions(doc)
	# checkHaveGot(doc)
	return c, doc


def get_mean_std(results):
	# calculate mean
	mean = statistics.mean(results)

	std = statistics.stdev(results, mean)
	return mean, std


if __name__ == '__main__':
	# text = "I watch little television nowadays 'cause I work on computers every day."
	# doc = nlp(text)
	#
	# for token in doc:
	# 	print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.morph)

	# count, doc = getWords("B:\home of someone.tex")
	# for token in doc:
	# 	print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.morph)
	# checkContractions(doc)
	# exit()

	try:
		p = sys.argv.index('--ref')
		folder = os.path.abspath(sys.argv[p + 1])
	except:
		raise Exception('Reference folder is not given. Use --ref option to provide it.')
	if not os.path.isdir(folder):
		raise Exception(f'{folder} is not a folder.')

	targetFiles = []
	for i in range(len(sys.argv)):
		f = os.path.abspath(sys.argv[-1 - i])
		if not os.path.isfile(f) or not f.lower().endswith('.tex'):
			break
		targetFiles.append(f)

	if len(targetFiles) == 0:
		raise Exception(f'No target files (.tex) are provided from command line. {sys.argv}')

	referenceFiles = [f for f in glob.glob(folder + "//*.tex") if f not in targetFiles]

	if len(referenceFiles) < 2:
		print('No enough files to calculate statistics.')
		exit(0)

	counts = [getWords(f)[0] for f in referenceFiles]

	mean, std = get_mean_std(counts)

	print(mean, std)

	for t in targetFiles:
		count, doc = getWords(t)
		if count < mean - std or count > mean + std:
			print(f'{os.path.basename(t)}: {count}. The number of words is off range ({mean - std :.2f}, {mean + std :.2f}).', file=sys.stderr)

		checkContractions(doc)
		checkHaveGot(doc)
