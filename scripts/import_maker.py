# coding=ISO-8859-2
import re
import os
import sys
import logging
import shutil
from argparse import ArgumentParser
import urllib
import zipfile
from datetime import datetime

from os.path import expanduser

DIR_HTML = 'html'
DIR_SOUNDS = 'sounds'
DIR_SENTENCES = 'sentences'
DIR_DONE = 'done'

'''
Takes all picture files from a given directory and for each of them then downloads a sound and IPA transcription
from the wiktionary. Prepares a txt file with description and filenames for Anki to import.
'''

userHomeDir = expanduser("~")    #c:\users\majkl
ankiDir = os.path.join(userHomeDir, 'Documents', 'Anki')  #c:\users\majkl\Documents\anki



'''
Projdi adresar
    pro kazdy obrazek (png nebo jpg)
        stahni stranku z wikti (testfile.retrieve("https://en.wiktionary.org/wiki/" + x.lower(), x +".html"))
        stahni zvuk z googlu (testfile.retrieve("https://ssl.gstatic.com/dictionary/static/sounds/de/0/" + x.lower() + ".mp3", x +".mp3")
            pokud neni, najdi zvuk z wiki (vyparsovat z  You can <a href="//upload.wikimedia.org/wikipedia/commons/a/a7/En-us-injury.ogg">download the clip</a>)
                a stahni
        vyparsuj ze stranky IPA (          <span class="IPA" lang="">/xxx/
          </span>
        pridej do vysledku radek obrazek; jmeno ; zvuk ; IPA;<pro bawn-jure>;<pro vase poznamky>
        uloz do archivu
uloz vysledek
uklid
'''
LOGFILE = 'import.log'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', filename=LOGFILE, datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()


def find_text(a_filename, a_regexp, a_not_found):
    ''' najde v souboru text regexpem, vrati obsah a_not_found, kdyz nenalezne'''
    with open(a_filename, 'r') as fd:
        logger.debug('otevren %s' %a_filename)
        p = re.compile(a_regexp)
        for line in fd:
            m = p.search(line)
            if m:
                try:
                    #logger.debug(str(m))
                    if m.group(1):
                        return m.group(1)
                    else:
                        return a_not_found
                except:
                    logger.warning('Nepodarilo se najit %s v souboru %s - %s' % (a_regexp, a_filename, str(sys.exc_info()[0])))
                    return a_not_found
    fd.close
    return a_not_found


def get_phonetic_pronunciation(a_filename):
    logger.debug('function get_phonetic_pronunciation:' + a_filename)
    return find_text(a_filename, '<span class="IPA" [^>]+>/([^/]*)/</sp', '//')


def get_extension(a_filename):
    ''' ze jmena souboru odvodi priponu'''

    logger.debug('get_extension ' + a_filename)
    if not a_filename:
        return None
    ext = a_filename.split('.')[-1].lower()
    logger.debug('returns:' + ext)
    return ext

def stahni (a_co, a_kam):
    ''' Pokud soubor jeste neexistuje, tak stahne soubor z internetu a ulozi ho pod danym jmenem'''
    logger.debug('stahni: z %s, do %s' % (a_co, a_kam))
    if (os.path.exists(a_kam)):
        logger.debug('jiz stazeno drive')
    else:
        testfile = urllib.URLopener()
        logger.debug('stahnu soubor')
        try:
            testfile.retrieve(a_co, a_kam)
        except:
            logger.warning('nenalezen soubor na adrese %s' % a_co)
            return False
    return True

def najdi_adresu(adr, a_page, a_word, a_regexp):
    ''' finds a link in a page using a regexp. Looks for exact word first and if the page is not found then tries a_word.lower as part of the address '''
    address = a_page.rstrip('/') + '/' + a_word
    local_file = os.path.join(adr, DIR_HTML, a_word + '_sound.html')
    if not os.path.exists(local_file):
        if not stahni(address, local_file):
            logger.debug('nenasel adresu, zkusim lower')
            if a_word == a_word.lower():
                logger.debug('a word = a_word.lower() - neni co znovu hledat')
            else:
                address = a_page.rstrip('/') + '/' + a_word.lower()
                logger.debug('adress %s' %address)
                stahni(address, local_file)
    sound_address = find_text(local_file, 'data-src-mp3="([^"]+)"', None)
    if sound_address:
        logger.debug('Found sound address - %s' % sound_address)
        return sound_address
    else:
        logger.debug('Not found sound address')
        return None




