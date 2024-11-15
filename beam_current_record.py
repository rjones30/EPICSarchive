#!/usr/bin/env python3
#
# beam_current_record.py - script to extract the historic record of
#                          electron  beam current from the EPIC archive
#                          from first beam in Hall D through the present,
#                          and save the results in a root tree.
#
# author: richard.t.jones at uconn.edu
# version: november 15, 2024

import sys
import ROOT
import mya
import beam_current as bc
from datetime import datetime
today = datetime.now()

rfile = ROOT.TFile("HallD_beam_current_record.root", "recreate")
rtree = bc.tfill("2000-01-01 00:00:00", 1, db="history")

for y in range(2015, today.year + 1):
   for m in range(1, 13):
      start = mya.time_string_to_epics(f"{y}-{m:02d}-01 00:00:00")
      if m < 12:
         end = mya.time_string_to_epics(f"{y}-{m+1:02d}-01 00:00:00")
      else:
         end = mya.time_string_to_epics(f"{y+1}-01-01 00:00:00")
      molen = (end - start) / mya.epics_second
      t = bc.tfill(f"{y}-{m:02d}-01 00:00:00", molen, tree=rtree)
rtree.Write()
