
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import urllib2
import shelve
import time
import re
from collections import Counter
import unicodedata
from operator import itemgetter
import webbrowser
import os
import random
import difflib


# In[2]:


class Environment:
    
    def __init__(self, mode): 
        
        # initializing knn K value from user
        self.mode = mode
        self.noOfClusters = 0
        
        if self.mode == 1:
            try:
                self.k_value = int(raw_input("Enter K value"))
                self.user_keywords = raw_input("Enter The search Keywords\t")
            except:
                print "Oops! Looks like you entered the wrong value,\nplease enter an integer value for k"
                self.__init__(mode)
                
            
            
        if self.mode == 2:
            self.k_value = 15
            try:
                self.noOfClusters = int(raw_input("Enter no of clusters\t"))
                self.user_keywords = raw_input("Enter The search Keywords\t")
            except:
                print "Oops! Looks like you entered the wrong value,\nplease enter an integer value for no of clusters"
                self.__init__(mode)
                
        
        
           
    def showJobs(self):
        agentInstance = Agent()
        agentInstance.sensor(self.user_keywords, self.mode,self.k_value,self.noOfClusters)
        jobLinks = agentInstance.actuator()
        
        if mode == 2:
            jobLinks = self.kMeansClustering(jobLinks,self.noOfClusters)
        
            
        htmlcontent = self.htmlmaker(mode,jobLinks)
        htmlfile = open('CareerResults.html','w')
        htmlfile.write(htmlcontent)
        htmlfile.close()
        webbrowser.open_new_tab('CareerResults.html')
    
    
    
    # Implementation of kMeansClustering 
    def kMeansClustering(self, jobLinks,k):
        
        # For selecting initial seed points from amongst the job links
        
        # selecting initial random seeds
        
        seedlist = []
        for i in range(0,k):
            seedlist.append(len(jobLinks)-(k*(i+1)))
        
        cluster_dict = {}
        index_list = []
        
        
        #jaccard distance
        for index in seedlist:
            seedkeys = jobLinks[index][1].keys()
            cluster_dict[index] = {}
            for i in range(0,len(jobLinks)):
                matches = 0
                if i == index or i in seedlist:
                    continue
                
                currentkeys = jobLinks[i][1].keys() 
                allkeys = set(currentkeys).union(set(seedkeys))
                
                for key in currentkeys:
                    if key in seedkeys:
                        matches +=1
                
                jaccard_similarity = float(matches)/len(allkeys)
                cluster_dict[index][i] = round(jaccard_similarity , 4)
                
                if i not in index_list:
                    index_list.append(i)

        # creating the initial clusters            
        self.initialcluster = {}
        for j in seedlist:
            self.initialcluster[j]=[]
            
        for i in index_list:     
            max_similarity = 0
            for j in seedlist:
                if cluster_dict[j][i] > max_similarity:
                    max_similarity = cluster_dict[j][i]
                    closest_centroid = j
            
            self.initialcluster[closest_centroid].append(i)
            

            
        
        # recursive function for k-means algorithm
        def itercluster(cluster):
            
            newseeds = []
            index_list = []
            
            
            # Finding the highest mode vectors in each cluster to make new centroids
            for key,valuelist in cluster.items():
                max_val = 0
                for index in valuelist:
                    currentvector = jobLinks[index][1]
                    mode = max(currentvector.iteritems(), key=itemgetter(1))[1]
                    if mode > max_val:
                        max_val = mode
                        newCentroid = index
                newseeds.append(newCentroid)
            

            
            #calculate jaccard similarity
            jaccard_dict = {}
            for index in newseeds:
                newseedkeys = jobLinks[index][1].keys()
                jaccard_dict[index] = {}
                for i in range(0,len(jobLinks)):
                    matches = 0
                    if i == index or i in newseeds:
                        continue
                    currentkeys = jobLinks[i][1].keys() 
                    allkeys = set(currentkeys).union(set(newseedkeys))
                
                    for key in currentkeys:
                        if key in newseedkeys:
                            matches +=1
                
                    jaccard_similarity = float(matches)/len(allkeys)
                    jaccard_dict[index][i] = round(jaccard_similarity , 4)


                    if i not in index_list:
                        index_list.append(i)
                
            # creating the new clusters            
            self.newcluster = {}
            for j in newseeds:
                self.newcluster[j]=[]
            
            for i in index_list:     
                max_similarity = 0
                for j in newseeds:

                    if jaccard_dict[j][i] > max_similarity:
                        max_similarity = jaccard_dict[j][i]
                        closest_centroid = j
                        
                self.newcluster[closest_centroid].append(i)
            
            self.curclusterarr = []
            for key, value in self.newcluster.items():
                list1 = value
                list1.append(key)
                self.curclusterarr.append(list1)
                
                
            self.initclusterarr = []
            for key, value in self.initialcluster.items():
                list1 = value
                list1.append(key)
                self.initclusterarr.append(list1)
            print self.curclusterarr
            
            #checking similarity of clusters and returning true for test value
            if self.curclusterarr == self.initclusterarr:
                return self.curclusterarr
            else:
                clusteringscore = 0
                for i in range(0,k-1):
                    similarity=difflib.SequenceMatcher(None,self.curclusterarr[i],self.initclusterarr[i])
                    similarity = round(similarity.ratio(),6)
                    if similarity >= 0.1:
                        clusteringscore +=1
                        
                if clusteringscore >= 1:
                    i=1
                    for row in self.curclusterarr:
                        print "cluster "+str(i)
                        i+=1
                        for element in row:
                            print jobLinks[element][1]
                    print "\n\n\nThank you."
                    exit()
                        
                else: 
                    self.initialcluster = self.newcluster
                    itercluster(self.initialcluster)
                

        itercluster(self.initialcluster)
        
    
    
    
    
    
    #creates html markup for displaying result
    def htmlmaker(self,mode,jobLinks): 
        tablerows = ""
        
        if self.mode == 1:
            algo = "KNN Algorithm with k - value as "+str(self.k_value)
            for row in jobLinks:
                tablerows+='<tr><td><a href="https://'+ row[0]+'style="display:inline;text-overflow:ellipsis;" ">'+row[0]+'</a><td></tr>'
