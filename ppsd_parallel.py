#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 10:44:57 2019

@author: davcra
"""

import matplotlib.pyplot as plt
import numpy as np
import glob
import os

from obspy import read, read_inventory, UTCDateTime
from obspy.signal import PPSD

import multiprocessing
from functools import partial





#%%
def ppsd_process(inv, mseed_dir, out_dir, net_code,sta_code,cha_code, t):
    '''
    

    Parameters
    ----------
    inv : TYPE        Obspy inventory object
        DESCRIPTION.  Inventory object containg response information for all data to be processed.
    mseed_dir : TYPE  STRING
        DESCRIPTION.  Path to parent directory of data to be processed.
    out_dir : TYPE    STRING
        DESCRIPTION.  Path to write ppsd data to.
    net_code : TYPE   STRING
        DESCRIPTION.  Seed network code.
    sta_code : TYPE   STRING
        DESCRIPTION.  Seed station code.
    cha_code : TYPE   STRING
        DESCRIPTION.  Seed channel code
    t : TYPE          Obspy UTCDateTime object
        DESCRIPTION.  time

    Returns
    -------
    None.

    '''
    


    y = t.year
    jday = str(t.julday).zfill(3)


    strgs = (mseed_dir,y,net_code,sta_code,cha_code,net_code,sta_code,cha_code,y,jday)


    if cha_code[-1] == 'H':
        special_handling = 'hydrophone' #no differentiation after instrument correction
        db_bins=(-100, 100, 1.0)
    else:
        special_handling = None
        db_bins=(-200, -50, 1.0)


    file_path = "%s/%d/%s/%s/%s.D/%s.%s..%s.D.%d.%s"%strgs
    if  os.path.isfile(file_path):

        st = read(file_path)
        ppsd = PPSD(st[0].stats, metadata=inv, db_bins=db_bins,
                    special_handling=special_handling)
        ppsd.add(st)
        ppsd.db_bins=db_bins
        print(out_dir,net_code,sta_code,cha_code,y,jday)
        ppsd.save_npz('%s/%s.%s..%s.%d.%s.npz'%(out_dir,net_code,sta_code,cha_code,y,jday))
    else:
        print(f'{file_path} does not exist')





def combine_ppsd(out_dir,net_code,sta_code,cha_code):
    '''
    

    Parameters
    ----------
    out_dir : TYPE    STRING
        DESCRIPTION.  Path to write ppsd data to.
    net_code : TYPE   STRING
        DESCRIPTION.  Seed network code.
    sta_code : TYPE   STRING
        DESCRIPTION.  Seed station code.
    cha_code : TYPE   STRING
        DESCRIPTION.  Seed channel code

    Returns
    -------
    None.

    '''

    files = glob.glob(out_dir+'/%s.%s..%s*'%(net_code,sta_code,cha_code))
    if len(files) == 0:
        print('No PPSD files found!!')
    else:
        ppsd = PPSD.load_npz(files[0])
        for f in files[1:]:
            ppsd.add_npz(f)
            cmd = 'rm %s'%f
            os.system(cmd)
        odir = f'{out_dir}/{net_code}/{sta_code}/{cha_code}/'
        if  not os.path.isfile(odir):
            os.system(f'mkdir -p {odir}')
        ofile = f'{odir}/{net_code}.{sta_code}..{cha_code}'
        print(ofile)
        ppsd.save_npz(ofile)
        # ppsd.save_npz(out_dir+'%s.%s..%s.npz'%(net_code,sta_code,cha_code))


def main(inv, mseed_directory, out_dir, net_code, sta_code, cha_code, t1, t2):
    '''
    

    Parameters
    ----------
    inv : TYPE        Obspy inventory object
        DESCRIPTION.  Inventory object containg response information for all data to be processed.
    mseed_dir : TYPE  STRING
        DESCRIPTION.  Path to parent directory of data to be processed.
    out_dir : TYPE    STRING
        DESCRIPTION.  Path to write ppsd data to.
    net_code : TYPE   STRING
        DESCRIPTION.  Seed network code.
    sta_code : TYPE   STRING
        DESCRIPTION.  Seed station code.
    cha_code : TYPE   STRING
        DESCRIPTION.  Seed channel code
    t1 : TYPE         Obspy UTCDateTime object
        DESCRIPTION.  Start date/time of data to process
    t2 : TYPE         Obspy UTCDateTime object
        DESCRIPTION.  Start date/time of data to process

    Returns
    -------
    None.

    '''

    pool = multiprocessing.Pool()

    times = np.arange(t1,t2,86400)
    func = partial(ppsd_process, inv, mseed_directory, out_dir, net_code, sta_code, cha_code)

    pool.map_async(func, times)
    pool.close()
    pool.join()



def plot_ppsd(ppsd, fig_dir, cmap='cividis'):
    '''
    

    Parameters
    ----------
    ppsd : TYPE      Obspy ppsd object
        DESCRIPTION. ppsd data to plot
    fig_dir : TYPE   pSTRING
        DESCRIPTION. path to save figure to.
    cmap : TYPE, optional. Obspy colormap object.
        DESCRIPTION. The default is 'cividis'. 
                     See https://matplotlib.org/stable/tutorials/colors/colormaps.html for more options.

    Returns
    -------
    None.

    '''

    fig_name = '%s/%s_%s.png'%(fig_dir,ppsd.station,ppsd.channel)
    if ppsd.channel[-1] == 'H':
        show_noise_models = False
    else:
        show_noise_models = True



    ppsd.plot(grid=False, show_coverage=True,
              show_noise_models=show_noise_models, show=True)
    print(fig_name)
