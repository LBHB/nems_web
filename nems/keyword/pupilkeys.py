#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pupil keywords: both pupil gain and pupil model

Created on Fri Aug 11 11:08:54 2017

@author: shofer
"""
import nems.modules as nm
from nems.keyword.keyhelpers import mini_fit
import nems.utilities as ut


# Pupil Model keywords
###############################################################################

def perfectpupil100(stack):
    """keyword to fit pupil gain using "perfect" model generated by pupil_model module.
    The idea here is not to fit a model to the data, but merely to see the effect of a 
    a linear pupil gain function on the "perfect" model generated by averaging the
    rasters of each trial for a given stimulus. This keyword loads up the data
    and generates the model. It should be used with pupgain and a fitter keyword.
    """
    file=ut.baphy_utils.get_celldb_file(stack.meta['batch'],stack.meta['cellid'],fs=200,stimfmt='ozgf',chancount=24)
    print("Initializing load_mat with file {0}".format(file))
    stack.append(nm.loaders.load_mat,est_files=[file],fs=100,avg_resp=False)
    stack.append(nm.est_val.crossval,valfrac=stack.valfrac)
    stack.append(nm.pupil.model)
    
def perfectpupil50(stack):
    """keyword to fit pupil gain using "perfect" model generated by pupil_model module.
    The idea here is not to fit a model to the data, but merely to see the effect of a 
    a linear pupil gain function on the "perfect" model generated by averaging the
    rasters of each trial for a given stimulus. This keyword loads up the data
    and generates the model. It should be used with pupgain and a fitter keyword.
    """
    file=ut.baphy_utils.get_celldb_file(stack.meta['batch'],stack.meta['cellid'],fs=200,stimfmt='ozgf',chancount=24)
    print("Initializing load_mat with file {0}".format(file))
    stack.append(nm.loaders.load_mat,est_files=[file],fs=50,avg_resp=False)
    stack.append(nm.est_val.crossval,valfrac=stack.valfrac)
    stack.append(nm.pupil.model)

# Pupil Gain keywords
###############################################################################


def nopupgain(stack):
    """
    Applies a DC gain function entry-by-entry to the datastream:
        y = v1 + v2*x
    where x is the input matrix and v1,v2 are fitted parameters applied to 
    each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='nopupgain',fit_fields=['theta'],theta=[0,1])
    mini_fit(stack,mods=['pupil.pupgain'])
    
def pupgainctl(stack):
    """
    Applies a DC gain function entry-by-entry to the datastream:
        y = v1 + v2*x + <randomly shuffled pupil dc-gain>
    where x is the input matrix and v1,v2 are fitted parameters applied to 
    each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='linpupgainctl',fit_fields=['theta'],theta=[0,1,0,0])
    mini_fit(stack,mods=['pupil.pupgain'])
    
def pupgain(stack):
    """
    Applies a linear pupil gain function entry-by-entry to the datastream:
        y = v1 + v2*x + v3*p + v4*x*p
    where x is the input matrix, p is the matrix of pupil diameters, and v1,v2 
    are fitted parameters applied to each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='linpupgain',fit_fields=['theta'],theta=[0,1,0,0])
    mini_fit(stack,mods=['pupil.pupgain'])
    
def polypupgain04(stack):#4th degree polynomial gain fn
    """
    Applies a poynomial pupil gain function entry-by-entry to the datastream:
        y = v1 + v2*x + v3*x*p + v4*x*(p^2) + v5*x*(p^3) + v6*x*(p^4)
    where x is the input matrix, p is the matrix of pupil diameters, and v1,v2,v3,v4,v5,v6 
    are fitted parameters applied to each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='polypupgain',fit_fields=['theta'],theta=[0,0,0,0,0,1])
    mini_fit(stack,mods=['pupil.pupgain'])
    
def polypupgain03(stack): #3rd degree polynomial gain fn
    """
    Applies a poynomial pupil gain function entry-by-entry to the datastream:
        y = v1 + v2*x + v3*x*p + v4*x*(p^2) + v5*x*(p^3)
    where x is the input matrix, p is the matrix of pupil diameters, and v1,v2,v3,v4,v5 
    are fitted parameters applied to each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='polypupgain',fit_fields=['theta'],theta=[0,0,0,0,1])
    mini_fit(stack,mods=['pupil.pupgain'])
    
def polypupgain02(stack): #2nd degree polynomial gain fn
    """
    Applies a poynomial pupil gain function entry-by-entry to the datastream:
        y = v1 + v2*x + v3*x*p + v4*x*(p^2) 
    where x is the input matrix, p is the matrix of pupil diameters, and v1,v2,v3,v4
    are fitted parameters applied to each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='polypupgain',fit_fields=['theta'],theta=[0,0,0,1])
    mini_fit(stack,mods=['pupil.pupgain'])
    
def exppupgain(stack):
    """
    Applies an exponential pupil gain function entry-by-entry to the datastream:
        y = v1 + v2*x*exp(v3*p-v4)
    where x is the input matrix, p is the matrix of pupil diameters, and v1,v2,v3,v4
    are fitted parameters applied to each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='exppupgain',fit_fields=['theta'],theta=[0,1,0,0])
    mini_fit(stack,mods=['pupil.pupgain'])

