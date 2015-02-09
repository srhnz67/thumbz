# thumbz

Create a 'contact sheet' style report on an image collection.
May need install/upgrade to latest Python Image Library (PIL) or Pillow (will work with either) 

Usage:
thumbz.py [-h] [-d Dir] [-o Filename] [-t Target] [-c Columns] [-r Report format] [-v]

optional arguments:
  -h, --help        show this help message and exit
  -d Dir            Image source target directory
  -o Filename       Output filename for the report
  -t Target         Image type to report - jpg[default], gif, png or all
  -c Columns        Number of columns [Default = 1, max = 3]
  -r Report format  Report output format - html, pdf, all
  -v                View html report in browser when finished [Optional]
  
  * Thumbnail scaling will be based on the number of columns requested + spaces between + margins.
  * Will insert a placeholder if a file with an image-like name is hit, but not a valid image.  This may happen if attempting to
      create a report directly from the output dir of a file carving tool.
  * Images will maintain aspect ratio, since thumbnail creation is based on scaling to the greater dimension of the source            image.
  
See code for additional comments
