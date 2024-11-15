#!/usr/bin/env python
#
# tagm_scalers.py - simple script to extract TAGM scaler rates 
#                   from the EPICS archive and plot them.
#
# author: richard.t.jones at uconn.edu
# version: november 28, 2018

scanrun = {300: 51644,
           250: 51659,
           200: 51647,
           150: 51657,
           100: 51649,
            50: 51655}

tagm_T = [0] * 103

import sys
import math
#import numpy
from ROOT import *

sys.path.append("/home/halld/offline/scalers")
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
   print "run", run, "beam_on_current was", cur, "nA"
   runobj = db.get_run(run)
   duration = (runobj.end_time - runobj.start_time).seconds
   return runobj.start_time.strftime("%Y-%m-%d %H:%M:%S"), duration

def Eseries(datetime, duration=0):
   """
   Plot the rate vs Etag from the tagm EPICS scalers recorded at time
   datatime, format "yyyy-mm-dd HH:MM:SS", and return the result as
   a TH1D object. The default duration=0 takes a snapshot at the
   given time. If duration > 0 then the full time period is scanned
   and the most probable value is taken.
   """
   epicstime = mya.time_string_to_epics(datetime)
   h1 = TH1D("Eseries", "TAGM rates", 102, 1, 103)
   for col in range(1,103):
      if not tagm_T[col]:
         tagm_T[col] = mya.lookup("TAGM:T:{0}:scaler_t1".format(col))
      rates, times = mya.fetch(tagm_T[col], epicstime, duration)
      nbins = 700
      h2 = TH1D("htemp", "", nbins, 0, 7)
      for samp in range(0, len(times)):
         if samp+1 < len(times):
            wgt = (times[samp+1] - times[samp]) / (1 << 32)
         else:
            wgt = 1
         h2.Fill(math.log10(rates[samp] + 1e-9), wgt)
      lograte = h2.GetMaximum()
      lograte0 = h2.GetBinContent(0)
      lograte1 = h2.GetBinContent(1001)
      if 10*lograte > lograte0 and lograte > lograte1:
         imax = h2.GetMaximumBin()
         icut0 = max(int(imax * 0.8), 1)
         icut1 = min(int(imax * 1.25), nbins)
         h2.GetXaxis().SetRange(icut0, icut1)
         mprate = 10**h2.GetMean()
      elif lograte0 > lograte1:
         mprate = 0
      else:
         mprate = 1e7
      h1.SetBinContent(col, mprate)
      h2.Delete()
   h1.SetStats(0)
   h1.GetXaxis().SetTitle("TAGM column number")
   h1.GetYaxis().SetTitle("rate (Hz)")
   h1.GetYaxis().SetTitleOffset(1.3)
   return h1

def tseries(col, datetime, duration, dt_sec=1):
   """
   Plot the rate vs time from the tagm EPICS scaler for column col,
   starting at datetime, format "yyyy-mm-dd HH:MM:SS", and continuing
   from there for duration seconds, sampling every dt_sec seconds.
   The result is returned in a TH1D.
   """
   epicstime = mya.time_string_to_epics(datetime)
   nbins = int(math.ceil(duration / dt_sec))
   h1 = TH1D("tseries", "TAGM rate for column {0}".format(col),
              nbins, 0, nbins * dt_sec)
   if not tagm_T[col]:
      tagm_T[col] = mya.lookup("TAGM:T:{0}:scaler_t1".format(col))
   rates, times = mya.fetch(tagm_T[col], epicstime, duration)
   s,t = 0,0
   for samp in range(0, len(times)):
      if samp+1 < len(times):
         tnext = (times[samp+1] - times[0]) / (1 << 32)
      else:
         tnext = 1e99
      while t < tnext and s < nbins:
         s += 1
         t += dt_sec
         h1.SetBinContent(s, rates[samp])
   h1.SetStats(0)
   h1.GetXaxis().SetTitle("time (s)")
   h1.GetYaxis().SetTitle("rate (Hz)")
   h1.GetYaxis().SetTitleOffset(1.3)
   return h1

start, duration = run_time(scanrun[300])
plot = Eseries(start, duration)
plot.Draw()
c1.Update()

c2 = TCanvas("c2")
plot2 = tseries(20,start,duration)
plot2.Draw()
c2.Update()
