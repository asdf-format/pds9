
Python implementation for ds9 support for ASDF files
====================================================

Requirements:

* The latest ds9 version (8.7)
* Astropy
* ds9samp
* numpy
* asdf

Installation instructions
=========================

This set of instructions will create an alternate version of ds9 that supports asdf.

# Install pds9::

  pip install git+https://github.com/asdf-format/pds9

# Generate the startup file's contents::

  pds9-config -p > ~/.ds9.ini

> [!NOTE]
> This will overwrite the contents in ~/.ds9.ini. If you already use this file consider
> appending to the existing file.

# Run ds9::

Start ds9 via the command line:

  /path/to/ds9/ds9

or start the installed app.


For convenience, you may add that path to the environmental
PATH (if not already added) or create an alias.

When you start ds9, you will see a new item on the file button
row at the end with the label "asdf".

Loading ASDF files
==================

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
details. This image is located at the various ASDF
internal locations:

* images
* moredata.images[2] for indices of 0-3
* moredata.deepstuff.moredata.images[1] for indices 0-3
