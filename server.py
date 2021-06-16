from flask import Flask
from flask import request
from flask import render_template
from flask import Response, json
from gevent import pywsgi
import pickle, datetime
from SearchUtil.SPchecker import SPchecker
from boolean_parser.parsers import Parser
from SearchUtil import wildcard_search as wild
from grammar import group_1, group_2, group_3

app = Flask(__name__, template_folder="templates", static_folder="statics", static_url_path="/static")


class Indexer:

    def __init__(self):
        self.index = self.meta_index = self.meta_raw = None
        with open('content.raw', 'rb') as reader:
            self.docs_raw = pickle.load(reader)
        self.doc_n = len(self.docs_raw)

    def buildIndex(self):
        with open('content.index', 'rb') as reader:
            self.index = pickle.load(reader)
        with open('meta.index', 'rb') as reader:
            self.meta_index = pickle.load(reader)
        with open('meta.raw', 'rb') as reader:
            self.meta_raw = pickle.load(reader)

    def foo(self, p1, p2, doc, pre, k):
        answer = {}
        within_k = (lambda x, y: x - y <= k) if pre else (lambda x, y: abs(x - y) <= k)
        within_k_0 = (lambda x, y: 0 < x - y <= k) if pre else within_k
        pp1 = pp2 = 0
        while pp1 < len(p1) and pp2 < len(p2):
            if pre and p2[pp2][-1] - p1[pp1][-1] < 0:
                pp2 += 1
            elif within_k(p2[pp2][-1], p1[pp1][-1]):
                answer.setdefault(doc, []).append((p1[pp1][-1], p2[pp2][-1]))
                if p2[pp2][-1] > p1[pp1][-1]:
                    pp2 += 1
                else:
                    pp1 += 1
            else:
                if p2[pp2][-1] > p1[pp1][-1]:
                    pp1 += 1
                else:
                    pp2 += 1
        for i in range(pp1 + 1, len(p1)):
            if within_k_0(p2[-1][-1], p1[i][-1]):
                answer.setdefault(doc, []).append((p1[i][-1], p2[-1][-1]))
        for i in range(pp2 + 1, len(p2)):
            if within_k_0(p2[i][-1], p1[-1][-1]):
                answer.setdefault(doc, []).append((p1[-1][-1], p2[i][-1]))
        return answer

    def proximity(self, q1, q2, k, where='D', pre=False):
        answer = {}
        if not (q1 in self.index and q2 in self.index): return answer
        doc_candidates = set(self.index[q1].keys()) & set(self.index[q2].keys())
        if where == 'D':
            for doc_id in doc_candidates:
                p1 = self.index[q1][doc_id]
                p2 = self.index[q2][doc_id]
                answer.update(self.foo(p1, p2, doc_id, pre, k))
        elif where == 'P':
            for doc_id in doc_candidates:
                p1 = self.index[q1][doc_id]
                p2 = self.index[q2][doc_id]
                for pid in set([p[0] for p in p1]):
                    cp2 = [p for p in p2 if p[0] == pid]
                    if cp2:
                        cp1 = [p for p in p1 if p[0] == pid]
                        for key, value in self.foo(cp1, cp2, doc_id, pre, k).items():
                            answer.setdefault(key, []).extend(value)
        elif where == 'S':
            for doc_id in doc_candidates:
                p1 = self.index[q1][doc_id]
                p2 = self.index[q2][doc_id]
                for pid, sid in set([p[:2] for p in p1]):
                    cp2 = [p for p in p2 if p[0] == pid and p[1] == sid]
                    if cp2:
                        cp1 = [p for p in p1 if p[0] == pid and p[1] == sid]
                        for key, value in self.foo(cp1, cp2, doc_id, pre, k).items():
                            answer.setdefault(key, []).extend(value)
        # print(answer)
        return answer

    def search_general(self, field, word):
        res = {}
        word = word.lower()
        if field == 'content':
            for doc in self.index.get(word, []):
                prev = -1e9
                words = indexer.docs_raw[doc]
                for _, _, pos in self.index[word][doc]:
                    if pos <= prev + 5: continue
                    context = " ".join(words[max(0, pos - 5): min(len(words), pos + 5)])
                    # print(len(words), pos)
                    context = context.replace(" " + words[pos] + " ", f" <span class='highlight'>{words[pos]}</span> ")
                    if context.startswith(words[pos]):
                        context = f" <span class='highlight'>{words[pos]}</span> " + context[len(words[pos]):]
                    res.setdefault(doc, []).append(context)
                    prev = pos
        if field == 'author':
            for doc in self.meta_index['authr'].get(word, []):
                context = "#Author: " + self.meta_raw[doc][3]
                for w in [word, word[0].upper() + word[1:], word.upper()]:
                    context = context.replace(w, f" <span class='highlight'>{w}</span> ")
                res.setdefault(doc, []).append(context)
        if field == 'year':
            for doc in self.meta_index['ptime'].get(word, []):
                context = "#Published Year: " + self.meta_raw[doc][0]
                for w in [word, word[0].upper() + word[1:], word.upper()]:
                    context = context.replace(w, f" <span class='highlight'>{w}</span> ")
                res.setdefault(doc, []).append(context)
        if field == 'descr':
            for doc in self.meta_index['descr'].get(word, []):
                context = "#Description: " + self.meta_raw[doc][1]
                for w in [word, word[0].upper() + word[1:], word.upper()]:
                    context = context.replace(w, f" <span class='highlight'>{w}</span> ")
                res.setdefault(doc, []).append(context)
        if field == 'title':
            for doc in self.meta_index['title'].get(word, []):
                context = "#Title: " + self.meta_raw[doc][2]
                for w in [word, word[0].upper() + word[1:], word.upper()]:
                    context = context.replace(w, f" <span class='highlight'>{w}</span> ")
                res.setdefault(doc, []).append(context)
        return res

    def search_content(self, q1, q2, k, where, pre):
        res = {}
        for doc, value in sorted(self.proximity(q1, q2, k, where=where, pre=pre).items(), key=lambda x: x[0]):
            words = indexer.docs_raw[doc]
            for w1, w2 in value:
                w1, w2 = min(w1, w2), max(w1, w2)
                context = " ".join(words[max(0, w1 - 5): min(len(words), w2 + 5)])
                context = context.replace(" " + words[w1] + " ", f" <span class='highlight'>{words[w1]}</span> ") \
                    .replace(" " + words[w2] + " ", f" <span class='highlight'>{words[w2]}</span> ")
                if context.startswith(words[w1]):
                    context = f" <span class='highlight'>{words[w1]}</span> " + context[len(words[w1]):]
                res.setdefault(doc, []).append(context)
        return res


