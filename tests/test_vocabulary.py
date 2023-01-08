import os
import sys

import pytest
from spacy.matcher import Matcher

testFolder = os.path.dirname(os.path.abspath(__file__))

# import local packages
sys.path.append(os.path.join(testFolder, '..'))
import WordCount


@pytest.mark.parametrize("text", ["I have got to go there.", "I've got to go there.", "He had not got to set off again."])
def test_haveGot(text):
	doc = WordCount.nlp(text)
	matcher = Matcher(WordCount.nlp.vocab)
	matcher.add("have got", WordCount.haveGotPatterns)
	matches = matcher(doc)
	assert len(matches) > 0
