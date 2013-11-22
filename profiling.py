from metric_calculator import MetricCalculator
import networkx as nx
import redis as rd

import cProfile, pstats, StringIO

redis = rd.StrictRedis(host='localhost', port=6379, db=0)

#random_runs = [[100,0.2],[100,0.3]]
random_runs = [[1000,0.05],[1000,0.1],[1000,0.2],[10000,0.3],[1000,0.4],[2000,0.2],[3000,0.2],[4000,0.2],[5000,0.2],[6000,0.2]]


for graph_configuration in random_runs:
  
  number_of_nodes = graph_configuration[0]
  probability_of_connection = graph_configuration[1]
  
  graph = nx.fast_gnp_random_graph(number_of_nodes,probability_of_connection,seed=1)

  nodes = nx.nodes(graph)
  #barabasi_albert_graph(n, m, seed=None)[source]

  if not nx.is_connected(graph):
    print "not connected"
    sys.exit(-1)

  redis.flushdb()
  redis.sadd('all_nodes', *nodes)

  mc = MetricCalculator(graph)

  pr = cProfile.Profile()
  pr.enable()

  mc.start()

  s = StringIO.StringIO()
  sortby = 'cumulative'
  ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
  ps.print_stats()

  outfile = open('auto_profiling_output_'+str(number_of_nodes)+'_'+str(probability_of_connection)+'.txt', 'w')
  outfile.write(s.getvalue())