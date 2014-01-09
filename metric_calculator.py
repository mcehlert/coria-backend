import networkx as nx
import redis as rd
import numpy as np
import indexing
import statistics
import normalizations
import config


class MetricCalculator(object):
  def __init__ (self, graph):
    self.graph                = graph
    self.redis                = rd.StrictRedis(host='localhost', port=6379, db=0)
    self.nodes                = nx.nodes(graph)

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



#    self.node_index_key        = 'all_nodes'
#    self.metric_index_key      = 'all_metrics'
#    self.score_index_key       = 'all_scores'
#
#    self.node_neighbors_prefix = 'node_neighbors:'
#    self.node_prefix           = 'node_metrics:'
#    self.metric_prefix         = 'metric:'
#    self.statistics_prefix     = 'statistics:'
#
#    self.normalization_suffix  = '_normalized'
#
#    # definition of all base metrics for which absolute values will be calculcated for each node in the first step
#    # key is the name of the metric and value is the implemented method which exposes the required interface
#    # interface: each method takes the node as the single parameter, performs the necessary calculation and
#    # returns a float containing the value for the specified node
#
#    self.metrics  = { 'clustering_coefficient'          : self.clustering_coefficient,
#                      'degree'                          : self.degree,
#                      'average_neighbor_degree'         : self.average_neighbor_degree,
#                      'iterated_average_neighbor_degree': self.iterated_average_neighbor_degree,
#                      'betweenness_centrality'          : self.betweenness_centrality,
#                      'eccentricity'                    : self.eccentricity,
#                      'average_shortest_path_length'    : self.average_shortest_path_length
#                    }
#
#
#    # some metrics might require some corrections or post processing which relies on the value of other metrics or normalizations
#    # key is the metric name and value the method for correction
#
#
#    self.advanced_metrics = { 'corrected_clustering_coefficient'          : self.correct_clustering_coefficient,
#                              'corrected_average_neighbor_degree'         : self.correct_average_neighbor_degree,
#                              'corrected_iterated_average_neighbor_degree': self.correct_iterated_average_neighbor_degree}
#
#
#
#    # for every metric, a normalization method has to be specified
#    # key is the name of the metric and value is the normalization method which also has to expose the required interface
#    # interface: normalization methods, take the name of the (absolute) metric as the single argument, no return value is required
#    # the method itself shall access the data which is required for normalization from the redis instance
#    # and the corresponding keys/values for the specified metric
#    # it shall then loop over all nodes and calculate the normalized value for the node and the metric
#    # afterwards it should save the result to redis using "metric_name_normalized" as the key
#    # the result is stored inside the node's hash for metrics
#
#    # also needs to include corrected metrics with their respective names
#    # 
#    self.normalization_methods = {  'clustering_coefficient'                    : self.min_max_normalization,
#                                    'corrected_clustering_coefficient'          : self.min_max_normalization,
#                                    'degree'                                    : self.min_max_normalization,
#                                    'average_neighbor_degree'                   : self.min_max_normalization,
#                                    'corrected_average_neighbor_degree'         : self.min_max_normalization,
#                                    'iterated_average_neighbor_degree'          : self.min_max_normalization,
#                                    'corrected_iterated_average_neighbor_degree': self.min_max_normalization,
#                                    'betweenness_centrality'                    : self.min_max_normalization,
#                                    'eccentricity'                              : self.inverse_min_max_normalization,
#                                    'average_shortest_path_length'              : self.inverse_min_max_normalization
#                                  }
#    
#    
#    # the easiest case for a score is a combination of normalized metric values with a weight which adds up to 1
#    # such scores can easily be defined here
#    # note: names are not methods but redis keys
#
#    self.scores = {'unified_risk_score': { #'corrected_clustering_coefficient': 0.2,
#                                                  'degree_normalized': 0.25,
#                                                  'corrected_average_neighbor_degree_normalized': 0.15,
#                                                  'corrected_iterated_average_neighbor_degree_normalized': 0.1,
#                                                  'betweenness_centrality_normalized': 0.25,
#                                                  'eccentricity_normalized': 0.125,
#                                                  'average_shortest_path_length_normalized': 0.125} 
#                          }
#
#
#    # other scores might require a more sophisticated algorithm to be calculated
#    # such scores need to be added here and implemented like the example below
#
#    self.advanced_scores = {'advanced_unified_risk_score': self.urs_clustering_coefficient_modification}




    
  def start(self):
    #clean all data in Redis
    self.redis.flushdb()
    
    #index creation
    #self.index_nodes()
    #self.index_neighbors()
    #self.index_metrics()
    #self.index_scores()

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
    indexing.index_nodes(self)
    indexing.index_neighbors(self)
    indexing.index_metrics(self)
    indexing.index_scores(self)


