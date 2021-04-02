'''
Dr. Britt Lundgren
Austin Shank

Created -      06 Dec 2020
Last updated - 08 Mar 2021

--- --- --- --- --- --- --- ---
Panoptes documentation:
https://panoptes-python-client.readthedocs.io/en/v1.1/index.html
https://panoptes-python-client.readthedocs.io/_/downloads/en/latest/pdf/
https://www.zooniverse.org/talk/18/737080?comment=1224201&page=1

--- --- --- --- --- --- --- ---
For easy access:
I AM DELETING THIS PROJECT
'''

''' ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
IMPORTS
'''
import os
import sys
import platform
import multiprocessing  # for multiprocessing parallelism
from multiprocessing import Pool, Lock
coreCount = 1
print(platform.system())
if(platform.system() == 'Linux'):
    coreCount = multiprocessing.cpu_count()
    multiprocessing.set_start_method('fork', force=True)
else:
    coreCount = multiprocessing.cpu_count()
    multiprocessing.set_start_method('spawn', force=True)
print(str(coreCount) + ' available logical processors')
import glob
import ast
import panoptes_client  
from panoptes_client import Panoptes, Project, SubjectSet, Subject
from panoptes_client.panoptes import PanoptesAPIException
from requests.exceptions import ConnectionError
import astropy
from astropy import units as u
from astropy.io import ascii, fits
from astropy.table import Table, unique, Column
import astroquery
import random
import json
import numpy as np
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout
import time

print('Imports complete')
    
''' ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

panoptesConnect - 
Used to connect to a Zooniverse account via username and password using the Panoptes API.

Parameters - 
    user :: String username for account connection.
    pw :: String password for account connection.

Returns - 
    0 :: If we make it through the connection fine, returns zero, else we get an error.

Sample - 
...

--- --- --- --- 
'''
def panoptesConnect(user, pw):
    
    return Panoptes.connect(username=user, password=pw)


''' ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

createZooniverseProject - 
Used to create basic Zooniverse projects using the Panoptes API.

Parameters - 
    projName :: String name of the project.
    projDesc :: String description of the project.
    primLang :: String primary language of the project. For english as primary language, use "en".
    flag_hidden :: Boolean flag for creating public/private project. For private project, use True.

Returns - 
    project :: Zooniverse project we have just created.

Sample - 
createZooniverseProject('sample', 'this is a sample desc', 'en', true)

--- --- --- --- 
'''
def createZooniverseProject(projName, projDesc, primLang, flag_hidden):
    
    print('--- --- --- ---')
    print('Establishing connection to Zooniverse and creating project')
    
    notSaved = True
    saveCheck = 0
    project = None
    connected = False
    
    while not connected:
        url = 'http://zooniverse.org/'
        print('Attempting connection.')
        try:
            response = requests.get(url, timeout=0.2)
        except ConnectionError as ce:
            print(ce)
        except HTTPError as he:
            print(he)
        except Timeout as to:
            print(to)
        else:
            print(response)
            connected = True
    
    while(notSaved and (saveCheck < 5)):
        notSaved = False
        #Make a new project
        project = Project()
        
        #Project name
        #tutorial_project.display_name = ('{}_test'.format(now))
        project.display_name = projName
        saveCheck += 1

        #Project description
        project.description = projDesc

        #Project language
        project.primary_language = primLang
        
        #Project visibility
        project.private = flag_hidden       
                   
        try:
            project.save()
        except PanoptesAPIException as e:
            print('!!! {} , Waiting 10 seconds...'.format(e))
            notSaved = True
            for i in range(0, 10):
                print('... Waiting {}...'.format(i))
                time.sleep(1)
            project.delete()
            saveCheck += 1
            
    print('Project successfully created.')
    
    return project

''' ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

createSubjectSet - 
Used to create subject sets for Zooniverse projects using the Panoptes API.

Parameters - 
    projName :: String name of the project.
    projDesc :: String description of the project.
    primLang :: String primary language of the project. For english as primary language, use "en".
    flag_hidden :: Boolean flag for creating public/private project. For private project, use True.

Returns - 
    subjectSet :: Subject set array to have metadata and subjects added later.

Sample - 
createZooniverseProject('sample', 'this is a sample desc', 'en', true)

--- --- --- --- 
'''
def createSubjectSet(subjName, project):
    
    #Create the subject set
    subjectSet = SubjectSet()
    
    #Link to the appropriate project
    subjectSet.links.project = project
    
    #Set display name of subject set
    subjectSet.display_name = subjName
    
    #Save subject set to the project
    subjectSet.save()
    
    return subjectSet

