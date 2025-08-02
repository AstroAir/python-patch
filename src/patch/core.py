"""
Core classes for patch parsing and application.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""
from __future__ import print_function

import copy
import os
import re
import shutil
from os.path import exists, isfile, abspath

from .compat import compat_next, tostr
from .constants import DIFF, PLAIN, GIT, HG, MERCURIAL, SVN, SUBVERSION, MIXED
from .logging_utils import debug, info, warning, debugmode
from .utils import xisabs, xnormpath, xstrip, pathstrip
from .parser import wrapumerate, detect_type, normalize_filenames
from .application import (diffstat, findfile, can_patch, match_file_hunks,
                         patch_stream, write_hunks, reverse_patchset, dump_patchset)


class Hunk(object):
    """Parsed hunk data container (hunk starts with @@ -R +R @@)"""

    def __init__(self):
        self.startsrc = None  #: line count starts with 1
        self.linessrc = None
        self.starttgt = None
        self.linestgt = None
        self.invalid = False
        self.desc = ''
        self.text = []

#  def apply(self, estream):
#    """ write hunk data into enumerable stream
#        return strings one by one until hunk is
#        over
#
#        enumerable stream are tuples (lineno, line)
#        where lineno starts with 0
#    """
#    pass


class Patch(object):
    """Patch for a single file.
    If used as an iterable, returns hunks.
    """
    def __init__(self):
        self.source = None
        self.target = None
        self.hunks = []
        self.hunkends = []
        self.header = []

        self.type = None

    def __iter__(self):
        for h in self.hunks:
            yield h


