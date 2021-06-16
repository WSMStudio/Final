import re, pickle, os

indexes, raw_docs = {}, {}

with open('docs.id', 'rb') as reader:
    docs = pickle.load(reader)

for i, doc_id in enumerate(docs[: 100]):
    if i % 10 == 0: print(f"Busy with {i}/{100} ...")
    with open(f"../crawler/guten_data/content/pg{doc_id}.txt", "r") as reader:
        doc = reader.read()
    word_id = 0
    raw_doc = []
    for para_id, para in enumerate(re.split(r'\n\n[\n]+', doc)):
        para = re.sub(r'[\n]+', " ", para).strip()
        para = re.sub(r'\s[\s]+', " ", para)
        for sen_id, sen in enumerate(re.split(r'[\.\?!]', para)):
            for word in sen.strip().split():
                raw_doc.append(word)
                word = re.sub(r'[^a-zA-Z0-9\.\?!\s]', "", word)
                indexes.setdefault(word.lower(), {}).setdefault(doc_id, []).append((para_id, sen_id, word_id))
                word_id += 1
    raw_docs[doc_id] = raw_doc

with open('content.raw', 'wb') as writer:
    pickle.dump(raw_docs, writer, 2)

with open('content.index', 'wb') as writer:
    pickle.dump(indexes, writer, 2)