"""Finds words that are similar in some way to other words."""

from collections import defaultdict
import csv
import nltk
import pickle
import random
import re
import warnings


class RelevantWordFinder:
    """Finds words that are relevant in some way."""

    def __init__(self, filepath):
        self.words_dict = {}
        self.stems = defaultdict(list)
        self.anagrams = defaultdict(list)
        self.definitions = {}
        self.switcheroos = {}
        self.cehioorsstw = {}
        self.load_words(filepath)
        self.num_anagrams = len(self.anagrams)
        self.num_words = len(self.words_dict)

    def load_words(self, filepath):
        with open(filepath, 'rb') as tsvin:
            tsvin = csv.reader(tsvin, delimiter='\t')
            for row in tsvin:
                self.anagrams[row[1]].append(row[0])
                self.words_dict[row[0]] = {
                    'alphagram': row[1],
                    'definition': row[2],
                    'probability2': int(row[3]),
                    'playability': row[4],
                    'front_hooks': row[5],
                    'back_hooks': row[6],
                    'definition_pks': [],
                    'definition_info': [],
                    'c_has_order_word': [],
                    'v_has_order_word': [],
                    'cv_has_order_word': [],
                    'c_has_order_alphagram': [],
                    'v_has_order_alphagram': [],
                    'cv_has_order_alphagram': [],
                    'back_extensions': [],
                    'front_extensions': [],
                    'is_naive_compound': False,
                    'switcheroos': [],
                    'cehioorsstw': [],
                    'reverse_synonyms': [],
                    'reverse_root_words': [],
                    'reverse_synonyms_of_synonym': []
                }

    def extract_info_from_definition(self):
        de = DefinitionExtractor()
        definition_pk = 0
        for word, word_info in self.words_dict.iteritems():
            definition_info = de.get_all_info(word, word_info['definition'])
            for definition in definition_info:
                self.definitions[definition_pk] = definition
                self.words_dict[word]['definition_info'].append(definition)
                self.words_dict[word]['definition_pks'].append(definition_pk)
                definition_pk += 1

        for word, word_info in self.words_dict.iteritems():
            definition_info = self.words_dict[word]['definition_info']
            self.get_reverse_synonyms(word, definition_info)
            self.get_reverse_root_words(word, definition_info)

        self.get_reverse_synonyms_of_synonym()

    def get_reverse_synonyms(self, word, definition_info):
        synonyms = [def_info['synonym']
                    for def_info in definition_info
                    if def_info['synonym']]
        for synonym in synonyms:
            if synonym in self.words_dict:
                self.words_dict[synonym]['reverse_synonyms'].append(word)
            else:
                warnings.warn("The synonym {} in definition of {} is not"
                              " valid.".format(synonym, word))

    def get_reverse_root_words(self, word, definition_info):
        root_words = [def_info['root_word']
                      for def_info in definition_info
                      if def_info['root_word']]
        for root_word in root_words:
            if root_word in self.words_dict:
                self.words_dict[root_word]
                ['reverse_root_words'].append(word)
            else:
                warnings.warn("The root_word {} in definition of {} is not"
                              " valid.".format(root_word, word))

    def get_reverse_synonyms_of_synonym(self):
        for word, word_info in self.words_dict.iteritems():
            for definition in word_info['definition_info']:
                if (definition['synonym']) and\
                   (word in self.words_dict) and\
                   (definition['synonym'] in self.words_dict):
                    self.words_dict[word]['reverse_synonyms_of_synonym'] =\
                        self.words_dict[definition['synonym']][
                            'reverse_synonyms']

    def get_extensions(self):
        for en, w in enumerate(self.words_dict):
            wl = len(w)
            windows = range(2, max(int(round(wl / 2.0)), wl - 2) + 1)
            for window in windows:
                w1 = w[0:window]
                w2 = w[window:wl]
                if w1 in self.words_dict:
                    self.words_dict[w1]['back_extensions'].append(w2)
                if w2 in self.words_dict:
                    self.words_dict[w2]['front_extensions'].append(w1)
                if (w1 in self.words_dict) and (w2 in self.words_dict):
                    self.words_dict[w1 + w2]['is_naive_compound'] = True

    def get_switcheroos(self, filepath):
        switcheroos = Switcheroos()
        for word_len in range(2, 16):
            for pos_1 in range(0, word_len - 1):
                for len_1 in range(0, word_len - pos_1):
                    zero_flag = 1 if len_1 == 0 else 0
                    for pos_2 in range(pos_1 + len_1 + zero_flag, word_len):
                        for len_2 in range(1, word_len - pos_2 + 1):
                            switcheroos.find_anagrams_with_switched_positions(
                                self.anagrams, pos_1, len_1, pos_2, len_2,
                                [word_len])
        for word, swaps in switcheroos.switcheroos:
            self.words_dict[word]['switcheroos'] = swaps
        for word, swaps in switcheroos.cehioorsstw:
            self.words_dict[word]['cehioorsstw'] = swaps

    def get_close_words(self):
        oea = OneEditAway(self.words_dict)
        for word in self.words_dict:
            one_edit_away = oea.get_edits_that_are_valid(oea.edits(word))
            self.words_dict[word]['deletes'] = one_edit_away['deletes']
            self.words_dict[word]['transposes'] = one_edit_away['transposes']
            self.words_dict[word]['replaces'] = one_edit_away['replaces']
            self.words_dict[word]['inserts'] = one_edit_away['inserts']

    def get_words_with_similar_cv_order(self):
        co = ConsonantOrder()
        temp_cv = co.cv_has_order(self.anagrams)
        temp_c = co.c_has_order(self.anagrams)
        temp_v = co.v_has_order(self.anagrams)
        for k, v in temp_cv.iteritems():
            for word in v:
                if word in self.words_dict:
                    self.words_dict[k]['cv_has_order_word'].append(word)
                if word in self.anagrams:
                    self.words_dict[k]['cv_has_order_alphagram'].append(word)
        for k, v in temp_c.iteritems():
            for word in v:
                if word in self.words_dict:
                    self.words_dict[k]['c_has_order_word'].append(word)
                if word in self.anagrams:
                    self.words_dict[k]['c_has_order_alphagram'].append(word)
        for k, v in temp_v.iteritems():
            for word in v:
                if word in self.words_dict:
                    self.words_dict[k]['v_has_order_word'].append(word)
                if word in self.anagrams:
                    self.words_dict[k]['v_has_order_alphagram'].append(word)

    def get_stems(self):
        st = nltk.PorterStemmer()
        for word in self.words_dict:
            stem = st.stem(word.lower()).upper()
            self.words_dict[word]['stem'] = stem
            self.stems[stem].append(word)

    def get_random_entry(self):
        random_word = random.sample(self.words_dict, 1)[0]
        return {random_word: [self.words_dict[random_word]]}

    def __repr__(self):
        return "<{} words and {} anagrams>".format(self.num_words,
                                                   self.num_anagrams)


