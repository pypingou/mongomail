#!/usr/bin/python -tt

# print somes statistics for the emails in the database

import pymongo
import re

connection = pymongo.Connection('localhost', 27017)
#db = connection['devel']
db = connection['packaging']
mails = db.mails

## The number of emails:
print '%s emails in the database' % mails.count()
mails.create_index('Message-ID')
mails.ensure_index('Message-ID')
print '%s distinct emails in the database' % len(mails.distinct('Message-ID'))


## There is something fishy going on about the dates, most likely needs
## to be fixed at the import in the database
# First email:
mails.create_index('Date')
mails.ensure_index('Date')
res = mails.find(sort=[('Date', pymongo.DESCENDING)])
print 'The first email in the database is from: %s' % res[0]['Date']
# Last email
res = mails.find(sort=[('Date', pymongo.ASCENDING)])
print 'The last email in the database is from: %s' % res[0]['Date']

# The number of people who mailed the list:
mails.create_index('From')
mails.ensure_index('From')
print '%s person emailed the list' % len(mails.distinct('From'))

# The number of different subject:
print '%s different subject where discussed' % len(mails.distinct('Subject'))

# Person who emailed the most
email_sent = 0
author = None
authors = {}
for sender in mails.distinct('From'):
    cnt = mails.find({'From':sender}).count()
    if cnt > email_sent:
        author = sender
        email_sent = cnt
    if cnt in authors:
        authors[cnt].append(sender)
    else:
        authors[cnt] = [sender]
order = authors.keys()
order.sort()
order.reverse()
print 'The maximum number of email sent by one person is: %s' % email_sent
print 'The maximum number of email sent by one person is: %s' % order[0]
print 'These prolifix authors are: %s' % author
print 'These prolifix authors are: %s' % ','.join(authors[order[0]])

print 'The following maximum number of email sent by one person is: %s' % order[1]
print 'These prolifix authors are: %s' % ','.join(authors[order[1]])

# Number of email sent by an email containing FamilleCollet.com
regex = '.*FamilleCollet.com.*'
cnt = mails.find({'From': re.compile(regex, re.IGNORECASE)}).count()
print 'FamilleCollet.com sent %s emails' % cnt

# Number of email sent by an email from pingoured.fr
regex = '.*pingoured.fr.*'
cnt = mails.find({'From': re.compile(regex, re.IGNORECASE)}).count()
print 'pingoured.fr sent %s emails' % cnt


# Number of email sent by an email redhat.com
regex = '.*redhat.com.*'
cnt = mails.find({'From': re.compile(regex, re.IGNORECASE)}).count()
print 'redhat.com sent %s emails' % cnt

# The subject of the email sent by an email containing FamilleCollet.com
#regex = '.*FamilleCollet.com.*'
#emails = mails.find({'From': re.compile(regex, re.IGNORECASE)})
#print 'Remi sent email about:'
#for email in emails:
    #print email['Date'], email['Subject']


# The subject of the email sent by an email containing pingoured.fr
#regex = '.*pingoured.fr.*'
#emails = mails.find({'From': re.compile(regex, re.IGNORECASE)})
#print 'pingou sent email about:'
#for email in emails:
    #print email['Date'], email['Subject']

# The thread who gathered the most people
mails.create_index('Subject')
mails.ensure_index('Subject')
email_sent = 0
subject = None
threads = {}
for sub in mails.distinct('Subject'):
    cnt = mails.find({'Subject': sub}).count()
    if cnt > email_sent:
        subject = sub
        email_sent = cnt
    if cnt in threads:
        threads[cnt].append(sub)
    else:
        threads[cnt] = [sub]
order = threads.keys()
order.sort()
order.reverse()
print 'The thread who gathered the most people is: "%s"' % subject
print 'The thread who gathered the most people is: "%s"' % ','.join(threads[order[0]])
print 'It gathered %s emails' % email_sent
print 'It gathered %s emails' % order[0]

print 'The second thread who gathered the most people is: "%s"' % ','.join(threads[order[1]])
print 'It gathered %s emails' % order[1]


# Email mentionning rawhide terms in their subject or body
mails.create_index('Content')
mails.ensure_index('Content')
for term in ['pingou', 'rawhide', 'rawhide.*report', '\!\!\!\!\!\!\!']:
    regex = '.*%s.*' % term
    cnt = mails.find({'Subject': re.compile(regex, re.IGNORECASE)}).count()
    print '%s emails mentionned %s in their subject' % (cnt, regex)
    cnt = mails.find({'Content': re.compile(regex, re.IGNORECASE)}).count()
    print '%s emails mentionned %s in their body' % (cnt, regex)

# Emails in February 2012
from datetime import datetime
start = datetime(2012, 2, 1)
end = datetime(2012, 3, 1)
mails.create_index('Date')
mails.ensure_index('Date')
res = db.mails.find({"Date": {"$gte": start, "$lt": end}}).count()
print '%s were sent between %s and %s' % (res, start, end)


def get_emails_thread(start_email, thread):
    for el in db.mails.find({'In-Reply-To': start_email['Message-ID']}):
        thread.append(el)
        get_emails_thread(el, thread)
    return thread

# Beginning of thread == No 'In-Reply-To' header
for el in db.mails.find({'In-Reply-To': {'$exists':False}},
        sort=[('Date', pymongo.ASCENDING)]):
    thread = get_emails_thread(el, [el])
    print el['Subject'], len(thread)
