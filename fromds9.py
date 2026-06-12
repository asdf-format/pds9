import sys
import os
import os.path
import pathlib
import numpy as np
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as filedialog
import asdf
from asdf.tagged import TaggedDict, TaggedList
from asdf.yamlutil import tagged_tree_to_custom_tree
import ds9samp

DS9TMP = None 

FILEPATH_DOC = """

How to specify ASDF images for DS9

The first part of specifying an ADSF image is to specify
the path to an ASDF file, as one might expect. This can
be an absolute path or a path relative to the current
directory that ds9 has (normally the directory that ds9
was started from).

That alone isn't sufficient since there is not a standard
place within the file that the image may be located. (We 
intend to provide mechanisms for presuming default
locations for variousdata types, but these do not exist
yet). Thus currently it is required to specify the
location of the image to be displayed.

Since the ASDF file is generally a tree structure, this
involves specifying the path from the base of the tree
to the image. There are two types of specifications, by
attribute name, or by an integer index depending on the
type of the nested structure (e.g., whether it is of a
dictionary type, or a list). The attribute names
(or keys, if you wish) are separated by periods.
Indices into lists use square brackets, i.e., '[]' and
do not need periods when adjacent to any other path
specifier, whether index or attribute.

So supposing the file is in the directory above the
default for ds9, then a more complex example would be:

../mydata.asdf:detector1.data.timeseries[7]image

Note the ':' separator between the file path and the
ADSF path.

Because ds9 uses square brackets as part of its mechanism
to load array data, the temporary file created replaces
the square brackets with parentheses when displayed in
its info section for the filename.

Once the file text entry box has a value, and it 
corresponds to an existing file, the "Browse for 
Image" button can be used to list all arrays of dimension
two or greater in the file, selecting one and pushing
the load button will append the ASDF object path to the
file/path specification and load the image. 
"""

def create_ds9_tmp_dir():
    """
    Currently generates a ds9tmp directory in user's home directory
    if one doesn't already exist
    """
    global DS9TMP
    if DS9TMP is not None:
        return
    homedir = pathlib.Path.home()
    DS9TMP = homedir / "ds9tmp"
    DS9TMP.mkdir(exist_ok=True)

def create_ds9_tmpfile_name(asdf_full_path):
    """
    First delete any files in the ds9tmp directory, then return a handle
    to a new writable binary file.
    """
    # If the global is None, either this is the first call during this 
    # session, in which case if the directory already exists, the 
    # global will be set, if not, the directory will be created.
    if DS9TMP is None:
        create_ds9_tmp_dir()
    # Delete any existing files.
    for filepath in DS9TMP.glob("*"):
        if filepath.is_file():
            filepath.unlink()
    # Remove any directories in the supplied asdf_full_path
    dummy, asdf_truncated_full_path = os.path.split(asdf_full_path)  
    fn = str((DS9TMP / asdf_truncated_full_path).resolve())
    # Replace square brackets with curly brackets since they will confuse ds9
    fn = fn.replace('[', '(')
    fn = fn.replace(']', ')')

    return fn

