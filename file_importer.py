import networkx as nx

class FileImporter(object):

  def __init__(self,filename):
    # initialize data file to parse and new empty graph

    self.data_file  = open(filename)
    self.graph      = nx.Graph()

  def read(self):
    for line in self.data_file:
      self.parse_line(line)
    return self.graph

  def parse_line(self, line):
    # split each line on tabstop
    # first field specifies the source node
    # second field specifies the target node

    fields = line.strip().split("\t")
    from_node = int(fields[0])
    to_node = int(fields[1])

    # add edge to the graph
    self.graph.add_edge(from_node, to_node)
