#statistics.py
import redis as rd
import numpy as np
from scipy.stats import pearsonr

def calculate_statistics(self,metric,redis_key):
  all_values = dict(self.redis.zrange(redis_key, 0, -1, withscores=True, score_cast_func=float)).values()
  min_value = np.min(all_values)
  max_value = np.max(all_values)

  average = np.average(all_values)
  median = np.median(all_values)
  standard_deviation = np.std(all_values)

  self.redis.hset(self.statistics_prefix+metric, 'min', min_value)
  self.redis.hset(self.statistics_prefix+metric, 'max', max_value)
  self.redis.hset(self.statistics_prefix+metric, 'average', average)
  self.redis.hset(self.statistics_prefix+metric, 'median', median)
  self.redis.hset(self.statistics_prefix+metric, 'standard_deviation', standard_deviation)


def calculate_correlations(self):
  m = self.base_metrics.keys()
  c = self.advanced_metrics.keys()

  metrics = m + c

  correlations = {}
  for metric1 in metrics:
    correlations[metric1] = {}
    for metric2 in metrics:
      correlations[metric1][metric2] = (0,0)
      if metric1 == metric2:
        correlations[metric1][metric2] = (1,0)
        continue

      dict_metric1 = dict(self.redis.zrange(self.metric_prefix+metric1, 0, -1, withscores=True, score_cast_func=float))
      dict_metric2 = dict(self.redis.zrange(self.metric_prefix+metric2, 0, -1, withscores=True, score_cast_func=float))
      values_metric1 = []
      values_metric2 = []

      for key in sorted(dict_metric1.iterkeys()):
        values_metric1.append(dict_metric1[key])

      for key in sorted(dict_metric2.iterkeys()):
        values_metric2.append(dict_metric2[key])

      correlations[metric1][metric2] = pearsonr(values_metric1,values_metric2)

  values_metric1 = []
  values_metric2 = []

  for source in correlations:
    for target in correlations[source]:
      self.redis.hset(self.statistics_prefix+"correlations:"+source+":"+target, "correlation", correlations[source][target][0])
      self.redis.hset(self.statistics_prefix+"correlations:"+source+":"+target, "confidence", correlations[source][target][1])