import os
import sys

import pytest

import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_trf")

testFolder = os.path.dirname(os.path.abspath(__file__))

# import local packages
sys.path.append(os.path.join(testFolder, '..'))
import P3


@pytest.mark.parametrize("s", ["This is difficult."])
def test_positive(s):
	matcher = Matcher(nlp.vocab)
	matcher.add("run", P3.createMatchRule(["difficult"]))

	doc = nlp(s)
	matches = matcher(doc)

	# for m in matches:
	# 	s = m[1] - 3
	# 	if s < 0:
	# 		s = 0
	# 	e = m[2] + 2
	# 	text = str(doc[s:e]).strip()
	# 	print(text)

	assert len(matches) == 1


@pytest.mark.parametrize("s", ["This is a little difficult."])
def test_negative(s):
	matcher = Matcher(nlp.vocab)
	matcher.add("run", P3.createMatchRule(["difficult"]))

	doc = nlp(s)
	matches = matcher(doc)

	# for m in matches:
	# 	s = m[1] - 3
	# 	if s < 0:
	# 		s = 0
	# 	e = m[2] + 2
	# 	text = str(doc[s:e]).strip()
	# 	print(text)

	assert len(matches) == 0
