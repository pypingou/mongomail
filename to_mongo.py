#!/usr/bin/python -tt

# Import the content of a mbox file into mongodb

import bson
import mailbox
import pymongo
import os
import sys

connection = pymongo.Connection('localhost', 27017)
db = connection['fedora-devel']
mails = db.mails

def to_mongo(mbfile):
    """ Upload all the emails in a mbox file into a mongo database. """
    cnt = 0
    for message in mailbox.mbox(mbfile):
        infos = {}
        for it in message.keys():
            infos[it] = message[it]
        keys = infos.keys()
        ## There seem to be a problem to parse some messages
        if not keys:
            #print infos.keys()
            #print mbfile
            #print message
            continue
        infos['content'] = message.as_string()
        try:
            if not mails.find(infos).count():
                mails.insert(infos)
                cnt = cnt + 1
        except bson.errors.InvalidStringData, err:
            ## My guess, another encoding issue as we meet sometime...
            ## 2010-February.txt has it
            #print mbfile
            #print err
            #print message
            continue
    print '  %s email added to the database' % cnt

def get_document_size():
    """ Return the size of the document in mongodb. """
    print '  %s emails are stored into the database' % mails.count()


if __name__ == '__main__':
    sys.argv.append('2012-January.txt')
    if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
        print '''USAGE:
python mbox_to_mongo.py mbox_file [mbox_file]'''
    else:
        for mbfile in sys.argv[1:]:
            if os.path.exists(mbfile):
                print mbfile
                to_mongo(mbfile)
                get_document_size()

"""
## Test command-line:
$ mongo
use fedora-devel
db.mails.find()
db.mails.count()
"""