#  def index_nodes(self):
#    self.redis.sadd(self.node_index_key, *self.nodes) 
#
#  def index_neighbors(self):
#    for node in self.nodes:
#      node_neighbors = self.graph.neighbors(int(node))
#      self.redis.sadd(self.node_neighbors_prefix+str(node), *node_neighbors)  
#
#  def index_metrics(self):
#    for metric in self.metrics:
#      self.redis.sadd(self.metric_index_key, metric)
#    
#    for advanced_metric in self.advanced_metrics:
#      self.redis.sadd(self.metric_index_key, advanced_metric)
#
#  def index_scores(self):
#    for score in self.scores:
#      self.redis.sadd(self.score_index_key, score)
#
#    for advanced_score in self.advanced_scores:
#      self.redis.sadd(self.score_index_key, advanced_score)

###########################
#### CALCULATION LOOPS ####
###########################
  # loop through all defined metrics and call specified calculation method for each node
  def calculate_metrics(self):
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

  # loop through all defined_advanced_metrics and call specified calculation method
  def calculate_advanced_metrics(self):
    for advanced_metric_name in self.advanced_metrics:
      metric_method = self.advanced_metrics[advanced_metric_name]
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
    


  
#  # normalizations
#  # min max normalization
#  def min_max_normalization(self,metric_name):
#    #perform min max normalization of specified metric for all nodes
#    #min_max normalization
#    #get min and max from redis
#    x_min = self.redis.zrange(metric_name, 0, 0, withscores=True, score_cast_func=float)[0][1]
#    x_max = self.redis.zrange(metric_name, -1, -1, withscores=True, score_cast_func=float)[0][1]
#    
#    #print x_min
#    #print x_max
#    
#    for node in self.nodes:
#      if x_min == x_max:
#        x_normalized = 1.0
#      else:
#        x = float(self.redis.hget(self.node_prefix+str(node), metric_name))
#        x_normalized = (x - x_min) / (x_max - x_min)     
#    
#      #store value for node and metric
#      self.redis.zadd(metric_name+self.normalization_suffix, x_normalized, str(node))
#      self.redis.hset(self.node_prefix+str(node),metric_name+self.normalization_suffix, x_normalized)
#
#  #max min normalization
#  def inverse_min_max_normalization(self,metric_name):
#    x_min = self.redis.zrange(metric_name, 0, 0, withscores=True, score_cast_func=float)[0][1]
#    x_max = self.redis.zrange(metric_name, -1, -1, withscores=True, score_cast_func=float)[0][1]
#    
#    for node in self.nodes:
#      if x_min == x_max:
#        x_normalized = 1.0
#      else:
#        x = float(self.redis.hget(self.node_prefix+str(node), metric_name))
#        x_normalized = (x_max - x) / (x_max - x_min)     
#
#      #store value for node and metric
#      self.redis.zadd(metric_name+self.normalization_suffix, x_normalized, str(node))
#      self.redis.hset(self.node_prefix+str(node),metric_name+self.normalization_suffix, x_normalized) 
#
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
      