#         else:
#             algo = "KNN Algorithm and clustering algorithm with no. of clusters as"+str(self.noOfClusters)
#             for row in jobLinks:
#                 print row
                

            contents = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"><html>
            <head>
              <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
              <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
              <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
              <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
              <title>Career Center</title>
            </head>
            <body>
         <div class="container">
          <div class="jumbotron">
            <h1>Saketh's Career and Job Center Agent</h1>      
            <p>
            Following are the relusts for the search keywords : ''' + self.user_keywords+'''<br>
            Using 
            '''+ algo +'''</p>
      </div>
    </div>
     <table class="table table-hover"><thead><tr><th>I have found the following job postings for you from www.acm.org, www.indeed.com, www.ieee.org
            </th>
          </tr>
        </thead><tbody>
        '''+tablerows+'''</tbody>
      </table>
    </div>
    </body>
    </html>'''
            return contents

        


# In[3]:


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
        jobLinks = []
        self.lookuptable = lookUpTable(user_keywords)
        self.jobLinks = self.lookuptable.controller()[:k_value]
        
        
    # sends back the results
    def actuator(self):
        return self.jobLinks
    
    
    


# In[4]:



# Stores a persistent lookup table using the shelve package which offers keys to 
# read, write and store data using key values in a file.
class lookUpTable:
    
    def __init__(self, user_keywords):
        
        self.user_keywords = user_keywords.replace(" ","+").upper()
        
        # list of sites to scrape data from after
        self.quote_pages = [
                            "http://jobs.ieee.org/jobs/results/keyword/"+self.user_keywords, 
                            "https://www.indeed.com/jobs?q="+self.user_keywords+"&l=", 
                            "http://jobs.acm.org/jobs/results/keyword/"+self.user_keywords+"?radius=0"
                           ]
        
        self.special_chars = '[^a-zA-Z0-9]'
        
        
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
      'yourselves'
      ]
        
   
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
            
    
    #todo retain special character if user keyword contains it.
    def scrapper(self):
        doc_obj = []
        page = urllib2.urlopen(self.quote_pages[0])
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.findAll('div',attrs={'class': 'aiResultsMainDiv'})
        for div in table:
            titlediv = div.find('div',attrs={'class':'aiResultTitle'})
            link = 'jobs.ieee.org'+titlediv.find('a')['href'],
            description = titlediv.find('a').contents[0]+" "+div.find('div',attrs={'class':'aiResultsDescriptionNoAdvert'}).get_text().strip()[:-19]
            description = self.makeDocObject(description) 
            #  distance calculation
            jaccardSimilarity = round(self.jaccard_similarity(self.user_keywords, description),4)
            doc_obj.append([link[0], description, jaccardSimilarity]) 
   
       
        # scrapper for indeed.com
        page = urllib2.urlopen(self.quote_pages[1])
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.findAll('div',attrs={'class':'row result'})+soup.findAll('div',attrs={'class':' row result'})
        #prepend https://www.indeed.com
        for div in table:
            link = 'www.indeed.com'+div.find('a')['href']
            description =  div.find('a').get_text()+" "+div.find('div',attrs={'class':'paddedSummaryExperience'}).get_text().strip()+" "+ div.find('span',attrs={'class':'summary'}).get_text().strip()
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
            description = titlediv.find('a').contents[0]+" "+div.find('div',attrs={'class':'aiResultsDescriptionNoAdvert'}).get_text().strip()
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
        description = set(description)-set(self.stop_words)
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
    
    


# In[6]:



"""
Exeuciton control for exiting the app
    1 - only KNN algorithm mode
    2 - Clustering mode clusters on 15 links returned by using KNN
# Any arbitrary input is treated as exit
"""

mode = 1

while True:
    try:
        mode = int(raw_input("Enter 1 for KNN only mode or 2 for clustering mode and anything else to exit\t"))
        if mode == 1 or mode == 2:
            CareerAgent = Environment(mode)
            CareerAgent.showJobs()
    except:
        print "Thank you for using Saketh's Career Agent, Good Bye!"
        break
    

    

