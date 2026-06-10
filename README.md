# pds9
Python implementation for ds9 support for ASDF files

Requirements:

* The latest ds9 version (8.7)
* Astropy
* ds9samp
* numpy
* asdf

Installation instructions

This very early version requires more manual steps than will eventually be required (hopfully just a simple pip install 
aside from the usual ds9 install)

There are two options for installing the modifications to allow
ds9 to load ASDF images.

Since this is an early version I recommend creating an alternate
ds9 command so as not to interfere with the behavior of the 
standard ds9 installation. This is fairly easy to do.

Instructions for alternate ds9 executable

First you must located where the ds9 executable is located. On MacOS, that is likely /Applications/SAOImageDS9.app/Contents/MacOS 
The executable is named ds9. Make a symbolic link to the executable 
with:

ln -s /Applications/SAOImageDS9.app/Contents/MacOS/ds9
      /Applications/SAOImageDS9.app/Contents/MacOS/ads9

It is useful to put the link in the same directory. You can create an alias to that new executable or include that path in PATH.

Then copy ds9.ini to the home directory as .ads9.ini (the name of
the root part of the ini file must be the same as that of
the executable with a period prepended).

Also copy fromds9.py to the same directory.

If you don't care about changing the behavior of the original
ds9. There is no need to create the link, and instead copy
ds9.ini to the home directory as .ds9.ini

When you start ads9 (or ds9 if no link is used), you will
see a new item on the file button row at the end with the
label "asdf" (Due to some odd behavior, one does not see
the top button row until the ds9 window is clicked somewhere
in the window; this oddity will be fixed in the future)r.

Loading ASDF files.

The initial user interface is quite basic. By clicking the asdf
button, that will open a new, persistent dialog window, that
will require closing the window specifically when stopping ds9. 
In the future, we will have the asdf dialog quit if the
corresponding ds9 window is closed.

This preliminary version assumes only one instance of
ds9 is running.

This version uses a simple text entry box to specify both
the path to the ASDF file, as well as the location of
the image within the ASDF file. The help button will 
display the details of how these two are combined.

The associated data file provided in the data subdirectory
contains the same image (M51 as used long ago as a sample
image for IRAF). References to the same image are located 
in a number of different locations in the ASDF tree. 
Details of how to specify both paths are given in the 
help dialog obtained by clicking the help button on the 
ASDF dialog window. Currently the load button must be
clicked to load the image (it does not yet trigger on use
of <enter> in the text entry field).

Currently no attempt is made to load one of the images
by default (that will change in the future). The image
will need a change to the stretch to see the fainter 
details. This image is located at the various ADSF
internal locations:

* images
* moredata.images[2] for indices of 0-3
* moredata.deepstuff.moredata.images[1] for indices 0-3
