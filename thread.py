#!/usr/bin/python -tt

# print the emails for a given ThreadID

from bunch import Bunch
import pymongo
import re

connection = pymongo.Connection('localhost', 27017)

def build_thread(emails):
    thread = {}
    for email in emails:
        #print email['Date'], email['From'] #, email['Message-ID']
        email = Bunch(email)
        ref = []
        if 'References' in email:
            ref.extend(email['References'].split()[-1:])
        elif 'In-Reply-To' in email:
            ref.append(email['In-Reply-To'])
        if email['Message-ID'] not in thread:
            thread[email['Message-ID']] = Bunch(
                {'email': email, 'child': []})
        else:
            thread[email['Message-ID']].email = email
        for ref in set(ref):
            if ref in thread:
                thread[ref].child.append(email['Message-ID'])
            else:
                thread[ref] = Bunch(
                {'email': None, 'child': [email['Message-ID']]})
    return thread

def tree_to_list(tree, mailid, level, thread_list):
    start = tree[mailid]
    start.level = level
    thread_list.append(start)
    for mail in start.child:
        mail = tree[mail]
        thread_list = tree_to_list(tree, mail.email['Message-ID'],
            level + 1, thread_list)
    return thread_list

# Display one thread:
db = connection['devel']
threadid = 62
thread = list(db.mails.find({'ThreadID': threadid},
    sort=[('Date', pymongo.ASCENDING)]))

tree = build_thread(thread)
thread_list = []
thread = tree_to_list(tree, thread[0]['Message-ID'], 0, thread_list)
for email in thread_list:
    print ' '* email.level, email.email.Date, email.email.From
    
