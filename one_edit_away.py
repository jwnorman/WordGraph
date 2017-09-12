import csv
import pandas as pd

from collections import defaultdict

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def load_words(filepath):
    words_dict = {}
    anagrams = defaultdict(list)
    with open(filepath, 'rb') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        for row in tsvin:
            anagrams[row[1]].append(row[0])
            words_dict[row[0]] = {
                'alphagram': row[1],
                'definition': row[2],
                'probability2': int(row[3]),
                'playability': row[4],
                'front_hooks': row[5],
                'back_hooks': row[6]
            }
    return words_dict, anagrams

words_dict, anagrams = load_words('owl3_relevant_fields.txt')


def edits(word):
    # resource: https://github.com/mattalcock/blog/blob/master/2012/12/5/\
    # python-spell-checker.rst
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts = [a + c + b for a, b in s for c in alphabet]
    return {
        'deletes': [delete for delete in deletes if delete != word],
        'transposes': [tp for tp in transposes if tp != word],
        'replaces': [replace for replace in replaces if replace != word],
        'inserts': [insert for insert in inserts if insert != word]
    }


def get_edits_that_are_valid(word_edits):
    new_dict = {}
    for k, v in word_edits.iteritems():
        new_dict[k] = list(
            set([word for word in v if word in words_dict]))
    return new_dict


def get_close_words():
    for word in words_dict:
        one_edit_away = get_edits_that_are_valid(edits(word))
        words_dict[word]['deletes'] = one_edit_away['deletes']
        words_dict[word]['transposes'] = one_edit_away['transposes']
        words_dict[word]['replaces'] = one_edit_away['replaces']
        words_dict[word]['inserts'] = one_edit_away['inserts']

get_close_words()

words = []
deletions = []
insertions = []
replations = []
transpositions = []
for word, info in words_dict.iteritems():
    words.append((word, info["back_hooks"], info["definition"], info["front_hooks"], info["probability2"], "Word"))
    for delete in info["deletes"]:
        deletions.append((word, delete, "delete"))
    for insert in info["inserts"]:
        insertions.append((word, insert, "insert"))
    for replace in info["replaces"]:
        replations.append((word, replace, "replace"))
    for transpose in info["transposes"]:
        transpositions.append((word, transpose, "transpose"))

words = pd.DataFrame(words)
deletions = pd.DataFrame(deletions)
insertions = pd.DataFrame(insertions)
replations = pd.DataFrame(replations)
transpositions = pd.DataFrame(transpositions)

words.columns = ["word:ID", "back_hooks", "definition", "front_hooks",
                 "probability2:int", ":LABEL"]
deletions.columns = [":START_ID", ":END_ID", ":TYPE"]
insertions.columns = [":START_ID", ":END_ID", ":TYPE"]
replations.columns = [":START_ID", ":END_ID", ":TYPE"]
transpositions.columns = [":START_ID", ":END_ID", ":TYPE"]

words.to_csv("words_nodes.csv", index=0)
deletions.to_csv("deletions_edges.csv", index=0)
insertions.to_csv("insertions_edges.csv", index=0)
replations.to_csv("replations_edges.csv", index=0)
transpositions.to_csv("transpositions_edges.csv", index=0)







