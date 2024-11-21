import matplotlib.pyplot as plt
import spiceypy as spice
from datetime import datetime
import matplotlib.dates as mdates
import plotly.express as px
import plotly.io as pio


def plotGanntSchedule(intervals, regions):
    """
    Creates a Gantt plot of observation intervals for different regions of interest.

    Parameters:
    - intervals: A list of tuples, where each tuple contains the start and end times in ephemeris time (ET).
    - regions: A list of region names corresponding to each interval.
    """
    
    def convert_to_datetime(et):
       
        utc_str = spice.et2utc(et, 'C', 3)  
        return datetime.strptime(utc_str, "%Y %b %d %H:%M:%S.%f")  

   
    plot_data = []
    for (start_et, end_et), region in zip(intervals, regions):
        start_dt = convert_to_datetime(start_et)
        end_dt = convert_to_datetime(end_et)
        plot_data.append(dict(Task=region, Start=start_dt, Finish=end_dt))

    
    fig = px.timeline(plot_data, x_start="Start", x_end="Finish", y="Task", color="Task", title='Observation Schedule Gantt Chart')

    
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),  
            type="date"
        ),
        yaxis=dict(autorange='reversed'),  
        height=max(400, len(set(regions)) * 20)  
        )
    #pio.renderers.default = "vscode"
    # Show the figure
    fig.show()


#
    ## Prepare data for plotting
    #plot_data = []
    #for (start_et, end_et), region in zip(intervals, regions):
    #    start_dt = convert_to_datetime(start_et)
    #    end_dt = convert_to_datetime(end_et)
    #    plot_data.append((start_dt, end_dt, region))
#
    ## Create a Gantt plot
    #fig, ax = plt.subplots(figsize=(40, len(set(regions)) * 5))
#
    ## Plot each interval
    #unique_regions = list(set(regions))  # Get unique region names
    #color_map = plt.cm.get_cmap('tab20', len(unique_regions))  # Use a colormap for different regions
#
    #for start, end, region in plot_data:
    #    y = unique_regions.index(region)  # Find y position based on unique region names
    #    
    #    # Correctly calculate duration for the bar width in days
    #    ax.barh(y, end - start, left=start, height=1.0, color=color_map(y), label=region if regions.index(region) == y else "", align='center')
#
    ## Format the plot
    #ax.set_yticks(range(len(unique_regions)))
    #ax.set_yticklabels(unique_regions, fontsize=6)
    #ax.set_xlim([min([d[0] for d in plot_data]), max([d[1] for d in plot_data])])
    #ax.set_xlabel('Time (UTC Date)')
    #ax.set_ylabel('Region of Interest')
    #ax.set_title('Observation Schedule Gantt Chart')
#
    ## Add more x-ticks using a DateFormatter and Locator for frequent ticks
    #ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))  # Set major ticks to every hour
    #ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))  # Set format for date labels
#
    #plt.grid(True)
#
    ## Move the legend outside the plot
    #ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    #
    ## Format the x-axis for better date representation
    #fig.autofmt_xdate()
#
    #plt.show()