from relevant_words import RelevantWordFinder, Switcheroos
import os
# from django.conf import settings

BASE_DIR = '/Users/jacknorman1/Documents/Scrabble/Studies/WordGraph/'
DATA_DIR = 'data/'
words_filename = 'owl3_relevant_fields.txt'
switcheroos_filename = 'switcheroos.p'
cehioorsstw_filename = 'cehioorsstw.p'


class Master:

    def __init__(self,
                 words_filename,
                 cehioorsstw_filename,
                 switcheroos_filename):
        words_filepath = os.path.join(
            BASE_DIR,
            DATA_DIR,
            words_filename)
        cehioorsstw_filepath = os.path.join(
            BASE_DIR,
            DATA_DIR,
            cehioorsstw_filename)
        switcheroos_filepath = os.path.join(
            BASE_DIR,
            DATA_DIR,
            switcheroos_filename)
        self.word_data = RelevantWordFinder(words_filepath)
        self.word_data.extract_info_from_definition()
        self.word_data.get_extensions()
        self.word_data.get_close_words()
        self.word_data.get_words_with_similar_cv_order()
        self.word_data.get_stems()

        for word, info in self.word_data.words_dict.iteritems():
            info['words_with_same_stem'] = [
                other_word for other_word in self.word_data.stems[info['stem']]
                if other_word != word]

        swaps = Switcheroos()
        cehioorsstw = swaps.load(cehioorsstw_filepath)
        switcheroos = swaps.load(switcheroos_filepath)
        switcheroos_id = 0
        cehioorsstw_id = 0
        for word, switcheroo in switcheroos.iteritems():
            self.word_data.words_dict[word]['switcheroos'].append(
                switcheroos_id)
            self.word_data.switcheroos[switcheroos_id] = switcheroo
            switcheroos_id += 1
        for word, cehioorstw in cehioorsstw.iteritems():
            self.word_data.words_dict[word]['cehioorsstw'].append(
                cehioorsstw_id)
            self.word_data.cehioorsstw[cehioorsstw_id] = cehioorstw
            cehioorsstw_id += 1
        for word in self.word_data.words_dict:
            self.word_data.words_dict[word]['switcheroos'] = switcheroos[word]
            self.word_data.words_dict[word]['cehioorsstw'] = cehioorsstw[word]
