import xmlschema
from pprint import pprint

file = "example.xml"
schema = xmlschema.XMLSchema("schema.xsd")

schema.validate(file)
