#!/usr/bin/python -tt

# Import the content of a mbox file into mongodb

import bson
import datetime
import mailbox
import os
import pymongo
import re
import sys
import time
from dateutil.parser import parse

connection = pymongo.Connection('localhost', 27017)

TOTALCNT = 0

def convert_date(date_string):
    """ Convert the string of the date to a datetime object. """
    date_string = date_string.strip()
    dt = parse(date_string)
    return dt

def get_max_thread_id(database):
    db = connection[database]
    db.mails.create_index('In-Reply-To')
    db.mails.ensure_index('In-Reply-To')
    db.mails.create_index('ThreadID')
    db.mails.ensure_index('ThreadID')
    res = db.mails.find(
        {'In-Reply-To': {'$exists': False},
         'ThreadID': {'$exists': True}},
          sort=[('ThreadID', pymongo.DESCENDING)]);
    for el in res:
        return int(el['ThreadID'])
    return 0


def to_mongo(mbfile, database):
    """ Upload all the emails in a mbox file into a mongo database. """
    global TOTALCNT
    db = connection[database]
    cnt = 0
    cnt_read = 0
    for message in mailbox.mbox(mbfile):
        cnt_read = cnt_read + 1
        TOTALCNT = TOTALCNT + 1
        infos = {}
        for it in message.keys():
            infos[it] = message[it]
        keys = infos.keys()
        ## There seem to be a problem to parse some messages
        if not keys:
            print '  Failed: %s keys: "%s"' % (mbfile, keys)
            #print message
            continue
        if 'From' in infos:
            regex = '(.*)\((.*)\)'
            email, name = re.match(regex, infos['From']).groups()
            infos['From'] = name
            email = email.replace(' at ', '@')
            infos['Email'] = email
        try:
            if '--assume-unique' in sys.argv or \
                db.mails.find({'Message-ID': infos['Message-ID']}).count() == 0:
                infos['Date'] = convert_date(infos['Date'])
                infos['Content'] = message.get_payload()
                thread_id = 0
                db.mails.create_index('Message-ID')
                db.mails.ensure_index('Message-ID')
                db.mails.create_index('ThreadID')
                db.mails.ensure_index('ThreadID')
                if not 'References' in infos and not 'In-Reply-To' in infos:
                    infos['ThreadID'] = get_max_thread_id(database) + 1
                else:
                    ref = None
                    if 'In-Reply-To' in infos:
                        ref= infos['In-Reply-To']
                    else:
                        ref= infos['References'].split('\n')[0].strip()
                    res = db.mails.find_one({'Message-ID': ref})
                    if res and 'ThreadID' in res:
                        infos['ThreadID'] = res['ThreadID']
                    else:
                        infos['ThreadID'] = get_max_thread_id(database) + 1
                infos['Category'] = 'Question'
                if 'agenda' in infos['Subject'].lower():
                    infos['Category'] = 'Agenda'
                if 'reminder' in infos['Subject'].lower():
                    infos['Category'] = 'Agenda'
                infos['Full'] = message.as_string()
                
                ## TODO: I'm not sure the TOTALCNT approach is the right one
                ## we should discuss this with the pipermail guys
                infos['LegacyID'] = TOTALCNT
                db.mails.insert(infos)
                cnt = cnt + 1
        except Exception, err:
            print '  Failed: %s error: "%s"' % (mbfile, err)
            print '  Failed:', message['Subject'], message['Date'], message['From']
    print '  %s email read' % cnt_read
    print '  %s email added to the database' % cnt

def get_document_size(database):
    """ Return the size of the document in mongodb. """
    db = connection[database]
    print '  %s emails are stored into the database' % db.mails.count()


if __name__ == '__main__':
    #sys.argv.extend(['devel', 'lists/devel-2012-03-March.txt'])
    if len(sys.argv) < 2 or '-h' in sys.argv or '--help' in sys.argv:
        print '''USAGE:
python mbox_to_mongo.py db_name mbox_file [mbox_file]'''
    else:
        print 'Adding to database: %s' % sys.argv[1]
        for mbfile in sys.argv[2:]:
            print mbfile
            if os.path.exists(mbfile):
                print mbfile
                to_mongo(mbfile, sys.argv[1])
                get_document_size(sys.argv[1])

"""
## Test command-line:
$ mongo
use fedora-devel
db.mails.find()
db.mails.count()
"""
