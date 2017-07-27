#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

nems_db library

Created on Fri Jun 16 05:20:07 2017

@author: svd
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

from nems.config.config import db_uri

SQLALCHEMY_DATABASE_URI = db_uri

# sets how often sql alchemy attempts to re-establish connection engine
# TODO: query db for time-out variable and set this based on some fraction of that
POOL_RECYCLE = 7200;

# create a database connection engine
engine = create_engine(SQLALCHEMY_DATABASE_URI,pool_recycle=POOL_RECYCLE)

#create base class to mirror existing database schema
Base = automap_base()
Base.prepare(engine, reflect=True)

NarfUsers = Base.classes.NarfUsers
NarfAnalysis = Base.classes.NarfAnalysis
NarfBatches = Base.classes.NarfBatches
NarfResults = Base.classes.NarfResults
tQueue = Base.classes.tQueue
sCellFile = Base.classes.sCellFile
sBatch = Base.classes.sBatch

# import this when another module needs to use the database connection.
# used like a class - ex: 'session = Session()'
Session = sessionmaker(bind=engine)


def enqueue_models(celllist, batch, modellist, force_rerun=False):
    """Call enqueue_single_model for every combination of cellid and modelname
    contained in the user's selections.
    
    Arguments:
    ----------
    celllist : list
        List of cellid selections made by user.
    batch : string
        batch number selected by user.
    modellist : list
        List of modelname selections made by user.
    
    Returns:
    --------
    data : string  <-- not yet finalized
        Some message indicating success or failure to the user, to be passed
        on to the web interface by the calling view function.
        
    See Also:
    ---------
    . : enqueue_single_model
    Narf_Analysis : enqueue_models_callback
    
    """
    # Not yet ready for testing - still need to coordinate the supporting
    # functions with the model queuer.
    for model in modellist:
        for cell in celllist:
            enqueue_single_model(cell, batch, model, force_rerun)
    
    data = 'Placeholder success/failure messsage for user if any.'
    return data


def enqueue_single_model(cellid, batch, modelname, force_rerun):
    """Not yet developed, likely to change a lot.
    
    Returns:
    --------
    tQueueId : int
        id (primary key) that was assigned to the new tQueue entry, or -1.
        
    See Also:
    ---------
    Narf_Analysis : enqueue_single_model
    
    """

    session = Session()
    tQueueId = -1
    
    # TODO: anything else needed here? this is syntax for nems_fit_single
    #       command prompt wrapper in main nems folder.
    commandPrompt = (
            "nems_fit_single %s %s %s"
            %(cellid,batch,modelname)
            )

    note = "%s/%s/%s"%(cellid,batch,modelname)
    
    result = (
            session.query(NarfResults)
            .filter(NarfResults.cellid == cellid)
            .filter(NarfResults.batch == batch)
            .filter(NarfResults.modelname == modelname)
            .all()
            )
    if result and not force_rerun:
        print("Entry in NarfResults already exists for: %s, skipping.\n"%note)
        return -1
    
    #query tQueue to check if entry with same cell/batch/model already exists
    qdata = session.query(tQueue).filter(tQueue.note == note).all()
    
    # if it does, check its 'complete' status and take different action based on
    # status
    
    if qdata and (int(qdata[0].complete) <= 0):
        #TODO:
        #incomplete entry for note already exists, skipping
        #update entry with same note? what does this accomplish?
        #moves it back into queue maybe?
        print("Incomplete entry for: %s already exists, skipping.\n"%note)
        return -1
    elif qdata and (int(qdata[0].complete) == 2):
        #TODO:
        #dead queue entry for note exists, resetting
        #update complete and progress status each to 0
        #what does this do? doesn't look like the sql is sent right away,
        #instead gets assigned to [res,r]
        print("Dead queue entry for: %s already exists, resetting.\n"%note)
        qdata[0].complete = 0
        qdata[0].progress = 0
        return -1
    elif qdata and (int(qdata[0].complete) == 1):
        #TODO:
        #resetting existing queue entry for note
        #update complete and progress status each to 0
        #same as above, what does this do?
        print("Resetting existing queue entry for: %s\n"%note)
        qdata[0].complete = 0
        qdata[0].progress = 0
        return -1
    else: #result must not have existed? or status value was greater than 2
        # add new entry
        print("Adding job to queue for: %s\n"%note)
        job = tQueue()
        session.add(add_model_to_queue(commandPrompt,note,job))
    
    # uncomment session.commit() when ready to test saving to database
    session.commit()
    tQueueId = job.id
    session.close()
    return tQueueId
    
def add_model_to_queue(commandPrompt,note,job,priority=1,rundataid=0):
    """Not yet developed, likely to change a lot.
    
    Returns:
    --------
    job : tQueue object instance
        tQueue object with variables assigned inside function based on
        arguments.
        
    See Also:
    ---------
    Narf_Analysis: dbaddqueuemaster
    
    """
    
    #TODO: does user need to be able to specificy priority and rundataid somewhere
    #       in web UI?
    
    #TODO: why is narf version checking for list vs string on prompt and note?
    #       won't they always be a string passed from enqueue function?
    #       or want to be able to add multiple jobs manually from command line?
    #       will need to rewrite with for loop to to add this functionality in the
    #       future if desired
    
    #TODO: set these some where else? able to choose from UI?
    #       could grab user name from login once implemented
    user = 'default-user-name-here?'
    progname = 'python3'
    allowqueuemaster=1
    waitid = 0
    dt = str(datetime.datetime.now().replace(microsecond=0))
    
    job.rundataid = rundataid
    job.progname = progname
    job.priority = priority
    job.parmstring = commandPrompt
    job.queuedate = dt
    job.allowqueuemaster = allowqueuemaster
    job.user = user
    job.note = note
    job.waitid = waitid
    
    return job