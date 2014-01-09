#!/usr/bin/env python
import argparse
from file_importer import FileImporter
from metric_calculator import MetricCalculator

parser = argparse.ArgumentParser(description='Read a Tab-separated Graph Datafile and start Calculation of Metrics and Statistics as configured in config.py')

parser.add_argument('filename', metavar='filename', type=str,
                   help='the name of the data file containing tab separated node ids')

args = parser.parse_args()

fi = FileImporter(args.filename)
graph = fi.read()
mc = MetricCalculator(graph)
mc.start()
