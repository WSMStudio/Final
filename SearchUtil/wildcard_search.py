import os
import codecs

permuterm = {}


# 建立inverted index字典
def init(str):
    if str == "content":
        temp = "SearchUtil/perm.txt"
    elif str == "title":
        temp = "SearchUtil/pre_title.txt"
    elif str == "year":
        temp = "SearchUtil/pre_year.txt"
    elif str == "author":
        temp = "SearchUtil/pre_au.txt"
    with open(temp) as perm:
        for line in perm:
            temp = line.split()
            permuterm[temp[0]] = temp[1]


docID = 0


# 返回前缀和prefix相同的所有term
def prefix_match(term, prefix):
    term_list = []
    for tk in term.keys():
        if tk.startswith(prefix):
            term_list.append(term[tk])
    return term_list


def bitwise_and(A, B):
    return set(A).intersection(B)


def wild_card(state, part):
    init(state)
    parts = part.strip().split("*")

    # X*Y*Z
    if len(parts) == 3:
        case = 4
    # X*
    elif parts[1] == ' ':
        case = 1
    # *X
    elif parts[0] == ' ':
        case = 2
    # X*Y
    elif parts[0] != ' ' and parts[1] != ' ':
        case = 3

    # *X*Y --> X*Y*
    if case == 4:
        if parts[0] == ' ':
            case = 1

    # print("case = ", case)

    if case == 1:
        query = parts[0]
    elif case == 2:
        query = parts[1] + "$"
    elif case == 3:
        query = parts[1] + "$" + parts[0]
    elif case == 4:
        query_1 = parts[2] + "$" + parts[0]
        query_2 = parts[1]
        # print("part 1 and part = ",query_1, query_2)
    # print("term_list1 =",query)
    if case != 4:
        return prefix_match(permuterm, query) + ["SJTU"]
    elif case == 4:
        # query_1 Z$X
        term_list_1 = prefix_match(permuterm, query_1)
        # print("term_list1 =",term_list_1)
        term_list_2 = prefix_match(permuterm, query_2)
        # print("term_list2 =", term_list_2)
        temp = bitwise_and(term_list_2, term_list_1)
        return list(temp) + ['SJTU']
