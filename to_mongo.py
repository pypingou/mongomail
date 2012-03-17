#!/usr/bin/python -tt

# Import the content of a mbox file into mongodb

import bson
import datetime
import email.Utils
import mailbox
import pymongo
import os
import sys
import time

connection = pymongo.Connection('localhost', 27017)
db = connection['devel']
mails = db.mails
mails.create_index('Message-ID')
mails.ensure_index('Message-ID')

def convert_date(date_string):
    """ Convert the string of the date to a datetime object. """
    date_string = date_string.strip()
    time_tuple = email.Utils.parsedate(date_string)

    # convert time_tuple to datetime
    EpochSeconds = time.mktime(time_tuple)
    dt = datetime.datetime.fromtimestamp(EpochSeconds)
    return dt

def to_mongo(mbfile):
    """ Upload all the emails in a mbox file into a mongo database. """
    cnt = 0
    cnt_read = 0
    for message in mailbox.mbox(mbfile):
        cnt_read = cnt_read + 1
        infos = {}
        for it in message.keys():
            infos[it] = message[it]
        keys = infos.keys()
        ## There seem to be a problem to parse some messages
        if not keys:
            print '  Failed: %s keys: "%s"' % (mbfile, keys)
            #print message
            continue
        try:
            if '--assume-unique' in sys.argv or \
                mails.find({'Message-ID': infos['Message-ID']}).count() == 0:
                infos['Date'] = convert_date(infos['Date'])
                infos['Content'] = message.get_payload()
                thread_id = 0
                db.mails.create_index('Message-ID')
                db.mails.ensure_index('Message-ID')
                db.mails.create_index('In-Reply-To')
                db.mails.ensure_index('In-Reply-To')
                db.mails.create_index('Thread-ID')
                db.mails.ensure_index('Thread-ID')
                if not 'In-Reply-To' in infos:
                    res = db.mails.find(
                        {'In-Reply-To': {'$exists': False},
                         'Thread-ID': {'$exists': True}},
                          sort=[('Thread-ID', pymongo.DESCENDING)]);
                    for el in res:
                        thread_id = int(el['Thread-ID'])
                        break
                    infos['Thread-ID'] = thread_id + 1
                else:
                    res = db.mails.find_one({'Message-ID': \
                        infos['In-Reply-To']})
                    if res and 'Thread-ID' in res:
                        infos['Thread-ID'] = res['Thread-ID']
                mails.insert(infos)
                cnt = cnt + 1
        except Exception, err:
            print '  Failed: %s error: "%s"' % (mbfile, err)
            print '  Failed:', message['Subject'], message['Date'], message['From']
    print '  %s email read' % cnt_read
    print '  %s email added to the database' % cnt

def get_document_size():
    """ Return the size of the document in mongodb. """
    print '  %s emails are stored into the database' % mails.count()


if __name__ == '__main__':
    #sys.argv.append('devel/2012-January.txt')
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
