from master import Master

from collections import defaultdict
import itertools
import pandas as pd
from pretty import pretty
import re

# from subprocess import call

# call('export DJANGO_SETTINGS_MODULE=glamour_profession.settings')

master = Master('owl3_relevant_fields.txt',
                'cehioorsstw.p',
                'switcheroos.p')


def get_words_by_length_and_probabilty(word_length, min_prob, max_prob):
    words = []
    for word, info in master.word_data.words_dict.iteritems():
        probability = info['probability2']
        if ((len(word) == word_length) and
                (probability > min_prob) and
                (probability < max_prob)):
            words.append(word)
    return words


def find_juicy_words(word_list):
    word_scores = {}
    for word in word_list:
        info = master.word_data.words_dict[word]
        score = (int(len(info['back_extensions']) > 0) +
                 int(len(info['back_hooks']) > 0) +
                 # int(len(info['c_has_order_alphagram']) > 0) +
                 # int(len(info['c_has_order_word']) > 0) +
                 int(len(info['cehioorsstw']) > 0) +
                 int(len(info['cv_has_order_alphagram']) > 0) +
                 int(len(info['cv_has_order_word']) > 0) +
                 2 * int(len(info['deletes']) > 0) +
                 3 * int(len(info['inserts']) > 0) +
                 5 * int(len(info['replaces']) > 0) +
                 int(len(info['reverse_root_words']) > 0) +
                 int(len(info['reverse_synonyms']) > 0) +
                 int(len(info['reverse_synonyms_of_synonym']) > 0) +
                 int(info['is_naive_compound']) +
                 # int(len(info['v_has_order_alphagram']) > 0) +
                 # int(len(info['v_has_order_word']) > 0) +
                 int(len(info['switcheroos']) > 0) +
                 int(len(info['words_with_same_stem']) > 0))
        word_scores[word] = score
    word_scores = pd.DataFrame().from_dict(word_scores, 'index')
    word_scores.columns = ['score']
    return word_scores.sort_values(by='score')


def consistent_lookup():
    all_words = master.word_data.words_dict.keys()
    vowel_symbol = re.compile(r"/v")
    consonant_symbol = re.compile(r"/c")
    power_symbol = re.compile(r"/p")
    one_pointer_symbol = re.compile(r"/1")
    two_pointer_symbol = re.compile(r"/2")
    three_pointer_symbol = re.compile(r"/3")
    four_pointer_symbol = re.compile(r"/4")
    while True:
        var = raw_input("~~~>> ")
        if var in ('q', 'Q', 'exit', 'quit', 'Quit', 'Exit'):
            return
        else:
            try:
                print pretty(master.word_data.words_dict[var.upper()])
                print '\n\n\n'
            except KeyError:
                var = vowel_symbol.sub("[aeiou]", var)
                var = consonant_symbol.sub("[bcdfghjklmnpqrstvwxz]", var)
                var = power_symbol.sub("[jxqz]", var)
                var = one_pointer_symbol.sub("[aeilnorstu]", var)
                var = two_pointer_symbol.sub("[dg]", var)
                var = three_pointer_symbol.sub("[bcmp]", var)
                var = four_pointer_symbol.sub("[fhvwy]", var)
                try:
                    compiled = re.compile("^" + var + "$", flags=re.IGNORECASE)
                    for word in all_words:
                        match = compiled.findall(word)
                        if match:
                            print match
                except:
                    print 'Nothing to show.\n'


def remove_nested_brackets():
    pass

letter_pattern = defaultdict(list)
adj_letter_pattern = defaultdict(list)
letter_location_pattern = defaultdict(list)
def break_apart_words(words):
    for word in words:
        for i in range(1, len(word)+1):
            if i < 3:
                for letters, indices in zip(itertools.combinations(word, i),
                                            itertools.combinations(
                                                range(0, len(word)), i)):
                    letter_pattern[letters].append(word)
                    letter_location_pattern[(letters, indices)].append(word)
                    if list(indices) == range(indices[0], len(indices) + len(indices)):
                        adj_letter_pattern[letters].append(word)

all_words = master.word_data.words_dict.keys()
words_subset = all_words[0:10000]
break_apart_words(words_subset)


# adjacency not required
patter_count_dict = defaultdict(list)
for p, words in letter_pattern.iteritems():
    patter_count_dict[len(words)].append(p)


# adjacency required
adj_patter_count_dict = defaultdict(list)
for p, words in adj_letter_pattern.iteritems():
    adj_patter_count_dict[len(words)].append(p)











