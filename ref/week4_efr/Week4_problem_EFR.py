import numpy as np
import pylab as pl
import matplotlib as mp

import scipy.io

def get_fft(fs, waveforms):
    '''
    Calculate the frequency response for the provided waveforms

    Parameters
    ----------
    fs : float
        Sampling frequency (in Hz)
    waveforms : n-dimensional array
        Set of waveforms where the last axis (i.e., dimension) is time.

    Returns
    -------
    frequencies : 1D array
        Array of frequencies
    psd : n-dimensional array
        Normalized power spectral density (i.e., the frequency response in units
        of V per Hz). All but the final dimension map to the original dimensions
        of the `waveforms` array. The final dimension is frequency.  For
        example, if `waveforms` is a 3D array with the dimensions corresponding
        to repetition, microphone, time, then `psd` will be a 3D array with
        dimensions corresponding to repetition, microphone, frequency.
    phase : Phase of the response

    Example
    -------
    To plot the frequency response of the microphone (remember that waveforms is
    a 3D array with repetition, microphone and time as the dimensions):
    >>> waveforms = np.load('microphone_data.npy')
    >>> fs = 200000
    >>> frequencies, psd = get_fft(fs, waveforms)
    >>> mean_psd = np.mean(psd, axis=0)
    >>> pl.loglog(frequencies, psd[0], 'k-')    # cheap microphone
    >>> pl.loglog(frequencies, psd[1], 'r-')    # expensive microphone
    >>> pl.xlabel('Frequency (Hz)')
    >>> pl.ylabel('Power (Volts)')
    '''
    n_time = waveforms.shape[-1]
    frequencies = np.fft.rfftfreq(n_time, fs**-1)
    csd = np.fft.rfft(waveforms)/n_time
    psd = 2*np.abs(csd)/np.sqrt(2.0)
    phase = np.angle(csd)
    return frequencies, psd, phase
    
    
# Introduction: The Envelope Following Response (EFR) is an auditory evoked 
# response to a sinusoidally amplitude-modulated tone, recorded using electrodes
# on the scalp (like an EEG but with fewer electrodes). An amplitude-modulated tone
# means a tone where the amplitude (volume) fluctuates over time. In this case, the 
# stimulus was a 32 kHz tone, modulated at a range of frequencies from 400 to 
# 1360 Hz. It was played to one ear of an anesthetized mouse. The auditory nerve
# fibers, the first neurons in the auditory system, respond to this sound with
# action potentials that are synchronized with the modulation frequency. Action
# potentials are changes in the voltage across a neuron, and therefore they 
# generate an electric field that can be recorded using electrodes on the scalp.
# Since this stimulus causes synchronized firing of hundreds of nerve fibers, 
# the signal on the scalp is strong enough to rise above the noise. Therefore, 
# the EFR can be used as a tool to non-invasively assess the health of auditory 
# nerve fibers.

# Auditory nerve fibers synapse with neurons in the cochlear nucleus, and so 
# these neurons are fire in sync with the modulation frequency, although with 
# some delay (about 1 ms) due to synaptic propagation. Cochlear nucleus neurons
# synapse with other neurons in the auditory system, and those neurons synapse 
# with others. All of these neurons contribute to the EFR recorded on the scalp.
# In addition, in the electrode configuration used here there is also a substantial
# contribution from hair cells in the cochlea. These cells transduce the pressure 
# waves generated by sound into electrical signals, and are the "inputs" to 
# auditory nerve fibers. 

# The goal of the experiment is to develop a non-invasive tool to asses the health
# of the auditory nerve, and so ideally we'd like a way to separate the 
# contributions to the EFR from different neural centers. Fortunately, as the 
# signal ascends the auditory pathway, the maximum frequency that a neuron can 
# synchronize to decreases due to synaptic jitter. For example, the synchronization
# of auditory nerve fibers start to decrease around 2 kHz while the synchronization 
# in the inferior colliculus decreases starting around 500 Hz.

# The data:
# These data are recordings to 100%-modulated SAM tones in a single mouse with 
# a carrier frequency of 32 kHz at 70 dB SPL. Responses to 17 different modulation
# frequencies were collected separately. The stimuli were presented continuously 
# for 160 seconds per modulation frequency. In the file the responses are already
# broken into 100 millisecond bins and averaged across bins.
# A full data set of the 17 modulation frequencies was collected for two conditions:
# before, and after applying ouabain to the round window. Ouabain kills auditory 
# nerve fibers without disrupting hair cell function. This allows use to determine
# how much of the response is generated by hair cells.

data = scipy.io.loadmat('/auto/users/luke/Python Summer Club/4 - EFR/EFR_data.mat',chars_as_strings=True)
# I know we haven't gone through scipy, but this is a useful function that will 
# load a MATLAB data file into a dictionary containing an entry for each variable.
# Let's separate the variables:

modulation_frequencies=data['modulation_frequencies'][0]
# This is an array of the stimulus modulation frequencies used

conditions=data['conditions'][0]
conditions=conditions.tolist()
conditions = [x[0].tolist() for x in conditions ]
# This is an array of the conditions (before and after ouabain)
# For some reason it imports as an array of arrays. These commands convert it to a list of strings.

microphone=data['microphone']
# This is an array of the signal recorded by a microphone used to monitor the sounds being presented
# Its shape is (1000,17,2) for (samples(time),modulation frequencies,conditions)
# Its units are micro-volts (uV)

electrode=data['electrode']
# This is an array of the electrode response
# Its shape is (1000,17,2) for (samples(time),modulation frequencies,conditions)
# Its units are micro-volts (uV)

