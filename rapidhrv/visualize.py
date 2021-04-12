from rapidhrv.analyze import _outlier_detect, _normalize_data, _get_peaks
import numpy as np
import matplotlib.pyplot as plt  # Plotting


# Visualize data
def _time_series_visualization(inputframe, ylim=None):
    if ylim is None:
        ylim = [30, 180, 2, 262]
    propscreened = (np.count_nonzero(np.isnan(inputframe['data']['BPM'])) * 100) / len(inputframe['data']['BPM'])
    propoutliers = (np.count_nonzero(np.isnan(inputframe['data']['CleanedBPM'])) * 100) / len(
        inputframe['data']['CleanedBPM']) - propscreened

    fig, axs = plt.subplots(4, 1)
    fig.set_size_inches(18, 10)
    fig.suptitle('Heart Rate and Variability Time Series', fontsize=25, fontweight='bold')

    # Text/labels
    boxprop = dict(boxstyle='round', pad=0.4, facecolor='khaki', alpha=0.7)
    rejection_text = f'{round(propoutliers + propscreened, 2)}% of windows excluded: \n' \
                     f'{round(propscreened, 2)}% = insufficient peaks \n' \
                     f'{round(propoutliers, 2)}% = outliers'
    plt.gcf().text(0.1, 0.92, s=rejection_text, fontsize=11, bbox=boxprop)
    axs[0].set_ylabel('BPM', fontsize=15)
    axs[0].xaxis.set_ticklabels([])
    axs[1].set_ylabel('BPM (cleaned)', fontsize=15)
    axs[1].xaxis.set_ticklabels([])
    axs[2].set_ylabel('RMSSD', fontsize=15)
    axs[2].xaxis.set_ticklabels([])
    axs[3].set_ylabel('RMSSD (cleaned)', fontsize=15)
    axs[3].set_xlabel('Time (seconds)', fontsize=20)

    # Grid
    for axisnum in range(0, 4):
        axs[axisnum].grid(b=True, axis='x', color='darkgrey')
        axs[axisnum].spines['bottom'].set_linewidth(2)
        axs[axisnum].spines['left'].set_linewidth(2)
        axs[axisnum].spines['top'].set_linewidth(0)
        axs[axisnum].spines['right'].set_linewidth(0)

    # HR Axes
    axs[0].set_xlim(inputframe['data']['Time'].iloc[0] - 5, inputframe['data']['Time'].iloc[-1] + 5)
    axs[0].set_ylim(ylim[0] - 20, ylim[1] + 20)
    axs[1].set_xlim(inputframe['data']['Time'].iloc[0] - 5, inputframe['data']['Time'].iloc[-1] + 5)
    axs[1].set_ylim(ylim[0] - 20, ylim[1] + 20)


    # HRV Axes
    axs[2].set_xlim(inputframe['data']['Time'].iloc[0] - 5, inputframe['data']['Time'].iloc[-1] + 5)
    axs[2].set_ylim(ylim[2] - 20, ylim[3] + 20)
    axs[3].set_xlim(inputframe['data']['Time'].iloc[0] - 5, inputframe['data']['Time'].iloc[-1] + 5)
    axs[3].set_ylim(ylim[2] - 20, ylim[3] + 20)

    # Drop NaNs and sort by cleaning
    rawoutput = inputframe['data'][['Time', 'BPM', 'RMSSD']].dropna()
    cleanedoutput = inputframe['data'][['Time', 'CleanedBPM', 'CleanedRMSSD']].dropna()

    # Plotting
    axs[0].plot(rawoutput['Time'], rawoutput['BPM'], color='red', linewidth=3, alpha=0.3)
    axs[0].scatter(rawoutput['Time'], rawoutput['BPM'], s=4, color='red')
    axs[1].plot(cleanedoutput['Time'], cleanedoutput['CleanedBPM'], color='red', linewidth=3, alpha=0.3)
    axs[1].scatter(cleanedoutput['Time'], cleanedoutput['CleanedBPM'], s=4, color='red')
    axs[2].plot(rawoutput['Time'], rawoutput['RMSSD'], color='purple', linewidth=3, alpha=0.3)
    axs[2].scatter(rawoutput['Time'], rawoutput['RMSSD'], s=4, color='purple')
    axs[3].plot(cleanedoutput['Time'], cleanedoutput['CleanedRMSSD'], color='purple', linewidth=3, alpha=0.3)
    axs[3].scatter(cleanedoutput['Time'], cleanedoutput['CleanedRMSSD'], s=4, color='purple')

    return fig


