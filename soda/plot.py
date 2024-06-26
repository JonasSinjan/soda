from datetime import datetime, timedelta
import portion

from bokeh.io import output_file, show
from bokeh.models import MultiChoice, PanTool, BoxZoomTool, FixedTicker, Div
from bokeh.plotting import figure
from bokeh.layouts import gridplot, Spacer, column

from soda.availability import DataProduct
from soda.trajectory import get_traj


class DataAvailabilityPlotter:
    def __init__(self, output_filename='soda.html'):
        output_file(output_filename, title='SODA')
        datestr = datetime.now().strftime('%Y-%m-%d')
        tools = [PanTool(dimensions='width'),
                 BoxZoomTool(dimensions='width'),
                 'undo',
                 'redo',
                 'reset']
        self.plotter = figure(sizing_mode='stretch_width', plot_height=500,
                              x_axis_type='datetime', y_range=[],
                              x_range=(datetime(2020, 2, 10), datetime.now()),
                              tools=tools)
        self.plotter.ygrid.grid_line_color = None
        self.plotter.outline_line_color = None

        self.all_options = ['SWA-PAS-MOM', 'SWA-PAS-GRND-MOM',
                            'SWA-EAS-PAD-PSD',
                            'MAG-RTN-NORMAL',
                            'RPW-BIA-DENSITY',
                            'EPD-EPT-SUN-RATES',
                            'EPD-STEP-RATES',
                            'EUI-FSI304-IMAGE', 'EUI-FSI174-IMAGE',
                            'EUI-HRILYA1216-IMAGE', 'EUI-HRIEUV174-IMAGE',
                            'PHI-FDT-BLOS',
                            'PHI-HRT-BLOS',
                            'SPICE-N-RAS',
                            'SPICE-N-EXP',
                            'SOLOHI-1FT'
                            ][::-1]
        self.all_options = [i.lower() for i in self.all_options]
        '''
        self.multi_choice = MultiChoice(
            value=self.all_options,
            options=self.all_options,
            width_policy='fit',
            width=200,
            sizing_mode='stretch_height',
            title='Select data products')
        '''

        self.r_plot = figure(sizing_mode='stretch_width', plot_height=150,
                             x_axis_type='datetime', y_range=[0.25, 1.05],
                             x_range=self.plotter.x_range,
                             title='Radial distance',
                             tools=tools)
        
        self.phi_plot = figure(sizing_mode='stretch_width', plot_height=150,
                               x_axis_type='datetime', y_range=[0, 180],
                               x_range=self.plotter.x_range,
                               title='Earth-Orbiter angle',
                               tools=tools)
        self.phi_plot.yaxis[0].ticker = FixedTicker(ticks=[0, 90, 180])

        self.hlat_plot = figure(sizing_mode='stretch_width', plot_height=150,
                               x_axis_type='datetime', y_range=[-40, 40],
                               x_range=self.plotter.x_range,
                               title='Orbiter Heliographic Latitude',
                               tools=tools)
        self.hlat_plot.yaxis[0].ticker = FixedTicker(ticks=[-40, -20, 0, 20, 40])
        self.add_trajectory()

        url = '<a href="http://soar.esac.esa.int/soar/">Solar Oribter Archive</a>'
        gurl = '<a href="https://github.com/JonasSinjan/soda">Github Repo</a>'
        self.title = Div(
            text=(f"<h1>Solar Orbiter data availability</h1> "
                  f"<p>Extension of project by David Stansby, available at this {gurl}</p> "
                  f"Last updated {datestr}, daily resolution, "
                  f"all data available at the {url}"))
        self.title.style = {'text-align': 'center'}

        panels = [self.plotter, self.r_plot, self.phi_plot, self.hlat_plot]
        for p in panels + [self.title]:
            p.align = 'center'
        layout = gridplot(panels, ncols=1,
                          sizing_mode='stretch_width',
                          toolbar_location='right')
        self.layout = column([self.title, layout], sizing_mode='stretch_width')
        # top, right, bottom, left
        self.layout.margin = (0, 75, 0, 75)
        # Add data
        for desc in self.all_options:
            self.add_interval_data(desc)

        # self.multi_choice.js_link("value", self.plotter.y_range, "factors")
        self.plotter.y_range.factors = self.all_options

    def add_interval_data(self, descriptor):
        product = DataProduct(descriptor)
        intervals = self.merge_intervals(product.intervals)
        for interval in intervals:
            self.plotter.hbar(y=[descriptor],
                              left=interval.lower,
                              right=interval.upper,
                              height=0.5,
                              color=self.get_color(descriptor))

    def add_trajectory(self):
        dates, r, sun_earth_angle, hlat_solo = get_traj()
        self.r_plot.line(x=dates, y=r)
        self.phi_plot.line(x=dates, y=sun_earth_angle)
        self.hlat_plot.line(x=dates, y=hlat_solo)

    @staticmethod
    def get_color(descriptor):
        return {'eui': '#e41a1c',
                'phi': '#808080',
                'mag': '#377eb8',
                'swa': '#4daf4a',
                'rpw': '#984ea3',
                'epd': '#ff7f00',
                'spi': '#a65628',
                'sol': '#dd1c77',
                }[descriptor[:3]]

    @staticmethod
    def merge_intervals(intervals):
        intervals = intervals.sort_values(by='Start')
        start_dates = intervals['Start'].map(lambda t: t.date()).unique()
        end_dates = (intervals['End'] +
                     timedelta(days=1) -
                     timedelta(microseconds=1)).map(lambda t: t.date()).unique()
        intervals = portion.empty()
        for start, end in zip(start_dates, end_dates):
            intervals = intervals | portion.closed(start, end)
        return intervals

    def show(self):
        show(self.layout)
