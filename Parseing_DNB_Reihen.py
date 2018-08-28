
# coding: utf-8

# # Parse German National Bibliography
# 
# This python script is parsing the [German National Bibliography](http://www.dnb.de/DE/Service/DigitaleDienste/DNBBibliografie/dnbbibliografie_node.html)
# 
# To use this script, you have to be an enregistered user at the German National Library with an active access-token for the SRU-API. 
# 
# ## Configuration
# 
# *  Line#10: Add your Access-Token
# *  Line#4: [DDC-Notation](http://www.dnb.de/SharedDocs/Downloads/DE/DNB/service/ddcSachgruppenDNB.html) to filter the national bibliography
# *  Line#5: Restrict to a specific year (Write '18' for 2018)
# *  Line#6: Choose a specific part ("reihe") of the bibliography
# *  Line#7: You can restrict for a specific number of the weekly publication of the bibliography.
# *  Line#8: If you have advanced knowledge about the CQL for the SRU-API, you can set here a specific Query.
# 

# In[1]:


import xml.etree.ElementTree as ET
import urllib.request

hsgDDC = 'DDC-Notation'
jahr = ''
reihe = 'A'
wvnr = '*'
query = 'hsg%3D' + hsgDDC + '%20' + "%20AND%20WVN%3D" + jahr + "%2C"+ reihe +"" + wvnr
#query = 'sw%3DStadt*' + '%20OR%20sw%3DRegion*' + '%20OR%20sw%3DRaum*' + "%20AND%20WVN%3D" + jahr + "%2C"+ reihe +"" + wvnr
DNBToken = 'YOUR-ACCESS-TOKEN'
maxRec = '100'
startPos = '1'

def buildDNBSRUuri(query,DNBToken,maxRec,startPos):
    DNBSRUuri = 'http://services.dnb.de/sru/dnb?version=1.1&operation=searchRetrieve&query='
    DNBSRUuri = DNBSRUuri + query
    DNBSRUuri = DNBSRUuri +  "&maximumRecords="+maxRec+"&startRecord="+startPos+"&recordSchema=MARC21-xml"
    DNBSRUuri = DNBSRUuri + "&accessToken="+DNBToken
    return DNBSRUuri

DNBSRUuri = buildDNBSRUuri(query,DNBToken,maxRec,startPos)
ns = {'srw' : 'http://www.loc.gov/zing/srw/', 'slim' : 'http://www.loc.gov/MARC21/slim'}

tree = ET.ElementTree(file=urllib.request.urlopen(DNBSRUuri))
root = tree.getroot()

NoR = root.findall(".//srw:numberOfRecords",ns)
runNoRfXml = root.findall(".//srw:recordPosition",ns)
runNoR = runNoRfXml[0].text


def printRecords( root, ns, runNoR):
    for record in root.findall(".//slim:record", ns):
        swRun = 0
        for dnbId in record.findall("slim:controlfield[@tag='001']",ns):
            print("#"+ str(runNoR) +" http://d-nb.info/"+dnbId.text)
        for title in record.findall("slim:datafield[@tag='245']/slim:subfield[@code='a']",ns):
            print(title.text)
        for author in record.findall("slim:datafield[@tag='100']/slim:supbbfield[@code='a']",ns):
            print(author.text)
        for sw in record.findall("slim:datafield[@tag='650']/slim:subfield[@code='a']",ns):
            print(sw.text, "; ", end=' ')
            swRun = 1
        if swRun == 1:
            print('') 
        for DocUrl in record.findall("slim:datafield[@tag='856']/[slim:subfield='kostenfrei']/../slim:datafield[@tag='856']/slim:subfield[@code='u']",ns):
            print(DocUrl.text)
        print("----------------------------")
        runNoR = int(runNoR)+1
    return runNoR
        

while int(runNoR) <  int(NoR[0].text):
    DNBSRUuri = buildDNBSRUuri(query,DNBToken,maxRec,str(runNoR))
    tree = ET.ElementTree(file=urllib.request.urlopen(DNBSRUuri))
    root = tree.getroot()
    runNoR = printRecords( root, ns, runNoR)

