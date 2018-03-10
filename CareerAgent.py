"""
Intelligent Career Agent 
Created by Saketh Saxena
Last tested 9/29
Requirements: Python 2.7.10 and above, beautifulsoup, webbrowser

No external packages except BeautifulSoup used.
"""

try:
    from bs4 import BeautifulSoup
except:
    print "Please install beautiful soup"


import urllib2
import shelve
import time
import re
from collections import Counter
try:
    import unicodedata
except:
    print "Please install unicodedata"

from operator import itemgetter

try:
    import webbrowser
except:
    print "Please install webbrowser packcage"
import os
import random

# Is a default python library and comes pre-installed in almost versions of python
try:
    import difflib
except:
    print "Please install difflib"



class Environment:
    
    def __init__(self, mode): 
        
        # initializing variables

        self.mode = mode
        self.noOfClusters = 0

        # Mode 1 signifies user wants only KNN result, so taking input accordingly        
        if self.mode == 1:
            try:

                self.k_value = int(raw_input("Enter K value\t"))
                self.user_keywords = raw_input("Enter The search Keywords\t")
            except:

                print "Oops! Looks like you entered the wrong value,\nplease enter an integer value for k\n"
                self.__init__(mode)
                
            
        # Mode 2 signifies user wants to run k means clustering algorithm
        if self.mode == 2:
            # Here the KNN algorithm will use the default value of k as 15 for clustering
            self.k_value = 15
            try:
                self.noOfClusters = int(raw_input("Enter no of clusters\t"))
                self.user_keywords = raw_input("Enter The search Keywords\t")
            except:
                print "Oops! Looks like you entered the wrong value,\nplease enter an integer value for no of clusters\n"
                self.__init__(mode)
            
                
        
        
    # Environment controller function which returns the result
    def performJobs(self):

        # The agent is instantiated
        agentInstance = Agent()

        # Percepts are sent to the sensor
        agentInstance.sensor(self.user_keywords, self.mode,self.k_value,self.noOfClusters)
        
        # Actuator returns k nearest job links
        self.jobLinks = agentInstance.actuator()
        
        # If run in mode 2, 15 or less jobs(depending on the total number of jobs found by search)
        #  will be returned
        #  and we call the KMeans function to cluster them together
        if mode == 2:
            self.iterator = 0
            self.jobLinkids = self.kMeansClustering()

            # preprocessing the links sent to the htmlmaker
            
            clusterLinks = []
            for row in self.jobLinkids:
                clusterLinks.append([self.jobLinks[index][0] for index in row])

            self.jobLinks = clusterLinks

        # Write the self.jobLinks output to a html file and open it. 
        # This file is rewritten for every input.
        htmlcontent = self.htmlmaker(mode)
        htmlfile = open('CareerResults.html','w')
        htmlfile.write(htmlcontent)
        htmlfile.close()
        webbrowser.open_new_tab('CareerResults.html')
    
    
    
    # Implementation of kMeansClustering 
    # k is the number of clusters
    def kMeansClustering(self):
        clusters = []
        self.oldClusters = None
        self.oldAverage = None
        
        # Generate random centroids from within the data points for first iteration
        while True:
            if self.oldClusters == None:
                centroids = random.sample(range(0,len(self.jobLinks)),self.noOfClusters)
                
            else:
                centroids = [self.getCentroids(value) for key, value in self.clustersMatrix.items()]

            # Gives the jaccard's similarities of the data points with the centroids
            similarityMatrix = self.jaccardSimilarityMatrix(centroids)
            # creates the clusterMatrix with centroids as keys and data points as a list of values
            self.clustersMatrix = self.createClusterMatrix(similarityMatrix, centroids)
            # combines the keys and values to give all points within a cluster for individual clusters 
            # as a list of lists
            clusters = self.createClusters(self.clustersMatrix)



            # If there is 100 % convergence then break out of the loop and return the final cluster
            if clusters == self.oldClusters:
                self.oldClusters = None
                break
            else:
                sm = 0
                total = 0
                averagesm = 0

                if self.oldClusters != None:
                    for index in range(self.noOfClusters):
                        sm = difflib.SequenceMatcher(None, self.oldClusters[index], clusters[index])
                        total += sm.ratio()   
                    averagesm = round((float(total)/self.noOfClusters),4)

                    try:
                        # Executing stopping condition to prevent loop from iterating 
                        # forever in case an exact cohesion isn't found
                        # Set stopping condition as the average Gestalt pattern matching similarity ratio;
                        # 
                        #  
                        # similarity ratio between the previous and current cluster
                        # should be greater than 0.7 or the variance between the oldAverage and the new Average must not be greater 
                        # than 0.1 (which is about 10% variance) and 30% dissimilarity is allowed.
                        if 0 <= abs(averagesm - self.oldAverage) <=0.1  or averagesm > 0.7:
                            break
                        else:
                            self.oldAverage = averagesm    
                    except:                       
                        self.oldAverage = averagesm

                self.oldClusters = clusters
                
        return clusters


    # Calculates centroids by selecting the vector with the highest mode in a cluster
    def getCentroids(self,pInCluster):
        max_val = 0
        new_center = 0
        for index in pInCluster:
            mode =  max(self.jobLinks[index][1].iteritems(), key=itemgetter(1))[1]
            if mode > max_val:
                max_val = mode
                new_center = index
        return new_center



    # Creates the actual clusters using the maximum similarity value to associate centroids to data points.
    def createClusterMatrix(self, similarityMatrix, centroids):
        clusterMatrix = {}
        for centroid in centroids:
            clusterMatrix[centroid]= []

        for key,value in similarityMatrix.items():
            closestCentroid = max(value.iteritems(), key=itemgetter(1))[0]
            clusterMatrix[closestCentroid].append(key)
        return clusterMatrix
    

    # Takes clustersMatrix as input and converts the dictionary into a list of lists 
    # with all the data points for each cluster to later compare the convergence amongst the clusters
    # across iterations
    def createClusters(self,clustersMatrix):     
        initialClusters = [] 
        for key, value in clustersMatrix.items():
            list1 = value
            list1.append(key)
            initialClusters.append(list1)   
        return initialClusters

    # Returns similarity matrix for clustering
    # transposing the similarity matrix and 
    # selecting the highest value of similarity gives us clusters of similar points/ least distance. 

    def jaccardSimilarityMatrix(self, centroids):
        similarityMatrix = {}
        i = 0
        for row in self.jobLinks:
            setofWords = set(row[1].keys())
            # print setofWords
            if i not in centroids:
                similarityMatrix[i] = {}
                for index in centroids:
                    matches = 0
                    similarityMatrix[i][index]={}
                    currCentroidWords = set(self.jobLinks[index][1])
                    for word in currCentroidWords:
                        if word in setofWords:
                            matches+=1
                    curr_similarity = round(float(matches)/len(setofWords.union(currCentroidWords)), 4)
                    similarityMatrix[i][index] = curr_similarity
            i+=1
        return similarityMatrix
    
    
    
    # Creates html markup for displaying result
    def htmlmaker(self,mode): 
        tablerows = ""

        # Encodes tablerows to write to html if table rows is not empty
        # returns no results found message if tablerows are empty 
        def checkTableRows(tablerows):
            # If there were some search results, encode the links to avoid string encoding errors and add them to html
            if tablerows != "":
                tablerows = unicodedata.normalize('NFKD', tablerows).encode('ascii','ignore')
            else:
                # else show no results message and delete the entry from the shelve
                tablerows = "<tr><td>Oops! looks like there were no results for this query, try a different combination</td></tr>"
                lookup_shelve = shelve.open('careerlookup')
                del lookup_shelve[self.user_keywords.upper().replace(" ","+")]
                lookup_shelve.close()
            return tablerows

        # If mode is KNN only, the results will be represented as table rows.
        if self.mode == 1:
            algo = "KNN Algorithm with k - value as "+str(self.k_value)
            for row in self.jobLinks:
                tablerows+='<tr><td><a href="https://'+ row[0]+'" style="display:block;overflow:hidden; width:1000px;text-overflow:ellipsis;">'+row[0]+'</a></td></tr>'

            tablerows = checkTableRows(tablerows)

        
        #else running in clustering mode, the results will be represented as clusters
        else:
            algo = "KNN Algorithm and clustering algorithm with "+str(self.noOfClusters)+" clusters."
            lookup_shelve = shelve.open('careerlookup')
            i = 1
            for cluster in self.jobLinks:
                tablerows += '<tr><ul><h3>Cluster '+str(i)+'</h3>'
                for link in cluster:
                    tablerows+='<li><a href="https://'+link+'" style="display:block-inline;text-overflow:ellipsis;">'+link+'</a></li>'
                tablerows+='</ul></tr><hr style="height:1px;border:none;color:#333;background-color:#333;">'
                i+=1
            # Encodes tablerows to write to html if table rows is not empty
            # returns no results found message if tablerows are empty
            tablerows = checkTableRows(tablerows)
            
        # initializing the HTML string to display result in browser
        contents = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"><html><head>
            <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
                <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
                <title>Career Center</title></head><body>
            <div class="container">
            <div class="jumbotron">
            <h3>Saketh's Career and Job Center Agent</h3> 
            <p style="font-size:20px;">
            Following are the relusts for the search keywords : ''' + self.user_keywords+'''<br>
            Using '''+ algo +'''<br><hr><br><small>job postings from from www.acm.org, www.indeed.com and www.ieee.org</small></p></div></div><table class="table table-hover"><thead</thead>
            <tbody>
            '''+ tablerows +'''
            </tbody></table>
            </div>
            
            </body></html>'''
        return contents

        




class Agent:
    
#    Recieves the keywords, mode, k_value and no of clusters from the environment and passes them to agent
    def sensor(self, user_keywords, mode, k_value,nClusters):
        self.user_keywords = user_keywords
        self.mode = mode
        self.k_value = k_value
        self.nClusters = nClusters
        self.agentFunction(self.user_keywords, self.mode,self.k_value,self.nClusters)

    # Searches the lookup table and returns the k job links based on knn, which  I have optimized and designed
    # while generating the lookuptable
    def agentFunction(self, user_keywords, mode, k_value,nClusters):
        self.jobList = []
        self.lookuptable = lookUpTable(user_keywords)
        self.jobList = self.lookuptable.controller()[:k_value]
        
        
    # sends back the results
    def actuator(self):
        return self.jobList
    
    
    





# Stores a persistent lookup table using the shelve package which offers keys to 
# read, write and store data using key values in a file.
class lookUpTable:
    
    def __init__(self, user_keywords):
        
        self.user_keywords = user_keywords.replace(" ","+")
        
        # list of sites to scrape data from after
        self.quote_pages = ["http://jobs.ieee.org/jobs/results/keyword/"+self.user_keywords, 
                            "https://www.indeed.com/jobs?q="+self.user_keywords+"&l=", 
                            "http://jobs.acm.org/jobs/results/keyword/"+self.user_keywords+"?radius=0"]
        self.user_keywords = self.user_keywords.upper()
        
        self.special_chars = '[^a-zA-Z0-9]'
        
        # list of stop words which are filtered out  
        self.stop_words = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are',
      'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
      'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down',
      'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t',
      'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself',
      'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it',
      'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of',
      'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same',
      'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that',
      'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they',
      'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up',
      'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s',
      'when', 'when\'s', 'where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with',
      'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself',
      'yourselves']
        
   
    # Logic to check if the search words are there in the table already
    # also checks to update the table ever 24 hours.
    def controller(self):
        # Open shelve file
        self.lookup_shelf = shelve.open('careerlookup')
        doc_obj = []
        # if keywords already in shelve check for time difference
        self.stop_words = [word.upper() for word in self.stop_words]
        if self.user_keywords in self.lookup_shelf.keys():

            old_time = self.lookup_shelf[self.user_keywords][1]
            new_time = time.time()
            
            #if time difference greater than 24 hours scrap the web again
            if new_time - old_time >  86400:
                doc_obj = self.scrapper()
            else:
                # else return the object from the shelve
                doc_obj = self.lookup_shelf[self.user_keywords][0]

        else:
            # scrap for search keywords 
            doc_obj = self.scrapper()

        self.lookup_shelf.close()
        return doc_obj
            
    
    #@todo retain special characters if user keyword contains it.
    def scrapper(self):
        doc_obj = []
        # scrapper ieee.org
        page = urllib2.urlopen(self.quote_pages[0])
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find_all('div',attrs={'class': 'aiResultsMainDiv'})
        
        for div in table:
            titlediv = div.find('div',attrs={'class':'aiResultTitle'})
            link = 'jobs.ieee.org'+titlediv.find('a')['href'],
            try:
                description = titlediv.find('a').contents[0]+" "+ div.find('div',attrs={'class':'aiClearfix'}).get_text.strip()[:-19]
            except:
                description = None
            if description != None:
                description = self.makeDocObject(description) 
                #  distance calculation
                jaccardSimilarity = round(self.jaccard_similarity(self.user_keywords, description),4)
                doc_obj.append([link[0], description, jaccardSimilarity]) 
   
       
        # scrapper for indeed.com
        page = urllib2.urlopen(self.quote_pages[1])
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.findAll('div',attrs={'class':'result'})
        # +soup.findAll('div',attrs={'class':' row result'})

        for div in table:
            link = 'www.indeed.com'+div.find('a')['href']
            try:
                description =  div.find('a').get_text()+" "+div.find('div',attrs={'class':'paddedSummaryExperience'}).get_text().strip()+" "+ div.find('span',attrs={'class':'summary'}).get_text().strip()
            except:
                description = None
            if description != None:
                description = self.makeDocObject(description) 
                #  distance calculation and storing 
                jaccardSimilarity = round(self.jaccard_similarity(self.user_keywords, description),4)
                doc_obj.append([link, description, jaccardSimilarity]) 


        # scrapper for acm.org
        page = urllib2.urlopen(self.quote_pages[2])
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.findAll('div',attrs={'class': 'aiResultsMainDiv'})
        for div in table:
            titlediv = div.find('div',attrs={'class':'aiResultTitle'})
            link = 'jobs.acm.org'+titlediv.find('a')['href'], 
            try:
                description = titlediv.find('a').contents[0]+" "+div.find('div',attrs={'class':'aiClearfix'}).get_text().strip()[:-19]
            except:
                description = None
            if description != None:
                description = self.makeDocObject(description) 
                #  distance calculation
                jaccardSimilarity = round(self.jaccard_similarity(self.user_keywords, description),4)
                doc_obj.append([link[0], description, jaccardSimilarity]) 
        
        doc_obj = sorted(doc_obj, key=itemgetter(2), reverse= True)
        self.lookup_shelf[self.user_keywords] = (doc_obj,time.time())
        return doc_obj
        
    # preprocessing the text data, filtering data using stop words and removing special characters, converting to upper case and encoding the text
    def makeDocObject(self, description):
        description = unicodedata.normalize('NFKD', description).encode('ascii','ignore')
        description = description.upper()
        description = re.sub(self.special_chars," ", description)
        description = description.split(" ") 
        description = filter(None ,description)
        description = l3 = [x for x in description if x not in self.stop_words]
        description = Counter(description)
        return description
    
    #preprocessing the similarity metrics using jaccardian similarity
    def jaccard_similarity(self, keywords, description):
        matches = 0.0
        for keyword in keywords.split('+'):
            if keyword in description.keys():
                matches = matches + 1
        finalset = set(description.keys()).union(set(keywords.split("+")))
        return float(matches)/len(finalset)
    
    




"""
Exeuciton control for exeucting the script
    1 - only KNN algorithm mode
    2 - Clustering mode clusters on 15 links returned by using KNN
    Any arbitrary input is treated as exit
"""

mode = 1

while True:
    # try:
    mode = int(raw_input("Enter 1 for KNN only mode or 2 for clustering mode and anything else to exit\t"))
    if mode == 1 or mode == 2:
        CareerAgent = Environment(mode)
        CareerAgent.performJobs()
    # except:
    #     print "Thank you for using Saketh's Career Agent, Good Bye!"
    #     break
    

    

