# encoding: utf-8
'''
This package uses the KANJIDIC dictionary file. (see http://www.csse.monash.edu.au/~jwb/kanjidic.html)
Theis file is the property of the Electronic Dictionary Research and Development Group,
and is used in conformance with the Group's licence.
'''

import os.path
import random
import pickle
import xml.etree.ElementTree as ET
from collections import OrderedDict
from math import sqrt

tree = ET.parse('kanjidic2.xml')
root = tree.getroot()
masterDictionary = OrderedDict()

if not os.path.isfile("kanjiPickle.p"):
    for kanji in root.findall('character'):
        if kanji[3].find('grade') is None:
            tempdict = OrderedDict()
            symbol = kanji.find('literal').text
            try:
                tempdict["freq"] = int(kanji[3].find('freq').text)
            except:
                tempdict["freq"] = "NA"

            try:
                tempdict["jlpt"] = int(kanji[3].find('jlpt').text)
            except:
                tempdict["jlpt"] = "NA"

            if kanji.find('dic_number') is not None:
                for node in kanji.find('dic_number'):
                    if node.attrib["dr_type"] == "nelson_c":
                        tempdict["Nelson"] = node.text
                    elif node.attrib["dr_type"] == "moro":

                        if "m_vol" in node:
                            tempdict["moro_vol"] = node.attrib["m_vol"]
                        else:
                            pass

                        if "m_page" in node:
                            tempdict["moro_page"] = node.attrib["m_page"]
                        else:
                            pass

                        if node.text is not None:
                            tempdict["moro_number"] = node.text
                        else:
                            pass

                    else:
                        pass
                else:
                    pass

            meaning = []
            onyomi = []
            kunyomi = []
            nanori = []

            if (kanji.find('reading_meaning') is not None) and (kanji.find('reading_meaning')[0] is not None):
                for child in kanji.find('reading_meaning')[0]:
                    #python seems to behave badly with series of if statements,
                    #preferred this to be set up as if, elif, elif, else
                    if (child.tag == "meaning") and (child.attrib == {}):
                        meaning.append(child.text)
                    elif ("r_type" in child.attrib) and (child.attrib["r_type"] == "ja_on"):
                        onyomi.append(child.text)
                    elif ("r_type" in child.attrib) and (child.attrib["r_type"] == "ja_kun"):
                        kunyomi.append(child.text)
                    else:
                        pass
            else:
                pass

            #nanori is in a different level of the xml file
            if kanji.find('reading_meaning') is not None:
                for child in kanji.find('reading_meaning'):
                    if child.tag == "nanori":
                        nanori.append(child.text)
                    else:
                        pass
            else:
                pass

            tempdict["ja_on"] = onyomi
            tempdict["ja_kun"] = kunyomi
            tempdict["meaning"] = meaning
            tempdict["nanori"] = nanori

            masterDictionary[symbol] = tempdict
    pickle.dump(masterDictionary, open("kanjiPickle.p", "wb"))
else:
    masterDictionary = pickle.load(open("kanjiPickle.p", "rb"))

reference_list = []
for key in masterDictionary:
    reference = key
    if "moro_number" in masterDictionary[key]:
        reference += " M" + masterDictionary[key]["moro_number"]
    else:
        pass
    for entry in masterDictionary[key]["meaning"]:
        reference += " " + entry + ","
    for entry in masterDictionary[key]["ja_on"]:
        reference += " " + entry + ","
    for entry in masterDictionary[key]["ja_kun"]:
        reference += " " + entry + ","
    if reference[len(reference) - 1] == ",":
        reference = reference[:len(reference) - 1]
    reference_list.append(reference)

a = 0
while a < 100:
    print(random.choice(reference_list))
    a += 1