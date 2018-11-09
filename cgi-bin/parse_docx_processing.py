#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import modules for CGI handling
import cgi, cgitb
import os, sys
import glob
import shutil
import re
import codecs

cgitb.enable()

cgi_bin_dir = os.getcwd()

server_name = os.environ["SERVER_NAME"]
if '.' in server_name:  # running on web host
    BASE_URL = 'http://'+server_name+'/parse_docx_web'.rstrip('/')
    TOP_DIR = '../parse_docx_web'.rstrip('/')
else:  # running on localhost
    BASE_URL = 'http://localhost:8000'.rstrip('/')
    TOP_DIR = '.'.rstrip('/')

ALIGNER_DIR = 'aligner'
MODULE_DIR = 'modules'.rstrip('/')
DATA_DIR = 'data'
UPLOAD_DIR = 'uploads'.rstrip('/')
TEMP_RESULT_DIR = 'results'.rstrip('/')
OUTPUT_DIR = 'downloads'.rstrip('/')
ABS_TOP_DIR = cgi_bin_dir.replace('/cgi-bin', '/parse_docx_web').rstrip('/')

# Note:
# Run from Linux terminal in the folder containing cgi-bin:
# python3 -m http.server --bind localhost --cgi 8000
# or with Python2:
# python -m CGIHTTPServer 8000 .
# Then access the web page (.html) on localhost:8000

# When running on localhost:8000, the TOP_DIR is '.', because the current directory
# is with the HTML file that calls to this Python script (upper dir)
# While running on web server of Hawkhost, TOP_DIR is '..'

from sys import path
path.append(TOP_DIR+'/'+MODULE_DIR)

import parse_docx
import Csv_Excel

def create_user_dir(base_dir):
    """Create directory for the request, with the structure
    base_dir/YYYY/MM/DD/hour-minute-second, and output the relative path
    """
    from datetime import datetime
    # Create directory

    def generate_parent_dir():
        today = datetime.utcnow()

        relative_path_dir_year = str(today.year)
        relative_path_dir_month = os.path.join(relative_path_dir_year, str(today.month))
        relative_path_dir_day = os.path.join(relative_path_dir_month, str(today.day))
        relative_path_dir_now = os.path.join(relative_path_dir_day, str(today.hour)+'-'+str(today.minute)+'-'+str(today.second))

        path_dir_year = os.path.join(base_dir, relative_path_dir_year)
        path_dir_month = os.path.join(base_dir, relative_path_dir_month)
        path_dir_day = os.path.join(base_dir, relative_path_dir_day)

        if not os.path.exists(path_dir_year):
            os.makedirs(path_dir_year)

        if not os.path.exists(path_dir_month):
            os.makedirs(path_dir_month)

        if not os.path.exists(path_dir_day):
            os.makedirs(path_dir_day)

        return relative_path_dir_now


    relative_path_dir_time = generate_parent_dir()

    while os.path.exists(os.path.join(base_data_dir, relative_path_dir_time)):
        relative_path_dir_time = generate_parent_dir()

    os.makedirs(os.path.join(base_data_dir, relative_path_dir_time))

    return relative_path_dir_time


base_data_dir = os.path.join(TOP_DIR, DATA_DIR)
relative_user_dir = create_user_dir(base_data_dir)

os.makedirs(os.path.join(base_data_dir, relative_user_dir, UPLOAD_DIR))
os.makedirs(os.path.join(base_data_dir, relative_user_dir, TEMP_RESULT_DIR))
os.makedirs(os.path.join(base_data_dir, relative_user_dir, OUTPUT_DIR))

# Create instance of FieldStorage, it can only be initiated once per request
form = cgi.FieldStorage()

# Get data from fields
delete_data = form.getvalue('delete_data')
if not delete_data:  # set default value
    delete_data = 'yes'
language1 = form.getvalue('language1')
language2 = form.getvalue('language2')
str_language1_bold = form.getvalue('language1_bold')
language1_bold = int(str_language1_bold)
str_language1_italic = form.getvalue('language1_italic')
language1_italic = int(str_language1_italic )
str_language2_bold = form.getvalue('language2_bold')
language2_bold  = int(str_language2_bold)
str_language2_italic = form.getvalue('language2_italic')
language2_italic = int(str_language2_italic)
str_eoi_eol = form.getvalue('eoi_eol')
eoi_eol = True if str_eoi_eol=="eol" else False
str_eoi_bold_to_unbold = form.getvalue('eoi_bold_to_unbold')
eoi_bold_to_unbold = True if str_eoi_bold_to_unbold=="bold_to_unbold" else False
str_eoi_unbold_to_bold = form.getvalue('eoi_unbold_to_bold')
eoi_unbold_to_bold = True if str_eoi_unbold_to_bold=="unbold_to_bold" else False
str_eoi_italic_to_unitalic = form.getvalue('eoi_italic_to_unitalic')
eoi_italic_to_unitalic = True if str_eoi_italic_to_unitalic=="italic_to_unitalic" else False
str_eoi_unitalic_to_italic = form.getvalue('eoi_unitalic_to_italic')
eoi_unitalic_to_italic = True if str_eoi_unitalic_to_italic=="unitalic_to_italic" else False