def logpupgain(stack):
    """
    Applies a logarithmic pupil gain function entry-by-entry to the datastream:
        y = v1 + v2*x*log(v3*p-v4)
    where x is the input matrix, p is the matrix of pupil diameters, and v1,v2,v3,v4
    are fitted parameters applied to each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='logpupgain',fit_fields=['theta'],theta=[0,1,0,1])
    mini_fit(stack,mods=['pupil.pupgain'])
    
def powergain02(stack): #This is equivalent ot what Zach is using
    """
    Applies a poynomial pupil gain function entry-by-entry to the datastream:
        y = v1 + v2*x + v3*(p^2) + v4*x*(p^2) 
    where x is the input matrix, p is the matrix of pupil diameters, and v1,v2,v3,v4
    are fitted parameters applied to each matrix entry (the same across all entries)
    """
    stack.append(nm.pupil.pupgain,gain_type='powerpupgain',fit_fields=['theta'],theta=[0,1,0,0],order=2)
    mini_fit(stack,mods=['pupil.pupgain'])
    
def butterworth01(stack):
    """
    Applies a 1st-order Butterworth high-pass filter entry-by-entry to the datastream,
    where the pupil diameter is used as the "frequency", and the -3dB is fit, along
    with a scalar gain term and a DC offset. 
    """
    stack.append(nm.pupil.pupgain,gain_type='butterworthHP',fit_fields=['theta'],theta=[1,25,0],order=1)
    mini_fit(stack,mods=['pupil.pupgain'])
    
def butterworth02(stack):
    """
    Applies a 2nd-order Butterworth high-pass filter entry-by-entry to the datastream,
    where the pupil diameter is used as the "frequency", and the -3dB is fit, along
    with a scalar gain term and a DC offset. 
    """
    stack.append(nm.pupil.pupgain,gain_type='butterworthHP',fit_fields=['theta'],theta=[1,25,0],order=2)
    mini_fit(stack,mods=['pupil.pupgain'])
    
def butterworth03(stack):
    """
    Applies a 3rd-order Butterworth high-pass filter entry-by-entry to the datastream,
    where the pupil diameter is used as the "frequency", and the -3dB is fit, along
    with a scalar gain term and a DC offset. 
    """
    stack.append(nm.pupil.pupgain,gain_type='butterworthHP',fit_fields=['theta'],theta=[1,25,0],order=3)
    mini_fit(stack,mods=['pupil.pupgain'])
    
def butterworth04(stack):
    """
    Applies a 4th-order Butterworth high-pass filter entry-by-entry to the datastream,
    where the pupil diameter is used as the "frequency", and the -3dB is fit, along
    with a scalar gain term and a DC offset. 
    """
    stack.append(nm.pupil.pupgain,gain_type='butterworthHP',fit_fields=['theta'],theta=[1,25,0],order=4)
    mini_fit(stack,mods=['pupil.pupgain'])
    
# weighted combination 2 PSTHS usign pupil

def pupwgt(stack,weight_type='linear'):
    """
    linear weighted sum of stim and stim2, determined by pupil
        w=(phi[0]+phi[1] * p)
        Y=stim1 * (1-w) + stim2 * w
    hard bound on w  in (0,1)
    """
    # find fir and duplicate
    wtidx=ut.utils.find_modules(stack,'filters.weight_channels')
    firidx=ut.utils.find_modules(stack,'filters.fir')
    wtidx=wtidx[0]
    firidx=firidx[0]
    num_chans=stack.modules[wtidx].num_chans
    wcoefs=stack.modules[wtidx].coefs
    num_coefs=stack.modules[firidx].num_coefs
    coefs=stack.modules[firidx].coefs
    baseline=stack.modules[firidx].baseline
    stack.modules[wtidx].output_name='stim2'
    stack.modules[firidx].input_name='stim2'
    stack.modules[firidx].output_name='stim2'
    stack.evaluate(wtidx)
    stack.append(nm.filters.weight_channels,num_chans=num_chans)
    stack.modules[-1].coefs=wcoefs
    stack.append(nm.filters.fir,num_coefs=num_coefs)
    stack.modules[-1].coefs=coefs*0.95
    stack.modules[-1].baseline=baseline*0.95

    stack.append(nm.pupil.state_weight,weight_type=weight_type,fit_fields=['theta'],theta=[0,0.01])
    stack.evaluate(wtidx)
    
    #mini_fit(stack,mods=['pupil.state_weight'])
    
def pupwgtctl(stack):
    """
    linear weighted sum of stim and stim2, determined by shuffled pupil
        w=(phi[0]+phi[1] * p_shuff)
        Y=stim1 * (1-w) + stim2 * w
    hard bound on w  in (0,1)
    """
    
    # call pupwgt with different weight_type
    pupwgt(stack,weight_type='linearctl')
    
    

    