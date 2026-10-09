# ttl_to_rdf.py - Convert Turtle (.ttl) file to RDF/XML (.rdf) format using rdflib
# In powershell, run this script using: python ttl_to_rdf.py

from rdflib import Graph

# Input and output files
input_file = "i14224_clause3.ttl"
output_file = "i14224_clause3.rdf"

# Read Turtle file
graph = Graph()
graph.parse(input_file, format="turtle")

# Export as RDF/XML
graph.serialize(
    destination=output_file,
    format="xml",
    encoding="utf-8"
)

print(f"Converted {input_file} to {output_file}")
print(f"Number of RDF triples: {len(graph)}")

# Verify the conversion
check_graph = Graph()
check_graph.parse(output_file, format="xml")

assert graph.isomorphic(check_graph), (
    "Conversion validation failed"
)

print("Validation successful: graphs are equivalent.")