###################################################
# actual metrics and corrections etc. below
# must return value which can be converted to float
###################################################
#
#  def clustering_coefficient(self,node):
#    #in the first run calculate the metric for all nodes at once and save in a hash of the instance to access later
#    #NOTE: this should result in a performance gain, but for very large graphs this might be a problem.
#    #      in this case, just returning nx.clustering(self.graph, node) might be better
#    if not hasattr(self, 'all_clustering_coefficients'):
#      self.all_clustering_coefficients = nx.clustering(self.graph)
#
#    #get the actual value from the pre-calculated hash
#    return self.all_clustering_coefficients[node]
#
#  def degree(self, node):
#    return self.graph.degree(node)
#
#
#  def average_neighbor_degree(self,node):
#    # same caching technique as in self.clustering_coefficient
#    # might also break for very large graphs
#    # nx.average_neighbor_degree(self.graph, nodes=node) might be the way to go
#
#    if not hasattr(self, 'all_average_neighbor_degrees'):
#      self.all_average_neighbor_degrees = nx.average_neighbor_degree(self.graph)
#    return self.all_average_neighbor_degrees[node]
#
#  def iterated_average_neighbor_degree(self, node):
#    
#    first_level_neighbors = self.graph.neighbors(node)
#    second_level_neighbors = []
#
#    # get all two-hop nodes
#    for first_level_neighbor in first_level_neighbors:
#      current_second_level_neighbors = self.graph.neighbors(first_level_neighbor)
#      second_level_neighbors.extend(current_second_level_neighbors)
#
#    #remove one-hop nodes and self
#    relevant_nodes = set(second_level_neighbors) - set(first_level_neighbors) - set([node])
#    
#    degree_sum = 0
#    for relevant_node in relevant_nodes:
#      degree_sum += self.graph.degree(relevant_node)
#
#    return float(degree_sum)/float(len(relevant_nodes))
#
#  def betweenness_centrality(self, node):
#    if not hasattr(self, 'all_betweenness_centralities'):
#      self.all_betweenness_centralities = nx.betweenness_centrality(self.graph)
#    return self.all_betweenness_centralities[node]
#
#  def eccentricity(self, node):
#    if not hasattr(self, 'all_eccentricities'):
#      self.all_eccentricities = nx.eccentricity(self.graph)
#    return self.all_eccentricities[node]
#
#  def average_shortest_path_length(self, node):
#    # caching average_shortest_path_length for all nodes at one failed
#    # already switched to single calculation
#
#    #get all shortest path lengths
#    all_shortest_path_lengths_for_node = nx.shortest_path_length(self.graph, source=node)
#
#    #calculate average
#    sum_of_lengths = 0
#    for target in all_shortest_path_lengths_for_node:
#      sum_of_lengths += all_shortest_path_lengths_for_node[target]
#    
#    return float(sum_of_lengths)/len(all_shortest_path_lengths_for_node)
#
#
##############
## corrections
##############
#  def correct_clustering_coefficient(self,node):
#    clustering_coefficient = float(self.redis.hget(self.node_prefix+str(node),'clustering_coefficient'))
#    degree = float(self.redis.hget(self.node_prefix+str(node), 'degree'))
#    corrected_cc = clustering_coefficient + (degree * clustering_coefficient) / float(4)
#
#    return corrected_cc
#
#  #def correct_clustering_coefficient(self):
#    
#  #  for node in self.nodes:
#  #    clustering_coefficient = float(self.redis.hget(self.node_prefix+str(node),'clustering_coefficient'))
#  #    degree = float(self.redis.hget(self.node_prefix+str(node), 'degree'))
#
#  #    corrected_cc = clustering_coefficient * (degree * clustering_coefficient) / float(4)
#
#  #    self.redis.hset(self.node_prefix+str(node), 'corrected_clustering_coefficient', corrected_cc)
#  #    self.redis.zadd('corrected_clustering_coefficient', corrected_cc, str(node))
#
#  def correct_average_neighbor_degree(self,node):
#    avgnd = float(self.redis.hget(self.node_prefix+str(node), 'average_neighbor_degree'))
#    
#    neighbors = self.graph.neighbors(node)
#    number_of_neighbors = float(len(neighbors))
#    neighbor_degrees = []
#    for neighbor in neighbors:
#      neighbor_degrees.append(self.graph.degree(neighbor))
#
#    #using numpy median and standard deviation implementation
#    numpy_neighbor_degrees = np.array(neighbor_degrees)
#    median = np.median(numpy_neighbor_degrees)
#    standard_deviation = np.std(numpy_neighbor_degrees)
#    
#    if avgnd == 0.0 or number_of_neighbors == 0.0 or standard_deviation == 0.0:
#      return avgnd
#    else:
#      return avgnd + ( ((median - avgnd) / standard_deviation) / number_of_neighbors ) * avgnd
#
#
#  def correct_iterated_average_neighbor_degree(self, node):
#    avgnd = float(self.redis.hget(self.node_prefix+str(node), 'iterated_average_neighbor_degree'))
#
#    first_level_neighbors = self.graph.neighbors(node)
#    second_level_neighbors = []
#
#    # get all two-hop nodes
#    for first_level_neighbor in first_level_neighbors:
#      current_second_level_neighbors = self.graph.neighbors(first_level_neighbor)
#      second_level_neighbors.extend(current_second_level_neighbors)
#
#    #remove one-hop neighbors and self
#    relevant_nodes = set(second_level_neighbors) - set(first_level_neighbors) - set([node])
#
#    number_of_nodes = len(relevant_nodes)
#    node_degrees = []
#    for rel_node in relevant_nodes:
#      node_degrees.append(self.graph.degree(rel_node))
#
#    numpy_node_degrees = np.array(node_degrees)
#    median = np.median(numpy_node_degrees)
#    standard_deviation = np.std(numpy_node_degrees)
#
#    if avgnd == 0.0 or number_of_nodes == 0.0 or standard_deviation == 0.0:
#      return avgnd
#    else:
#      return avgnd + ( ((median - avgnd) / standard_deviation) / number_of_nodes ) * avgnd
#    
#
#
#
#################
##advanced scores
#################
#
#  def urs_clustering_coefficient_modification(self):
#
#    #caching of values
#    all_ccs_normalized = dict(self.redis.zrange('corrected_clustering_coefficient'+self.normalization_suffix, 0, -1, withscores=True, score_cast_func=float))
#    all_urs = dict(self.redis.zrange('unified_risk_score', 0, -1, withscores=True, score_cast_func=float))
#
#    urs_percentile_10 = np.percentile(all_urs.values(), 10)
#    urs_percentile_90 = np.percentile(all_urs.values(), 90)
#
#    for node in self.nodes:
#      #cc_normalized = float(self.redis.hget(self.node_prefix+str(node),'corrected_clustering_coefficient'+self.normalization_suffix))
#      #urs = float(self.redis.hget(self.node_prefix+str(node),'unified_risk_score'))
#
#      cc_normalized = all_ccs_normalized[str(node)]
#      urs = all_urs[str(node)]
#
#
#      if (urs >= urs_percentile_90 or urs <= urs_percentile_10):
#        if (cc_normalized >= 0.25):
#          advanced_unified_risk_score = ((urs * 3.0) + cc_normalized) / 4.0
#        else:
#          advanced_unified_risk_score = urs
#      else:
#        advanced_unified_risk_score = urs
#
#      #save for node  
#      self.redis.hset(self.node_prefix+str(node), 'advanced_unified_risk_score', advanced_unified_risk_score)
#      #save for metric
#      self.redis.zadd('advanced_unified_risk_score', advanced_unified_risk_score, str(node))

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

