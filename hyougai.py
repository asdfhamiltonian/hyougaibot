# encoding: utf-8
'''
This package uses the KANJIDIC dictionary file.
This file is the property of the Electronic Dictionary Research and
Development Group, and is used in conformance with the Group's license.
(see http://www.csse.monash.edu.au/~jwb/kanjidic.html)
-----
significant parts of the twitter interface design for this bot
were borrowed from/inspired by github user tpinecone's
hello-world-bot
'''

import os.path
import tweepy
import secrets
import random
import pickle
import xml.etree.ElementTree as ET
from collections import OrderedDict
import time

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

            if ((kanji.find('reading_meaning') is not None) and
                    (kanji.find('reading_meaning')[0] is not None)):
                for child in kanji.find('reading_meaning')[0]:
                    '''python seems to behave badly with series of ifs
                    preferred this to be set up as if, elif, elif, else'''
                    if (child.tag == "meaning") and (child.attrib == {}):
                        meaning.append(child.text)
                    elif (("r_type" in child.attrib) and
                            (child.attrib["r_type"] == "ja_on")):
                        onyomi.append(child.text)
                    elif (("r_type" in child.attrib) and
                            (child.attrib["r_type"] == "ja_kun")):
                        kunyomi.append(child.text)
                    else:
                        pass
            else:
                pass

            '''nanori readings are in a higher level in the xml file than
            the on/kun readings for some reason'''
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

if not os.path.isfile("definitionListPickle.p"):
    reference_list = []
    for key in masterDictionary:
        reference = ""

        reference += " " + key

        for entry in masterDictionary[key]["ja_on"]:
            reference += " " + entry + ","
        for entry in masterDictionary[key]["ja_kun"]:
            reference += " " + entry + ","
        for entry in masterDictionary[key]["meaning"]:
            reference += " " + entry + ","
        if reference[len(reference) - 1] == ",":
            reference = reference[:len(reference) - 1]

        if "moro_number" in masterDictionary[key]:
            reference += " (Morohashi " + masterDictionary[key]["moro_number"]
        else:
            pass
        if "Nelson" in masterDictionary[key]:
            reference += ", Nelson " + masterDictionary[key]["Nelson"]
        else:
            pass
        if "moro_number" in masterDictionary[key]:
            reference += ")"

        reference_list.append(reference)
    pickle.dump(reference_list, open("definitionListPickle.p", "wb"))
else:
    reference_list = pickle.load(open("definitionListPickle.p", "rb"))

"""
a = 0
while a < 1000:
    print(random.choice(reference_list))
    a += 1
"""

# ran an analysis on reference_list, and it turns out there are 6 items longer
# than 140 characters. However, they only need to be split up into a maximum
# of two tweets. Can add simple for loop before posting to account for this.

def tweet(message):
    auth = tweepy.OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
    auth.set_access_token(secrets.access_token, secrets.access_token_secret)
    api = tweepy.API(auth)
    auth.secure = True
    print(len(reference_list))
    print("Posting message {}".format(message))
    if len(message) <= 140:
        api.update_status(status=message)
    elif len(message) > 140:
        message1 = message[:140]
        message2 = message[140:]
        api.update_status(status=message1)
        api.update_status(status=message2)
    else:
        pass


def get_next_definition():
    reference_list = pickle.load(open("definitionListPickle.p", "rb"))
    message = reference_list[0]
    del reference_list[0]
    pickle.dump(reference_list, open("definitionListPickle.p", "wb"))
    return message

"""
for i in range(0, 20):
    print(get_next_definition())
"""

tweet(get_next_definition())

# tweet("The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog. The quick brown fox...")