def asdf_send_array(
        self,
        img: np.ndarray,
        filename,
        *,
        # cube: Cube | None = None,
        # mask: bool = False,
        timeout: int | None = None,
    ) -> None:
        """Send the array to DS9.

        This creates a temporary file to store the data,
        sends the data, and then deletes the file.

        This version is based on whe ds9samp method of the same name with
        changes to how temporary files are named and where they are stored.

        The created file is not deleted until this method is called again. 
        In prinicple, there will one file remaining in the directory, to
        simplify the initial version of this code.

        Files currently are stored in the ds9tmp subdirectory of the user's
        home directory.

        """
        dbf = open('xxx.txt', 'w')
        print(filename, file=dbf)
        print(DS9TMP, file=dbf)
        dbf.close()

        # Map between NumPy and DS9 storage fields.
        #
        # Hack in support for bool values
        if img.dtype.type == np.bool_:
            img = img.astype("int8")

        arr = ds9samp.np_to_array(img)

        # # Validate the cube argument when given.
        # #
        action = ""
        # if cube is not None:
        #     if img.ndim != 3:
        #         raise ValueError("data must be 3D to set the cube argument")
        #     if img.shape[0] != 3:
        #         raise ValueError(
        #             "z axis must have size 3 when cube argument is set"
        #         )

        #     match cube:
        #         case Cube.RGB:
        #             action = "rgb"
        #         case Cube.HLS:
        #             action = "hls"
        #         case Cube.HSV:
        #             action = "hsv"

        #         case _:
        #             raise ValueError(f"Invalid argument: cube={cube}")

        # Create a frame if necessary, since otherwise the ARRAY call
        # will fail.
        #
        if self.get("frame active") is None:
            self.set("frame new")

        # with tempfile.NamedTemporaryFile(prefix="ds9samp", suffix=".arr") as fh:
        ##with open(create_ds9_tmpfile(filename), 'wb')  as fh:
        
        tmp_filename = create_ds9_tmpfile_name(filename)
        fp = np.memmap(tmp_filename, mode="w+", dtype=img.dtype, shape=img.shape)
        fp[:] = img
        fp.flush()

        #     # If given a RGB/HLS/HSV cube then create a frame. We
        #     # could try and check if we have one already, but it's not
        #     # clear how to do this, so always create it. If a user
        #     # wants to re-use the frame then they can try and do this
        #     # manually (probably by creating a FITS file and loading
        #     # that?).
        #     #
        #     if action != "":
        #         self.set(action, timeout=timeout)

        #     # Should this over-ride the filename as it is going to be
        #     # invalid as soon as this call ends? I am not sure that it
        #     # is possible.
        #     #
        cmd = f"{action}array "
        #     if mask:
        #         cmd += "mask "
        cmd += f" {tmp_filename}{arr}"
        self.set(cmd, timeout=timeout)



def parse_filename(filename):
    """
    Separate the filename into two major parts:
    First being the filename itself
    Second being a list of tuples, 
    Each tuple consisting of a itemtype and value pair.
    The item type indicates whether the value is a dict key (attribute)
    or index into a list
    The expected syntax is that the filename is separated from the 
    ASDF path with a colon.
    The asdf path uses '.' as a separator between keys and uses [<number>] 
    to identify list indices.
    The tree attribute is considered implicit.
    Example of a filename input:
    /Users/bozo/data/mydata.asdf:level1.level2[4].image.sci
    """
    fn, apath = filename.split(':')
    # Parse asdf path (assumes no use of these special characters as part of 
    # the attrbutes)
    # Prepend  '.' if it doesn't start with '['
    if apath[0] != '[':
        apath = '.' + apath
    alist = []
    finished = False
    while not finished:
        if apath[0] == '[':  # index case
            endind = apath[1:].find(']')
            if endind < 0:
                messagebox.showerror("Path Syntax Error", "matching end of index ']' not found")
                return
            else:
                indexstr = apath[1:endind+1]
                try:
                    index = int(indexstr)
                except ValueError:
                    messagebox.showerror("Path Syntax Error", f"Index must be an integer instead of {indexstr}")
                    return
            alist.append(('i', index))
            apath = apath[endind+2:]
        elif apath[0] == '.':  # attribute case
            nextperiod = apath[1:].find('.')
            nextbracket = apath[1:].find('[')
            end = len(apath[1:])
            if nextperiod > 0 and nextbracket > 0:
                attend = min(nextperiod, nextbracket)
            elif nextperiod > 0:
                attend = nextperiod
            elif nextbracket > 0:
                attend = nextbracket
            else:
                attend = end
            attr = apath[1:attend+1]
            apath = apath[attend+1:]
            if len(apath) == 0:
                finished = True
            alist.append(('a', attr))
        else:
            messagebox.showerror("Path Syntax Error", "Expected path delimiters: '.'' or '[' not found")
            return
        if len(apath) == 0:
            finished = True
    fd = open('parse.txt','w')
    fd.close()
    return fn, alist

