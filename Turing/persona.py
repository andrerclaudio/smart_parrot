# Libraries
from random import choice
from string import punctuation

import enchant
import numpy
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

from Database.database import database_find_strings, database_add_string, database_fetch_answer, \
    database_add_related_string, strings_table, answer_table, \
    database_list_column_names, database_bring_tablet
from Transmission.print_scheme import print_function
from replacers import RegexpReplacer

replacer = None
word_dict = None
stops = None
last_question = None


def be_or_not_to_be():
    return choice([True, False])


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


def make_question():
    pass


def await_question():
    pass


def dialog():
    while True:

        if be_or_not_to_be() is True:
            all_table = database_bring_tablet(strings_table)
            if len(all_table) is not 0:
                obj_string = []
                obj_prob = []

                index_occurrences = database_list_column_names(strings_table).index('occurrences')
                index_string = database_list_column_names(strings_table).index('string')

                for i in all_table:
                    obj_string.append(i[index_string])
                    obj_prob.append(i[index_occurrences])

                total = 0
                for i in obj_prob:
                    i = int(i)
                    total = total + i

                index = 0
                for i in obj_prob:
                    obj_prob[index] = '{0: .4f}'.format(int(i)/total)
                    index = index + 1

                cdf = 0
                for i in obj_prob:
                    i = float(i)
                    cdf = cdf + i

                if cdf != 1.0:
                    s = sorted(obj_prob, reverse=True)
                    index_p = obj_prob.index(s[0])
                    diff = cdf - 1
                    fix = float(obj_prob[index_p]) - diff
                    obj_prob[index_p] = str(fix)

                if last_question is None:
                    active_question = numpy.random.choice(obj_string, p=obj_prob)
                    answer = print_function('IN', '\n\n[ME]  --> {}\n'
                                                  '[YOU] --> '.format(active_question)).lower()
                else:
                    pass

                if answer.isprintable():
                    if answer.isspace() is False:
                        answer = replacer.replace(answer)
                        database_add_related_string(answer_table, active_question, answer)

        else:

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
            bkp_content = content
            content = remove_punctuation(replacer.replace(content))

            # Check if the entire content is already added into the database table.
            data = database_find_strings(strings_table, 'string', content)

            if len(data) is 0:
                # If there is no occurrence yet for the same string, let's take off the stopwords.
                small_content = dealing_with_stopwords(content)
                # Find into the database for the same string but now, without the stopwords.
                data = database_find_strings(strings_table, 'small', small_content)

                if len(data) is 0:
                    # Until here, if We did not find the input string in the database, the sentence must be sliced into
                    # small parts, using punctuation rules to perform this segmentation.
                    content = sent_tokenize(bkp_content)
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
                    content = data[0]
                    content = content[database_list_column_names(strings_table).index('string')]
                    database_add_string(content, '')
                    data = database_find_strings(answer_table, 'string', content)
                    print_function('OUT', database_fetch_answer(data[0]))

                    if be_or_not_to_be() is True:
                        new_answer = print_function('IN', '\n\nPlease, teach me another answer for this question.\n--> ')

                        if new_answer is not '':
                            database_add_related_string(answer_table, content, new_answer)

            else:
                database_add_string(content, '')
                data = database_find_strings(answer_table, 'string', content)
                print_function('OUT', database_fetch_answer(data[0]))

                if be_or_not_to_be() is True:
                    new_answer = print_function('IN', '\n\nPlease, teach me another answer for this question.\n--> ')

                    if new_answer is not '':
                        database_add_related_string(answer_table, content, new_answer)

    return
