#   --------------------------------------------------------------------------
# Copyright (c) <2017> <Lionel Garcia>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#   --------------------------------------------------------------------------
#
#   Not fully documented


import matplotlib as mpl
from cycler import cycler
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


def use_colors(tones, i=None):
    """
    Use specific color tones for plotting. If i is specified, this function returns a specific color from the corresponding color cycle

    Args:
        tones : 'hot' or 'cold' for hot and cold colors

    Returns:
        color i of the color cycle
    """

    hot = ['#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#b10026']
    cold = ['#a6bddb', '#67a9cf', '#3690c0', '#02818a', '#016c59', '#014636']
    # cold = ['#44AE7E', '#388A8D', '#397187', '#3E568E', '#463883', '#461167']

    if i is None:
        if tones is 'hot':
            colors = hot
        elif tones is 'cold':
            colors = cold
        else:
            colors = tones
        plt.rc('axes', prop_cycle=(cycler('color', colors)))
        return colors

    else:
        if tones is 'hot':
            colors = hot
        elif tones is 'cold':
            colors = cold
        else:
            colors = tones
        return colors[i % len(colors)]


def use():

    use_colors('cold')

    mpl.rcParams['font.family'] = 'arial'
    mpl.rcParams['axes.titlesize'] = 9
    mpl.rcParams['axes.titlepad'] = 6
    mpl.rcParams['text.antialiased'] = True
    mpl.rcParams['text.color'] = '#545454'
    mpl.rcParams['axes.labelcolor'] = '#545454'
    mpl.rcParams['ytick.color'] = '#545454'
    mpl.rcParams['xtick.color'] = '#545454'
    mpl.rcParams['axes.titleweight'] = 'demibold'
    mpl.rcParams['axes.labelsize'] = 9
    mpl.rcParams['xtick.labelsize'] = 8
    mpl.rcParams['ytick.labelsize'] = 8
    mpl.rcParams['axes.spines.left'] = True
    mpl.rcParams['axes.spines.bottom'] = True
    mpl.rcParams['axes.spines.right'] = True
    mpl.rcParams['axes.spines.top'] = True
    mpl.rcParams['lines.antialiased'] = True
    mpl.rcParams['lines.linewidth'] = 1
    mpl.rcParams['lines.markersize'] = 3
    mpl.rcParams['legend.fontsize'] = 8
    mpl.rcParams['legend.columnspacing'] = 0.5

    mpl.rcParams['axes.grid'] = True
    mpl.rcParams['grid.color'] = '#DBDBDB'
    mpl.rcParams['grid.alpha'] = 0.2


def style(axe, ticks=True):
    """
    Apply Bokeh-like styling to a specific axe

    Args:
        axe : axe to be styled
    """
    use()

    if hasattr(axe, 'spines'):
        axe.spines['bottom'].set_color('#545454')
        axe.spines['left'].set_color('#545454')
        axe.spines['top'].set_color('#DBDBDB')
        axe.spines['right'].set_color('#DBDBDB')
        axe.spines['top'].set_linewidth(1)
        axe.spines['right'].set_linewidth(1)

    if hasattr(axe, 'yaxis'):
        axe.yaxis.labelpad = 3

    if hasattr(axe, 'xaxis'):
        axe.xaxis.labelpad = 3

    if ticks is True:
        if hasattr(axe, 'yaxis'):
            x_ticks = axe.xaxis.get_majorticklocs()
            axe.xaxis.set_minor_locator(MultipleLocator((x_ticks[1] - x_ticks[0]) / 5))
        if hasattr(axe, 'yaxis'):
            y_ticks = axe.yaxis.get_majorticklocs()
            axe.yaxis.set_minor_locator(MultipleLocator((y_ticks[1] - y_ticks[0]) / 5))