// Find shortest path between two words using any relationship
MATCH (hilloa:Word { word: 'PAINTING' }), (hello:Word { word: 'TABLE' }), p = shortestPath((hilloa)-[*]-(hello))
RETURN p

// Find the 8 letter words that have the most connections
MATCH (w1)-[a]-(w2)
WHERE length(w1.word) = 8
RETURN w1, count(distinct w2) as num_connected_words
ORDER BY num_connected_words DESC
LIMIT 10


// Find a pair of words, one two letter word and one 13 letter word and show
// a shortest path between them.
MATCH
    (word1 :Word)
        WHERE length(word1.word)=2
MATCH
    (word2 :Word)
        WHERE length(word2.word)=13
MATCH
    p = shortestPath((word1)-[*]-(word2))
RETURN p
LIMIT 30


// Same as above mostly
MATCH
    (word1 :Word {word: "MA"})
        WHERE length(word1.word)=2
MATCH
    (word2 :Word)
        WHERE length(word2.word)=13
MATCH
    p = shortestPath((word1)-[*]-(word2))
RETURN p
LIMIT 30


// Things you might find interesting in a set of 100 words
MATCH p=(w :Word)-[r:anagrams_to|:insert|:replace|:delete]->(w2)
WHERE length(w.word) = 7
AND w.probability2 >= 11000
AND w.probability2 <= 11100
RETURN w.probability2, w.word, w2.word, type(r)
ORDER BY w.probability2
LIMIT 1000;
