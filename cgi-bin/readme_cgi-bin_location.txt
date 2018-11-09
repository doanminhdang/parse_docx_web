This cgi-bin folder needs to be put under ~/public_html/ in order to be executable on the web server.
Or better, make a symbolic link at the required location to point to the Python script in this folder: 
[~/public_html/cgi-bin]# ln -s ../parse_docx_web/cgi-bin/parse_docx_processing.py
so that there is only one version of this script, it is not confusing for maintaining the code.