fs=int(data['Fs'][0])
# This is the sampling frequency for both the microphone and electrode signals
# I converted it to an integer because this is what is expected by the fft function


# Problem 1: Plot the microphone and electrode signals for the control condition 
# for a few different modulation frequencies. Observe how the electrode response 
# is synchronized with the stimulus modulation frequency

## PROBLEM 1 ANSWER


# Problem 2: In the first problem, you may have noticed that the electrode signal
# is not centered at 0 uV. For each modulation frequency and condition, subtract the
# mean across time. Use broadcasting. In practice this isn't necessary, but it 
# will make your plots look better.

## PROBLEM 2 ANSWER

# Problem 3: Calculate the frequency response of the microphone and electrode
# signals for the 1000 Hz modulation frequency stimulus. This can be done using Brad's get_fft 
# function he posted for the problem of week 3, which is included at the begenning 
# of this file. I modified his function to also return the phase of the response,
# which will be used later in the problem. Plot the microphone frequency response
# using a linear frequency (X) axis and a logarithmic amplitude (Y) axis. Plot the electrode 
# frequency response using a linear frequency (X) axis and a linear amplitude (Y) axis.
# Observe that there is no frequency component in the microphone signal at the
# modulation frequency. Instead, there are components at the carrier frequency (32 kHz),
# and 1000 Hz up and down from this frequency (or whatever the modulation frequency is).
# This is a general property of sinusoidally amplitude-modulated tones.
# Observe that there is little energy at the carrier frequency (32 kHz) in the 
# electrode signal (the small amount that there is is due to an artifact), and 
# instead there is substantial energy at the modulation frequency.

## PROBLEM 3 ANSWER


# Problem 4: For each stimulus, let's extract the response at the modulation frequnecy,
# as well as the noise floor of the response. Let's estimate the noise floor as the
# amplitude of the response averaged over frequencies from 30 Hz below to 10 Hz
# below the modulation frequency together with the response from 10 Hz above to
# 30 Hz above the modulation frequency. (Average all values that fit these criterea together)
# Create a function that will compute the frequency response of a signal and 
# return the response and noise floor for a specified frequency (outlined below). 
# Use this function to compute the amplitude of the response at the modulation frequency 
# for each of the 17 modulation frequencies in the control condition, and then plot these 
# amplitudes as a function of modulation frequency. Plot the noise floor on the same plot 
# as a dashed line of the same color.

# Interpretation: There are multiple peaks because the response from different generators 
# (neural centers and hair cells) is combined. Since there is a delay between the response 
# of each of these centers, at some modulation frequencies they are in phase and add, 
# and at some they are out of phase and cancel out, causing a pattern of peaks and troughs.


## PROBLEM 4 ANSWER
def efr_resp(fs, waveform,desired_frequency):
    sig_amp, sig_phase, noise=[[],[],[]] #remove this line and replace it with your function
    
    return sig_amp, sig_phase, noise
    


# Problem 5: In order to isolate the EFR component coming from hair cells, we
# applied ouabain to the round window. Ouabain kills auditory nerve fibers without 
# disrupting hair cell function, eliminating the response from the auditory
# nerve and beyond, and leaving only the response from the hair cells. Compute the 
# response from the 'After Ouabain' condition as you did for the 'Control' condition
# in Problem 3, and plot it on the same graph using a different color.
# Observe that the response is now flat across modulation frequency, consistent
# with a response from a single source (presumably the hair cells)

## PROBLEM 5 ANSWER



# PART 6 and beyond is a bit tricky to understand, so it's extra optional :-)

# Problem 6: The latency of an unknown system can be ustimated using something
# called group delay. This can be estimated as the slope of the phase vs. 
# modulation frequency function. To compute the group delay, first plot the phase:
#   1) Get an array of the phase at the modulation frequency for each stimulus.
#   2) Plot the phase vs modulation frequency for both the control and ouabain 
#       conditions. Notice how the phase jumps for the control condition
#       This happens because phase is ambiguous (if you have a 1 kHz sine wave,
#       its period is 1 millisecond, so you can't tell the difference between a 
#       delay of 0 ms and 1 ms, 2 ms, etc).


## PROBLEM 6 ANSWER



# Problem 7: If you have sampled using fine enough modulation frequency steps,
# you can remove the amibguity by "unwrapping" the phase. We will use np.unwrap
# to do this. This function looks for indexes where the difference in phase between
# adjacent points is greater than a half a period (pi radians), and adds or subtracts 
# one full period (2*pi) to make the difference less than a half period. 
# Continuing the steps to estimate group delay:
#   3) call np.unwrap on the phase plotted in part 6 to unwrap the phase
#   4) plot the unwrapped phase

## PROBLEM 7 ANSWER


# Problem 8: Compute the slope of the unwrapped phase to find the group delay:
#   5) Compute the slope of the curve
#       slope = diff(unwrapped_phase)/(difference_between_modulation_frequency_steps)        
#       difference_between_modulation_frequency_steps is 60 Hz in this case
#   6) Turn the slope into group delay in milleseconds. The slope is in units
#       of radians * seconds, convert it to group delay by:
#       group_delay = [slope / (2*pi)] * 1000 * -1
#   Plot the group delay for both conditions. Notice how the group delay goes from 
#   a curve with big peaks (due to the response from multiple neural centers 
#   combining with different delays) to a flat line (because there is only one source 
#   left, the hair cells).

## PROBLEM 8 ANSWER