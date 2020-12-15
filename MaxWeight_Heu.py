import csv
import numpy
import networkx as nx
import matplotlib.pyplot as plt
import copy
import time
import sys

M_vector=numpy.array([1000,2000,3000,4000,5000])
tran_max=1000

#Importing the set of edges
bi_edges=numpy.loadtxt("ripple_graph.txt",dtype=int)
bi_edges=numpy.unique(bi_edges,axis=0)

#Making a graph from the given set of edges
wei=numpy.ones(len(bi_edges)) #initializing the weights of the edges
bi_G = nx.DiGraph() #Initializing the directed graph
for i in range(0,len(bi_edges)):
    bi_G.add_weighted_edges_from([(bi_edges[i,0], bi_edges[i,1],wei[i])]) #adding edges to the graph and assigning weights

#Importing Transactions
with open('transactions.csv') as csvDataFile:
    tran=csv.reader(csvDataFile)
    tran=list(tran) #converting the imported data into a list
    tran=numpy.array(tran) #converting the list into numpy array
tran=numpy.ndarray.astype(tran,float)
k=0
for i in range(0,len(tran)):
    if tran[i,2]>tran_max:
        tran=numpy.delete(tran,obj=i,axis=0) #removing all the transactions that are greater than tran_max
    k=k+1
    if len(tran)<k:
        break

def minwp_heu(G,s,d,tran,K): 
    X=nx.shortest_simple_paths(G,s,d,'imbalance') 
    #returns a generator which returns one path at a time from shortest to longest
    weight2=100000 #initialize by a very large number
    for j, path in enumerate(X): #enumerate shortest to longest paths 
        weight1=0 #initialize by 0 to calculate the weight of path
        for k in range(0,len(path)-1):
            weight1=weight1+G[path[k]][path[k+1]]['weight']-G[path[k+1]][path[k]]['weight'] 
            #calculating the actual weight of path p
        if min(weight1,weight2)==weight1 and weight1!=weight2: #comparing with the best weight obtained so far
            min_wei_path=path #picking the minimum weight path
            weight2=weight1 #updating the best weight obtained so for
        if j == K-1: #break after looking at K shortest paths according to the imbalance
            break
    var=1
    for l in range(0,len(min_wei_path)-1):
        s=min(G[min_wei_path[l]][min_wei_path[l+1]]['weight'],G[min_wei_path[l+1]][min_wei_path[l]]['weight'],M)
        if G[min_wei_path[l]][min_wei_path[l+1]]['weight']+tran-s>M: 
            #Checking if a has enough capacity to route tran
            var=0
    if var!=0:
        return min_wei_path #We will either get a path from s to d or 0 if min_wei_path cannot route tran
    else:
        return 0

def UpdateWeights(G,path,tran):
    for i in range(0,len(path)-1):
        s=min(G[path[i]][path[i+1]]['weight'],G[path[i+1]][path[i]]['weight'],M) #calculating the amount of service
        G[path[i]][path[i+1]]['weight']=G[path[i]][path[i+1]]['weight']+tran-s
        G[path[i+1]][path[i]]['weight']=G[path[i+1]][path[i]]['weight']-s
        bi_G[path[i]][path[i+1]]['imbalance']=max(bi_G[path[i]][path[i+1]]['weight']
            -bi_G[path[i+1]][path[i]]['weight'],0)#initializing the weights
        bi_G[bi_edges[k,1]][bi_edges[k,0]]['imbalance']=max(bi_G[path[i+1]][path[i]]['weight']
            -bi_G[path[i]][path[i+1]]['weight'],0) #initializing the weights
    return G

for argument in range(1,len(sys.argv)):
    M=M_vector[int(sys.argv[argument])]
    no_of_succ_tran=0
    amount_of_succ_tran=0
    total_buffer=0
    for k in range(0,len(bi_edges)):
        bi_G[bi_edges[k,0]][bi_edges[k,1]]['weight']=0.01/len(bi_edges) #initializing the weights
        bi_G[bi_edges[k,0]][bi_edges[k,1]]['imbalance']=0 #initializing the imbalance
    for i in range(0,len(tran)):
        min_wei_path=minwp_heu(bi_G,tran[i,0],tran[i,1],float(tran[i,2]),1) #finding the minimum weighted path from sender to reciever
        if min_wei_path!=0: #If a path exists
            bi_G=UpdateWeights(bi_G,min_wei_path,tran[i,2]) #Route the transaction using min_wei_path
            no_of_succ_tran=no_of_succ_tran+1
            amount_of_succ_tran=amount_of_succ_tran+tran[i,2]
        print(no_of_succ_tran, "out of", i)
    for i in range(0,len(bi_edges)):
        total_buffer=total_buffer+bi_G[bi_edges[i,0]][bi_edges[i,1]]['weight']
    f = open("max_weight_heu.txt","a+")
    f.write('------------------------------------')
    f.write("\r\n")
    f.write("no_of_succ_tran =%f," %no_of_succ_tran)
    f.write("\r\n")
    f.write("amount_of_succ_tran=%f" %amount_of_succ_tran)
    f.write("\r\n")
    f.write("total_buffer = %f," %total_buffer)
    f.write("\r\n")
    f.write("M = %f," %M)
    f.write("\r\n")
    f.write('------------------------------------')
    f.write("\r\n")
    f.close()