class PatchSet(object):
    """PatchSet is a patch parser and container.
    When used as an iterable, returns patches.
    """

    def __init__(self, stream=None):
        # --- API accessible fields ---

        # name of the PatchSet (filename or ...)
        self.name = None
        # patch set type - one of constants
        self.type = None

        # list of Patch objects
        self.items = []

        self.errors = 0    # fatal parsing errors
        self.warnings = 0  # non-critical warnings
        # --- /API ---

        if stream:
            self.parse(stream)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        for i in self.items:
            yield i

    def parse(self, stream):
        """parse unified diff
        return True on success
        """
        lineends = dict(lf=0, crlf=0, cr=0)
        nexthunkno = 0    #: even if index starts with 0 user messages number hunks from 1

        p = None
        hunk = None
        # hunkactual variable is used to calculate hunk lines for comparison
        hunkactual = dict(linessrc=None, linestgt=None)

        # define states (possible file regions) that direct parse flow
        headscan = True  # start with scanning header
        filenames = False  # lines starting with --- and +++

        hunkhead = False  # @@ -R +R @@ sequence
        hunkbody = False  #
        hunkskip = False  # skipping invalid hunk mode

        hunkparsed = False  # state after successfully parsed hunk

        # regexp to match start of hunk, used groups - 1,3,4,6
        re_hunk_start = re.compile(br"^@@ -(\d+)(,(\d+))? \+(\d+)(,(\d+))? @@")

        self.errors = 0
        # temp buffers for header and filenames info
        header = []
        srcname = None
        tgtname = None

        # start of main cycle
        # each parsing block already has line available in fe.line
        fe = wrapumerate(stream)
        while fe.next():

            # -- deciders: these only switch state to decide who should process
            # --           line fetched at the start of this cycle
            if hunkparsed:
                hunkparsed = False
                if re_hunk_start.match(fe.line):
                    hunkhead = True
                elif fe.line.startswith(b"--- "):
                    filenames = True
                else:
                    headscan = True
            # -- ------------------------------------

            # read out header
            if headscan:
                while not fe.is_empty and not fe.line.startswith(b"--- "):
                    header.append(fe.line)
                    fe.next()
                if fe.is_empty:
                    if p == None:
                        debug("no patch data found")  # error is shown later
                        self.errors += 1
                    else:
                        info("%d unparsed bytes left at the end of stream" % len(b''.join(header)))
                        self.warnings += 1
                        # TODO check for \No new line at the end..
                        # TODO test for unparsed bytes
                        # otherwise error += 1
                    # this is actually a loop exit
                    continue

                headscan = False
                # switch to filenames state
                filenames = True

            line = fe.line
            lineno = fe.lineno

            # hunkskip and hunkbody code skipped until definition of hunkhead is parsed
            if hunkbody:
                # [x] treat empty lines inside hunks as containing single space
                #     (this happens when diff is saved by copy/pasting to editor
                #      that strips trailing whitespace)
                if line.strip(b"\r\n") == b"":
                    debug("expanding empty line in a middle of hunk body")
                    self.warnings += 1
                    line = b' ' + line

                # process line first
                if re.match(b"^[- \\+\\\\]", line):
                    # gather stats about line endings
                    if line.endswith(b"\r\n"):
                        p.hunkends["crlf"] += 1
                    elif line.endswith(b"\n"):
                        p.hunkends["lf"] += 1
                    elif line.endswith(b"\r"):
                        p.hunkends["cr"] += 1

                    if line.startswith(b"-"):
                        hunkactual["linessrc"] += 1
                    elif line.startswith(b"+"):
                        hunkactual["linestgt"] += 1
                    elif not line.startswith(b"\\"):
                        hunkactual["linessrc"] += 1
                        hunkactual["linestgt"] += 1
                    hunk.text.append(line)
                    # todo: handle \ No newline cases
                else:
                    warning("invalid hunk no.%d at %d for target file %s" % (nexthunkno, lineno+1, p.target))
                    # add hunk status node
                    hunk.invalid = True
                    p.hunks.append(hunk)
                    self.errors += 1
                    # switch to hunkskip state
                    hunkbody = False
                    hunkskip = True

                # check exit conditions
                if hunkactual["linessrc"] > hunk.linessrc or hunkactual["linestgt"] > hunk.linestgt:
                    warning("extra lines for hunk no.%d at %d for target %s" % (nexthunkno, lineno+1, p.target))
                    # add hunk status node
                    hunk.invalid = True
                    p.hunks.append(hunk)
                    self.errors += 1
                    # switch to hunkskip state
                    hunkbody = False
                    hunkskip = True
                elif hunk.linessrc == hunkactual["linessrc"] and hunk.linestgt == hunkactual["linestgt"]:
                    # hunk parsed successfully
                    p.hunks.append(hunk)
                    # switch to hunkparsed state
                    hunkbody = False
                    hunkparsed = True

                    # detect mixed window/unix line ends
                    ends = p.hunkends
                    if ((ends["cr"]!=0) + (ends["crlf"]!=0) + (ends["lf"]!=0)) > 1:
                        warning("inconsistent line ends in patch hunks for %s" % p.source)
                        self.warnings += 1
                    if debugmode:
                        debuglines = dict(ends)
                        debuglines.update(file=p.target, hunk=nexthunkno)
                        debug("crlf: %(crlf)d  lf: %(lf)d  cr: %(cr)d\t - file: %(file)s hunk: %(hunk)d" % debuglines)
                    # fetch next line
                    continue

            if hunkskip:
                if re_hunk_start.match(line):
                    # switch to hunkhead state
                    hunkskip = False
                    hunkhead = True
                elif line.startswith(b"--- "):
                    # switch to filenames state
                    hunkskip = False
                    filenames = True
                    if debugmode and len(self.items) > 0:
                        debug("- %2d hunks for %s" % (len(p.hunks), p.source))

            if filenames:
                if line.startswith(b"--- "):
                    if srcname != None:
                        # XXX testcase
                        warning("skipping false patch for %s" % srcname)
                        srcname = None
                        # XXX header += srcname
                        # double source filename line is encountered
                        # attempt to restart from this second line
                    re_filename = b"^--- ([^\t]+)"
                    match = re.match(re_filename, line)
                    # todo: support spaces in filenames
                    if match:
                        srcname = match.group(1).strip()
                    else:
                        warning("skipping invalid filename at line %d" % (lineno+1))
                        self.errors += 1
                        # XXX p.header += line
                        # switch back to headscan state
                        filenames = False
                        headscan = True
                elif not line.startswith(b"+++ "):
                    if srcname != None:
                        warning("skipping invalid patch with no target for %s" % srcname)
                        self.errors += 1
                        srcname = None
                        # XXX header += srcname
                        # XXX header += line
                    else:
                        # this should be unreachable
                        warning("skipping invalid target patch")
                    filenames = False
                    headscan = True
                else:
                    if tgtname != None:
                        # XXX seems to be a dead branch
                        warning("skipping invalid patch - double target at line %d" % (lineno+1))
                        self.errors += 1
                        srcname = None
                        tgtname = None
                        # XXX header += srcname
                        # XXX header += tgtname
                        # XXX header += line
                        # double target filename line is encountered
                        # switch back to headscan state
                        filenames = False
                        headscan = True
                    else:
                        re_filename = br"^\+\+\+ ([^\t]+)"
                        match = re.match(re_filename, line)
                        if not match:
                            warning("skipping invalid patch - no target filename at line %d" % (lineno+1))
                            self.errors += 1
                            srcname = None
                            # switch back to headscan state
                            filenames = False
                            headscan = True
                        else:
                            if p:  # for the first run p is None
                                self.items.append(p)
                            p = Patch()
                            p.source = srcname
                            srcname = None
                            p.target = match.group(1).strip()
                            p.header = header
                            header = []
                            # switch to hunkhead state
                            filenames = False
                            hunkhead = True
                            nexthunkno = 0
                            p.hunkends = lineends.copy()
                            continue

            if hunkhead:
                match = re.match(br"^@@ -(\d+)(,(\d+))? \+(\d+)(,(\d+))? @@(.*)", line)
                if not match:
                    if not p.hunks:
                        warning("skipping invalid patch with no hunks for file %s" % p.source)
                        self.errors += 1
                        # XXX review switch
                        # switch to headscan state
                        hunkhead = False
                        headscan = True
                        continue
                    else:
                        # TODO review condition case
                        # switch to headscan state
                        hunkhead = False
                        headscan = True
                else:
                    hunk = Hunk()
                    hunk.startsrc = int(match.group(1))
                    hunk.linessrc = 1
                    if match.group(3): hunk.linessrc = int(match.group(3))
                    hunk.starttgt = int(match.group(4))
                    hunk.linestgt = 1
                    if match.group(6): hunk.linestgt = int(match.group(6))
                    hunk.invalid = False
                    hunk.desc = match.group(7)[1:].rstrip()
                    hunk.text = []

                    hunkactual["linessrc"] = hunkactual["linestgt"] = 0

                    # switch to hunkbody state
                    hunkhead = False
                    hunkbody = True
                    nexthunkno += 1
                    continue

        # /while fe.next()

        if p:
            self.items.append(p)

        if not hunkparsed:
            if hunkskip:
                warning("warning: finished with errors, some hunks may be invalid")
            elif headscan:
                if len(self.items) == 0:
                    warning("error: no patch data found!")
                    self.errors += 1
                    return False
                else:  # extra data at the end of file
                    pass
            else:
                warning("error: patch stream is incomplete!")
                self.errors += 1
                if len(self.items) == 0:
                    return False

        if debugmode and len(self.items) > 0:
            debug("- %2d hunks for %s" % (len(p.hunks), p.source))

        # XXX fix total hunks calculation
        debug("total files: %d  total hunks: %d" % (len(self.items),
            sum(len(p.hunks) for p in self.items)))

        # ---- detect patch and patchset types ----
        for idx, p in enumerate(self.items):
            self.items[idx].type = detect_type(p)

        types = set([p.type for p in self.items])
        if len(types) > 1:
            self.type = MIXED
        else:
            self.type = types.pop()
        # --------

        normalize_filenames(self)

        return (self.errors == 0)

    def diffstat(self):
        """calculate diffstat and return as a string"""
        return diffstat(self)

    def findfile(self, old, new):
        """return name of file to be patched or None"""
        return findfile(old, new)

    def can_patch(self, filename):
        """Check if specified filename can be patched. Returns None if file can
        not be found among source filenames. False if patch can not be applied
        clearly. True otherwise.

        :returns: True, False or None
        """
        return can_patch(self, filename)

    def _match_file_hunks(self, filepath, hunks):
        return match_file_hunks(filepath, hunks)

    def patch_stream(self, instream, hunks):
        """Generator that yields stream patched with hunks iterable"""
        return patch_stream(instream, hunks)

    def write_hunks(self, srcname, tgtname, hunks):
        return write_hunks(srcname, tgtname, hunks)

    def _reverse(self):
        """reverse patch direction (this doesn't touch filenames)"""
        reverse_patchset(self)

    def dump(self):
        dump_patchset(self)

    def apply(self, strip=0, root=None):
        """Apply parsed patch, optionally stripping leading components
        from file paths. `root` parameter specifies working dir.
        return True on success
        """
        if root:
            prevdir = os.getcwd()
            os.chdir(root)

        total = len(self.items)
        errors = 0
        if strip:
            # [ ] test strip level exceeds nesting level
            #   [ ] test the same only for selected files
            #     [ ] test if files end up being on the same level
            try:
                strip = int(strip)
            except ValueError:
                errors += 1
                warning("error: strip parameter '%s' must be an integer" % strip)
                strip = 0

        #for fileno, filename in enumerate(self.source):
        for i, p in enumerate(self.items):
            if strip:
                debug("stripping %s leading component(s) from:" % strip)
                debug("   %s" % p.source)
                debug("   %s" % p.target)
                old = pathstrip(p.source, strip)
                new = pathstrip(p.target, strip)
            else:
                old, new = p.source, p.target

            filename = self.findfile(old, new)

            if not filename:
                warning("source/target file does not exist:\n  --- %s\n  +++ %s" % (old, new))
                errors += 1
                continue
            if not isfile(filename):
                warning("not a file - %s" % filename)
                errors += 1
                continue

            # [ ] check absolute paths security here
            debug("processing %d/%d:\t %s" % (i+1, total, filename))

            # validate before patching
            f2fp = open(filename, 'rb')
            hunkno = 0
            hunk = p.hunks[hunkno]
            hunkfind = []
            hunkreplace = []
            validhunks = 0
            canpatch = False
            for lineno, line in enumerate(f2fp):
                if lineno+1 < hunk.startsrc:
                    continue
                elif lineno+1 == hunk.startsrc:
                    hunkfind = [x[1:].rstrip(b"\r\n") for x in hunk.text if x[0] in b" -"]
                    hunkreplace = [x[1:].rstrip(b"\r\n") for x in hunk.text if x[0] in b" +"]
                    #pprint(hunkreplace)
                    hunklineno = 0

                    # todo \ No newline at end of file

                # check hunks in source file
                if lineno+1 < hunk.startsrc+len(hunkfind)-1:
                    if line.rstrip(b"\r\n") == hunkfind[hunklineno]:
                        hunklineno += 1
                    else:
                        info("file %d/%d:\t %s" % (i+1, total, filename))
                        info(" hunk no.%d doesn't match source file at line %d" % (hunkno+1, lineno+1))
                        info("  expected: %s" % hunkfind[hunklineno])
                        info("  actual  : %s" % line.rstrip(b"\r\n"))
                        # not counting this as error, because file may already be patched.
                        # check if file is already patched is done after the number of
                        # invalid hunks if found
                        # TODO: check hunks against source/target file in one pass
                        #   API - check(stream, srchunks, tgthunks)
                        #           return tuple (srcerrs, tgterrs)

                        # continue to check other hunks for completeness
                        hunkno += 1
                        if hunkno < len(p.hunks):
                            hunk = p.hunks[hunkno]
                            continue
                        else:
                            break

                # check if processed line is the last line
                if lineno+1 == hunk.startsrc+len(hunkfind)-1:
                    debug(" hunk no.%d for file %s  -- is ready to be patched" % (hunkno+1, filename))
                    hunkno += 1
                    validhunks += 1
                    if hunkno < len(p.hunks):
                        hunk = p.hunks[hunkno]
                    else:
                        if validhunks == len(p.hunks):
                            # patch file
                            canpatch = True
                            break
            else:
                if hunkno < len(p.hunks):
                    warning("premature end of source file %s at hunk %d" % (filename, hunkno+1))
                    errors += 1

            f2fp.close()

            if validhunks < len(p.hunks):
                if self._match_file_hunks(filename, p.hunks):
                    warning("already patched  %s" % filename)
                else:
                    warning("source file is different - %s" % filename)
                    errors += 1
            if canpatch:
                backupname = filename+b".orig"
                if exists(backupname):
                    warning("can't backup original file to %s - aborting" % backupname)
                else:
                    import shutil
                    shutil.move(filename, backupname)
                    if self.write_hunks(backupname, filename, p.hunks):
                        info("successfully patched %d/%d:\t %s" % (i+1, total, filename))
                        os.unlink(backupname)
                    else:
                        errors += 1
                        warning("error patching file %s" % filename)
                        shutil.copy(filename, filename+".invalid")
                        warning("invalid version is saved to %s" % filename+".invalid")
                        # todo: proper rejects
                        shutil.move(backupname, filename)

        if root:
            os.chdir(prevdir)

        # todo: check for premature eof
        return (errors == 0)

    def revert(self, strip=0, root=None):
        """apply patch in reverse order"""
        reverted = copy.deepcopy(self)
        reverted._reverse()
        return reverted.apply(strip, root)