def deleteFiles(flag_delete, subjTo):
    if(flag_delete):
        deleteThese = glob.glob(subjTo + '/*')    
        for dt in deleteThese:
            #print(dt)
            deleteFiles = glob.glob(dt + '/*')
            for df in deleteFiles:
                #print(df)
                if os.path.exists(df):
                    #print('delete file')
                    os.remove(df)
                else:
                    print("The file does not exist")
            if os.path.exists(dt):
                #print('delete dir')
                os.rmdir(dt)
            else:
                print("The directory does not exist")                
        os.rmdir(subjTo)
    return 0
        
def makeMetadataFile(metadata, newDirStr):
    
    metadataFile = open((newDirStr + '/metadata.txt'), 'w+')
    for key in metadata:
        writeLine = str(key) + ',' + str(metadata[key]) + '\n'
        metadataFile.write(writeLine)
    metadataFile.close()
    
    return 0
    
def unwrapMetadataFile(f):
    
    metadataFile = open(f, 'r')
    
    if f[-5:] == '.txt':
        for line in metadataFile:
            lineSplit = line.split(delim=',')
            metadata[lineSplit[0]] = lineSplit[1]   
        
    return metadata
    
def pushSubject(subjectSet, project, imageLocations, metadata, livePost):
    
    if(livePost):
        subject = Subject()
        subject.links.project = project
        
        for image in imageLocations:
            subject.add_location(image)
            
        subject.metadata.update(metadata)
        
        notSaved = True
        while(notSaved):
            notSaved = False       
            try:
                subject.save()
            except ConnectionError as e:
                print('{} , TRYING AGAIN'.format(e))
                for i in range(0, 5):
                    print('... Waiting {}...'.format(i))
                    time.sleep(1)
                notSaved = True
            
        subjectSet.add(subject) 
        
        return subject
    
    else:
        return None
       
def zooniverseTutorial(args, fs):
    
    mdHead = []
    mdf = glob.glob(fs+'/*.csv')[0]
    
    metadataTable = Table.read(mdf)
    for item in metadataTable:
        print(fs+'/'+item['image'])
        metadata = {}
        metadata['#index'] = str(item['index'])
        metadata['#fileName'] = str(item['image'])
        metadata['ra'] = str(item['ra'])
        metadata['dec'] = str(item['dec'])
        pushSubject(args['subjectSet'], args['project'], [fs+'/'+str(item['image'])], metadata, True)

def unwrapFunction(argsArray):
    
    print('working on ', os.getpid())
    item = argsArray[0]
    args = argsArray[1]
    customArgs = argsArray[2]
    
    args['mainFunction'](item, args, customArgs)
    
    return 0
    
# --- --- --- --- --- --- --- ---

def parseItem(f2, args, customArgs):
    
    args['mainFunction'](f2, args, customArgs)
    
# --- --- --- --- --- --- --- ---

def processFiberList(coreIndex, coreCount, files, args, customArgs):
    
    newSubjects = []
    for k in range(coreIndex, len(files), coreCount):
        if(k%100 == 0):
            print('Parsing file #{} of {}'.format(k, len(files)))
        parseItem(files[k], args, customArgs)   
        
# --- --- --- --- --- --- --- ---

