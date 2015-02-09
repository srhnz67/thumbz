#!/usr/bin/python

# Imports - Standard modules in Python
import sys, os, io
try:
	from PIL import Image, ImageFile
	import base64, glob, argparse, webbrowser, time, Tkinter, hashlib
	from reportlab.pdfgen import canvas
except ImportError as e:
	print "\nError importing required modules:\n" + str(e)
	sys.exit(1)

# define some vars
iname = ""
rname = ""
rview = ""
f = 0

def usage(errMsg):
	print errMsg
	print "\nusage: " + sys.argv[0] + " [-h] [-d] [-o O] [-c C] [-t T] [-v]\n"
	sys.exit(1)

#def ihash(fname):
#	print fname
#	ihash = hashlib.md5(open(fname).read()).hexdigest()
#	return ihash

# Process commandline arguments
argsp = argparse.ArgumentParser()
argsp.add_argument('-d', help='Image source target directory', metavar='Dir')
argsp.add_argument('-o', help='Output filename for the report', metavar='Filename')
argsp.add_argument('-t', default='jpg', help='Image type to report - jpg[default], gif, png or all',metavar='Target')
argsp.add_argument('-c', default='1', help='Number of columns [Default = 1, max = 3]',metavar='Columns')
argsp.add_argument('-r', help='Report output format - html, pdf, all',metavar='Report format')
argsp.add_argument('-v', action='store_true', help='View html report in browser when finished [Optional]')
args = argsp.parse_args()

# Do we have everything we need for a run?
if args.d:
	iname = args.d
else:
	usage("Needs input directory")

if  args.o:
	rname = args.o
else:
	usage("Missing report filename")
if args.v == "": rview = '1'

# Adjust col count if > 3
if int(args.c) > 3:
	print "\n" + str(args.c) + " columns requested, adjusting col count back to 3[maximum]\n"
	cols = 3
else:
	cols = int(args.c)

# Are we able to write the report to the target dir?
try:
	fout = open(rname + ".htm","w")
except IOError as err:
	print "Unable to write to the destination\nError Description: " + str(err) + "\n"
	sys.exit(1)

# Go to the dir with the image collection
try:
	os.chdir(iname)
except IOError as err:
	print "There is a problem accessing the source directory\nError Description: " + str(err) + "\n"
	sys.exit(1)

# Get a list of the target image types
if args.t == 'gif':
	ilist = glob.glob("*.gif")
elif args.t == 'png':
	ilist = glob.glob("*.png")
elif args.t == 'all':
	ilist = glob.glob("*.jpg") + glob.glob("*.gif") + glob.glob("*.png")
else:
	ilist = glob.glob("*.jpg")

if len(ilist) == 0:
	print "ERROR:\tThere are no images of that type in \"" + iname + "\"\n"
	sys.exit(1)

        #size = sz,sz


# Process the image list and create output files
# HTML generator
if args.r == 'htm' or args.r == 'all':
	# Set thumbnail width based off screen width
	q = Tkinter.Tk()
	sz = (q.winfo_screenwidth()/cols)
	sz = int(round(sz,1))
	# Begin writing HTML
	rptOut = "<html><head></head><body><table border='1'><tr>"
	while f < len(ilist):
		# For every row
		for x in range(0,int(cols)):
			try:
				img = Image.open(ilist[f])
				fExt = img.format
				fSize = img.size
				img.thumbnail((sz,sz))
				oData = io.BytesIO()
				img.save(oData, format=fExt)
				hex_data = oData.getvalue()
				# Convert thumbnail binary data to base64 to create standalone HTML page
				rptOut += "<td><img src='data:image/" + fExt + ";base64," + base64.b64encode(hex_data) + "'>"
				# Add some file info
				rptOut += "<br>FileName: " + ilist[f] + "<br>Original Size:  " + str(fSize[0]) + " x " + str(fSize[1]) 
				rptOut += "</td>" + "\n"
				f += 1
			except IndexError:
				break
			except IOError as e:
			#	Found mis-named or corrupt file
				print "\nWARNING: \"" + ilist[f] + "\" is not a valid image file - Skipped"
				rptOut += "<td><font color='maroon'>Invalid Image Data - Skipped</font><br>FileName: " + ilist[f]
	       	        	rptOut += "</td>" + "\n"
				f += 1
		rptOut += "</tr>"
	# Finish off the page code
	rptOut += "</table></body></html>"
	fout.write(rptOut)
	fout.close()

	if rview == '1':
		webbrowser.open_new_tab(rname + ".htm")
	print '\nDone\nReport \"' + rname + '.htm\" can be found in ' + iname + '\n'

