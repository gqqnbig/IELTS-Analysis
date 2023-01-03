import pytest

import WordCount


# @pytest.mark.parametrize("input", ["({\cjkfont 平静一些})", r"\footnote{\cjkfont 注意元音长度规则，gave比give长}"])
# def test_removeCommandsToEmpty(input):
# 	res = WordCount.removeCommands(input)
# 	assert res.strip() == ""


def test_revealTextInCommands():
	res = WordCount.revealTextInCommands(r'he \usemore{scored} \ps{two} based \textipa{/beI\pr{st}/} on his \usemore{\ps{official} title}')

	assert res == r'he scored two based \textipa{/beIst/} on his official title'