class DefinitionExtractor:

    def get_all_info(self, word, definition):
        definition_extraction = []
        definitions = definition.split("/")
        for defin in definitions:
            definition_extraction.append({
                'word': word,
                'definition': defin,
                'synonym': self.get_synonym(defin),
                'root_word': self.get_root_word(defin),
                'part_of_speech': self.get_part_of_speech(defin),
                'conjugation': self.get_conjugations(defin),
                'similar_word_other_part_of_speech':
                    self.get_similar_word_other_part_of_speech(defin)
            })

        return definition_extraction

    def get_synonym(self, definition):
        if "(" in definition:
            return self._strip_nonalpha(re.sub(
                "(.+?)\(.+", "\\1", definition).strip().split()[-1].upper())
        else:
            return None

    def get_root_word(self, definition):
        if definition:
            match = re.match("[A-Z]+[^a-z]+", definition.split()[0])
            return self._strip_nonalpha(match.group()) if match else match

    def get_part_of_speech(self, definition):
        if definition and ("[" in definition):
            return re.sub(".*\[(\w*)\s*.*", "\\1", definition)
        else:
            return None

    def get_conjugations(self, definition):
        if definition and ("[" in definition):
            conjugation = re.sub("[^[]*\[[a-z]+ ([A-Za-z,\- (or)]+).*",
                                 "\\1", definition, flags=re.IGNORECASE)
            if conjugation != definition:
                return re.sub("\s*or", ",", conjugation).strip().split(', ')
            else:
                return None
        else:
            return None

    def get_similar_word_other_part_of_speech(self, definition):
        if ':' in definition:
            return re.sub("[^:]+:([^~]+)~.*", "\\1",
                          definition).strip().split(', ')
        else:
            return None

    def _strip_nonalpha(self, word):
        return re.findall('[a-z]+', word, flags=re.IGNORECASE)[0]


class Switcheroos:

    def __init__(self):
        self.switcheroos = defaultdict(list)
        self.cehioorsstw = defaultdict(list)

    def find_anagrams_with_switched_positions(self, anagram_dict, pos_1, len_1,
                                              pos_2, len_2, word_lengths):
        for word_len in word_lengths:
            for alphagram, anagram_list in anagram_dict.iteritems():
                if len(alphagram) == word_len:
                    for word in anagram_list:
                        potential_word = self._make_intraword_swap(
                            word, pos_1, len_1, pos_2, len_2)
                        if (word != potential_word) and\
                           (potential_word in anagram_list):
                            self.switcheroos[word].append({
                                "anagram": potential_word,
                                "pos_1": pos_1,
                                "len_1": len_1,
                                "pos_2": pos_2,
                                "len_2": len_2
                            })
                        potential_alphagram = self._make_intraword_swap(
                            word, pos_1, len_1, pos_2, len_2)
                        if (potential_alphagram == alphagram):
                            self.cehioorsstw[word].append({
                                "alphagram": potential_alphagram,
                                "pos_1": pos_1,
                                "len_1": len_1,
                                "pos_2": pos_2,
                                "len_2": len_2
                            })

    def _make_intraword_swap(self, word, pos_1, len_1, pos_2, len_2):
        word_list = list(word)
        temp = ''.join(word_list[pos_1:pos_1 + len_1])
        temp_ignore = ''.join(word_list[pos_2:pos_2 + len_2])
        adjustment = len(temp) - len(temp_ignore)
        word_list[pos_1:pos_1 + len_1] = word_list[pos_2:pos_2 + len_2]
        word_list[pos_2 - adjustment:pos_2 + len_2 - adjustment] = temp
        return ''.join(word_list)

    def load(self, filepath):
        return pickle.load(open(filepath, "rb"))


