#redis test
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

nodes = [1,2,3,4,5,6,7,8,9]
for node in nodes:
  print str(node)
  print r.get('node:'+str(node)+':degree')
  print r.get('node:'+str(node)+':average_neighbor_degree')
  print r.get('node:'+str(node)+':eccentricity')
  print r.get('node:'+str(node)+':betweenness_centrality')
  print r.get('node:'+str(node)+':clustering_coefficient')
  print r.get('node:'+str(node)+':average_shortest_path_length')



print r.get('all_nodes').strip('[]').split(', ').type()