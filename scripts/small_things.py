

import logging
import utils
''' small, may be temporary things
'''

DIR_HTML = 'html/'
#
# with open('frek1.txt', 'rU') as in_file:
#     with open('frek1_clean.txt', 'w') as out_file:
#         for line in in_file:
#             print (line.split()[-1])
#             out_file.write(line.split()[-1] + '\n')
#     out_file.close()
# in_file.close()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()


def get_page(a_word):
    return 'http://dictionary.cambridge.org/dictionary/english/%s' % a_word.strip()

def get_file_name(a_word):
    return DIR_HTML + a_word.strip() + '.html'

def define_words(a_list):
    '''
    :param a_list: a list of words
    :return: alist of semicolon separated information about each word
        - word, type of word, example usage
    '''
    a_result = []
    with open('words_wiki_500.txt', 'w') as out_file:
        for word in a_list:
            '''stahni stranku z cambridge
               najdi jednotlive casti pomoci regexpu
               sloz vysledek
               pridej do resultu
            '''
            clean_word = word.strip()
            logger.debug('word: %s' %clean_word)

            utils.download(get_page(clean_word), get_file_name(clean_word), logger)

            word_type = utils.get_info(get_file_name(clean_word), 'span class="headword">.*?%s.*?span class="pos".*?>(.*?)<' %clean_word, logger)
            out_line = '%s\t%s\n' % (clean_word, word_type)
            logger.debug(out_line)
            out_file.write(out_line)
    out_file.close()

logger.debug('small things begin')
#define_words(['the', 'hello'])
with open('wiki_500.txt', 'r') as test_file:
    define_words(test_file)