def iterateItems(args, customArgs):
    
    files = []
    for loc in args['datasetLocations']:
        print('Gathering from ', loc)
        if type(loc) in [list, np.array]:
            files.append(loc)
        elif loc[-5:] in ['.fits', '.csv']:
            items = Table.read(loc)
            files.append(items)
        elif os.path.isdir(loc):
            files.append(glob.glob(loc + args['directoryStructure']))
        else:
            print('*Data structure not recognized.*')
            return 0        
    
    print('File total - {}'.format(len(files)))
    coreCount = args['coreCount']
    processList = []
    
    time.sleep(1)
    
    if args['coreCount'] == 1:
        for f in files:
            for item in f:
                parseItem(item, args, customArgs) 
    else:
        args['L_mainLock'] = Lock()
        for count, f in enumerate(files):
            if args['sampleSize'] > 0:
                f = f[0:args['sampleSize']]
            itemsRemain = True
            itemCount = 0
            while(itemCount < len(f)):
                # Remove ended processes
                for p in processList:
                    if p.is_alive() == False:
                        p.close()
                        processList.remove(p)
                # Launch new processes
                while (len(processList) < coreCount) and (itemCount < len(f)):
                    p = multiprocessing.Process(target=parseItem, args=(f[itemCount], args, customArgs))
                    itemCount += 1
                    processList.append(p)
                    p.start()
                    if itemCount % 100 == 0 or itemCount == 1:
                        print('Currently at item', itemCount, 'of', len(f), 'in file', args['datasetLocations'][count])                  
            args['customArgsIndex'] += 1
        '''
        for f in files:
            for coreIndex in range(0, args['coreCount']):
                p = None
                if args['sampleSize'] == -1:
                    p = multiprocessing.Process(target=processFiberList, args=(coreIndex, coreCount, f, args, customArgs))
                else:
                    p = multiprocessing.Process(target=processFiberList, args=(coreIndex, coreCount, f[0:args['sampleSize']], args, customArgs))
                processList.append(p)
                p.start()      
            for p in processList:
                p.join()
            args['customArgsIndex'] += 1
        '''
    print('--- --- --- ---') 
    
def formNewSubjectImages(args, customArgs):
    
    os.mkdir(args['imageDestination'])
    print('imageLocations\tmetadata', file=open(args['imageDestination'] + '/' + 'metadata.txt', 'a'))
    
    iterateItems(args, customArgs)

def makeZooniverseProject(args, customArgs, tutorial=False):
    
    if tutorial == True:
        args['F_livePost'] = True
        
    if(args['F_livePost']):
        #Connect to Zooniverse account
        connection = panoptesConnect(args['username'], args['password'])
        args['zooniverseConnection'] = connection

        #Create new project
        project = createZooniverseProject(args['projectName'], args['projectDescription'], args['primaryLanguage'], args['F_private'])
        args['project'] = project

        #Create new subject set
        subjectSet = createSubjectSet(args['subjectSetTitle'], args['project'])
        args['subjectSet'] = subjectSet
    else:
        args['project'] = None
        args['subjectSet'] = None       

    #Create new subjects and populate project with filled subject set
    if tutorial:
        zooniverseTutorial(args, args['datasetLocations'][0])
    else:
        formNewSubjectImages(args, customArgs)

    return args
    
def pushNewSubjectSet(args, customArgs, projID):
    
    connection = panoptesConnect(args['username'], args['password'])
    args['zooniverseConnection'] = connection

    #Get existing project
    project = Project(projID)
    if project == None:
        print('Could not find this project')
        return None
    print(project.display_name)
    args['project'] = project

    #Create new subject set
    subjectSet = createSubjectSet(args['subjectSetTitle'], args['project'])
    args['subjectSet'] = subjectSet

    #Create new subjects and populate project with filled subject set
    formNewSubjectImages(args, customArgs)

    return args

# --- --- --- --- --- --- --- ---

def pushSubjectFile(args, customArgs):
    
    items = Table.read(f, format='ascii.tab')
    for item in items:
        imageLocations = ast.literal_eval(item['imageLocations'])
        metadata = json.loads(item['metadata'])
        #print(len(imageLocations))
        pushSubject(args['subjectSet'], args['project'], imageLocations, metadata, args['F_livePost'])

# --- --- --- --- --- --- --- ---
     
def run(username, password, projectName, dsLocations, customArgs={}, verbose=False, newProject=True, projID=-1, tutorial=False):
    
    args = {}
    
    args['username'] = username
    args['password'] = password
    args['projectName'] = projectName
    
    if type(dsLocations) == list:
        args['datasetLocations'] = dsLocations
    else:
        args['datasetLocations'] = [dsLocations]
 
    if verbose:
        print('not done')
    else:
        args['projectDescription'] = 'This project was created by ' + username + ' using the Zooniverse Tutorial script.'
        args['primaryLanguage'] = 'en'
        args['subjectSetTitle'] = 'Zooniverse Tutorial Subject Set'
        args['coreCount'] = multiprocessing.cpu_count()
        args['customArgsIndex'] = 0
        args['F_private'] = False
    
    if newProject:
        makeZooniverseProject(args, customArgs, tutorial)
    else:
        pushNewSubjectSet(args, customArgs, projID)
    
    
