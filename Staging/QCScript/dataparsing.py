import csv
import glob
from lxml import etree

def data_parser (xml_source_file):
    xml_doc = etree.parse(xml_source_file)
    document_root = xml_doc.getroot()
    print(etree.tostring(document_root))

    filename = input("Choose a filename")

    if etree.iselement(document_root):
        output_file = open ("xml_"+ filename + ".csv","w")
        output_writer = csv.writer(output_file)
        output_writer.writerow(document_root[0].attrib.keys())
        for child in document_root:
            output_writer.writerow(child.attrib.values())
    output_file.close()


def xml_file_given_set (filepath):
    xml_source_file = open(filepath, 'rb')
    data_parser(xml_source_file)

def directory_given_set (filepath):
    for i in filepath:
        data_parser()