def get_asdf_image(asdfpath):
    print(asdfpath)
    retval = parse_filename(asdfpath)
    if retval is not None:
        fn, alist = retval
    else:
        return
    # Must load in raw format to make the entire structure easily searchable
    try:
        af = asdf.open(fn, _force_raw_types=True)
    except FileNotFoundError:
        messagebox.showerror("File not Found", f"File {fn} not found")
        return None
    # Extract the referenced array
    node = af.tree
    return extract_asdf_array(node, alist, af)

def extract_asdf_array(tree, apath, ctx):
    """
    Given an asdf tree instance, follow the path to the array item,
    convert it into an array and return the array instance.
    """
    node = tree
    for ptype, value in apath:
        if ptype == 'a':
            try:
                if type(node) == TaggedDict:
                    node = node.data[value]
                else:
                    node = node[value]
            except KeyError:
                messagebox.showerror("ASDF Path Error", f"Specified ADSF path component '{value}' not in file")
                return
        elif ptype == 'i':
            try:
                if type(node) == TaggedList:
                    node = node.data[value]
                else:
                    node = node[value]
            except KeyError:
                messagebox.showerror("ASDF Path Error", f"Specified ASDF index component '{value}' not in file")
                return
    if not node._tag.startswith('tag:stsci.edu:asdf/core/ndarray-'):
        messagebox.showerror("Given ADSF path does not correspond to an array")
        return
    arr = tagged_tree_to_custom_tree(node, ctx)._make_array()
    return arr

def callsearch(pathlist, nodeitem, index, ctx, path, min_nelements):
    spath = path.copy()
    spath.append(index)
    sresult = search_tree(nodeitem[index], ctx, spath, min_nelements)
    if sresult is not None:
        if isinstance(sresult, dict):
            pathlist.append(sresult)
        else:
            pathlist += sresult

def search_tree(tree, ctx, path=None, min_nelements=1000):
    """
    Walk through the tree recursively to find all images and their associated paths
    """
    if path is None:
        path = []
    pathlist = []
    if isinstance(tree, TaggedDict):
        if tree._tag.startswith('tag:stsci.edu:asdf/core/ndarray-'):
            # Convert and check for size
            lazyim = tagged_tree_to_custom_tree(tree, ctx)
            if len(lazyim.shape) < 2:
                return None
            nelements = np.prod(lazyim.shape)
            if nelements < min_nelements:
                return None
            if lazyim.dtype is complex:
                return None
            iminfo = (lazyim.dtype, lazyim.shape)
            return {'path': path, 'iminfo': iminfo}
        else:
            for key in tree.data.keys():
                callsearch(pathlist, tree.data, key, ctx, path, min_nelements)
    elif isinstance(tree, TaggedList):
        for i, item in enumerate(tree.data):
            callsearch(pathlist, tree.data, i, ctx, path, min_nelements)
    elif isinstance(tree, dict):
        for key in tree.keys():
            callsearch(pathlist, tree, key, ctx, path, min_nelements)
    elif isinstance(tree, list):
        for i, item in enumerate(tree):
            callsearch(pathlist, tree, i, ctx, path, min_nelements)
    if pathlist:
        return pathlist
    else:
        return None

def process_path_lists(pathlists):
    """
    Generate a simple list of text paths useful for ds9 and a corresponding
    list of image info as single strings.
    """
    paths =[]
    shapes = []
    for item in pathlists:
        path, imshape = convert_path_list(item)
        paths.append(path)
        shapes.append(imshape)
    return paths, shapes

def convert_path_list(pathlist):
    """
    Generate a text path useful for ds9 and a corresponding image description 
    string.
    """
    plist = pathlist['path']
    iminfo = pathlist['iminfo']
    path = ''
    for item in plist:
        if type(item) == type(1):
            path += f"[{item}]"
        else:
            if not path or path[-1] == ']':
                path += item
            else:
                path += f".{item}"
    imshape = str(iminfo[1])
    return path, imshape