# Class to make figure interactive
class Visualize:
    """Class to plot uncleaned and cleaned heart rate and variability time series. The user can click on points in
    the time series. This will plot the specific window, and let the user know whether said window was cleaned.

     Parameters:
         inputdata (list): cardiac data that was analysed, ideally preprocessed
         inputframe (pandas DataFrame): analysed data, returned from extract_heart
         ylim (list): minimum and maximum values for BPM and RMSSD ya axes [BPM min, BPM max, RMSSD min, RMSSD max].
         These are adjusted slightly by RapidHRV (+-20). Optional (default = [30, 180, 2, 262])

     Returns:
     matplotlib object

    """

    def __init__(self, inputdata, inputframe, ylim=None):
        if ylim is None:
            ylim = [30, 180, 2, 262]
        self.processeddata = inputdata

        self.bpm = inputframe['data']['BPM']
        self.rmssd = inputframe['data']['RMSSD']
        self.exptime = inputframe['data']['Time']

        self.samplingrate = inputframe['features']['samplingrate']
        self.windowwidth = inputframe['features']['windowwidth']
        self.numpeaksneeded = inputframe['features']['numpeaksneeded']
        self.mad = inputframe['features']['mad']
        self.ibimad = inputframe['features']['ibimad']
        self.minamplitude = inputframe['features']['minamplitude']
        self.minwindow = inputframe['features']['minwindow']
        self.bpmrange = inputframe['features']['bpmrange']
        self.rmssdrange = inputframe['features']['rmssdrange']
        self.mindistance = inputframe['features']['mindistance']
        self.k = inputframe['features']['ecgclustering']

        fig = _time_series_visualization(inputframe=inputframe, ylim=ylim)
        fig.canvas.mpl_connect('button_press_event', self.onclick)

    def onclick(self, event):
        self.window_plot(event.xdata)  # Once user clicks on graph, pass to window_plot

    def window_plot(self, xclick):
        timeArray = np.asarray(self.exptime)
        idx = int((np.abs(timeArray - xclick)).argmin())
        section = int(timeArray[idx] * self.samplingrate)
        timepoint = round(self.exptime.iloc[idx], 2)

        # Get plotting data
        normed_data = _normalize_data(self.processeddata[section:section + (self.windowwidth * self.samplingrate)])

        # Initialize plot
        fig, axarr = plt.subplots()
        segtime = np.arange(0, self.windowwidth,
                            self.windowwidth / (self.samplingrate * self.windowwidth))  # x axis times
        fig.set_size_inches(18, 10)
        fig.suptitle(f'{self.windowwidth}s window at {round(timepoint, 2)} seconds (Index {idx}; Sample {section})',
                     fontsize=25)
        axarr.set_xlabel('Time (s)', fontsize=20)

        # Get and screen peaks
        peaks, properties = _get_peaks(inputdata=normed_data, distance=self.mindistance, prominence=self.minamplitude,
                                       k=self.k)
        Outliers, prom_thresholds, height_thresholds, _, _, IBIOutliers, baseheight = \
            _outlier_detect(inputdata=normed_data, inputpeaks=peaks, properties=properties,
                            minpeaks=self.numpeaksneeded, minwindow=self.minwindow, samplingrate=self.samplingrate,
                            mad=self.mad, ibimad=self.ibimad, bpmrange=self.bpmrange, rmssdrange=self.rmssdrange)

        # Plot Rapid HRV data
        axarr.set_ylabel('Processed data', fontsize=20)
        axarr.set_ylim(-5, 105)
        # axarr.set_xlim(self.exptime[0]-10, self.exptime[-1]+10)
        axarr.plot(segtime, normed_data, linewidth=5)  # Plot processed data
        axarr.plot(peaks / self.samplingrate, normed_data[peaks], marker="x", color="red", markersize=20,
                   linewidth=0)  # plot peaks

        if peaks.size > 1:  # Plot peak-relevant data if more than one peak
            axarr.plot(np.repeat(height_thresholds[0], self.windowwidth + 1), "--",
                       color="gray", linewidth=3)  # plot height thresholds
            axarr.plot(np.repeat(height_thresholds[1], self.windowwidth + 1), "--", color="gray",
                       linewidth=3)  # +1 to extend to end
            axarr.plot(peaks / self.samplingrate, prom_thresholds[0], "--", color="purple",
                       linewidth=3)  # plot height thresholds
            axarr.plot(peaks / self.samplingrate, prom_thresholds[1], "--", color="purple", linewidth=3)
            axarr.plot(peaks / self.samplingrate, baseheight, "--", color="black", linewidth=3)

        # Plot Labchart data
        textBox = f'HR = {np.round(self.bpm.iloc[idx], 2)}, RMSSD = {np.round(self.rmssd.iloc[idx], 2)}'
        if Outliers:
            axarr.text(0, 0, textBox, fontsize=18, bbox=dict(boxstyle="round", facecolor="pink"))
        else:
            axarr.text(0, 0, textBox, fontsize=18, bbox=dict(boxstyle="round", facecolor="white"))

        fig.show()