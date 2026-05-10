# Created test to see if CSV data has been parsed correctly to turtle
from rdflib import Graph

path = r"C:\\Users\\00040628\\LocalData\\GitHub\\14224ontologies_public\\inDevelopment\\vocab14224_appendixB.ttl"

g = Graph()
g.parse(path, format="turtle")

print(f"Parsed successfully: {len(g)} triples")