#!/usr/bin/env python
import datetime
import argparse
import cProfile, pstats, StringIO
from file_importer import FileImporter
from metric_calculator import MetricCalculator

parser = argparse.ArgumentParser(description='Read a Tab-separated Graph Datafile and start Calculation of Metrics and Statistics as configured in config.py')

parser.add_argument('filename', metavar='filename', type=str,
                   help='the name of the data file containing tab separated node ids')

parser.add_argument('--profiling',dest='profiling',action='store_true', help='enable runtime profiling into profiling.txt file')

args = parser.parse_args()

if args.profiling:
  pr = cProfile.Profile()
  s = StringIO.StringIO()
  timestamp = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
  outfile = open('profiling_output_'+timestamp+'.txt', 'w')
  pr.enable()

fi = FileImporter(args.filename)
graph = fi.read()
mc = MetricCalculator(graph)
mc.start()

if args.profiling:
  ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
  ps.print_stats()
  outfile.write(s.getvalue())