#!/usr/bin/env python
#
# beam_currents.py - simple script to extract beam current
#                    from the EPICS archive and plot it.
#
# author: richard.t.jones at uconn.edu
# version: november 15, 2024

beam_cur = {}

import sys
import math
import numpy as np
import ROOT

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

def tfill(datetime, duration, tree=None, epics_var="IBCAD00CRCUR6", db="ops"):
   """
   Plot the rate vs time from the EPICS record for variable epics_var,
   starting at datetime, format "yyyy-mm-dd HH:MM:SS", and continuing
   from there for duration seconds. The result is returned in a TTree.
   Argument db can be either "ops" for the recent past, or "history"
   for dates going back before 2019.
   """
   tepoch_s = np.zeros(1, dtype=np.uint32)
   ibeam_nA = np.zeros(1, dtype=np.uint32)
   if tree:
      tree.SetBranchAddress("tepoch", tepoch_s)
      tree.SetBranchAddress("ibeam", ibeam_nA)
   else:
      tree = ROOT.TTree("beamcur", "GlueX electron beam current from EPICS")
      tree.Branch("tepoch", tepoch_s, "tepoch_s/i")
      tree.Branch("ibeam", ibeam_nA, "ibeam_nA/i")

   epicstime = mya.time_string_to_epics(datetime)
   beam_cur = mya.lookup(epics_var, deployment=db)
   curs, times = mya.fetch(beam_cur, epicstime, duration)
   print("fetched", len(curs), "current values,", len(times), "times.")
   if len(times) > 0:
      print("  ", mya.time_epics_to_string(times[0]), curs[0])
   if len(times) > 1:
      print("  ...")
      print("  ", mya.time_epics_to_string(times[-1]), curs[-1])
   for i in range(len(times)):
      tepoch_s[0] = times[i] // mya.epics_second
      ibeam_nA[0] = curs[i]
      tree.Fill()
   return tree

def help():
   print("Example usage:")
   print("  tree = beam_current.tfill('2023-02-25 00:00:00', 10000)")
   print("  tree.Draw('ibeam_nA:tepoch_s')")
