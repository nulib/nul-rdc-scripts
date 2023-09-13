#!/usr/bin/env ruby

# Dependencies: Ruby 2.2.2

require 'optparse'
require 'yaml'
require 'nokogiri'
require_relative 'indent_string'

options = {}

option_parser = OptionParser.new do |opts|
  executable_name = File.basename($PROGRAM_NAME)
  opts.banner = "Usage: #{executable_name} [options] input_file output_file_name"

  opts.banner= <<-EOS
  Convert a mets xml file into a yml file according to the Hathi Trust specifications for ingest
  Usage: ruby #{executable_name} [options] input_file output_file_basename
  Example usage: ruby #{executable_name} --force --resolution="300" /cygdrive/e/books/limb_output/35556004429411/35556004429411.mets.xml meta
  Example output: meta.yml
  Options:
  EOS

  opts.on("--[no-]force",
          "Overwrite existing files") do |force| #(1)
    options[:force] = force
  end

  opts.on("--suprascan",
          "\"SupraScan Quartz A1\" will override default \"Kirtas APT 1200\"") do |suprascan|
    options[:suprascan] = true
  end

  opts.on("--resolution=resolution_integer",
          "Enter numeric value of scanning resolution to override default 300") do |resolution|
    options[:resolution] = resolution
  end

  opts.on("--scanning_order_rtl",
          "Use if the scanning order is right-to-left to override default left-to-right") do |resolution|
    options[:scanning_order_rtl] = true
  end

  opts.on("--reading_order_rtl",
          "Use if the reading order is right-to-left to override default left-to-right") do |resolution|
    options[:reading_order_rtl] = true
  end

end

begin
  option_parser.parse!
  if ARGV.length < 2
    puts
    puts "error: you must supply an input file and an output file name"
    puts
    puts option_parser.help
    exit 2
  end
rescue OptionParser::InvalidArgument => ex
  STDERR.puts ex.message
  STDERR.puts option_parser
  exit 1
end

#set input to first command-line argument
input_file = File.open(ARGV[0])
input_file_location = File.dirname(ARGV[0])

#convert mets xml to nokorigi doc
begin
  nokogiri_doc = Nokogiri::XML(input_file) { |config| config.strict }
rescue Nokogiri::XML::SyntaxError => e
  puts "caught exception: #{e}"
end

# FILENAME_FINDER
def find_filename_by_file_id(nokogiri_doc, id)
  nokogiri_doc.xpath("//xmlns:file[@ID=\"#{id}\"]/xmlns:FLocat")[0]['xlink:href'][7..-1]
end

# Descriptive and technical information

# Capture Date
#   <metsHdr CREATEDATE="2015-07-01T15:26:39" RECORDSTATUS="Complete">
yaml = "capture_date: #{nokogiri_doc.xpath("//xmlns:metsHdr")[0].attr("CREATEDATE")}-06:00\n"
# Scanner Make and Model
if options[:suprascan]
  yaml += "scanner_make: SupraScan\n"
  yaml += "scanner_model: Quartz A1\n"
else
  yaml += "scanner_make: Kirtas\n"
  yaml += "scanner_model: APT 1200\n"
end
# Scanner User
yaml += "scanner_user: \"Northwestern University Library: Repository & Digital Curation\"\n"
# Resolution
yaml += "contone_resolution_dpi: #{options[:resolution] || 300}\n"
# Image Compression Date
yaml += "image_compression_date: #{nokogiri_doc.xpath("//xmlns:metsHdr")[0].attr("CREATEDATE")}-06:00\n"
# Image Compression Agent
yaml += "image_compression_agent: northwestern\n"
# Image Compression Tool
yaml += "image_compression_tool: [\"LIMB v4.5.0.0\"]\n"
# Scanning Order
if options[:scanning_order_rtl]
  yaml += "scanning_order: right-to-left\n"
else
  yaml += "scanning_order: left-to-right\n"
