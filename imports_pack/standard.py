#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 16:52:09 2017

@author: shofer
"""
import scipy.io as si



def standard_import(filepath):
    data=dict.fromkeys(['stim','resp','pup'])
    meta=dict.fromkeys(['stimf','respf','iso','prestim','duration','poststim'])
    matdata=si.loadmat(filepath,chars_as_strings=True)
    m=matdata['data'][0][0]
    data['resp']=m['resp_raster']
    data['stim']=m['stim']
    meta['stimf']=m['stimfs'][0][0]
    meta['respf']=m['respfs'][0][0]
    meta['iso']=m['isolation'][0][0]
    meta['prestim']=m['tags'][0]['PreStimSilence'][0][0][0]
    meta['poststim']=m['tags'][0]['PostStimSilence'][0][0][0]
    meta['duration']=m['tags'][0]['Duration'][0][0][0] 
    try:
        data['pup']=m['pupil']
    except:
        data['pup']=None
    return(data,meta)