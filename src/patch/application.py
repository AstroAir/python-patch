"""
Patch application functionality.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""
import copy
import os
import shutil
from os.path import exists, isfile, abspath

from .compat import tostr
from .logging_utils import debug, info, warning, debugmode
from .utils import pathstrip


def diffstat(patchset):
    """calculate diffstat and return as a string
    Notes:
      - original diffstat ouputs target filename
      - single + or - shouldn't escape histogram
    """
    names = []
    insert = []
    delete = []
    delta = 0    # size change in bytes
    namelen = 0
    maxdiff = 0  # max number of changes for single file
                 # (for histogram width calculation)
    for patch in patchset.items:
        i, d = 0, 0
        for hunk in patch.hunks:
            for line in hunk.text:
                if line.startswith(b'+'):
                    i += 1
                    delta += len(line)-1
                elif line.startswith(b'-'):
                    d += 1
                    delta -= len(line)-1
        names.append(patch.target)
        insert.append(i)
        delete.append(d)
        namelen = max(namelen, len(patch.target))
        maxdiff = max(maxdiff, i+d)
    output = ''
    statlen = len(str(maxdiff))  # stats column width
    for i, n in enumerate(names):
        # %-19s | %-4d %s
        format = " %-" + str(namelen) + "s | %" + str(statlen) + "s %s\n"

        hist = ''
        # -- calculating histogram --
        width = len(format % ('', '', ''))
        histwidth = max(2, 80 - width)
        if maxdiff < histwidth:
            hist = "+"*insert[i] + "-"*delete[i]
        else:
            iratio = (float(insert[i]) / maxdiff) * histwidth
            dratio = (float(delete[i]) / maxdiff) * histwidth

            # make sure every entry gets at least one + or -
            iwidth = 1 if 0 < iratio < 1 else int(iratio)
            dwidth = 1 if 0 < dratio < 1 else int(dratio)
            #print(iratio, dratio, iwidth, dwidth, histwidth)
            hist = "+"*int(iwidth) + "-"*int(dwidth)
        # -- /calculating +- histogram --
        output += (format % (tostr(names[i]), str(insert[i] + delete[i]), hist))

    output += (" %d files changed, %d insertions(+), %d deletions(-), %+d bytes"
               % (len(names), sum(insert), sum(delete), delta))
    return output


def findfile(old, new):
    """return name of file to be patched or None"""
    # Handle None inputs
    if old is None or new is None:
        return None

    # Handle empty inputs
    if not old or not new:
        return None

    if exists(old):
        return old
    elif exists(new):
        return new
    else:
        # [w] Google Code generates broken patches with its online editor
        debug("broken patch from Google Code, stripping prefixes..")
        if old.startswith(b'a/') and new.startswith(b'b/'):
            old, new = old[2:], new[2:]
            debug("   %s" % old)
            debug("   %s" % new)
            if exists(old):
                return old
            elif exists(new):
                return new
        return None


def can_patch(patchset, filename):
    """Check if specified filename can be patched. Returns None if file can
    not be found among source filenames. False if patch can not be applied
    clearly. True otherwise.

    :returns: True, False or None
    """
    # Handle both bytes and string input
    if isinstance(filename, bytes):
        filename = filename.decode('utf-8')

    filename = abspath(filename)
    for p in patchset.items:
        # Handle both absolute and relative path matching
        source_path = p.source
        if isinstance(source_path, bytes):
            source_path = source_path.decode('utf-8')

        # Try absolute path comparison
        if filename == abspath(source_path):
            return match_file_hunks(filename, p.hunks)

        # Try basename comparison for relative paths
        import os
        if os.path.basename(filename) == os.path.basename(source_path):
            return match_file_hunks(filename, p.hunks)
    return None


def match_file_hunks(filepath, hunks):
    matched = True
    fp = open(abspath(filepath), 'rb')

    class NoMatch(Exception):
        pass

    lineno = 1
    line = fp.readline()
    hno = None
    try:
        for hno, h in enumerate(hunks):
            # skip to first line of the hunk
            while lineno < h.starttgt:
                if not len(line):  # eof
                    debug("check failed - premature eof before hunk: %d" % (hno+1))
                    raise NoMatch
                line = fp.readline()
                lineno += 1
            for hline in h.text:
                if hline.startswith(b"-"):
                    continue
                if not len(line):
                    debug("check failed - premature eof on hunk: %d" % (hno+1))
                    # todo: \ No newline at the end of file
                    raise NoMatch
                if line.rstrip(b"\r\n") != hline[1:].rstrip(b"\r\n"):
                    debug("file is not patched - failed hunk: %d" % (hno+1))
                    raise NoMatch
                line = fp.readline()
                lineno += 1

    except NoMatch:
        matched = False
        # todo: display failed hunk, i.e. expected/found

    fp.close()
    return matched


def patch_stream(instream, hunks):
    """Generator that yields stream patched with hunks iterable
    
    Converts lineends in hunk lines to the best suitable format
    autodetected from input
    """

    # todo: At the moment substituted lineends may not be the same
    #       at the start and at the end of patching. Also issue a
    #       warning/throw about mixed lineends (is it really needed?)

    hunks = iter(hunks)

    srclineno = 1

    lineends = {b'\n': 0, b'\r\n': 0, b'\r': 0}
    def get_line():
        """
        local utility function - return line from source stream
        collecting line end statistics on the way
        """
        line = instream.readline()
        # 'U' mode works only with text files
        if line.endswith(b"\r\n"):
            lineends[b"\r\n"] += 1
        elif line.endswith(b"\n"):
            lineends[b"\n"] += 1
        elif line.endswith(b"\r"):
            lineends[b"\r"] += 1
        return line

    for hno, h in enumerate(hunks):
        debug("hunk %d" % (hno+1))
        # skip to line just before hunk starts
        while srclineno < h.startsrc:
            yield get_line()
            srclineno += 1

        for hline in h.text:
            # todo: check \ No newline at the end of file
            if hline.startswith(b"-") or hline.startswith(b"\\"):
                get_line()
                srclineno += 1
                continue
            else:
                if not hline.startswith(b"+"):
                    get_line()
                    srclineno += 1
                line2write = hline[1:]
                # detect if line ends are consistent in source file
                if sum([bool(lineends[x]) for x in lineends]) == 1:
                    newline = [x for x in lineends if lineends[x] != 0][0]
                    yield line2write.rstrip(b"\r\n")+newline
                else:  # newlines are mixed
                    yield line2write

    for line in instream:
        yield line


def write_hunks(srcname, tgtname, hunks):
    src = open(srcname, "rb")
    tgt = open(tgtname, "wb")

    debug("processing target file %s" % tgtname)

    tgt.writelines(patch_stream(src, hunks))

    tgt.close()
    src.close()
    # [ ] TODO: add test for permission copy
    shutil.copymode(srcname, tgtname)
    return True


def reverse_patchset(patchset):
    """reverse patch direction (this doesn't touch filenames)"""
    for p in patchset.items:
        for h in p.hunks:
            h.startsrc, h.starttgt = h.starttgt, h.startsrc
            h.linessrc, h.linestgt = h.linestgt, h.linessrc
            for i, line in enumerate(h.text):
                # need to use line[0:1] here, because line[0]
                # returns int instead of bytes on Python 3
                if line[0:1] == b'+':
                    h.text[i] = b'-' + line[1:]
                elif line[0:1] == b'-':
                    h.text[i] = b'+' + line[1:]


def dump_patchset(patchset):
    for p in patchset.items:
        for headline in p.header:
            print(headline.rstrip(b'\n').decode('utf-8', errors='replace'))
        print('--- ' + p.source.decode('utf-8', errors='replace'))
        print('+++ ' + p.target.decode('utf-8', errors='replace'))
        for h in p.hunks:
            print('@@ -%s,%s +%s,%s @@' % (h.startsrc, h.linessrc, h.starttgt, h.linestgt))
            for line in h.text:
                print(line.rstrip(b'\n').decode('utf-8', errors='replace'))
