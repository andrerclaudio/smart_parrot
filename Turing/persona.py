# Libraries
from string import punctuation

import enchant
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

from Database.database import *
from Transmission.print_scheme import print_function
from replacers import RegexpReplacer

replacer = None
word_dict = None
stops = None


def nltk_ignition():
    global replacer
    global word_dict
    global stops

    replacer = RegexpReplacer()
    word_dict = enchant.Dict("en_US")
    stops = set(stopwords.words('english'))
    return None


def dealing_with_stopwords(string):
    string_without_stopwords = ''
    string_without_punctuation = ''
    words = word_tokenize(string)

    for i in words:
        if i not in punctuation:
            if word_dict.check(i):
                string_without_punctuation = string_without_punctuation + i + ' '
                if i not in stops:
                    string_without_stopwords = string_without_stopwords + i + ' '

    if len(string_without_stopwords) is 0:
        return string_without_punctuation[0:(len(string_without_punctuation) - 1)]
    else:
        return string_without_stopwords[0:(len(string_without_stopwords) - 1)]


def remove_punctuation(content_with_punctuation):
    w = word_tokenize(content_with_punctuation)
    concat = ''
    for j in w:
        if j not in punctuation:
            concat = concat + j + ' '

    content_without_punctuation = concat[0:(len(concat) - 1)]

    return content_without_punctuation


def dialog():
    while True:
        # Input string. In order to start normalizing the sentence, it will force all the words to lower case.
        content = print_function('IN', '\n\nSay something ...\n'
                                       '--> ')

        if content.isprintable() is False:
            break
        if content.isspace() is True:
            break

        content = content.lower()

        # Escape word
        if content == 'exit':
            break

        # Normalize the content exchanging the contraction form of words with its complete format.
        content = replacer.replace(content)
        concat = remove_punctuation(content)

        # Check if the entire content is already added into the database table.
        data = database_find_strings(strings_table, 'string', concat)

        if len(data) is 0:
            # If there is no occurrence yet for the same string, let's take off the stopwords.
            small_content = dealing_with_stopwords(content)
            # Find into the database for the same string but now, without the stopwords.
            data = database_find_strings(strings_table, 'small', small_content)

            if len(data) is 0:
                # Until here, if We did not find the input string in the database, the sentence must be sliced into
                # small parts, using punctuation rules to perform this segmentation.
                content = sent_tokenize(content)
                length = len(content)

                for i in content:
                    concat = remove_punctuation(i)
                    if len(database_find_strings(strings_table, 'string', concat)) is 0:
                        print_function('OUT', 'How should I answer this sentence?\n')
                        answer = print_function('IN', '{} --> '.format(i)).lower()
                        if answer.isprintable():
                            if answer.isspace() is False:
                                answer = replacer.replace(answer)
                                small_content = dealing_with_stopwords(i)
                                database_add_string(concat, small_content)
                                database_add_related_string(answer_table, concat, answer)
                    else:
                        length = length - 1
                        database_add_string(concat, '')

                if length is 0:
                    for i in content:
                        data = database_find_strings(strings_table, 'string', i)
                        database_add_string(i, '')
                        print_function('OUT', database_fetch_answer(data[0]) + '\n')

            else:
                data = database_find_strings(strings_table, 'small', small_content)

                index = fetch_column_name_list(answer_table).index('string')
                content = data[0]
                content = content[index]
                database_add_string(content, '')
                data = database_find_strings(answer_table, 'string', content)
                print_function('OUT', database_fetch_answer(data[0]))

                new_answer = print_function('IN', '\n\nPress ENTER to continue, or please, '
                                                  'teach me another answer for this question.\n--> ')

                if new_answer is not '':
                    database_add_related_string(answer_table, content, new_answer)

        else:
            database_add_string(concat, '')
            data = database_find_strings(answer_table, 'string', concat)
            print_function('OUT', database_fetch_answer(data[0]))

            new_answer = print_function('IN', '\n\nPress ENTER to continue, or please, '
                                              'teach me another answer for this question.\n--> ')

            if new_answer is not '':
                database_add_related_string(answer_table, concat, new_answer)

    return
