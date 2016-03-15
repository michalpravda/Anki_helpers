
import os
import urllib
import re
'''
common utility functions
'''

def download (a_what, a_where, logger):
    ''' Pokud soubor jeste neexistuje, tak stahne soubor z internetu a ulozi ho pod danym jmenem
        If the particular file doesn't exist then it is downloaded from internet and saved '''
    logger.debug('download: z %s, do %s' % (a_what, a_where))
    if (os.path.exists(a_where)):
        logger.debug('downloaded before')
    else:
        testfile = urllib.URLopener()
        logger.debug('before download')
        try:
            testfile.retrieve(a_what, a_where)
            logger.debug('download successfull')
        except:
            logger.warning('file not found %s' % a_what)
            return False
    return True

def get_info(a_filename, a_regexp, logger):
    logger.debug('get_info: a_file %s, a_regexp: %s' % (a_filename, a_regexp))
    try:
        with open(a_filename, 'r') as test_file:
            for line in test_file:
                result = re.search(a_regexp, line)
                if result:
                    group = result.group(1)
                    logger.debug('Found %s' %group)
                    test_file.close()
                    return group

        test_file.close()
    except IOError:
        logger.warning('file not found %s' % a_filename)