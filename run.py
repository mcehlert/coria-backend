#!/usr/bin/env python

from file_importer import FileImporter
from metric_calculator import MetricCalculator

import cProfile, pstats, StringIO

import networkx as nx
import redis as rd

# start import
#fi    = FileImporter('data/Dataset_2012.txt')
#fi    = FileImporter('data/test_dataset.txt')
#graph = fi.read()

#print "Nodes:" 
#print graph.number_of_nodes()
#print "Edges:"
#print graph.number_of_edges()

redis = rd.StrictRedis(host='localhost', port=6379, db=0)
redis.flushdb()
all_nodes = range(1,100)
graph = nx.fast_gnp_random_graph(100,0.15,seed=1)
redis.sadd('all_nodes', *all_nodes)

mc = MetricCalculator(graph)

pr = cProfile.Profile()
pr.enable()

mc.start()

s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()

outfile = open('profiling_run_result.txt', 'w')
outfile.write(s.getvalue())