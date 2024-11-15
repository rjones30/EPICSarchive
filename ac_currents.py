#!/usr/bin/env python
#
# ac_currents.py - simple script to extract AC currents
#                  from the EPICS archive and plot them.
#
# author: richard.t.jones at uconn.edu
# version: december 17, 2018

ac_cur = {}

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

def tseries(wedge, datetime, duration, dt_sec=1):
   """
   Plot the rate vs time from the EPICS record for variable wedge,
   starting at datetime, format "yyyy-mm-dd HH:MM:SS", and continuing
   from there for duration seconds, sampling every dt_sec seconds.
   The wedge argument is a string formatted as "[io][xy][+-]" where
   i=inner, o=outer, and the meaning of x,y and +,- should be obvious.
   The result is returned in a TH1D.
   """
   epicstime = mya.time_string_to_epics(datetime)
   nbins = int(math.ceil(duration / dt_sec))
   h1 = TH1D("tseries", "{} current".format(wedge),
              nbins, 0, nbins * dt_sec)
   if not wedge in ac_cur:
      if 'I' in wedge or 'i' in wedge:
         inout = "inner"
         chanset = "1"
      else:
         inout = "outer"
         chanset = "2"
      if 'X' in wedge or 'x' in wedge:
         xy = 'x'
         chan = 1
      else:
         xy = 'y'
         chan = 3
      if '+' in wedge:
         plusm = "plus"
      else:
         plusm = "minus"
         chan += 1
      var = "AC:{0}:ped:{1}_{2}".format(inout, xy, plusm)
      var = "IOCHDCOL:VMICADC{0}_{1}".format(chan, chanset)
      ac_cur[wedge] = mya.lookup(var)
   curs, times = mya.fetch(ac_cur[wedge], epicstime, duration)
   print("fetched", len(curs), "current values,", len(times), "times.")
   if len(times) > 0:
      print("  ", mya.time_epics_to_string(times[0]), curs[0])
   if len(times) > 1:
      print("  ...")
      print("  ", mya.time_epics_to_string(times[-1]), curs[-1])
   s,t = 0,0
   for samp in range(0, len(times)):
      if samp+1 < len(times):
         tnext = (times[samp+1] - times[0]) / (1 << 32)
      else:
         tnext = 1e99
      while t < tnext and s < nbins:
         s += 1
         t += dt_sec
         h1.SetBinContent(s, curs[samp])
   print("total samples", s, "total time", t)
   h1.SetStats(0)
   h1.GetXaxis().SetTitle("time (s)")
   h1.GetYaxis().SetTitle("current (nA)")
   h1.GetYaxis().SetTitleOffset(1.3)
   return h1

def help():
   print("Example plot commands:")
   print("  start = '2018-09-01 00:00:00'")
   print("  duration = 10e6")
   print("  c1 = TCanvas('c1')")
   print("  plot1 = ac_currents.tseries('oy-',start,duration,dt_sec=24*3600)")
   print("  plot1.Draw()")
   print("  c1.Update()")
