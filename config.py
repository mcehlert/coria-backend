#config.py
import metrics
import normalizations
import advancedscores

node_index_key        = 'all_nodes'
metric_index_key      = 'all_metrics'
score_index_key       = 'all_scores'

node_neighbors_prefix = 'node_neighbors:'
node_prefix           = 'node_metrics:'
metric_prefix         = 'metric:'
score_prefix          = 'score:'
statistics_prefix     = 'statistics:'

normalization_suffix  = '_normalized'

# definition of all base metrics for which absolute values will be calculcated for each node in the first step
# key is the name of the metric and value is the implemented method which exposes the required interface
# interface: each method takes the node as the single parameter, performs the necessary calculation and
# returns a float containing the value for the specified node

base_metrics  = { 'clustering_coefficient'          : metrics.clustering_coefficient,
                  'degree'                          : metrics.degree,
                  'average_neighbor_degree'         : metrics.average_neighbor_degree,
                  'iterated_average_neighbor_degree': metrics.iterated_average_neighbor_degree,
                  'betweenness_centrality'          : metrics.betweenness_centrality,
                  'eccentricity'                    : metrics.eccentricity,
                  'average_shortest_path_length'    : metrics.average_shortest_path_length
          }


# some metrics might require some corrections or post processing which relies on the value of other metrics or normalizations
# key is the metric name and value the method for correction

advanced_metrics = {'corrected_clustering_coefficient'          : metrics.correct_clustering_coefficient,
                    'corrected_average_neighbor_degree'         : metrics.correct_average_neighbor_degree,
                    'corrected_iterated_average_neighbor_degree': metrics.correct_iterated_average_neighbor_degree}


# for every metric, a normalization method has to be specified
# key is the name of the metric and value is the normalization method which also has to expose the required interface
# interface: normalization methods, take the name of the (absolute) metric as the single argument, no return value is required
# the method itself shall access the data which is required for normalization from the redis instance
# and the corresponding keys/values for the specified metric
# it shall then loop over all nodes and calculate the normalized value for the node and the metric
# afterwards it should save the result to redis using "metric_name_normalized" as the key
# the result is stored inside the node's hash for metrics

# also needs to include corrected metrics with their respective names
# 
normalization_methods = { 'clustering_coefficient'                    : normalizations.min_max,
                          'corrected_clustering_coefficient'          : normalizations.min_max,
                          'degree'                                    : normalizations.min_max,
                          'average_neighbor_degree'                   : normalizations.min_max,
                          'corrected_average_neighbor_degree'         : normalizations.min_max,
                          'iterated_average_neighbor_degree'          : normalizations.min_max,
                          'corrected_iterated_average_neighbor_degree': normalizations.min_max,
                          'betweenness_centrality'                    : normalizations.min_max,
                          'eccentricity'                              : normalizations.max_min,
                          'average_shortest_path_length'              : normalizations.max_min
                        }


# the easiest case for a score is a combination of normalized metric values with a weight which adds up to 1
# such scores can easily be defined here
# note: names are not methods but redis keys

scores = {'unified_risk_score': { 'degree': 0.25,
                                  'corrected_average_neighbor_degree': 0.15,
                                  'corrected_iterated_average_neighbor_degree': 0.1,
                                  'betweenness_centrality': 0.25,
                                  'eccentricity': 0.125,
                                  'average_shortest_path_length': 0.125}
                      }


# other scores might require a more sophisticated algorithm to be calculated
# such scores need to be added here and implemented like the example below

advanced_scores = {'advanced_unified_risk_score': advancedscores.adv_unified_risk_score}