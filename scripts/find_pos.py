#!/usr/bin/python

import sys
import os
from astropy.coordinates import SkyCoord,get_icrs_coordinates
import astropy.units as u
from surveys_db import SurveysDB
from auxcodes import sepn
import numpy as np

factor=180.0/np.pi

def separation(ra1,dec1,ra2,dec2):
    # same as sepn but in degrees
    return factor*sepn(ra1/factor,dec1/factor,ra2/factor,dec2/factor)

def find_pos(ra,dec,name=None,offset=4):
    raoffset=offset/np.cos(dec/factor)
    minoffset=None
    with SurveysDB() as sdb:
        sdb.cur.execute('select * from fields where ra>%f and ra<%f and decl>%f and decl<%f' % (ra-raoffset,ra+raoffset,dec-offset,dec+offset))
        results=sdb.cur.fetchall()
        for r in results:
            sdb.cur.execute('select * from observations where field="%s"' % r['id'])
            count=len(sdb.cur.fetchall())
            sdb.cur.execute('select * from observations where field="%s" and status="DI_processed"' % r['id'])
            proc_count=len(sdb.cur.fetchall())
            sep=separation(ra,dec,r['ra'],r['decl'])
            print '%-16s %-16s %2i %2i %8.3f %8.3f %6.3f %s' % (r['id'],r['status'],count,proc_count,r['ra'],r['decl'],sep,r['location'])
            if r['status']=='Archived':
                if minoffset is None or sep<minoffset:
                    minoffset=sep
                    bestfield=r['id']
    if minoffset is None:
        return None
    else:
        return bestfield

if __name__=='__main__':

    retval=None
    if len(sys.argv)==3:
        try:
            ra=float(sys.argv[1])
            dec=float(sys.argv[2])
        except ValueError:
            if sys.argv[1]=='object':
                c=get_icrs_coordinates(sys.argv[2])
            else:
                c = SkyCoord(sys.argv[1],sys.argv[2], frame='icrs',unit=(u.hourangle, u.deg))
            ra=float(c.ra.degree)
            dec=float(c.dec.degree)
            print ra,dec
        retval=find_pos(ra,dec)
    elif len(sys.argv)==2:
        s=sys.argv[1][4:]
        coord=s[0:2]+':'+s[2:4]+':'+s[4:9]+' '+s[9:12]+':'+s[12:14]+':'+s[14:]
        sc = SkyCoord(coord,unit=(u.hourangle,u.deg))
        ra=sc.ra.value
        dec=sc.dec.value
        print 'Parsed coordinates to ra=%f, dec=%f' % (ra,dec)
        name=sys.argv[1]
        retval=find_pos(ra,dec,name=name)
    else:
        print 'Call me with the name of a source OR RA, Dec in degrees OR "object objectname"'
    if retval is not None:
        print 'Return value was',retval
