import redis as rd
import numpy as np
from scipy.stats import pearsonr

metrics  = ['clustering_coefficient',
            'degree',
            'average_neighbor_degree',
            'iterated_average_neighbor_degree',
            'betweenness_centrality',
            'eccentricity',
            'average_shortest_path_length',
            'corrected_clustering_coefficient',
            'corrected_average_neighbor_degree',
            'corrected_iterated_average_neighbor_degree']

rdb = rd.StrictRedis(host='localhost', port=6379, db=0)


correlations = {}
for metric1 in metrics:
  correlations[metric1] = {}
  for metric2 in metrics:
    correlations[metric1][metric2] = (0,0)
    if metric1 == metric2:
      correlations[metric1][metric2] = (1,0)
      continue

    dict_metric1 = dict(rdb.zrange(metric1, 0, -1, withscores=True, score_cast_func=float))
    dict_metric2 = dict(rdb.zrange(metric2, 0, -1, withscores=True, score_cast_func=float))

    values_metric1 = []
    values_metric2 = []

    for key in sorted(dict_metric1.iterkeys()):
      values_metric1.append(dict_metric1[key])

    for key in sorted(dict_metric2.iterkeys()):
      values_metric2.append(dict_metric2[key])

    correlations[metric1][metric2] = pearsonr(values_metric1,values_metric2)

for source in correlations:
  for target in correlations[source]:
    rdb.hset("correlations:"+source+":"+target, "correlation", correlations[source][target][0])
    rdb.hset("correlations:"+source+":"+target, "confidence", correlations[source][target][1])