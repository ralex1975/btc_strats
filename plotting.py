import plotly
import plotly.graph_objs as go


def linechart():
    pass

def barchart(data, filename):
    pass

def heatmap(var1, var2, filename):
    pass




def AnalyzeResults(self, plot=True, *args):
    """
    Applies only to optimized strategies where there are more than 1 strategy result
    """

   


    # Else plot all of the heatmaps
    for performance_list in performance_dict:
        if performance_list in ["draw_length"]:
            reversescale = True
        else:
            reversescale = False

        # Create plotly graph object
        trace = go.Heatmap(x=first_param, y=second_param, z=performance_dict[performance_list], zsmooth=None,
                           connectgaps=True,
                           colorscale='Viridis', reversescale=reversescale,
                           colorbar=dict(thickness=60, tickfont=dict(
                                   size=18)))

        # Stylize the layout
        layout = dict(xaxis=dict(range=[min(first_param), max(first_param)], title=param_name1, tickfont=dict(
                size=25)),
                      yaxis=dict(range=[min(second_param), max(second_param)], title=param_name2, tickfont=dict(
                              size=25)),
                      title=str(performance_list), width=3000, height=2100, titlefont=dict(size=40))

        data = [trace]
        figure = dict(data=data, layout=layout)
        stratname = self.strat_list[0].__class__.__name__
        plotly.offline.plot(figure, filename=str(performance_list) + stratname + '.html', image='png')