def prox_action(data):
    q1 = data['q1'].replace('"', '').replace("'", "").lower()
    tmp = checker.checker(q1)
    if not (len(tmp) == 1 and tmp[0] == q1):
        spell_hints[q1] = tmp
    q2 = data['q2'].replace('"', '').replace("'", "").lower()
    tmp = checker.checker(q2)
    if not (len(tmp) == 1 and tmp[0] == q2):
        spell_hints[q2] = tmp
    op = data['op']
    pre = 'order' in op
    where = op.get('type', 'D').upper()
    k = int(op.get('within', 1e9))
    command.setdefault('content', []) \
        .append((q1, q2, k, where, pre))


def Action1(data):
    dd = data[0].asDict()
    if 'value' in dd:
        value = dd['value'].replace('"', '').replace("'", "").lower()
        # if "*" in value:
        #     for v in wild.wild_card('content', value):
        #         command.setdefault('content', []).append((v, None, None, None, None))
        # else:
        #     command.setdefault('content', []). \
        #         append((value, None, None, None, None))
        command.setdefault('content', []).append((value, None, None, None, None))
        tmp = checker.checker(value)
        if not (len(tmp) == 1 and tmp[0] == value):
            spell_hints[value] = tmp
    elif 'prox' in dd:
        value = dd['prox']
        prox_action(value)
    return 'content', len(command['content']) - 1


def Action2(data):
    dd = data[0].asDict()
    field = dd['field'].lower()
    value = dd['value'].replace('"', '').replace("'", "")
    # if "*" in dd['value']:
    #     for value in wild.wild_card(field, dd['value']):
    #         command.setdefault(field, []).append(value)
    # else:
    #     command.setdefault(field, []).append(dd['value'])
    command.setdefault(field, []).append(value)
    return field, len(command[field]) - 1


