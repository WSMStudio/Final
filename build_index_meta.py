import re, pickle, requests, time

indexes, docs, meta_raw = {}, [], {}

with open('gutenberg_0-4999.txt', 'r') as reader:
    indexes['ptime'] = {}
    indexes['descr'] = {}
    indexes['title'] = {}
    indexes['authr'] = {}
    for line in reader.readlines()[:100]:
        link_intro, authors, title, ptime, descr, link_down = line.split('\t')
        authors = [author.strip() for author in authors.split(',') if not "-" in author]
        doc_id = int(link_intro.split("/")[-1])

        indexes['ptime'].setdefault(ptime, set()).add(doc_id)

        if descr == "No description": descr = ""
        descr = re.sub(r'[^a-zA-Z0-9\s]', "", descr)
        for word in re.split(r'\s', descr):
            indexes['descr'].setdefault(word.lower(), set()).add(doc_id)

        title = re.sub(r'[^a-zA-Z0-9\s]', "", title)
        for word in re.split(r'\s', title):
            indexes['title'].setdefault(word.lower(), set()).add(doc_id)

        for author in authors:
            author = re.sub(r"[^a-zA-Z\s]", "", author)
            for word in re.split(r'\s', author):
                indexes['authr'].setdefault(word.lower(), set()).add(doc_id)

        docs.append(doc_id)
        meta_raw[doc_id] = (ptime, descr, title, ' '.join(authors))

file = open("docs.id", 'wb')
pickle.dump(docs, file, 2)

file = open('meta.index', 'wb')
pickle.dump(indexes, file, 2)

file = open('meta.raw', 'wb')
pickle.dump(meta_raw, file, 2)