def get_sound(adr, a_word):
    ''' najde pro dane slovo nahravku
        nejdrive jiz existujici nahravku v adresari, jinak zkusi stahnout z googlu a pak z wiktionary
        vrati tag pro pouziti v anki [sound:word.mp3]'''
    logger.debug('get_sound:%s %s' %(adr ,a_word))
    sound_file =  os.path.join (adr, DIR_SOUNDS, a_word + '.mp3')
    logger.debug ('sound_file: %s' % sound_file)
    sound_address = "https://ssl.gstatic.com/dictionary/static/sounds/de/0/" + a_word.lower() + ".mp3"
    if stahni (sound_address, sound_file):
        logger.debug('stahnul jsem z googlu')
        return '[sound:%s.mp3]' % a_word
    else:
        logger.debug('zkusim stahnout zvuk odjinud')
        sound_address = najdi_adresu(adr, 'http://dictionary.cambridge.org/us/dictionary/english/', a_word, 'data-src-mp3="([^"]+)"')
        if stahni (sound_address, sound_file):
            logger.debug('stahnul jsem z odjinud')
            l_result = '[sound:%s.mp3]' % a_word
            logger.debug(l_result)
            return l_result
    return ''

def get_pronunciation(adr, a_word):
    ''' najde pro dane slovo vyslovnost
        zkusi v adresari najit stazenou stranku
        z ni vyparsovat vyslovnost,
        todo pripadne pak stahne patricnou stranku
    '''
    logger.debug('function get_pronunciation (%s)' %a_word)
    pronunciation_file = os.path.join(adr, DIR_HTML, a_word + '.html')
    logger.debug('pronunciation_file: %s' % pronunciation_file)
    if stahni("https://en.wiktionary.org/wiki/" + a_word.lower(), pronunciation_file):
        pronunciation = get_phonetic_pronunciation(pronunciation_file)
    else:
        pronunciation = '//'

    #nenasel jsem na wiki, zkusim cambridge
    if pronunciation == '//':
        if (stahni ('http://dictionary.cambridge.org/us/dictionary/english/%s' %a_word.lower(), pronunciation_file + '2')):
            pronunciation = find_text(pronunciation_file + '2', '<span class="ipa">([^<]+)</span>', '//')
    return pronunciation

def \
        get_sentence(adr, a_word):
    ''' najde pro dane slovo priklad ve vete '''
    logger.debug('get sentence: %s' %a_word)
    ulozena_veta = os.path.join(adr, DIR_SENTENCES, a_word + '.html')
    logger.debug('ulozena veta:' + ulozena_veta)
    if os.path.exists(ulozena_veta):
        logger.debug('nestahuju, uz byla')
    else:
        logger.debug(ulozena_veta)
        testfile = urllib.URLopener()
        sentence_address = "http://sentence.yourdictionary.com/%s" % a_word.lower()
        logger.debug('sentence_address: %s' % sentence_address)
        try:
            testfile.retrieve(sentence_address, ulozena_veta)
        except IOError:
            logger.warning('nenalezena veta: %s' % sentence_address)
            return ''

    p = re.compile('>[^>]+<b>%s</b>[^>]+<' % a_word)

    with open(ulozena_veta, 'r') as r_sentence:
        for line in r_sentence:
            logger.debug(line)
            vety = p.findall(line)
            if vety:
                logger.debug('nalezeny vety')
                logger.debug(vety)
                #vratim nejkratsi z prvnich 5 - vety jsou serazeny podle jakehosi score a vyse jsou smysluplnejsi
                vety = vety[0:5]
                vety.sort(key=len)
                return vety[0][1:-1] #vrati nejkratsi nalezenou vetu

    r_sentence.close()
    return ""


def check_subdirs(a_dir):
    ''' otestuje, ze existuji pomocne podadresare v danem adresari, pripadne je vytvori '''
    for dir in [DIR_HTML, DIR_SOUNDS, DIR_DONE, DIR_SENTENCES]:
        if not os.path.exists(os.path.join(a_dir, dir)):
            os.mkdir(os.path.join(a_dir, dir))


