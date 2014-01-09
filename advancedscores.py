# advancedscores.py
import numpy as np

################
#advanced scores
################

def adv_unified_risk_score(self):

  #caching of all values in dictionaries
  all_ccs_normalized = dict(self.redis.zrange(self.metric_prefix+'corrected_clustering_coefficient'+self.normalization_suffix, 0, -1, withscores=True, score_cast_func=float))
  all_urs = dict(self.redis.zrange(self.score_prefix+'unified_risk_score', 0, -1, withscores=True, score_cast_func=float))

  urs_percentile_10 = np.percentile(all_urs.values(), 10)
  urs_percentile_90 = np.percentile(all_urs.values(), 90)

  for node in self.nodes:
    cc_normalized = all_ccs_normalized[str(node)]
    urs = all_urs[str(node)]


    if (urs >= urs_percentile_90 or urs <= urs_percentile_10):
      if (cc_normalized >= 0.25):
        advanced_unified_risk_score = ((urs * 3.0) + cc_normalized) / 4.0
      else:
        advanced_unified_risk_score = urs
    else:
      advanced_unified_risk_score = urs

    #save for node  
    self.redis.hset(self.node_prefix+str(node), 'advanced_unified_risk_score', advanced_unified_risk_score)
    #save for score
    self.redis.zadd(self.score_prefix+'advanced_unified_risk_score', advanced_unified_risk_score, str(node))