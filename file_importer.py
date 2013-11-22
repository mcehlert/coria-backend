import networkx as nx
import redis as rd

class FileImporter(object):
  def __init__(self,filename):
    self.data_file  = open(filename)
    self.all_nodes  = []
    self.redis      = rd.StrictRedis(host='localhost', port=6379, db=0)
    self.graph      = nx.Graph()

  def read(self):
    self.redis.flushdb()
    for line in self.data_file:
      self.parse_line(line)
    self.save_all_nodes()
    return self.graph

  def parse_line(self, line):
    fields = line.strip().split("\t")
    from_node = int(fields[0])
    to_node = int(fields[1])
    self.all_nodes.extend([from_node,to_node])
    self.graph.add_edge(from_node, to_node)

  def save_all_nodes(self):
    self.unique_nodes = list(set(self.all_nodes))
    self.unique_nodes.sort()
    self.redis.sadd('all_nodes', *self.unique_nodes)