class OneEditAway:

    def __init__(self, words_dict):
        self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.words_dict = words_dict

    def edits(self, word):
        # resource: https://github.com/mattalcock/blog/blob/master/2012/12/5/\
        # python-spell-checker.rst
        s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in s if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1]
        replaces = [a + c + b[1:] for a, b in s for c in self.alphabet if b]
        inserts = [a + c + b for a, b in s for c in self.alphabet]
        return {
            'deletes': [delete for delete in deletes if delete != word],
            'transposes': [tp for tp in transposes if tp != word],
            'replaces': [replace for replace in replaces if replace != word],
            'inserts': [insert for insert in inserts if insert != word]
        }

    def get_edits_that_are_valid(self, word_edits):
        new_dict = {}
        for k, v in word_edits.iteritems():
            new_dict[k] = list(set([word
                                    for word in v
                                    if word in self.words_dict]))
        return new_dict


class ConsonantOrder:

    def is_consonant(self, letter):
        """letter is a string, output is Boolean."""
        return letter in ('B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M',
                          'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y',
                          'Z')

    def get_consonants(self, word):
        """word is a string, output is a list."""
        return [letter for letter in word if self.is_consonant(letter)]

    def get_vowels(self, word):
        """word is a string, output is a list."""
        return [letter for letter in word if not self.is_consonant(letter)]

    def num_unique(self, letter_list):
        """letter_list is a list of letters, output is an integer."""
        return len(set(letter_list))

    def has_same_consonant_order(self, word1, word2):
        """word1/2 are strings, output is an Boolean."""
        cons1 = self.get_consonants(word1)
        cons2 = self.get_consonants(word2)
        return (cons1 == cons2) | (cons1 == cons2[::-1])

    def has_same_vowel_order(self, word1, word2):
        """word1/2 are strings, output is an Boolean."""
        vowels1 = self.get_vowels(word1)
        vowels2 = self.get_vowels(word2)
        return (vowels1 == vowels2) | (vowels1 == vowels2[::-1])

    def c_has_order(self, anagrams):
        """consonants keep same or reversed order."""
        temp = defaultdict(list)
        for alphagram, anagram_list in anagrams.iteritems():
            if self.num_unique(self.get_consonants(alphagram)) >= 3:
                for anagram1 in anagram_list:
                    for anagram2 in anagram_list:
                        if (anagram1 != anagram2) and \
                                self.has_same_consonant_order(
                                    anagram1, anagram2):
                            temp[anagram1].append(anagram2)
                    if self.has_same_consonant_order(anagram1, alphagram):
                        temp[anagram1].append(alphagram)
        return temp

    def v_has_order(self, anagrams):
        """vowels keep same or reversed order."""
        temp = defaultdict(list)
        for alphagram, anagram_list in anagrams.iteritems():
            if self.num_unique(self.get_vowels(alphagram)) >= 3:
                for anagram1 in anagram_list:
                    for anagram2 in anagram_list:
                        if (anagram1 != anagram2) and \
                                self.has_same_vowel_order(anagram1, anagram2):
                            temp[anagram1].append(anagram2)
                    if self.has_same_vowel_order(anagram1, alphagram):
                        temp[anagram1].append(alphagram)
        return temp

    def cv_has_order(self, anagrams):
        """vowels and consonants keep same or reversed order."""
        temp = defaultdict(list)
        for alphagram, anagram_list in anagrams.iteritems():
            if (self.num_unique(self.get_consonants(alphagram)) >= 3) and \
                    (self.num_unique(self.get_vowels(alphagram)) >= 3):
                for anagram1 in anagram_list:
                    for anagram2 in anagram_list:
                        if (anagram1 != anagram2) and \
                                self.has_same_vowel_order(
                                    anagram1, anagram2) and \
                                self.has_same_consonant_order(
                                    anagram1, anagram2):
                            temp[anagram1].append(anagram2)
                    if self.has_same_vowel_order(anagram1, alphagram) and \
                            self.has_same_consonant_order(anagram1, alphagram):
                        temp[anagram1].append(alphagram)
        return temp
