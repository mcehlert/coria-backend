#normalizations.py
def min_max(self,metric_name):
  #perform min max normalization of specified metric for all nodes
  #min_max normalization
  #get min and max from redis
  x_min = self.redis.zrange(self.metric_prefix+metric_name, 0, 0, withscores=True, score_cast_func=float)[0][1]
  x_max = self.redis.zrange(self.metric_prefix+metric_name, -1, -1, withscores=True, score_cast_func=float)[0][1]
  
  #print x_min
  #print x_max
  
  for node in self.nodes:
    if x_min == x_max:
      x_normalized = 1.0
    else:
      x = float(self.redis.hget(self.node_prefix+str(node), metric_name))
      x_normalized = (x - x_min) / (x_max - x_min)     
  
    #store value for node and metric
    self.redis.zadd(self.metric_prefix+metric_name+self.normalization_suffix, x_normalized, str(node))
    self.redis.hset(self.node_prefix+str(node),metric_name+self.normalization_suffix, x_normalized)

#max min normalization
def max_min(self,metric_name):
  x_min = self.redis.zrange(self.metric_prefix+metric_name, 0, 0, withscores=True, score_cast_func=float)[0][1]
  x_max = self.redis.zrange(self.metric_prefix+metric_name, -1, -1, withscores=True, score_cast_func=float)[0][1]
  
  for node in self.nodes:
    if x_min == x_max:
      x_normalized = 1.0
    else:
      x = float(self.redis.hget(self.node_prefix+str(node), metric_name))
      x_normalized = (x_max - x) / (x_max - x_min)     

    #store value for node and metric
    self.redis.zadd(self.metric_prefix+metric_name+self.normalization_suffix, x_normalized, str(node))
    self.redis.hset(self.node_prefix+str(node),metric_name+self.normalization_suffix, x_normalized)