end
# Reading Order
if options[:reading_order_rtl]
  yaml += "reading_order: right-to-left\n"
else
  yaml += "reading_order: left-to-right\n"
  yaml += "pagedata:\n"
end



# File List

# Loop through pages within logical structMap
nokogiri_doc.search('structMap[@TYPE="logical"]//div[@TYPE="page"]').each do |element|
  # Store the fileid for the jp2
  file_id = element.xpath('./xmlns:fptr[starts-with(@FILEID, "JP2")]')[0]["FILEID"]
  # Store the jp2 filename
  filename = find_filename_by_file_id(nokogiri_doc, file_id)
  # Since the yaml flattens out the xml structure,
  # the first child of each parent gets special treatment (of course)
  # i.e. labels for covers, titles, chapters, etc.
  if element == element.parent.first_element_child
    case
    when element.parent["LABEL"] == "Cover" && element.parent["TYPE"] == "cover" && element.parent == nokogiri_doc.search('structMap[@TYPE="logical"]//div[@TYPE="cover"]').first
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"FRONT_COVER\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"FRONT_COVER\" }\n"
      end
    when element.parent["LABEL"] == "Front Matter"
      next if element["ORDERLABEL"].empty?
      line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\" }\n"
    when element.parent["LABEL"] == "Cover" && element.parent["TYPE"] == "appendix"
      next if element["ORDERLABEL"].empty?
      line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\" }\n"
    when element.parent["LABEL"] == "Title"
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"TITLE\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"TITLE\" }\n"
      end
    when element.parent["LABEL"] == "Contents"
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"TABLE_OF_CONTENTS\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"TABLE_OF_CONTENTS\" }\n"
      end
    when element.parent["LABEL"] == "Preface"
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"PREFACE\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"PREFACE\" }\n"
      end
    # First page within the body, can be within a div with label attribute "Introduction" or "Chapter"
    when element == nokogiri_doc.at('structMap[@TYPE="logical"]//div[@TYPE="body"]/div[1]/div[1]') && (element.parent["LABEL"] == "Introduction" || element.parent["LABEL"].start_with?("Chapter"))
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"FIRST_CONTENT_CHAPTER_START\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"FIRST_CONTENT_CHAPTER_START\" }\n"
      end
    when element.parent["LABEL"] == "Back Matter"
      next if element["ORDERLABEL"].empty?
      line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\" }\n"
    when element.parent["LABEL"].start_with?("Chapter") || element.parent["LABEL"] == "Appendix"
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"CHAPTER_START\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"CHAPTER_START\" }\n"
      end
    when element.parent["LABEL"] == "Notes" || element.parent["LABEL"] == "Bibliography"
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"REFERENCES\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"REFERENCES\" }\n"
      end
    when element.parent["LABEL"] == "Index"
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"INDEX\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"INDEX\" }\n"
      end
    when element.parent["LABEL"] == "Cover" && element.parent["TYPE"] == "cover" && element.parent == nokogiri_doc.search('structMap[@TYPE="logical"]//div[@TYPE="cover"]').last
      if element["ORDERLABEL"].empty?
        line = filename + ": { label: \"BACK_COVER\" }\n"
      else
        line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\", label: \"BACK_COVER\" }\n"
      end
    end
  else
    # remaining pages
    # skip pages that don't have page numbers (stored in "ORDERLABEL" attribute)
    next if element["ORDERLABEL"].empty?
    line = filename + ": { orderlabel: \"#{element["ORDERLABEL"]}\" }\n"
  end
  yaml += line.indent(4)
end

#set output file based on second command-line argument
output_file_basename = ARGV[1]
output_file = File.join(input_file_location, "#{output_file_basename}.yml")

if File.exists? output_file
  if options[:force]
    STDERR.puts "Overwriting #{output_file}"
  else
    STDERR.puts "error: #{output_file} already exists, use --force to overwrite"
    exit 1
  end
end

unless ENV['NO_RUN']
  File.write(output_file, yaml)
end
