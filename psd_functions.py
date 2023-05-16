from matplotlib import mlab
from obspy.signal.invsim import cosine_taper
from obspy.signal.util import prev_pow_2

def plot_stream(stream):
    
    l = len(stream)
    fig, axes = plt.subplots(l,1, figsize=(10,10), sharex=True)
    
    for i,tr in enumerate(stream):
        times = tr.times()
        times = [(tr.stats.starttime+t).datetime for t in times]
        axes[i].plot(times, tr.data)
    
def calc_psd(trace):
    
    ppsd_length=3600.0
    noverlap = int(ppsd_length/2)
    nfft = 1024
    spec = 0
    num = 0
    for tr in trace.slide(ppsd_length, ppsd_length/2):
        if len(tr.data)%2 == 1:
            tr.data = tr.data[:-1]

        _spec, freq = mlab.psd(trace.data, nfft, int(trace.stats.sampling_rate),
                               detrend=mlab.detrend_linear, window=fft_taper,
                               #noverlap=noverlap, 
                               sides='onesided',
                               scale_by_freq=True)
        spec += _spec
        num += 1
    
    spec /= num    
        
    # leave out first entry (offset)
    spec = spec[1:]
    freq = freq[1:]
    
    return spec, freq

def fft_taper(data):
    """
    Cosine taper, 10 percent at each end (like done by [McNamara2004]_).

    .. warning::
        Inplace operation, so data should be float.
    """
    data = (data * cosine_taper(int(len(data)), 0.2))
    return data
    
def plot_ppsd(ppsd, fig_dir, cmap='cividis'):

    fig_name = '%s/%s_%s.png'%(fig_dir,ppsd.station,ppsd.channel)
    if ppsd.channel[-1] == 'H':
        show_noise_models = False
    else:
        show_noise_models = True

    ppsd.plot(grid=False, show_coverage=True, cmap=cmap,
              show_noise_models=show_noise_models, show=False)
    print(fig_name)

    fig= plt.gcf()
    fig.set_size_inches(fig_size_y*1.4, fig_size_y)
    ax1,ax2,ax3 = fig.get_axes()
    
    #fig,axes = plt.subplots(2,2,figsize=(15,15), sharex=True, sharey=True)
    #ax1,ax2,ax3,ax4 = axes.flatten()
    
    ax1.grid(True, linestyle='-.', lw=0.5, c='w', alpha=0.3)
    ax1.grid(True, linestyle='-.', which='minor', lw=0.3, c='w', alpha=0.3)
    # ax.tick_params(labelcolor='r', labelsize='medium', width=3)
    
    mn = ppsd.get_mean()
    md = ppsd.get_mode()
    p50 = ppsd.get_percentile(50)
    p90 = ppsd.get_percentile(90)
    p10 = ppsd.get_percentile(10)
    
    
    
    ax1.plot(mn[0], mn[1], 'k', linestyle='-.', label='mean')
    ax1.plot(md[0], md[1], 'k', label='mode')
    ax1.plot(p90[0], p90[1], 'k', linestyle=(0, (1, 1)), label='90%')
    ax1.plot(p10[0], p10[1], 'k', linestyle=(0, (1, 1)), label='10%')
    
    
    ax1.fill_between(p90[0], p90[1], ppsd.db_bins[1], color='blue', alpha=.05)
    ax1.fill_between(p10[0], p10[1], ppsd.db_bins[0], color='blue', alpha=.1)


    ax1.legend(loc=3, facecolor="lightgray")
    
    if ppsd.channel[-1] != 'H':
        ax1.text(0.1, -94, 'NHNM', rotation=-15)
        ax1.text(0.1, -166, 'NLNM', rotation=3)
    
    ax2.text(0.1,-4.5,'Green patches represent available data and red patches represent gaps in streams.\nThe bottom row in blue shows psd measurements that are actually present in the \nhistogram whereas gray patches show unselected data.',
              transform=ax2.transAxes)
    plt.savefig(fig_name, bbox_inches='tight')
    
