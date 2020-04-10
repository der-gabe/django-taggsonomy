import json

from graphviz import Digraph

with open('tags.json') as tags_file:
    tag_list = json.load(tags_file)

graph = Digraph(comment='Tags', format='svg')

for tag in tag_list:
    pk = str(tag.get('pk'))
    name = tag.get('fields').get('name')
    graph.node(pk, '{} ({})'.format(name, pk))
    for inclusion in tag.get('fields').get('_inclusions'):
        graph.edge(pk, str(inclusion))
    for exclusion in tag.get('fields').get('_exclusions'):
        graph.edge(pk, str(exclusion), color='red', constraint='false', dir='both', minlen='2')

graph.render('tags')