#
#
#  def calculate_statistics_for_absolute_values(self,metric):
#    all_values = dict(self.redis.zrange(metric, 0, -1, withscores=True, score_cast_func=float)).values()
#    min_value = np.min(np.array(all_values))
#    max_value = np.max(all_values)
#
#    average = np.average(all_values)
#    median = np.median(all_values)
#    standard_deviation = np.std(all_values)
#
#    self.redis.hset(self.statistics_prefix+str(metric), 'min', min_value)
#    self.redis.hset(self.statistics_prefix+str(metric), 'max', max_value)
#    self.redis.hset(self.statistics_prefix+str(metric), 'average', average)
#    self.redis.hset(self.statistics_prefix+str(metric), 'median', median)
#    self.redis.hset(self.statistics_prefix+str(metric), 'standard_deviation', standard_deviation)
#
#  def calculate_statistics_for_normalized_values(self,metric):
#    all_values = dict(self.redis.zrange(metric+self.normalization_suffix, 0, -1, withscores=True, score_cast_func=float)).values()
#    
#    min_value = np.min(all_values)
#    max_value = np.max(all_values)
#
#    average = np.average(all_values)
#    median = np.median(all_values)
#    standard_deviation = np.std(all_values)
#
#    self.redis.hset(self.statistics_prefix+str(metric)+self.normalization_suffix, 'min', min_value)
#    self.redis.hset(self.statistics_prefix+str(metric)+self.normalization_suffix, 'max', max_value)
#    self.redis.hset(self.statistics_prefix+str(metric)+self.normalization_suffix, 'average', average)
#    self.redis.hset(self.statistics_prefix+str(metric)+self.normalization_suffix, 'median', median)
#    self.redis.hset(self.statistics_prefix+str(metric)+self.normalization_suffix, 'standard_deviation', standard_deviation)
#
#
#  def calculate_correlations(self):
#    m = self.metrics.keys()
#    c = self.corrections.keys()
#
#    metrics = m + c
#
#    correlations = {}
#    for metric1 in metrics:
#      correlations[metric1] = {}
#      for metric2 in metrics:
#        correlations[metric1][metric2] = (0,0)
#        if metric1 == metric2:
#          correlations[metric1][metric2] = (1,0)
#          continue
#
#        dict_metric1 = dict(self.redis.zrange(metric1, 0, -1, withscores=True, score_cast_func=float))
#        dict_metric2 = dict(self.redis.zrange(metric2, 0, -1, withscores=True, score_cast_func=float))
#        values_metric1 = []
#        values_metric2 = []
#
#        for key in sorted(dict_metric1.iterkeys()):
#          values_metric1.append(dict_metric1[key])
#
#        for key in sorted(dict_metric2.iterkeys()):
#          values_metric2.append(dict_metric2[key])
#
#        correlations[metric1][metric2] = pearsonr(values_metric1,values_metric2)
#
#    values_metric1 = []
#    values_metric2 = []
#
#    for source in correlations:
#      for target in correlations[source]:
#        self.redis.hset("correlations:"+source+":"+target, "correlation", correlations[source][target][0])
#        self.redis.hset("correlations:"+source+":"+target, "confidence", correlations[source][target][1])