def save_uploaded_file(cgi_form, form_field, upload_dir, whitelist_ext):
    """This saves a file uploaded by an HTML form.
       The form_field is the name of the file input field from the form.
       For example, the following form_field would be "file_1":
           <input name="file_1" type="file">
       The upload_dir is the directory where the file will be written.
       The whitelist_ext is the set of allowed file extensions for uploading.
       If no file was uploaded or if the field does not exist then
       this does nothing.
    """
    if not cgi_form.has_key(form_field): return False
    file_item = cgi_form[form_field]
    if not file_item.file: return False
    # Strip leading path from file name to avoid
    # directory traversal attacks.
    # Replace \ by / to make sure compatibility with Windows path
    filename_base = os.path.basename(file_item.filename.replace("\\", "/"))
    mainname, extname = os.path.splitext(filename_base)  # mainname is '123.php.', extname is '.jpg'
    # Use white list of file type to be uploaded
    if not extname in whitelist_ext: return False
    # Replace non alpha numeric characters to _ for URL friendly
    mainname = re.sub('[^0-9a-zA-Z/]+', '_', mainname)
    # Replace . by _ to protect against double extension attacks which can activate PHP scripts
    filename_base = mainname.replace('.', '_') + extname
    file_path = os.path.join(upload_dir, filename_base)
    with open(file_path, 'wb') as outfile:
        shutil.copyfileobj(file_item.file, outfile)
        # outfile.write(file_item.file.read())
        # while 1:
        #     chunk = file_item.file.read(100000)
        #     if not chunk: break
        #     outfile.write (chunk)
    return filename_base

text_ext = set(['.docx', '.DOCX'])

white_list = set()
white_list = white_list.union(text_ext)

file_input_1 = save_uploaded_file(form, "upload1", os.path.join(TOP_DIR, DATA_DIR, relative_user_dir, UPLOAD_DIR), white_list)

if file_input_1:
    file_1_path = os.path.join(ABS_TOP_DIR, DATA_DIR, relative_user_dir, UPLOAD_DIR, file_input_1)
    csv_file_path = os.path.join(ABS_TOP_DIR, DATA_DIR, relative_user_dir, OUTPUT_DIR, file_input_1 + '.csv')
    xls_file_path = os.path.join(ABS_TOP_DIR, DATA_DIR, relative_user_dir, OUTPUT_DIR, file_input_1 + '.xls')
    url_file_1 = BASE_URL+'/'+DATA_DIR+'/'+relative_user_dir+'/'+UPLOAD_DIR+'/'+file_input_1
    url_file_csv = BASE_URL+'/'+DATA_DIR+'/'+relative_user_dir+'/'+UPLOAD_DIR+'/'+file_input_1 + '.csv'
    url_file_xls = BASE_URL+'/'+DATA_DIR+'/'+relative_user_dir+'/'+UPLOAD_DIR+'/'+file_input_1 + '.xls'
    message_file_1 = 'File 1: '+file_input_1+' was uploaded successfully.'
else:
    message_file_1 = 'File 1 is not an accepted file. It was not uploaded.'

proceed_flag = file_input_1

if proceed_flag:
    # Create key word arguments
    print 'enter proceed_flag'
    kwargs = {'group1_condition':{'bold':language1_bold, 'italic':language1_italic}, 'group2_condition':{'bold':language2_bold, 'italic':language2_italic}, 'eoi_eol':eoi_eol, 'eoi_bold_to_unbold':eoi_bold_to_unbold, 'eoi_unbold_to_bold':eoi_unbold_to_bold, 'eoi_italic_to_unitalic':eoi_italic_to_unitalic, 'eoi_unitalic_to_italic':eoi_unitalic_to_italic}
    
    # Parsing the DOCX file
    parse_docx.docx_to_csv(file_1_path, csv_file_path, **kwargs)
    
    # Add the header line to the CSV file, quick and dirty with delimiter='\t'
    csv_header = language1 + '\t' + language2 + '\n'
    with open(csv_file_path, 'rt') as csv_file:
        old_csv_text = csv_file.read()
    with open(csv_file_path, 'wt') as csv_file:
        csv_file.write(csv_header + old_csv_text)
    
    # Convert CSV to XLS for user to open in Excel
    Csv_Excel.csv_to_xls(csv_file_path, xls_file_path)

# Clean up
if not delete_data != 'yes':
    # os.system('rm -r ../data/uploads/*')
    os.system('rm -r '+TOP_DIR+'/'+DATA_DIR+'/'+relative_user_dir+'/'+UPLOAD_DIR+'/*')

# Output to the web
print "Content-type:text/html"
print ""
print "<html>"
print "<head>"
print "<title>Ket qua boc tach file van ban de tao ra bang song ngu</title>"
print "</head>"
print "<body>"
print "<h1>Results of parsing docx:</h1>"
print "<h2>%s</h2>" % (message_file_1)
if delete_data != 'yes' and file_input_1:
    print "<h2>Link to the uploaded DOCX file: <a href=\"%s\">%s</a></h2>" % (url_file_1, url_file_1)
if proceed_flag:
    print "<h2>Link to the result CSV file: <a href=\"%s\">%s</a></h2>" % (url_file_csv, url_file_csv)
    print "<h2>Result converted to XLS file: <a href=\"%s\">%s</a></h2>" % (url_file_xls, url_file_xls)
if not delete_data != 'yes':
    print "<h2>Data (except the result files) was deleted on the server.</h2>"
print "</body>"
print "</html>"
