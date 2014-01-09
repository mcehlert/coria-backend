#metrics.py
import networkx as nx
import numpy as np

def clustering_coefficient(self,node):
  #in the first run calculate the metric for all nodes at once and save in a hash of the instance to access later
  #NOTE: this should result in a performance gain, but for very large graphs this might be a problem.
  #      in this case, just returning nx.clustering(self.graph, node) might be better
  if not hasattr(self, 'all_clustering_coefficients'):
    self.all_clustering_coefficients = nx.clustering(self.graph)

  #get the actual value from the pre-calculated hash
  return self.all_clustering_coefficients[node]

def degree(self, node):
  return self.graph.degree(node)


def average_neighbor_degree(self,node):
  # same caching technique as in self.clustering_coefficient
  # might also break for very large graphs
  # nx.average_neighbor_degree(self.graph, nodes=node) might be the way to go

  if not hasattr(self, 'all_average_neighbor_degrees'):
    self.all_average_neighbor_degrees = nx.average_neighbor_degree(self.graph)
  return self.all_average_neighbor_degrees[node]

def iterated_average_neighbor_degree(self, node):
  
  first_level_neighbors = self.graph.neighbors(node)
  second_level_neighbors = []

  # get all two-hop nodes
  for first_level_neighbor in first_level_neighbors:
    current_second_level_neighbors = self.graph.neighbors(first_level_neighbor)
    second_level_neighbors.extend(current_second_level_neighbors)

  #remove one-hop nodes and self
  relevant_nodes = set(second_level_neighbors) - set(first_level_neighbors) - set([node])
  
  degree_sum = 0
  for relevant_node in relevant_nodes:
    degree_sum += self.graph.degree(relevant_node)

  return float(degree_sum)/float(len(relevant_nodes))

def betweenness_centrality(self, node):
  if not hasattr(self, 'all_betweenness_centralities'):
    self.all_betweenness_centralities = nx.betweenness_centrality(self.graph)
  return self.all_betweenness_centralities[node]

def eccentricity(self, node):
  if not hasattr(self, 'all_eccentricities'):
    self.all_eccentricities = nx.eccentricity(self.graph)
  return self.all_eccentricities[node]

def average_shortest_path_length(self, node):
  # caching average_shortest_path_length for all nodes at one failed
  # already switched to single calculation

  #get all shortest path lengths
  all_shortest_path_lengths_for_node = nx.shortest_path_length(self.graph, source=node)

  #calculate average
  sum_of_lengths = 0
  for target in all_shortest_path_lengths_for_node:
    sum_of_lengths += all_shortest_path_lengths_for_node[target]
  
  return float(sum_of_lengths)/len(all_shortest_path_lengths_for_node)


#############
# advanced metrics
#############
def correct_clustering_coefficient(self,node):
  clustering_coefficient = float(self.redis.hget(self.node_prefix+str(node),'clustering_coefficient'))
  degree = float(self.redis.hget(self.node_prefix+str(node), 'degree'))
  corrected_cc = clustering_coefficient + (degree * clustering_coefficient) / float(4)
  return corrected_cc

def correct_average_neighbor_degree(self,node):
  avgnd = float(self.redis.hget(self.node_prefix+str(node), 'average_neighbor_degree'))
  
  neighbors = self.graph.neighbors(node)
  number_of_neighbors = float(len(neighbors))
  neighbor_degrees = []
  for neighbor in neighbors:
    neighbor_degrees.append(self.graph.degree(neighbor))

  #using numpy median and standard deviation implementation
  numpy_neighbor_degrees = np.array(neighbor_degrees)
  median = np.median(numpy_neighbor_degrees)
  standard_deviation = np.std(numpy_neighbor_degrees)
  
  if avgnd == 0.0 or number_of_neighbors == 0.0 or standard_deviation == 0.0:
    return avgnd
  else:
    return avgnd + ( ((median - avgnd) / standard_deviation) / number_of_neighbors ) * avgnd


def correct_iterated_average_neighbor_degree(self, node):
  avgnd = float(self.redis.hget(self.node_prefix+str(node), 'iterated_average_neighbor_degree'))

  first_level_neighbors = self.graph.neighbors(node)
  second_level_neighbors = []

  # get all two-hop nodes
  for first_level_neighbor in first_level_neighbors:
    current_second_level_neighbors = self.graph.neighbors(first_level_neighbor)
    second_level_neighbors.extend(current_second_level_neighbors)

  #remove one-hop neighbors and self
  relevant_nodes = set(second_level_neighbors) - set(first_level_neighbors) - set([node])

  number_of_nodes = len(relevant_nodes)
  node_degrees = []
  for rel_node in relevant_nodes:
    node_degrees.append(self.graph.degree(rel_node))

  numpy_node_degrees = np.array(node_degrees)
  median = np.median(numpy_node_degrees)
  standard_deviation = np.std(numpy_node_degrees)

  if avgnd == 0.0 or number_of_nodes == 0.0 or standard_deviation == 0.0:
    return avgnd
  else:
    return avgnd + ( ((median - avgnd) / standard_deviation) / number_of_nodes ) * avgnd
  

