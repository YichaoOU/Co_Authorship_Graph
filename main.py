from Bio import Entrez
from Bio import Medline
import datetime
import sys
from operator import attrgetter
'''
Esearch to find paper id for author
Efetch to return medline text for each paper id

Usage: python test3.py Author Name

Sample:
python test3.py Welch Lonnie 


The script will create a file "author.json"
'''
global author_class_dict
author_class_dict = {}
global count
count = 0


class author:	
	
	def __init__(self,name,id):
		self.name = name
		self.link = []
		self.size = 1
		self.year = 1900
		self.color = ""
		self.affiliation = "Unknown"
		self.id = id
	def set_year(self,year):
		if year>self.year:
			self.year = year
	def add_size(self):
		self.size += 1
	def set_color(self,color):
		self.color = color
	def add_link(self,author):
		self.link.append(author)
	def set_aff(self,affiliation):
		if self.affiliation == "Unknown":
			self.affiliation = affiliation

def first_letter_CAP(x):
	x = x[0].upper()+x[1:]
	return x		
def refine_author_name(x):
	x = x.replace(",","")
	x = x.split()
	if "-" in x[0]:
		y = x[0].split("-")
		y = map(lambda x:first_letter_CAP(x),y)
		x[0] = "-".join(y)
	name = " ".join(x[0:2])
	return name

	
Entrez.email = "unfashionable@unfashionable.me" 


query_author = " ".join(sys.argv[1:])

# print query_author

esearch_handle = Entrez.esearch(db="pubmed", term=query_author,field="Author")
esearch_record_obj = Entrez.read(esearch_handle)
paper_list = esearch_record_obj["IdList"]
# print esearch_record_obj.keys()
# exit()
# query_author = esearch_record_obj["QueryTranslation"]
# query_author = query_author.split("[")
# print query_author
def parse_medline_record(medline_record):
	global count
	for record in medline_record:
		# for k in  record.keys():
			# print k,record[k]
		FAU = record["FAU"]
		FAU = map(lambda x: refine_author_name(x),FAU)
		del FAU[FAU.index(query_author)]
		try:
			Aff = record["AD"].split(";")
			# print count
			# print FAU
			# print record["AD"]
		except:
			Aff = ["Unknown"]*len(FAU)
		# print len(FAU)
		Year = record["DP"].split()[0]
		for i in range(len(FAU)):
			name = FAU[i]
			# if name == query_author:
				# print "asd\nsad\nsdf"
				# continue
			
			if author_class_dict.has_key(name):
				author_class_dict[name].add_size()
			else:
				author_class_dict[name] = author(name,count)
				count += 1
			try:
				author_class_dict[name].set_aff(Aff[i])
			except:
				print "some errors in :",Aff
				
			temp_list = list(FAU)
			
			
			del temp_list[i]
			# print temp_list
			# print name
			for item in temp_list:
			
				author_class_dict[name].add_link(item)
			# print author_class_dict[name]
			author_class_dict[name].set_year(Year)
			
			
		# print FAU[0]
		
		
		# print "Year",Year
		# print "Aff",Aff	

for id in paper_list:
	efetch_handle = Entrez.efetch(db="pubmed", id=id,retmode="text",rettype="medline")
	medline_record = Medline.parse(efetch_handle)	
	parse_medline_record(medline_record)
	# for k in author_class_dict.keys():
		# v = author_class_dict[k]
		# print v
		# print v.name
		# print v.size
		# print v.affiliation
		# print v.link
	# break

nodes=[]
edges=[]
node_template = '{"name":"node_name","affiliation":"node_affiliation","size":node_size,"year":"node_year","color":node_color}'
edge_template = '{"source":source_id,"target":target_id,"value":1}'
color_group = map(lambda x:x.affiliation,author_class_dict.values())
color_group = list(set(color_group))
print color_group
# b = list(author_class_dict.values())
# b.sort(key=attrgetter('id'))
# print b
for v in sorted(author_class_dict.values(), key=attrgetter('id')):
	#{"name":"Brujon","group":4},
	node = node_template.replace("node_name",v.name)
	node = node.replace("node_affiliation",v.affiliation)
	node = node.replace("node_size",str(v.size+5))
	node = node.replace("node_year",str(v.year))
	node = node.replace("node_color",str(color_group.index(v.affiliation)+1))
	nodes.append(node)
	for au in v.link:
		target_id = author_class_dict[au].id
		edge = edge_template.replace("source_id",str(v.id))
		edge = edge.replace("target_id",str(target_id))
		edges.append(edge)
	# print v.name
	# print v.id
	# print v.affiliation
	# print v.link
nodes_output = ",\n\t\t".join(nodes)	
edges_output = ",\n\t\t".join(edges)
output = '{\n\t"nodes":[\n\t\tnodes_output\n\t],\n\t"links":[\n\t\tedges_output\n\t]}'	
output = output.replace("nodes_output",nodes_output)
output = output.replace("edges_output",edges_output)
f=open(query_author+".json","wb")
print >>f,output
# print output

# for k in author_class_dict.keys():
	# v = author_class_dict[k]
	# print v
	# print v.name
	# print v.size
	# print v.affiliation
	# print v.link

