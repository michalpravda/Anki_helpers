# coding=windows-1250
import logging
'''
Vezme seznam slov se stitky
Doplni obrazek a zvuk a anglicky vyznam a slovni druh a poradi
'''

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()


pole = {}
with open ("d:\\majkl\\fluent forever\\spanelstina\\Essential Spanish Vocabulary Top 5000_pozn.txt", 'r') as top5000:
    for f in top5000:
   #    absoluto (adj)	"<img src=""paste-4562608183050241.jpg"" />"	absolute	[sound:yandex-ed786d1b-be3786b7-8c793710-a9852788-0ac15d82.mp3] 	574 	1000   adj
        polozky = f.split('\t')

        logger.debug(polozky[0])
        index = polozky[0].split(' ')[0]
        logger.debug(index)

        pole[index] = polozky
    top5000.close()


with open ('d:\\majkl\\fluent forever\\spanelstina\\CZ - Španělština pro samouky4.txt', 'r') as infile:
# sbohem	adiós		L01 stitek
    with open ('d:\\majkl\\fluent forever\\spanelstina\\CZ - Španělština pro samouky_obr.txt', 'w') as outfile:
        for f in infile:
            polozky_radku = f.split('\t')
            if polozky_radku[1] in pole:
                logger.debug('nasel jsem %s' % polozky_radku[1])
                r = pole[polozky_radku[1]]
                outfile.write('%s;%s;%s;%s;%s;%s;%s;%s;\n' %(polozky_radku[0], polozky_radku[1], r[1], r[2], r[3], r[0].split(' ')[1], r[4], polozky_radku[3].strip()))
            else:
                logger.debug('nenasel jsem %s' % polozky_radku[1])
                outfile.write('%s;%s;%s;%s;%s;%s;%s;%s;\n' %(polozky_radku[0], polozky_radku[1], '', '', '', '', '', polozky_radku[3].strip()))


    infile.close()