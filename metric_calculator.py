import networkx as nx
import redis as rd
import numpy as np
import indexing
import statistics
import normalizations
import config


class MetricCalculator(object):
  def __init__ (self, graph):
    #class constructor
    #define required class variables such as the graph to work on, the redis connection and the nodes of the graph

    self.graph                = graph
    self.redis                = rd.StrictRedis(host='localhost', port=6379, db=0)
    self.nodes                = nx.nodes(graph)


    # configuration variables are read from the config file and are also saved to class variables for easy access
    self.node_index_key       = config.node_index_key
    self.metric_index_key     = config.metric_index_key
    self.score_index_key      = config.score_index_key
    
    self.node_neighbors_prefix = config.node_neighbors_prefix
    self.node_prefix           = config.node_prefix
    self.metric_prefix         = config.metric_prefix
    self.score_prefix          = config.score_prefix
    self.statistics_prefix     = config.statistics_prefix

    self.normalization_suffix  = config.normalization_suffix

    self.base_metrics          = config.base_metrics
    self.advanced_metrics      = config.advanced_metrics

    self.normalization_methods = config.normalization_methods

    self.scores                = config.scores
    self.advanced_scores       = config.advanced_scores


    
  def start(self):
    #clean all data in Redis
    self.redis.flushdb()
    
    #index creation
    self.create_indexes()
    

    #main calculations
    self.calculate_metrics()
    self.calculate_advanced_metrics()
    self.normalize_metrics()
    self.calculate_scores()
    self.calculate_advanced_scores()

    #statistics
    self.calculate_statistics()

##################
#### INDEXING ####
##################
  def create_indexes(self):
    #call methods defined in indexing.py
    indexing.index_nodes(self)
    indexing.index_neighbors(self)
    indexing.index_metrics(self)
    indexing.index_scores(self)

###########################
#### CALCULATION LOOPS ####
###########################
  
  def calculate_metrics(self):
    # loop through all defined metrics and call specified calculation method for each node
    for metric_name in self.base_metrics:
      metric_method = self.base_metrics[metric_name]
  
    # loop through all nodes
      for node in self.nodes:
        # call calculation method of supplied metric for current node
        node = int(node)
        value = float(metric_method(self,node))
     
        #store result in node values
        self.redis.hset(self.node_prefix+str(node), metric_name, value)

        #also store result to metric set
        self.redis.zadd(self.metric_prefix+metric_name, value, str(node))

  
  def calculate_advanced_metrics(self):
    # loop through all defined_advanced_metrics and call specified calculation method
    for advanced_metric_name in self.advanced_metrics:
      metric_method = self.advanced_metrics[advanced_metric_name]

      # loop through all nodes
      for node in self.nodes:
        node = int(node)
        value = float(metric_method(self,node))

        #store result in node values
        self.redis.hset(self.node_prefix+str(node), advanced_metric_name, value)

        #also store result to metric set
        self.redis.zadd(self.metric_prefix+advanced_metric_name, value, str(node))


  # loop through all defined normalizations and call respective normalization method
  # no default normalizations for metrics not listed in the "normalization_methods" hash
  def normalize_metrics(self):
    #fallback normalization: min-max
    
    all_metrics = dict(self.base_metrics.items() + self.advanced_metrics.items())

    for metric_name in all_metrics:
      if self.normalization_methods.has_key(metric_name):
        normalization_method = self.normalization_methods[metric_name]
      else:
        #fallback normalization is min-max
        normalization_method = normalizations.min_max
      normalization_method(self,metric_name)
    

  def calculate_scores(self):
    for score_name in self.scores:
      metrics_with_weights = self.scores[score_name]

      for node in self.nodes:
        score_value = 0.0

        # get normalized values
        for metric in metrics_with_weights:
          weight = self.scores[score_name][metric]
          value = float(self.redis.hget(self.node_prefix+str(node),metric+self.normalization_suffix))
          score_value += weight * value
          
        self.redis.hset(self.node_prefix+str(node),score_name, score_value)
        self.redis.zadd(self.score_prefix+score_name, score_value, str(node))

  def calculate_advanced_scores(self):
    for advanced_score in self.advanced_scores:
      self.advanced_scores[advanced_score](self)   


  #############
  # statistics
  #############
  
  def calculate_statistics(self):
    for metric in self.base_metrics:
      #absolute and normalized
      statistics.calculate_statistics(self, metric, self.metric_prefix+metric)
      statistics.calculate_statistics(self, metric+self.normalization_suffix, self.metric_prefix+metric+self.normalization_suffix)

    for advanced_metric in self.advanced_metrics:
      #absolute and normalized
      statistics.calculate_statistics(self, advanced_metric, self.metric_prefix+advanced_metric)
      statistics.calculate_statistics(self, advanced_metric+self.normalization_suffix, self.metric_prefix+advanced_metric+self.normalization_suffix)

    for score in self.scores:
      statistics.calculate_statistics(self, score, self.score_prefix+score)

    for advanced_score in self.advanced_scores:
      statistics.calculate_statistics(self, advanced_score, self.score_prefix+advanced_score)

    statistics.calculate_correlations(self)

