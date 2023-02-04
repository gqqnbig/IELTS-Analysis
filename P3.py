import os
import sys

import spacy

from WordCount import loadTextFromLatexFormat


# try:
# 	nlp = spacy.load("en_core_web_sm")
# except:
# 	nlp = spacy.load("en_core_web_trf")


def checkAdvAdjCollocation(text):
	collocations = {
		'highly': ['successful', 'vital', 'probable', 'improbable', 'competitive', 'recommended', 'effective', 'contagious', 'critical', 'intelligent', 'likely', 'unlikely', 'sensitive', 'controversial', 'suspicious'],
		'utterly/absolutely': ['disastrous', 'disgusting', 'disgusted', 'impossible', 'useless', 'miserable', 'wrong', 'pointless', 'worthless', 'fabulous', 'unrealistic'],
		'unbelievably/ridiculously/incredibly': ['cheap', 'expensive', 'big', 'small', 'long', 'short', 'easy', 'early', 'late', 'cold', 'old'],
		'potentially': ['dangerous', 'hazardous', 'fatal', 'toxic', 'fruitful', 'game-changing', 'life threatening'],
		'blatantly': ['false', 'unfair', 'untrue', 'dishonest', 'wrong', 'mistaken'],
		'widely': ['believed', 'practiced', 'spoken', 'used', 'distributed', 'known', 'publicized', 'available'],

		'absurdly': ['low', 'high', 'easy', 'difficult'],
		'thoroughly': ['prepared', 'enjoyable', 'convinced', 'agree', 'satisfying', 'clean'],
		'patently': ['true', 'false', 'clear', 'clever'],
		'wildly': ['inappropriate', 'inaccurate', 'exaggerated', 'unrealistic', 'popular', 'successful', 'unsuccessful'],
		'mildly': ['entertained', 'surprised', 'amused', 'irritated', 'offensive'],
		'downright': ['wrong', 'dishonest', 'hostile', 'rude', 'disgraceful', 'immoral', 'ugly', 'mean'],
		'heavily': ['armed', 'pregnant', 'subsidized', 'criticized'],
		'seriously': ['stubborn', 'genius', 'strong', 'smart', 'delicious', 'good', 'injured', 'damaged', 'hurt', 'wounded'],
		'strictly': ['speaking', 'regulated', 'limited', 'comparative'],
		'bitterly': ['disappointed', 'resentful', 'sad', 'regretful', 'complain', 'cry', 'weep', 'cold', 'opposed'],
		'deeply': ['concerned', 'ashamed', 'moved', 'attached', 'divided', 'hurt', 'regretful', 'affected', 'touched'],
		'strongly': ['oppose', 'influence', 'believe', 'deny', 'recommend', 'argue', 'object', 'support', 'suggest', 'correlate'],

		'perfectly': ['normal', 'balanced', 'safe', 'serious', 'acceptable', 'ordinary', 'disgusting'],
		'fully/extensively': ['prepared', 'understand', 'comprehend', 'informed', 'automated', 'equipped'],
		'totally/completely/entirely/quite': ['unprepared', 'unexpected', 'out of control', 'wrong', 'composed', 'inadequate', 'different', 'dependent', 'harmless', 'unbelievable', 'unacceptable', 'irrational', 'unaware', 'oblivious', 'ignorant', 'intolerant', 'inaccurate', 'unthinkable', 'improbable', 'unconvincing'],
		'constantly/persistently/continuously': ['study', 'develop', 'improve'],
		'extremely/significantly/exceptionally/intensively': ['useful', 'confident', 'important', 'dangerous', 'suspicious'],

		'hopelessly': ['addicted', 'romantic', 'optimistic'],
		'vaguely': ['familiar', 'aware', 'remember', 'worded', 'threatening'],
		'financially': ['active', 'independent', 'secure'],
		'astronomically': ['high', 'low', 'large', 'expressive', 'immense', 'difficult'],
		'loosely': ['based on', 'construed', 'structured', 'connected', 'related'],
		'excessively': ['detailed'],

		'vastly': ['different'],
		'simply': ['ridiculous', 'disastrous'],
		'undoubtedly': ['threatening'],
		'truly': ['handy'],
		'entirely': ['unfathomable'],
		'overly': ['competitive'],

		'unreservedly': ['agree'],
		'certainly': ['harmful'],
		'positively': ['brilliant'],
		'conclusively': ['inaccurate'],
		'decidedly': ['dangerous']
	}

	sum = 0
	possibleRevisions = {}
	for adv in collocations:
		heads = adv.split('/')
		if any(h in text for h in heads):
			continue

		matches = []
		for adj in collocations[adv]:
			try:
				p = text.index(adj)
				matches.append(p)
			except:
				pass
		if len(matches) != 0:
			sum += len(matches)
			possibleRevisions[adv] = matches

	if sum > 3:
		print('Try to add an adverb to the following sentences:')
		for adv in possibleRevisions:
			for p in possibleRevisions[adv]:
				s = p - 10
				if s < 0:
					s = 0
				# If the ending index goes beyond the length, it's treated as the end.
				print(f'Add {adv} -> {text[s:p + 20].strip()}')


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
		# doc = nlp(text)

		checkAdvAdjCollocation(text)
