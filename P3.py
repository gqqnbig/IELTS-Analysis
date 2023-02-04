import glob
import os
import sys

import spacy
from spacy.matcher import Matcher

from WordCount import loadTextFromLatexFormat

# try:
# 	nlp = spacy.load("en_core_web_sm")
# except:
nlp = spacy.load("en_core_web_trf")


def createMatchRule(textList):
	if any(' ' in t or '-' in t for t in textList):
		raise Exception(f"You can't have more than one word in text list. You passed in {textList}.")

	return [{'OP': '!', 'POS': 'ADV'}, {'LOWER': {'IN': textList}}, {'OP': '!', 'TEXT': '-'}]


def checkAdvAdjCollocation(doc):
	matcher = Matcher(nlp.vocab)
	matcher.add("highly", [createMatchRule(['successful', 'vital', 'probable', 'improbable', 'competitive', 'recommended', 'effective', 'contagious', 'critical', 'intelligent', 'likely', 'unlikely', 'sensitive', 'controversial', 'suspicious'])])
	matcher.add('utterly/absolutely', [createMatchRule(['disastrous', 'disgusting', 'disgusted', 'impossible', 'useless', 'miserable', 'wrong', 'pointless', 'worthless', 'fabulous', 'unrealistic'])])
	matcher.add('unbelievably/ridiculously/incredibly', [createMatchRule(['cheap', 'expensive', 'big', 'small', 'long', 'short', 'easy', 'early', 'late', 'cold', 'old'])])
	matcher.add('potentially', [
		createMatchRule(['dangerous', 'hazardous', 'fatal', 'toxic', 'fruitful']),
		[{'OP': '!', 'POS': 'ADV'}, {'LOWER': 'game'}, {'LOWER': '-'}, {'LOWER': 'changing'}],
		[{'OP': '!', 'POS': 'ADV'}, {'LOWER': 'life'}, {'LOWER': 'threatening'}],
	])
	matcher.add('blatantly', [createMatchRule(['false', 'unfair', 'untrue', 'dishonest', 'wrong', 'mistaken'])])
	matcher.add('widely', [createMatchRule(['believed', 'practiced', 'spoken', 'used', 'distributed', 'known', 'publicized', 'available'])])

	matcher.add('absurdly', [createMatchRule(['low', 'high', 'easy', 'difficult'])])
	matcher.add('thoroughly', [createMatchRule(['prepared', 'enjoyable', 'convinced', 'agree', 'satisfying', 'clean'])])
	matcher.add('patently', [createMatchRule(['true', 'false', 'clear', 'clever'])])
	matcher.add('wildly', [createMatchRule(['inappropriate', 'inaccurate', 'exaggerated', 'unrealistic', 'popular', 'successful', 'unsuccessful'])])
	matcher.add('mildly', [createMatchRule(['entertained', 'surprised', 'amused', 'irritated', 'offensive'])])
	matcher.add('downright', [
		createMatchRule(['wrong', 'dishonest', 'hostile', 'rude', 'disgraceful', 'immoral', 'ugly']),
		[{'OP': '!', 'POS': 'ADV'}, {'LOWER': 'mean', 'POS': 'ADJ'}],
		[{'LOWER': 'mean', 'POS': 'ADJ', 'IS_SENT_START': True}],
	])
	matcher.add('heavily', [createMatchRule(['armed', 'pregnant', 'subsidized', 'criticized'])])
	matcher.add('seriously', [createMatchRule(['stubborn', 'genius', 'strong', 'smart', 'delicious', 'good', 'injured', 'damaged', 'hurt', 'wounded'])])
	matcher.add('strictly', [createMatchRule(['speaking', 'regulated', 'limited', 'comparative'])])
	matcher.add('bitterly', [createMatchRule(['disappointed', 'resentful', 'sad', 'regretful', 'complain', 'cry', 'weep', 'cold', 'opposed'])])
	matcher.add('deeply', [createMatchRule(['concerned', 'ashamed', 'moved', 'attached', 'divided', 'hurt', 'regretful', 'affected', 'touched'])])
	matcher.add('strongly', [createMatchRule(['oppose', 'influence', 'believe', 'deny', 'recommend', 'argue', 'object', 'support', 'suggest', 'correlate'])])

	matcher.add('perfectly', [createMatchRule(['normal', 'balanced', 'safe', 'serious', 'acceptable', 'ordinary', 'disgusting'])])
	matcher.add('fully/extensively', [createMatchRule(['prepared', 'understand', 'comprehend', 'informed', 'automated', 'equipped'])])
	matcher.add('totally/completely/entirely/quite', [
		createMatchRule(['unprepared', 'unexpected', 'wrong', 'composed', 'inadequate', 'different', 'dependent', 'harmless', 'unbelievable', 'unacceptable', 'irrational', 'unaware', 'oblivious', 'ignorant', 'intolerant', 'inaccurate', 'unthinkable', 'improbable', 'unconvincing']),
		[{'OP': '!', 'POS': 'ADV'}, {'LOWER': 'out'}, {'LOWER': 'of'}, {'LOWER': 'control'}],
	])
	matcher.add('constantly/persistently/continuously', [createMatchRule(['study', 'develop', 'improve'])])
	matcher.add('extremely/significantly/exceptionally/intensively', [createMatchRule(['useful', 'confident', 'important', 'dangerous', 'suspicious'])])

	matcher.add('hopelessly', [createMatchRule(['addicted', 'romantic', 'optimistic'])])
	matcher.add('vaguely', [createMatchRule(['familiar', 'aware', 'remember', 'worded', 'threatening'])])
	matcher.add('financially', [createMatchRule(['active', 'independent', 'secure'])])
	matcher.add('astronomically', [createMatchRule(['high', 'low', 'large', 'expressive', 'immense', 'difficult'])])
	matcher.add('loosely', [
		createMatchRule(['construed', 'structured', 'connected', 'related']),
		[{'OP': '!', 'POS': 'ADV'}, {'LOWER': 'based'}, {'LOWER': 'on'}],
	])
	matcher.add('excessively', [createMatchRule(['detailed'])])

	matcher.add('vastly', [createMatchRule(['different'])])
	matcher.add('simply', [createMatchRule(['ridiculous', 'disastrous'])])
	matcher.add('undoubtedly', [createMatchRule(['threatening'])])
	matcher.add('truly', [createMatchRule(['handy'])])
	matcher.add('entirely', [createMatchRule(['unfathomable'])])
	matcher.add('overly', [createMatchRule(['competitive'])])

	matcher.add('unreservedly', [createMatchRule(['agree'])])
	matcher.add('certainly', [createMatchRule(['harmful'])])
	matcher.add('positively', [createMatchRule(['brilliant'])])
	matcher.add('conclusively', [createMatchRule(['inaccurate'])])
	matcher.add('decidedly', [createMatchRule(['dangerous'])])

	text = str(doc[0:])
	# copy keys to a new list because we change the dict during iteration.
	for ruleId in list(matcher._patterns.keys()):
		ruleName = matcher.vocab.strings[ruleId]
		heads = ruleName.split('/')
		if any(h in text for h in heads):
			print(f'{ruleName} is already used.')
			matcher.remove(ruleName)

	matches = matcher(doc)


	revisionPoints = {}
	for m in matches:
		s = m[1] - 3
		if s < 0:
			s = 0
		e = m[2] + 2
		text = str(doc[s:e]).strip()
		adv = nlp.vocab.strings[m[0]]
		if text in revisionPoints:
			revisionPoints[text] += "/" + adv
		else:
			revisionPoints[text] = adv

	if len(revisionPoints) > 10:
		print("Try to add an adverb to the following sentences:", file=sys.stderr)
	else:
		return
	for text in revisionPoints:
		print(f"{revisionPoints[text]}:\t{text}", file=sys.stderr)
	print(f'Totally {len(revisionPoints)} possible revisions.')



if __name__ == '__main__':
	targetFiles = []
	# The first argument is the file name of this script.
	for i in range(len(sys.argv) - 1):
		f = os.path.abspath(sys.argv[-1 - i])
		if not os.path.isfile(f):
			break
		targetFiles.append(f)

	if len(targetFiles) == 0:
		raise Exception(f'No target files are provided from command line. {sys.argv}')

	for t in targetFiles:
		text = loadTextFromLatexFormat(t)
		doc = nlp(text)

		checkAdvAdjCollocation(doc)
