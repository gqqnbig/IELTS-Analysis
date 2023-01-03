import glob
import math
import os
import re
import statistics
import sys

import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")

import Program


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
	while True:
		text, n1 = re.subn(r'\\(ps|ss|used|usemore|pr)\{([^\\]+?)\}', r'\2', text)
		text, n2 = re.subn(r'\\topicKeyword{.+?}{(.+?)}', r'\1', text)
		if n1 + n2 == 0:
			break
	return text


def removeCommands(text):
	while True:
		# \linebreak[1]
		text, n1 = re.subn(r'\\(linebreak\[\d\]|pause)', r'', text)
		# \footnote{...}
		text, n2 = re.subn(r'\\\w+(\{.+?\})*', r'', text)
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


def getWords(path):
	text = loadTextFromLatexFormat(path)
	doc = nlp(text)

	counts = Program.countWords(doc)

	# print(text)
	c = sum(counts.values())

	print(f'{path}: {c}')
	return c


def get_mean_std(results):
	# calculate mean
	mean = statistics.mean(results)

	std = statistics.stdev(results, mean)
	return mean, std


if __name__ == '__main__':
	# getWords(r'E:\IELTS Speaking\Jerry\Part 2\place for sports.tex')
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

	counts = [getWords(f) for f in referenceFiles]

	mean, std = get_mean_std(counts)

	print(mean, std)

	for t in targetFiles:
		count = getWords(t)
		if count < mean - std or count > mean + std:
			print(f'{os.path.basename(t)}: {count}. The number of words is off range ({mean - std :.2f}, {mean + std :.2f}).', file=sys.stderr)