def zpracuj(adr, a_picture):
    ''' stahne k danemu obrazku co nejvice doplnujicich informaci (zvuk, vyslovnost),
    zkopiruje media do anki folderu
    vrati radek k importu do anki.
        Predpoklada, ze obrazek ma jmeno slovicko.jpg/png/gif
    '''
    # word; picture; sound; pronunciation; example sentence
    # hello; <img src="hello.jpg">; [sound:hello.mp3]; /h??l??/; Hello world!
    logger.debug('function zpracuj: ' + a_picture)

    word = "".join(a_picture.split('.')[0:-1])
    logger.debug('word ' + str(word))
    img = '<img src="' + a_picture + '">'
    logger.debug('img' + img)
    sound = get_sound(adr, word)
    logger.debug('sound:' + sound)
    pronunciation = get_pronunciation(adr, word)
    logger.debug('pronunciation:' + pronunciation)
    sentence = get_sentence(adr, word)
    logger.debug('sentence:' + sentence)
    result = word + ';' + img + ';' + sound + ';' + pronunciation + ';' + sentence
    logger.debug('result' + result)
    return result

def get_sound_filename(adr, a_filename):
    ''' vrati nazev souboru s nahravkou, zatim jen mp3'''
    logger.debug('function get_sound_filename %s' % a_filename)
    result  = os.path.join(adr, DIR_SOUNDS, "".join(a_filename.split('.')[0:-1]) + '.mp3')
    logger.debug(result)
    return result

def zip_log(args, profile_path):
    '''zazipuje log a nahraje jej do adresare anki, odtamtud se synchronizaci dostane ke mne p� p�i ka�d�m pokusu'''
    if args.zip:
        logger.debug('zipuju logfile - %s' %LOGFILE)

        zipfl = 'log_%s.zip' %datetime.now().strftime('%Y%m%d_%H%M%S')
        with zipfile.ZipFile(zipfl, 'w', zipfile.ZIP_DEFLATED) as myzip:
            myzip.write(LOGFILE)
        myzip.close

        shutil.copy(zipfl, profile_path)
        return None

def process_command_line(argv):
    ''' zpracuje cmd parametry do promennych'''

    parser = ArgumentParser()

    parser.add_argument("-d", "--directory", help="directory with pictures to make an import script upon")
    parser.add_argument("--debug", help='show debug messages', action='store_true')
    parser.add_argument("-p", "--profil", help="Anki profile to be used (pictures and sound will be copied to it's media folder")
    parser.add_argument("--zip", help='zip logfile and copy it to anki media folder', action='store_true')

    args = parser.parse_args()

    logger.debug('vstupni argumenty')
    logger.debug(args)

    #    if not (args.changelistfrom or args.date):
    #     if len(sys.argv)==1:
    #         parser.print_help()
    #         sys.exit(1)    #logger.debug('parsed args')
    return args


def main(argv=None):
    ''' entry point of the script '''
    args = process_command_line(argv)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    adr = args.directory

    check_subdirs(adr)

    profile_path = os.path.join(ankiDir, args.profil, 'collection.media')
    logger.debug('profile_path:' + profile_path)
    with open(adr + '/import.txt', 'w') as wr:
        # for adres, podadr, soubory in os.walk(adr):
        # for soubory in
            #pro kazdy soubor
            # print (adres)
        for s in os.listdir(adr):
            logger.debug('filename:' + s)
            if get_extension(s) in ['jpg', 'gif', 'png']:
                try:
                    wr.write(zpracuj(adr, s) + '\n')
                    logger.debug('zapsano do import filu')
                    shutil.copy(os.path.join(adr, s), profile_path)
                    logger.debug('zkopirovan obrazek do profilu')
                    sound_fl = get_sound_filename(adr, s)
                    logger.debug('zkopiruju ' + sound_fl)
                    if os.path.exists(sound_fl):
                        shutil.copy(sound_fl, profile_path)
                    else:
                        logger.debug('nepodarilo se stahnout sound file neni jej odkud kopirovat')
                    done_path = os.path.join(adr, DIR_DONE, s)
                    logger.debug('done:' + done_path)
                    shutil.move(os.path.join(adr, s), done_path)
                    logger.info('zpracovano: %s' %s)
                except:
                    # print (s.ljust(20) + get_phonetic_pronunciation(s))
                    # wr.write(s.ljust(20) + '/' + get_phonetic_pronunciation(s) + '/\n')
                    logger.warn(s + ' ' + str(sys.exc_info()))
                    raise
    wr.close()
    zip_log(args, profile_path)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)