class AsdfEvents:

    def __init__(self, root):
        self.root = root
        self.imbrow = None
        self.imlist = None
        self.impaths = None
        self.imshapes = None
        self.af = None
        self.ds9 = ds9samp.start()
        self.ds9.send_array = asdf_send_array.__get__(self.ds9, ds9samp.Connection)
        tk.Label(root, text="asdf filename").grid(row=1)        
        self.entry = tk.Entry(root)
        self.entry.grid(row=1, column=1)
        self.entry.bind('<Return>', self.load_entry_field)
        tk.Button(root, text="quit", command=root.quit).grid(row=2, column=0,
                                                              sticky=tk.W, pady=4)
        tk.Button(root, text="load", command=self.load_entry_field).grid(row=2, column=1,
                                                                           sticky=tk.W, pady=4)
        tk.Button(root, text="Help", command=self.show_filename_help).grid(row=2, column=2,
                                                                           sticky=tk.W, pady=4)
        tk.Button(root, text="Browse for ASDF file", command=self.browse_filename).grid(row=0, column=0,
                                                                           sticky=tk.W, pady=4)
        self.browse_image_button = tk.Button(root, text="Browse for Image", command=self.browse_image)
        self.browse_image_button.grid(row=0, column=1, sticky=tk.W, pady=4)
        self.browse_image_button.config(state=tk.DISABLED)
    
    def load_entry_field(self, event=None):

        filepath = self.entry.get()
        print(filepath)
        if filepath:
            self.browse_image_button.config(state=tk.NORMAL)
        else:
            self.browse_image_button.config(state=tk.DISABLED)
            return
        if ':' in filepath:
            # print("filename: %s" % filepath)
            im = get_asdf_image(filepath)
            if im is None:
                return
        else:
            return
        self.ds9.send_array(im, filepath)

    def show_filename_help(self):
        messagebox.showinfo(title="Filename/Image Path Info", message=FILEPATH_DOC)

    def browse_filename(self):
        filename = filedialog.askopenfilename()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, filename)
        self.browse_image_button.config(state=tk.NORMAL)

    def browse_image(self):
        filename = self.entry.get()
        # Discard the image path if it exists
        filename = filename.split(':')[0]
        with asdf.open(filename, _force_raw_types=True) as af:
            self.af = af
            pathlists = search_tree(af.tree, af)
            imbrow = tk.Toplevel(self.root)
            imbrow.wm_title("ASDF Image Browser")
            imlist = tk.Listbox(imbrow, width=60, height=20)
            imlist.pack(side="top", fill="both", expand=True, padx=10, pady=10)
            button_load = tk.Button(imbrow, text="Load Image", command=self.load_selected_image)
            button_load.pack()
            self.imbrow = imbrow
            self.imlist = imlist
            impaths, imshapes = process_path_lists(pathlists)
            self.impaths = impaths
            self.imshapes = imshapes
            imdescs = ['  '.join((impath, str(imshape))) for impath, imshape in zip(impaths, imshapes)]
            for imdesc in imdescs:
                imlist.insert(tk.END, imdesc)
            
    def load_selected_image(self):
        impathindex = self.imlist.curselection()[0]
        impath = self.impaths[impathindex]
        # Construct new file/imagepath string
        filepath = self.entry.get()
        if ':' in filepath:
            filepath = filepath.split(':')[0]
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{filepath}:{impath}")
        print(self.entry.get())
        self.imbrow.destroy()
        self.load_entry_field()
        



def bring_to_front(window):
    window.attributes('-topmost', True)
    window.update_idletasks()  # Ensure window is rendered
    window.attributes('-topmost', False)
    window.focus_force()

root = tk.Tk()
root.title("ASDF File Access")
root.lift()
bring_to_front(root)
asdfevents = AsdfEvents(root)
root.mainloop()

