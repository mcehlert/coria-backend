#indexing
def index_nodes(self):
  self.redis.sadd(self.node_index_key, self.nodes) 

def index_neighbors(self):
  for node in self.nodes:
    node_neighbors = self.graph.neighbors(int(node))
    self.redis.sadd(self.node_neighbors_prefix+str(node), node_neighbors)

def index_metrics(self):
  for metric in self.base_metrics:
    self.redis.sadd(self.metric_index_key, metric)
  
  for advanced_metric in self.advanced_metrics:
    self.redis.sadd(self.metric_index_key, advanced_metric)

def index_scores(self):
  for score in self.scores:
    self.redis.sadd(self.score_index_key, score)

  for advanced_score in self.advanced_scores:
    self.redis.sadd(self.score_index_key, advanced_score)