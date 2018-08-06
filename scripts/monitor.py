#!/usr/bin/python

# Code to run continuously and keep an eye on the state of the queue
# Download new files if needed
# Eventually, archive using the archive script

from time import sleep
import datetime
from surveys_db import SurveysDB,get_next
import os
import threading
from run_pipeline import do_run_pipeline
from upload import do_upload

queuelimit=10
cluster=os.environ['DDF_PIPELINE_CLUSTER']
download_thread=None
download_name=None
upload_thread=None
upload_name=None
basedir='/beegfs/car/mjh'

while True:

    with SurveysDB() as sdb:
        sdb.cur.execute('select * from fields where status!="Not started" and clustername="%s"' % cluster)
        result=sdb.cur.fetchall()

    d={}
    for r in result:
        status=r['status']
        if status in d:
            d[status]=d[status]+1
        else:
            d[status]=1
    print '\n\n-----------------------------------------------\n\n'
    print 'DDF-pipeline status on cluster',cluster
    print(datetime.datetime.now())
    print
    for k in sorted(d.keys()):
        print "%-20s : %i" % (k,d[k])
    if download_thread is not None:
        print 'Download thread is running (%s)' % download_name
    if upload_thread is not None:
        print 'Upload thread is running (%s)' % upload_name
        
    if download_thread is not None and not download_thread.isAlive():
        print 'Download thread seems to have terminated'
        download_thread=None

    if upload_thread is not None and not upload_thread.isAlive():
        print 'Upload thread seems to have terminated'
        upload_thread=None

    if d['Queued']<queuelimit and download_thread is None:
        download_name=get_next()
        print 'We need to download a new file (%s)!' % download_name
        download_thread=threading.Thread(target=do_run_pipeline, args=(download_name,basedir))
        download_thread.start()

    if d['Complete']>0 and upload_thread is None:
        for r in result:
            if r['status']=='Complete':
                upload_name=r['id']
                print 'We need to upload a new file (%s)!' % upload_name
                upload_thread=threading.Thread(target=do_upload, args=(upload_name,basedir))
                upload_thread.start()
                break
        
    print '\n\n-----------------------------------------------\n\n'
        
    sleep(300)
