#!/usr/bin/env python
#
# beamline_cond.py - simple script to scan a run range in rcdb
#                    and list runs with different beamline settings,
#                    useful for setting run-dependent geometry in ccdb.
#
# author: richard.t.jones at uconn.edu
# version: december 20, 2018

scanruns = {50000:60000}

import sys
sys.path.append("/home/halld/rcdb/python")
import rcdb
from rcdb.model import *

rcdb_source = "mysql://rcdb@hallddb.jlab.org/rcdb"
db = rcdb.RCDBProvider(rcdb_source)

converter = ""
collimator = ""
firstrun = 0
lastrun = 0
for runrange in scanruns:
   query = db.session.query(Run)\
             .filter(Run.number.between(runrange,scanruns[runrange]))
   runs = query.all()
   for run in runs:
      try:
         tpolconv = run.get_condition("polarimeter_converter").value
         collim = run.get_condition("collimator_diameter").value
      except:
         continue
      if tpolconv != converter or collim != collimator:
         if firstrun:
            print firstrun,
            if lastrun:
              print "-", lastrun,
            print ":", converter, collimator
         converter = tpolconv
         collimator = collim
         firstrun = run.number
         lastrun = 0
      else:
         lastrun = run.number
