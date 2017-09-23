import pandas as pd

from master import Master


master = Master('owl3_relevant_fields.txt',
                'cehioorsstw.p',
                'switcheroos.p')

anagrams = master.word_data.anagrams
words_dict = master.word_data.words_dict

# Put words_dict into neo4j structure for words and one edit distance
# relationships
# (:Word)
# (:Word)-[:deletes]->(:Word)
# (:Word)-[:inserts]->(:Word)
# (:Word)-[:replaces]->(:Word)
# (:Word)-[:transposes]->(:Word)
words = []
deletions = []
insertions = []
replations = []
transpositions = []
for word, info in words_dict.iteritems():
    label = "Word"
    # don't just use word as pk because there are alphagrams that would have
    # the same pk. Adding the label to the pk will make it sufficiently unique.
    pk = label + word
    words.append((pk, word, label, info["back_hooks"], info["definition"],
                  info["front_hooks"], info["probability2"],
                  info["is_naive_compound"], info["alphagram"], info["stem"]))
    for delete in info["deletes"]:
        deletions.append((pk, label + delete, "delete"))
    for insert in info["inserts"]:
        insertions.append((pk, label + insert, "insert"))
    for replace in info["replaces"]:
        replations.append((pk, label + replace, "replace"))
    for transpose in info["transposes"]:
        transpositions.append((pk, label + transpose, "transpose"))

words = pd.DataFrame(words)
deletions = pd.DataFrame(deletions)
insertions = pd.DataFrame(insertions)
replations = pd.DataFrame(replations)
transpositions = pd.DataFrame(transpositions)

# originally had `is_naive_compound` specified as boolean
# (`is_naive_compound:boolean`) but neo4j was coverting everything to false
# even though the csv had appropriate Trues. I will just keep it as a string.
words.columns = ["pk:ID", "word", ":LABEL", "back_hooks", "definition",
                 "front_hooks", "probability2:int",
                 "is_naive_compound", "alphagram", "stem"]
deletions.columns = [":START_ID", ":END_ID", ":TYPE"]
insertions.columns = [":START_ID", ":END_ID", ":TYPE"]
replations.columns = [":START_ID", ":END_ID", ":TYPE"]
transpositions.columns = [":START_ID", ":END_ID", ":TYPE"]

words.to_csv("words_nodes.csv", index=0)
deletions.to_csv("deletions_edges.csv", index=0)
insertions.to_csv("insertions_edges.csv", index=0)
replations.to_csv("replations_edges.csv", index=0)
transpositions.to_csv("transpositions_edges.csv", index=0)


# Put anagrams into neo4j structure for word and anagrams
# (:Alphagram)
# (:Word)-[:anagrams_to]->(:Word)
# (:Word)-[:has_alphagram]->(:Alphagram)
alphagrams = []
word_to_alphagram = []
word_to_anagram = []
for alphagram, words in anagrams.iteritems():
    label = "Alphagram"
    pk = label + alphagram
    alphagrams.append((pk, alphagram, label))
    for word in words:
        word_to_alphagram.append(("Word" + word, pk, "has_alphagram"))
        for word_2 in words:
            if word != word_2:
                word_to_anagram.append(
                    ("Word" + word, "Word" + word_2, "anagrams_to"))

alphagrams = pd.DataFrame(alphagrams)
word_to_alphagram = pd.DataFrame(word_to_alphagram)
word_to_anagram = pd.DataFrame(word_to_anagram)

alphagrams.columns = ["pk:ID", "alphagram", ":LABEL"]
word_to_alphagram.columns = [":START_ID", ":END_ID", ":TYPE"]
word_to_anagram.columns = [":START_ID", ":END_ID", ":TYPE"]

alphagrams.to_csv("alphagrams_nodes.csv", index=0)
word_to_alphagram.to_csv("word_to_alphagram_edges.csv", index=0)
word_to_anagram.to_csv("word_to_anagram_edges.csv", index=0)
