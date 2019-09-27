import re
import enchant
from nltk.corpus import wordnet
from nltk.metrics import edit_distance

replacement_patterns = [(r'won\'t', 'will not'),
                        (r'can\'t', 'cannot'),
                        (r'i\'m', 'i am'),
                        (r'ain\'t', 'is not'),
                        (r'(\w+)\'ll', '\g<1> will'),
                        (r'(\w+)n\'t', '\g<1> not'),
                        (r'(\w+)\'ve', '\g<1> have'),
                        (r'(\w+)\'s', '\g<1> is'),
                        (r'(\w+)\'re', '\g<1> are'),
                        (r'(\w+)\'d', '\g<1> would')]


class RegexpReplacer(object):
    """ Replaces regular expression in a text."""

    def __init__(self, patterns=replacement_patterns):
        self.patterns = [(re.compile(regex), repl) for (regex, repl) in patterns]

    def replace(self, text):
        s = text
        for (pattern, repl) in self.patterns:
            (s, count) = re.subn(pattern, repl, s)
        return s


class RepeatReplacer(object):
    """ Removes repeating characters until a valid word is found."""

    def __init__(self):
        self.repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
        self.repl = r'\1\2\3'

    def replace(self, word):
        if wordnet.synsets(word):
            return word

        repl_word = self.repeat_regexp.sub(self.repl, word)

        if repl_word != word:
            return self.replace(repl_word)
        else:
            return repl_word


class SpellingReplacer(object):
    """ Replaces misspelled words with a likely suggestion based on shortest
    edit distance."""

    def __init__(self, dict_name='en', max_dist=2):
        self.spell_dict = enchant.Dict(dict_name)
        self.max_dist = max_dist

    def replace(self, word):
        if self.spell_dict.check(word):
            return word

        suggestions = self.spell_dict.suggest(word)

        if suggestions and edit_distance(word, suggestions[0]) <= self.max_dist:
            return suggestions[0]
        else:
            return word


class WordReplacer(object):
    """ WordReplacer that replaces a given word with a word from the word_map,
    or if the word isn't found, returns the word as is."""

    def __init__(self, word_map):
        self.word_map = word_map

    def replace(self, word):
        return self.word_map.get(word, word)
