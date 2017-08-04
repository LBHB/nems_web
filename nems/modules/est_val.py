#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 13:21:47 2017

@author: shofer
"""
from nems.modules.base import nems_module
import numpy as np
import copy
import math as mt

import nems.utilities.utils as nu


class standard(nems_module):
    """
    Splits stack.data object into estimation and validation datasets. If 
    estimation and validation datasets are already flagged in stack.data (i.e.
    if d['est'] exists), it will simply pass the datasets as is. If not, it will
    split the data based on the 'repcount' list. Stimuli with large numbers of
    repetitions are placed in the validation dataset, while most of the stimuli,
    which have low repetitions, are placed in the estimation dataset.
    
    This estimation/validation routine is not compatible with nested
    crossvalidation.
    """
    #TODO: make this work given changes to stack
    name='standard_est_val'
    user_editable_fields=['output_name','valfrac']
    
    def my_init(self):
        print('Using standard est/val')
    
    def evaluate(self,**kwargs):
        del self.d_out[:]
         # for each data file:
        for i, d in enumerate(self.d_in):
            #self.d_out.append(d)
            try:
                if d['est']:
                    # flagged as est data
                    self.d_out.append(d)
                elif self.parent_stack.valmode:
                    self.d_out.append(d)
                    
            except:
                # est/val not flagged, need to figure out
                
                #--made a new est/val specifically for pupil --njs, June 28 2017
                
                # figure out number of distinct stim
                s=d['repcount']
                
                m=s.max()
                validx = s==m
                estidx = s<m
                if not estidx.sum():
                    s[-1]+=1
                    m=s.max()
                    validx = s==m
                    estidx = s<m
                
                d_est=d.copy()
                #d_val=d.copy()
                
                d_est['repcount']=copy.deepcopy(d['repcount'][estidx])
                d_est['resp']=copy.deepcopy(d['resp'][estidx,:])
                d_est['stim']=copy.deepcopy(d['stim'][:,estidx,:])
                #d_val['repcount']=copy.deepcopy(d['repcount'][validx])
                #d_val['resp']=copy.deepcopy(d['resp'][validx,:])
                #d_val['stim']=copy.deepcopy(d['stim'][:,validx,:])
                try:
                    d_est['pupil']=copy.deepcopy(d['pupil'][estidx,:])
                except:
                    print('No pupil data')
                    d_est['pupil']=[]

                #d_val['pupil']=copy.deepcopy(d['pupil'][validx,:])
                    #for j in (d_est,d_val):
                    #    for i in ('resp','pupil'):
                    #        s=j[i].shape
                    #        j[i]=np.reshape(j[i],(s[0]*s[1],s[2]),order='F')
                    #        j[i]=np.transpose(j[i],(1,0))
                    #    j['stim']=np.tile(j['stim'],(1,1,s[1]))
                
                d_est['est']=True
                #d_val['est']=False
                
                self.d_out.append(d_est)
                if self.parent_stack.valmode:
                    
                    d_val=d.copy()
                    d_val['repcount']=copy.deepcopy(d['repcount'][validx])
                    d_val['resp']=[copy.deepcopy(d['resp'][validx,:])]
                    d_val['stim']=[copy.deepcopy(d['stim'][:,validx,:])]
                    try:
                        d_val['pupil']=[copy.deepcopy(d['pupil'][validx,:])]
                    except:
                        print('No pupil data')
                        d_val['pupil']=[]
                        
                    d_val['est']=False
                    self.d_out.append(d_val)

            
class crossval(nems_module):
    """
    Splits data into estimation and validation datasets. If estimation and 
    validation sets are already flagged (if d['est'] exists), it just passes 
    these. If not, it splits a given percentage of the dataset off as validation
    data, and leaves the rest as estimation data. 
    
    Inputs:
        valfrac: fraction of the dataset to allocate as validation data
    
    This module is set up to work with nested crossvalidation. If this is the 
    case, it will run through the dataset, taking a different validation set 
    each time. 
    
    @author: shofer
    """
    name='crossval'
    plot_fns=[nu.raster_plot]
    valfrac=0.05
    
    def my_init(self,valfrac=0.05):
        self.valfrac=valfrac
        try:
            self.iter=int(1/valfrac)-1
        except:
            self.iter=0
        
    def evaluate(self,nest=0):

        del self.d_out[:]

        for i, d in enumerate(self.d_in):
            try:
                if d['est']:
                    # flagged as est data
                    self.d_out.append(d)
                elif self.parent_stack.valmode:
                    self.d_out.append(d)
                self.parent_stack.cond=True
                self.parent_stack.pre_flag=True
            except:
                count=self.parent_stack.cv_counter
                re=d['resp'].shape
                if re[0]<self.parent_stack.nests:
                    raise IndexError('Fewer stimuli than nests; use a higher valfrac/less nests')
                spl=mt.ceil(re[0]*self.valfrac)
                count=count*spl
                
                d_est=d.copy()
                
                d_est['resp']=np.delete(d['resp'],np.s_[count:(count+spl)],0)
                d_est['stim']=np.delete(d['stim'],np.s_[count:(count+spl)],1)
                
                if self.parent_stack.avg_resp is True:
                    try:
                        d_est['pupil']=np.delete(d['pupil'],np.s_[count:(count+spl)],2)
                    except TypeError:
                        print('No pupil data')
                        d_est['pupil']=[]  
                    d_est['repcount']=np.delete(d['repcount'],np.s_[count:(count+spl)],0)
                else:
                    try:
                        d_est['pupil']=np.delete(d['pupil'],np.s_[count:(count+spl)],0)
                    except TypeError:
                        print('No pupil data')
                        d_est['pupil']=[]
                    try:
                        d_est['replist']=np.delete(d['replist'],np.s_[count:(count+spl)],0)
                    except KeyError:
                        d_est['replist']=None
                

                d_est['est']=True
                
                self.d_out.append(d_est)
                if self.parent_stack.valmode is True:
                    
                    d_val=d.copy()
                    d_val['est']=False
                    
                    d_val['stim']=[]
                    d_val['resp']=[]
                    d_val['pupil']=[]
                    d_val['replist']=[]
                    d_val['repcount']=[]

                    for count in range(0,self.parent_stack.nests):
                        #print(count)
                        re=d['resp'].shape
                        spl=mt.ceil(re[0]*self.valfrac)
                        count=count*spl
                        if self.parent_stack.avg_resp is True:
                            try:
                                d_val['pupil'].append(copy.deepcopy(d['pupil'][:,:,count:(count+spl)]))
                            except TypeError:
                                print('No pupil data')
                                d_val['pupil']=[]
                            d_val['repcount'].append(copy.deepcopy(d['repcount'][count:(count+spl)]))
                        else:
                            try:
                                d_val['pupil'].append(copy.deepcopy(d['pupil'][count:(count+spl),:]))
                            except TypeError:
                                print('No pupil data')
                                d_val['pupil']=[]
                            d_val['replist'].append(copy.deepcopy(d['replist'][count:(count+spl)]))
                            d_val['repcount']=copy.deepcopy(d['repcount'])
                        d_val['resp'].append(copy.deepcopy(d['resp'][count:(count+spl),:]))
                        d_val['stim'].append(copy.deepcopy(d['stim'][:,count:(count+spl),:]))
                        
                      
                    #TODO: this code runs if crossval allocated
                    #an empty nest at the end of the validation list. This 
                    #should not happen as often as it does, and it would be a 
                    #better long term thing to do to change how the indices for
                    #allocating the datasets are chosen (something better than 
                    #mt.ceil), since then estimation nests with no validation
                    #nest would not be fit, as they are currently.
                    #    ----njs, August 2 2017
                    
                    s=d_val['stim'][-1].shape
                    sr=d_val['resp'][-1].shape
                    while s[1]==0 or sr[0]==0:
                        del(d_val['stim'][-1])
                        del(d_val['resp'][-1])
                        del(d_val['pupil'][-1])
                        try:
                            del(d_val['replist'][-1])
                        except:
                            pass
                        self.parent_stack.nests-=1
                        s=d_val['stim'][-1].shape
                        sr=d_val['resp'][-1].shape
                        print('Final nest has no stimuli, updating to have {0} nests'.format(
                                self.parent_stack.nests))
                    self.d_out.append(d_val)
                
                if self.parent_stack.cv_counter==self.iter:
                    self.parent_stack.cond=True