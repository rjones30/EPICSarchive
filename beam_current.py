#!/usr/bin/env python
#
# beam_currents.py - simple script to extract beam current
#                    from the EPICS archive and plot it.
#
# author: richard.t.jones at uconn.edu
# version: december 17, 2018

beam_cur = {}

import sys
import math
#import numpy
from ROOT import *

import mya

rcdb_source = "mysql://rcdb@hallddb.jlab.org/rcdb"
sys.path.append("/home/halld/rcdb/python")
import rcdb

def run_time(run):
   """
   Look up the start time and duration of a run in the GlueX rcdb.
   """
   db = rcdb.RCDBProvider(rcdb_source)
   cur = db.get_condition(run, "beam_on_current").value
   print("run", run, "beam_on_current was", cur, "nA")
   runobj = db.get_run(run)
   duration = (runobj.end_time - runobj.start_time).seconds
   return runobj.start_time.strftime("%Y-%m-%d %H:%M:%S"), duration

def tseries(datetime, duration, epics_var="IBCAD00CRCUR6", deployment="ops"):
   """
   Plot the rate vs time from the EPICS record for variable epics_var,
   starting at datetime, format "yyyy-mm-dd HH:MM:SS", and continuing
   from there for duration seconds. The result is returned in a TTree.
   """
   epicstime = mya.time_string_to_epics(datetime)
   beam_cur = mya.lookup(epics_var, deployment=deployment)
   curs, times = mya.fetch(beam_cur, epicstime, duration)
   print("fetched", len(curs), "current values,", len(times), "times.")
   if len(times) > 0:
      print("  ", mya.time_epics_to_string(times[0]), curs[0])
   if len(times) > 1:
      print("  ...")
      print("  ", mya.time_epics_to_string(times[-1]), curs[-1])
   return None

def help():
   print("Example plot commands:")
   print("  start = '2018-09-01 00:00:00'")
   print("  duration = 10e6")
   print("  c1 = TCanvas('c1')")
   print("  tree = beam_currents.tseries(start,duration)")
   print("  tree.Draw('Ibeam_nA:time_s')")
   print("  c1.Update()")
