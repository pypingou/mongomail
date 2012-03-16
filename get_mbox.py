#! /bin/python

import itertools
import urlgrabber
import gzip
from multiprocessing import Pool

years = (2010, 2011, 2012,)
months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')


def archive_downloader(i):
    basename = "{0}-{1}.txt.gz".format(*i)
    filename = "http://lists.fedoraproject.org/pipermail/devel/{0}".format(basename)
    try:
        urlgrabber.urlgrab(filename)
        with open(basename.replace(".gz", ""), "w") as f:
           f.write(gzip.open(basename).read())
        print "== {0} downloaded ==".format(filename)
    except urlgrabber.grabber.URLGrabError:
        pass

if __name__ == "__main__":
    p = Pool(5)
    p.map(archive_downloader, itertools.product(years, months))


