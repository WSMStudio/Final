import pyparsing as pp


word = pp.Word(pp.alphanums) | pp.quotedString

prox_a = pp.oneOf(['D', 'P', 'S', 'd', 'p', 's']).setResultsName("type") \
         + pp.Optional('^' + pp.Word(pp.nums).setResultsName('within'))
prox_b = pp.Word(pp.nums).setResultsName('within') | prox_a

prox = pp.Combine(
    pp.Optional("PRE").setResultsName('order')
    + '/'
    + prox_b
).setResultsName('op')

prox_query = pp.Group('[' +
    pp.Word(pp.alphanums).setResultsName('q1')
    + prox +
    pp.Word(pp.alphanums).setResultsName('q2')
+ ']').setResultsName('prox')

field_1 = pp.oneOf(['CONTENT', 'content']).setResultsName('field')
value_1 = (pp.Word(pp.alphanums) | pp.quotedString).setResultsName('value') | prox_query
group_1 = pp.Group(field_1 + ':' + value_1)


field_2 = pp.oneOf(['AUTHOR', 'YEAR', 'author', 'year']).setResultsName('field')
value_2 = word.setResultsName('value')
group_2 = pp.Group(field_2 + ':' + value_2)

field_3 = pp.oneOf(['TITLE', 'DESCR', 'title', 'descr']).setResultsName('field')
value_3 = word.setResultsName('value')
group_3 = pp.Group(field_3 + ':' + value_3)

# res = parser.parse('CONTENT : ["hello world" PRE/D^1 b] and TITLE : abc or AUTHOR : "Mark Twain"')
# res = parser.parse('CONTENT : ["hello world" PRE/D^1 b]')
# print(res)
