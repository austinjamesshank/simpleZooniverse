'''
Dr. Britt Lundgren
Austin Shank

Created -      06 Dec 2020
Last updated - 14 May 2021

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
if 'google.colab' in str(get_ipython()):  
    from google.colab import drive
    
import os
import sys
import platform
import multiprocessing 
from multiprocessing import Pool, Lock

coreCount = 1
print('OS:', platform.system())
if(platform.system() == 'Linux'):
    coreCount = multiprocessing.cpu_count()
    multiprocessing.set_start_method('fork', force=True)
else:
    coreCount = multiprocessing.cpu_count()
    multiprocessing.set_start_method('spawn', force=True)
print('{} available processors.'.format(coreCount))

import glob
import ast
import panoptes_client  
from panoptes_client import Panoptes, Project, SubjectSet, Subject
from panoptes_client.panoptes import PanoptesAPIException
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
import getpass

print('Imports complete')
print('---')
    
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
        
    if user == None:
        print('Enter your Zooniverse username')  
        user = input('Username: ')
    if pw == None:
        print('Enter your Zooniverse password')
        pw = getpass.getpass('Password: ')
    
    notConnected = True
    while notConnected:
        notConnected = False
        try:    
            connection = Panoptes.connect(username=user, password=pw)
        except PanoptesAPIException as e:
            notConnected = True
            print(e)
            if str(e) == 'Invalid email or password.':
                print('Please re-enter your Zooniverse username and password')  
                user = input('Username: ')
                pw = getpass.getpass('Password: ')
                    
    return connection, user, pw


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
    print('Confirming connection to Zooniverse...')
    
    notSaved = True
    saveCheck = 0
    project = None
    connected = False
    copyNum = 1
    ogName = projName
    
    while not connected:
        url = 'http://zooniverse.org/'
        try:
            response = requests.get(url, timeout=0.2)
        except ConnectionError as ce:
            print(ce)
        except HTTPError as he:
            print(he)
        except Timeout as to:
            print(to)
        else:
            print('\tConnection confirmed.')
            connected = True
    
    print('--- --- --- ---')
    print('Creating a new project.')
    while(notSaved and (saveCheck < 100)):
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
            #print(type(e))
            #print(e)
            if str(e) == 'Validation failed: Display name Must be unique for owner':
                if copyNum == 1:
                    print('!!! {}. Trying a duplicate name.'.format(e))
                projName = ogName + ' {}'.format(copyNum)
                copyNum += 1
            else:
                print('!!! {} , Waiting 5 seconds...'.format(e))
                for i in range(0, 5):
                    time.sleep(1)
                project.delete()
                saveCheck += 1
            notSaved = True
    
    if not notSaved:                  
        print('\tCreated project: {}'.format(projName))
        return project
    else:
        print('\tFailed to create project.')
        return None

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
                print('!!! {} , TRYING AGAIN'.format(e))
                for i in range(0, 5):
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
        elif loc[-5:] == '.fits' or loc[-4:] == '.csv':
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
        #sys.stdout.write("]\n")
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
            args['customArgsIndex'] += 1
    print('--- --- --- ---') 
    
def formNewSubjectImages(args, customArgs):
    
    os.mkdir(args['imageDestination'])
    print('imageLocations\tmetadata', file=open(args['imageDestination'] + '/' + 'subject.aus', 'a'))
    
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
        if project == None:
            return None
        args['project'] = project

    else:
        args['project'] = None
        args['subjectSet'] = None       

    #Push images and metadata
    pushNewSubjectSet(args, customArgs, args['project'], False)

    return args
    
def pushNewSubjectSet(args, customArgs, project, needImages):

    #Get existing project
    if project == None:
        print('!!! Could not find this project.')
        return None
    print(project.display_name)
    args['project'] = project

    subjectSet = None
    #Create new subject set
    if args['subjSetID'] == -1:
        subjectSet = createSubjectSet(args['subjectSetTitle'], args['project'])
    else:
        subjectSet = SubjectSet(args['subjSetID'])
        if subjectSet == None:
            print('!!! Could not find this subject set.')
            return None
    args['subjectSet'] = subjectSet
    
    if needImages:
        #Create new subjects and populate project with filled subject set
        formNewSubjectImages(args, customArgs)
    else:
        print('Pushing subject set.')
        for fPath in args['datasetLocations']:
            csv = glob.glob(fPath + '/*.csv')
            aus = glob.glob(fPath + '/*.aus')
            f = None
            if len(csv) > 0:
                f = csv[0].split('/')[-1]
                print('Found .csv manifest: {}'.format(f))
            elif len(aus) > 0:
                f = aus[0].split('/')[-1]
                print('Found .aus manifest: {}'.format(f))
            else:
                print('No manifest file found.')
                print('\tCreating basic manifest file: {}'.format(fPath+'/'+'subjects.aus'))
                currentLock = Lock()
                print('imageLocations\tmetadata', file=open(fPath + '/' + 'subjects.aus', 'a'))
                for img in glob.glob(fPath + '/*'):
                    if img[-3:] != 'aus':
                        printSubjectInfo([img], {}, fPath, currentLock)
                f = 'subjects.aus'
                if args['colab']:
                    drive.mount('/content/drive', force_remount=True)
            pushSubjectFile(f, fPath, args)
            print('--- --- --- ---')
        
    return args

# --- --- --- --- --- --- --- ---

def pushSubjectFile(f, fPath, args):
    
    fullPath = fPath[:fPath.rfind('/')]
    extension = f.split('.')[-1]
    #print(f)
    #print(fPath)
    #print(fullPath)
    #print('File is {}'.format(extension))
    if extension == 'aus':
        items = Table.read(fPath+'/'+f, format='ascii.tab')
        for item in items:
            imageLocations = ast.literal_eval(item['imageLocations'])
            metadata = json.loads(item['metadata'])
            #print(len(imageLocations))
            pushSubject(args['subjectSet'], args['project'], imageLocations, metadata, args['F_livePost'])
    elif extension == 'csv':
        items = Table.read(fPath+'/'+f)
        #print('Pushing subjects from {}'.format(f))
        for item in items:
            imageLocations = []
            metadata = {}
            for i, col in enumerate(item):
                col = str(col)
                if os.path.splitext(col)[1].lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
                    imgExt = os.path.splitext(col)[1]
                    #print(imgExt)
                    imageLocations.append(fullPath + '/' + col)
                else:
                    metadata[items.colnames[i]] = col
            pushSubject(args['subjectSet'], args['project'], imageLocations, metadata, args['F_livePost'])
    else:
        items = glob.glob(fPath + '/*')
        for item in items:
            imageLocations = [item]
            metadata = {}
            pushSubject(args['subjectSet'], args['project'], imageLocations, metadata, args['F_livePost'])

# --- --- --- --- --- --- --- ---

def printSubjectInfo(imgs, metadata, dest, lock):
    
    lock.acquire()
    try:
        print('{}\t{}'.format(str(imgs), str(metadata)), file=open(dest + '/' + 'subjects.aus', 'a'))
    finally:
        lock.release() 
        
# --- --- --- --- --- --- --- ---
     
def run(username=None, password=None, makeImages=False, projID=-1, subjSetID=-1, projectName='Simple Zooniverse Project', dsLocations=None, customArgs={}, verbose=False, tutorial=False, coreCount=multiprocessing.cpu_count()):
    
    args = {}
    
    connection, username, password = panoptesConnect(username, password)
    
    args['username'] = username
    args['password'] = password
    args['projectName'] = projectName
    args['zooniverseConnection'] = connection
    args['projID'] = projID
    args['subjSetID'] = subjSetID
    
    if dsLocations == None:
        pass
    elif type(dsLocations) != list:
        args['datasetLocations'] = [dsLocations]
    else:
        args['datasetLocations'] = dsLocations
        
    if verbose:
        args['projectDescription'] = input('Enter project description: ')
        args['subjectSetTitle'] = input('Enter subject set title: ')
    else:
        args['projectDescription'] = 'This project was created by ' + username + ' using Simple Zooniverse.'
        args['subjectSetTitle'] = 'Simple Zooniverse Subject Set'
    args['F_private'] = False
    args['coreCount'] = coreCount
    args['primaryLanguage'] = 'en'
    args['customArgsIndex'] = 0
    args['F_livePost'] = True
    
    if 'google.colab' in str(get_ipython()):
        args['colab'] = True
    else:
        args['colab'] = False
    
    if not makeImages:
        # User has images.
        if not projID == -1:
            # User has project.
            project = Project(projID)
            pushNewSubjectSet(args, customArgs, project, False)
        else:
            # User does not have project.
            makeZooniverseProject(args, customArgs, tutorial)
    else:
        # User does not have images.
        if not projID == -1:
            # User has project.
            pass
        else:
            # User does not have project.
            pass

def parseOutput(f):

    pass
           