# PDF generator
if args.r == 'pdf' or args.r == 'all':
	# Set some static numbers
	margin = 50
	padding = 20	
	# Set page width/height to standard A4
	# US Letter = 612 x 792
	# A4 = 595 x 841
        pwidth = 595
        pheight = 841
	fontHeight = 16 # includes gap between lines, actual is 13

	# Work out correct thumbnail size to meet column number,
	# then use that value to set thumbnail size
        sz = ((pwidth-(margin))/cols)-padding

	# Set origin point for first image
	# Set counter for image list loop
        x = margin
        y = pheight - sz - (margin * 1.5)
        f = 0

	c = canvas.Canvas(rname + ".pdf", bottomup=1)
	pg = 1

	while f < len(ilist):
		# Start processing rows
	        for i in range(0,int(cols)):
			try:
				img = Image.open(ilist[f])
				fExt = img.format
				fSize = img.size
				# fhash = ihash(ilist[f])
				img.thumbnail((sz,sz))
				img.save('imgTemp-' + str(f), format=fExt)
				c.drawImage('imgTemp-' + str(f), x, y + padding, width=sz, height=sz, preserveAspectRatio=True)
				os.remove('imgTemp-'+str(f))
                                # Create the image caption
				c.drawString(x, y - fontHeight,"Filename: " + ilist[f][:sz/10] + "~")
				c.drawString(x, y - (fontHeight * 2),"Original Size: " + str(fSize[0]) + " x " + str(fSize[1]))
				# c.drawString(x, y - (fontHeight * 3),"MD5: " + fhash.upper())
				x = x + (sz + padding)
				f += 1
			except IndexError:
				break
			except IOError: # Indicates mis-named file
				# Add placeholder for non-image
				c.setFillColorRGB(0.5,0,0)
				c.rect(x,y,sz,sz,fill=0)
				print "\nWARNING: \"" + ilist[f] + "\" is not a valid image file - Skipped"
				c.drawString(x + 5, y + (sz/2),"Filename: " + ilist[f][:sz/10])
				c.drawString(x + 5, y + (sz/2) + fontHeight,"Invalid Image Data")
				c.setFillColorRGB(0,0,0)
				x = x + (sz + padding)
				i += 1
				f += 1
		# New row - Set start point for next row
		x = margin
		y = y - (sz + round(fontHeight * 2.5,1) + margin)
		#Do we have enough space for another row incl text?
		if y <= (margin*2):
			# If not, create a new page and reset x,y values
			if f < len(ilist):
				c.drawString(pwidth/2,fontHeight+(margin/3),"Page No." + str(pg))
				c.showPage()
				pg += 1
				x = margin
        			y = pheight - sz - (margin * 1.5)
	# Finished processing, summarise and write file
	c.drawString(pwidth/2,margin / 3 + (fontHeight * 2),"End of images, Page " + str(pg) + " of " + str(pg))
	c.drawString(pwidth/2,margin / 3 + fontHeight,"File generated: " + (time.strftime('%d/%m/%Y %H:%M:%S')))
	c.save(author='Bob')
	print '\nPDF Report \"' + rname + '.pdf\" can be found in ' + iname + '\n'

alist = ['all','htm','pdf']
if args.r not in alist:
	usage("\nWell...since you didn't specify a valid report output format (all, htm or pdf),\nthat was a bit of a waste of time...wasn't it?\n")
