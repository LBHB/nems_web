#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modules for computing scores/ assessing model performance

Created on Fri Aug  4 13:44:42 2017

@author: shofer
"""
from nems.modules.base import nems_module
import nems.utilities.utils
import nems.utilities.plot

import numpy as np
import scipy.stats as spstats

class mean_square_error(nems_module):
 
    name='metrics.mean_square_error'
    user_editable_fields=['input1','input2','norm','shrink']
    plot_fns=[nems.utilities.plot.pred_act_psth,nems.utilities.plot.pred_act_psth_smooth,nems.utilities.plot.pred_act_scatter]
    input1='stim'
    input2='resp'
    norm=True
    shrink=0
    mse_est=np.ones([1,1])
    mse_val=np.ones([1,1])
        
    def my_init(self, input1='stim',input2='resp',norm=True,shrink=False):
        self.field_dict=locals()
        self.field_dict.pop('self',None)
        self.input1=input1
        self.input2=input2
        self.norm=norm
        self.shrink=shrink
        self.do_trial_plot=self.plot_fns[1]
        
    def evaluate(self,nest=0):
        if nest==0:
            del self.d_out[:]
            for i, d in enumerate(self.d_in):
                self.d_out.append(d.copy())
            
        if self.shrink is True:
            X1=self.unpack_data(self.input1,est=True)
            X2=self.unpack_data(self.input2,est=True)
            bounds=np.round(np.linspace(0,len(X1)+1,11)).astype(int)
            E=np.zeros([10,1])
            P=np.mean(np.square(X2))
            for ii in range(0,10):
                E[ii]=np.mean(np.square(X1[bounds[ii]:bounds[ii+1]]-X2[bounds[ii]:bounds[ii+1]]))
            E=E/P
            mE=E.mean()
            sE=E.std()
            if mE<1:
                # apply shrinkage filter to 1-E with factors self.shrink
                mse=1-nems.utilities.utils.shrinkage(1-mE,sE,self.shrink)
            else:
                mse=mE
                
        else:
            X1=self.unpack_data(self.input1,est=True)            
            X2=self.unpack_data(self.input2,est=True)
            keepidx=np.isfinite(X1) * np.isfinite(X2)
            X1=X1[keepidx]
            X2=X2[keepidx]
            E=np.sum(np.square(X1-X2))
            P=np.sum(X2*X2)
            N=X1.size
            
#            E=np.zeros([1,1])
#            P=np.zeros([1,1])
#            N=0
#            for f in self.d_out:
#                #try:
#                E+=np.sum(np.square(f[self.input1]-f[self.input2]))
#                P+=np.sum(np.square(f[self.input2]))
#                #except TypeError:
#                    #print('error eval')
#                    #nems.utilities.utils.concatenate_helper(self.parent_stack)
#                    #E+=np.sum(np.square(f[self.input1]-f[self.input2]))
#                    #P+=np.sum(np.square(f[self.input2]))
#                N+=f[self.input2].size

            if self.norm:
                if P>0:
                    mse=E/P
                else:
                    mse=1    
            else:
                mse=E/N
                
            self.mse_est=mse
            self.parent_stack.meta['mse_est']=[mse]
                
            if self.parent_stack.valmode is True:   
                X1=self.unpack_data(self.input1,est=False)            
                X2=self.unpack_data(self.input2,est=False)
                keepidx=np.isfinite(X1) * np.isfinite(X2)
                X1=X1[keepidx]
                X2=X2[keepidx]
                E=np.sum(np.square(X1-X2))
                P=np.sum(X2*X2)
                N=X1.size
    
                if self.norm:
                    if P>0:
                        mse=E/P
                    else:
                        mse=1    
                else:
                    mse=E/N
                self.mse_val=mse
                self.parent_stack.meta['mse_val']=mse
        
        return mse

    def error(self, est=True):
        if est:
            return self.mse_est
        else:
            # placeholder for something that can distinguish between est and val
            return self.mse_val
        
class pseudo_huber_error(nems_module):
    """
    Pseudo-huber "error" to use with fitter cost functions. This is more robust to
    ouliers than simple mean square error. Approximates L1 error at large
    values of error, and MSE at low error values. Has the additional benefit (unlike L1)
    of being convex and differentiable at all places.
    
    Pseudo-huber equation taken from Hartley & Zimmerman, "Multiple View Geometry
    in Computer Vision," (Cambridge University Press, 2003), p619
    
    C(delta)=2(b^2)(sqrt(1+(delta/b)^2)-1)
    
    b mediates the value of error at which the the error is penalized linearly or quadratically.
    Note that setting b=1 is the soft l1 loss
    
    @author: shofer, June 30 2017
    """
    #I think this is working (but I'm not positive). When fitting with a pseudo-huber
    #cost function, the fitter tends to ignore areas of high spike rates, but does
    #a good job finding the mean spike rate at different times during a stimulus. 
    #This makes sense in that the huber error penalizes outliers, and could be 
    #potentially useful, depending on what is being fit? --njs, June 30 2017
    
    
    name='metrics.pseudo_huber_error'
    user_editable_fields=['input1','input2','b']
    plot_fns=[nems.utilities.plot.pred_act_psth,nems.utilities.plot.pred_act_scatter]
    input1='stim'
    input2='resp'
    b=0.9 #sets the value of error where fall-off goes from linear to quadratic\
    huber_est=np.ones([1,1])
    huber_val=np.ones([1,1])
    
    def my_init(self, input1='stim',input2='resp',b=0.9):
        self.field_dict=locals()
        self.field_dict.pop('self',None)
        self.input1=input1
        self.input2=input2
        self.b=b
        self.do_trial_plot=self.plot_fns[1]
        
    def evaluate(self,nest=0):
        del self.d_out[:]
        for i, d in enumerate(self.d_in):
            self.d_out.append(d.copy())
    
        for f in self.d_out:
            delta=np.divide(np.sum(f[self.input1]-f[self.input2],axis=1),np.sum(f[self.input2],axis=1))
            C=np.sum(2*np.square(self.b)*(np.sqrt(1+np.square(np.divide(delta,self.b)))-1))
            C=np.array([C])
        self.huber_est=C
            
    def error(self,est=True):
        if est is True:
            return(self.huber_est)
        else: 
            return(self.huber_val)
        
class correlation(nems_module):
 
    name='metrics.correlation'
    user_editable_fields=['input1','input2','norm']
    plot_fns=[nems.utilities.plot.pred_act_psth, nems.utilities.plot.pred_act_scatter, nems.utilities.plot.pred_act_scatter_smooth]
    input1='stim'
    input2='resp'
    r_est=np.ones([1,1])
    r_val=np.ones([1,1])
        
    def my_init(self, input1='stim',input2='resp',norm=True):
        self.field_dict=locals()
        self.field_dict.pop('self',None)
        self.input1=input1
        self.input2=input2
        self.do_plot=self.plot_fns[1]
        
    def evaluate(self,**kwargs):
        del self.d_out[:]
        for i, d in enumerate(self.d_in):
            self.d_out.append(d.copy())

        X1=self.unpack_data(self.input1,est=True)            
        X2=self.unpack_data(self.input2,est=True)
        keepidx=np.isfinite(X1) * np.isfinite(X2)
        X1=X1[keepidx]
        X2=X2[keepidx]
        if not X1.sum() or not X2.sum():
            r_est=0
        else:
            r_est,p=spstats.pearsonr(X1,X2)
        self.r_est=r_est
        self.parent_stack.meta['r_est']=[r_est]
        
        X1=self.unpack_data(self.input1,est=False)            
        if X1.size:
            X2=self.unpack_data(self.input2,est=False)
            keepidx=np.isfinite(X1) * np.isfinite(X2)
            X1=X1[keepidx]
            X2=X2[keepidx]
            if not X1.sum() or not X2.sum():
                r_val=0
            else:
                r_val,p=spstats.pearsonr(X1,X2)
            self.r_val=r_val
            self.parent_stack.meta['r_val']=[r_val]
        
            # if running validation test, also measure r_floor
            rf=np.zeros([1000,1]) 
            for rr in range(0,len(rf)):
                n1=(np.random.rand(500,1)*len(X1)).astype(int)
                n2=(np.random.rand(500,1)*len(X2)).astype(int)
                rf[rr],p=spstats.pearsonr(X1[n1],X2[n2])
            rf=np.sort(rf[np.isfinite(rf)],0)
            if len(rf):
                self.parent_stack.meta['r_floor']=[rf[np.int(len(rf)*0.95)]]
            else:
                self.parent_stack.meta['r_floor']=0
                
            return [r_val]
        else:
            return [r_est]

class ssa_index(nems_module):

    '''
    SSA index (SI) calculations as stated by Ulanovsky et al., 2003. The module take a in stimulus envelope input
    with 3 dimensions corresponding to stream (tone 1 or tone 2), trial and time; and a response input lacking
    the first dimention.

    Using the envelope defines for each trial which tone is being standard, deviant and onset, and then precedes to
    cut the response to such tones and pool them in 6 bins (3 tone natures times to streams)

    for each pool, all tone responses are averaged and then the average is integrated from the onset of the tone to
    twice the lenght of the tone (to include any offset responses).

    for each stream (tone 1 or 2) the SI is calculated as:

        (tone n deviant - tone n standard) / (tone n devian + tone n standard)

    SI can also be calculated for the whole cell in a tone "independent" way:

        (tone1 deviant + tone2 deviant - tone1 standard - tone2 standard) /
        (tone1 deviant + tone2 deviant + tone1 standard + tone2 standard)



    '''

    name = 'metrics.ssa_index'
    user_editable_fields = ['input1', 'input2', 'baseline', 'window']
    plot_fns = [nems.utilities.plot.plot_ssa_idx]
    input1 = 'stim'
    input2 = 'resp'
    baseline = False
    window = 'start'
    SI0 = 0
    SI1 = 0
    SIcell = 0
    folded_tones = list()
    SI_dict = dict()

    def my_init(self, input1='stim', input2='resp', baseline=False, window='start') :
        self.field_dict = locals()
        self.field_dict.pop('self',None)
        self.input1 = input1
        self.input2 = input2
        # todo, implement baseline substraction and integration window selection, are they really necessary?
        self.baseline = baseline
        self.window = window
        self.do_plot = self.plot_fns[0]
        self.do_trial_plot = self.plot_fns[0]

    def evaluate(self, **kwargs):
        del self.d_out[:]
        for i, d in enumerate(self.d_in):
            self.d_out.append(d.copy())

        ssa_index = list()
        folded_tones = list()

        # get the data, then slice the tones and asign to the right bin
        # this iteration asumes that multiple sets of data are from multiple states e.g. jitter on/off
        # this totaly obviates that the datasets might instead differ in estimation / validation nature.

        for iid, b in enumerate(self.d_in):
            stim = b['stim'] # input 3d array: 0d #streasm ; 1d #trials; 2d time
            stim = stim.astype(np.int16) #input stim is in uint8 which is problematic for diff
            resp = b['resp'] # input 2d array: 0d #trials ; 1d time
            diff = np.diff(stim, axis=2)

            slice_dict = {'stream0Std': list(),
                          'stream0Dev': list(),
                          'stream0Ons': list(),
                          'stream1Std': list(),
                          'stream1Dev': list(),
                          'stream1Ons': list()}

            # define the length of the tones, assumes all tones are equal. defines flanking silences as with the same
            # lenght as the tone
            # TODO; this infers the tone length from the envelope shape, overlaping tones will give problems, import values form parameter file


            adiff = diff[0, 0, :]
            IdxStrt = np.where(adiff == 1)[0][0]
            IdxEnd = np.where(adiff == -1)[0][0]
            toneLen = IdxEnd - IdxStrt

            for trialcounter in range(stim.shape[1]):

                # get starting indexes for both streams

                where0 = np.where(diff[0, trialcounter, :] == 1)[0] + 1
                where1 = np.where(diff[1, trialcounter, :] == 1)[0] + 1

                # slices both streams

                stream0 = [resp[trialcounter, ii - toneLen: ii + (toneLen * 2)] for ii in where0]
                stream1 = [resp[trialcounter, ii - toneLen: ii + (toneLen * 2)] for ii in where1]

                # checks which comes first and extract onset

                if where0[0] < where1[0]:
                    # Onset is in stream 0
                    slice_dict['stream0Ons'] = slice_dict['stream0Ons'] + [stream0[0]]
                    stream0 = stream0[1:]

                elif where0[0] > where1[0]:
                    # Onset in in stream 1
                    slice_dict['stream1Ons'] = slice_dict['stream1Ons'] + [stream1[0]]
                    stream1 = stream1[1:]

                # Count tones by integration
                tone_count = np.nansum(stim[:, trialcounter, :], axis=1)

                # Check which stream is standard and appends slices in the right list
                if tone_count[0] > tone_count[1]:
                    # stream 0 is standard, stream 1 is deviant
                    slice_dict['stream0Std'] = slice_dict['stream0Std'] + stream0
                    slice_dict['stream1Dev'] = slice_dict['stream1Dev'] + stream1

                elif tone_count[0] < tone_count[1]:
                    # Stream 1 is standard, stream 0 is deviant

                    slice_dict['stream1Std'] = slice_dict['stream1Std'] + stream1
                    slice_dict['stream0Dev'] = slice_dict['stream0Dev'] + stream0

            # calculates activity for each slice pool: first averages across trials, then integrates from the start
            # of the tone to the end of the slice. Organizes in an Activity dictionary with the same keys
            slice_dict = {key: np.asarray(value) for key, value in slice_dict.items()}

            act_dict = {key: np.nansum(np.nanmean(value, axis=0)[toneLen:])
                        for key, value in slice_dict.items()}

            SI_dict = {'stream0': (act_dict['stream0Dev'] - act_dict['stream0Std']) /  # dev - std over...
                                  (act_dict['stream0Dev'] + act_dict['stream0Std']),  # dev + std

                       'stream1': (act_dict['stream1Dev'] - act_dict['stream1Std']) /  # dev - std over...
                                  (act_dict['stream1Dev'] + act_dict['stream1Std']),  # dev + std

                       'cell': (act_dict['stream0Dev'] + act_dict['stream1Dev'] -  # dev + dev minus
                                act_dict['stream0Std'] - act_dict['stream1Std']) /  # std - std over
                               (act_dict['stream0Dev'] + act_dict['stream1Dev'] +  # dev + dev plus
                                act_dict['stream0Std'] + act_dict['stream1Std'])}  # std + std
            folded_tones.append(slice_dict)
            ssa_index.append(SI_dict)

        self.folded_tones = folded_tones
        self.SI_dict = ssa_index
        self.SI0  = [block['stream0'] for block in ssa_index]
        self.SI1 = [block['stream1'] for block in ssa_index]
        self.SIcell = [block['cell'] for block in ssa_index]