def Action3(data):
    dd = data[0].asDict()
    field = dd['field'].lower()
    value = dd['value'].replace('"', '').replace("'", "")
    # if "*" in dd['value']:
    #     for value in wild.wild_card(field, dd['value']):
    #         command.setdefault(field, []).append(value)
    # else:
    #     command.setdefault(field, []).append(dd['value'])
    command.setdefault(field, []).append(value)
    return field, len(command[field]) - 1


@app.route('/', methods=['GET'])
def paste():
    return render_template("index.html")


@app.route('/search', methods=['POST'])
def search():
    search_old_time = datetime.datetime.now()
    query = request.form.get('query')
    command.clear()
    spell_hints.clear()
    boolean = query_parser.parse(query).__repr__()
    response_tmp = {}
    print(command)
    if "content" in command:
        for q1, q2, k, where, pre in command['content']:
            if not q2:
                if "*" in q1:
                    for v in wild.wild_card('content', q1):
                        response_tmp.setdefault('content', []).append(indexer.search_general('content', v))
                else:
                    response_tmp.setdefault("content", []).append(indexer.search_general('content', q1))
            else:
                response_tmp.setdefault("content", []).append(indexer.search_content(q1, q2, k, where, pre))
    if "author" in command:
        for value in command['author']:
            if "*" in value:
                for v in wild.wild_card('author', value):
                    response_tmp.setdefault('author', []).append(indexer.search_general('author', v))
            else:
                response_tmp.setdefault('author', []).append(indexer.search_general('author', value))
    if "year" in command:
        for value in command['year']:
            if "*" in value:
                for v in wild.wild_card('year', value):
                    response_tmp.setdefault('year', []).append(indexer.search_general('year', v))
            else:
                response_tmp.setdefault('year', []).append(indexer.search_general('year', value))
    if "descr" in command:
        for value in command['descr']:
            if "*" in value:
                for v in wild.wild_card('descr', value):
                    response_tmp.setdefault('descr', []).append(indexer.search_general('descr', v))
            else:
                response_tmp.setdefault('descr', []).append(indexer.search_general('descr', value))
    if "title" in command:
        for value in command['title']:
            if "*" in value:
                for v in wild.wild_card('title', value):
                    response_tmp.setdefault('title', []).append(indexer.search_general('title', v))
            else:
                response_tmp.setdefault('title', []).append(indexer.search_general('title', value))

    def and_(*params):
        sets = [set(response_tmp[field][i].keys()) for field, i in params]
        docs = sets[0].intersection(*sets[1:])
        field_ret, i_ret = params[0]
        temp = {}
        for field, i in params:
            for doc in docs:
                temp.setdefault(doc, []).extend(response_tmp[field][i][doc])
        response_tmp[field_ret][i_ret] = temp
        return field_ret, i_ret

    def or_(*params):
        sets = [set(response_tmp[field][i].keys()) for field, i in params]
        docs = sets[0].union(*sets[1:])
        field_ret, i_ret = params[0]
        temp = {}
        for field, i in params:
            for doc in docs:
                temp.setdefault(doc, []).extend(response_tmp[field][i].get(doc, []))
        response_tmp[field_ret][i_ret] = temp
        return field_ret, i_ret

    def not_(param):
        (field_, i_), temp = param, {}
        for doc_id in set(indexer.docs_raw.keys()) - set(response_tmp[field_][i_].keys()):
            temp[doc_id] = ["Result Unavailable"]
        response_tmp[field_][i_] = temp
        return field_, i_

    field, i = eval(boolean)
    search_new_time = datetime.datetime.now()
    return Response(json.dumps({
        'data': response_tmp[field][i],
        'hint': spell_hints,
        'time': (search_new_time - search_old_time).total_seconds()
    }), content_type='application/json')


old_time = datetime.datetime.now()
Parser.build_parser(clauses=[group_1, group_2, group_3], actions=[Action1, Action2, Action3])
query_parser = Parser()
indexer = Indexer()
indexer.buildIndex()
command = {}
spell_hints = {}
checker = SPchecker()
server = pywsgi.WSGIServer(("localhost", 8000), app)
new_time = datetime.datetime.now()
print((new_time - old_time).total_seconds())
try:
    server.serve_forever()
except KeyboardInterrupt:
    print('Searching Engine stopped serving.')
