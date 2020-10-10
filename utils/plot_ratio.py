#!/usr/bin/env python
#
# Author: Zishuo Yang, Yipeng Sun
# License: GPLv2
# Based on:
#   https://github.com/ZishuoYang/my-hammer-reweighting/blob/master/plot_ratio.py
# Last Change: Sat Oct 10, 2020 at 10:32 PM +0800

import ROOT as rt

from argparse import ArgumentParser


#################################
# Command line arguments parser #
#################################

def parse_input():
    parser = ArgumentParser(description='''
Plot fit variables of R(D(*)) with and without FF reweighting.''')

    parser.add_argument('-o', '--output-path',
                        nargs='?',
                        default='./gen',
                        help='''
specify output path for plots.''')

    parser.add_argument('-d', '--data-ntuple',
                        nargs='?',
                        required=True,
                        help='''
specify path to ntuple that contains fit variables.''')

    parser.add_argument('-w', '--weight-ntuple',
                        nargs='?',
                        required=True,
                        help='''
specify path to ntuple that contains FF weights.''')

    parser.add_argument('-t', '--data-tree',
                        nargs='?',
                        required=True,
                        help='''
specify tree name in fit-variable ntuple.''')

    parser.add_argument('-T', '--weight-tree',
                        nargs='?',
                        required=True,
                        help='''
specify tree name in weight ntuple.''')

    parser.add_argument('--ff-weight',
                        nargs='?',
                        default='w_ff',
                        help='''
specify branch name of the FF weight.''')

    parser.add_argument('--vars',
                        nargs='+',
                        default=['q2', 'mm2', 'el'],
                        help='''
specify variables to plot.''')

    parser.add_argument('--bin-ranges',
                        nargs='+',
                        default=['(80,-3,12)', '(80,-3,12)', '(80,-0.5,3.5)'],
                        help='''
specify number of bins and x ranges.''')

    parser.add_argument('--up-y-min',
                        nargs='+',
                        default=[0, 0, 0],
                        type=float,
                        help='''
specify up plot min y.''')

    parser.add_argument('--up-y-max',
                        nargs='+',
                        default=[80, 180, 200],
                        type=float,
                        help='''
specify up plot max y.''')

    parser.add_argument('--down-y-min',
                        nargs='+',
                        default=[0.5, 0.5, 0.5],
                        type=float,
                        help='''
specify down plot min y.''')

    parser.add_argument('--down-y-max',
                        nargs='+',
                        default=[1.2, 1.2, 1.2],
                        type=float,
                        help='''
specify down plot max y.''')

    return parser.parse_args()


###########
# Helpers #
###########

def plot_ratio(tree, output_path,
               var, weight, title,
               bin_range,
               up_y_min, up_y_max,
               down_y_min, down_y_max):
    rt.gStyle.SetOptStat(0)
    canvas = rt.TCanvas('canvas', 'A ratio plot')

    tree.Draw('{}>>h1{}'.format(var, bin_range), '', 'goff', 50000, 20000)
    h1 = rt.gDirectory.Get('h1')
    h1.SetMarkerColor(rt.kBlue)
    h1.SetLineColor(rt.kBlue)

    tree.Draw('{}*{}>>h2{}'.format(var, weight, bin_range),
              '', 'goff', 50000, 20000)
    h2 = rt.gDirectory.Get('h2')
    h2.SetMarkerColor(rt.kRed)
    h2.SetLineColor(rt.kRed)

    rp = rt.TRatioPlot(h1, h2, 'divsym')
    rp.Draw()
    rp.GetLowerRefXaxis().SetTitle(title)
    rp.GetUpperRefYaxis().SetRangeUser(up_y_min, up_y_max)
    rp.GetLowerRefYaxis().SetRangeUser(down_y_min, down_y_max)
    canvas.Update()

    canvas.Print('{}/{}.png'.format(output_path, var))


if __name__ == '__main__':
    args = parse_input()

    data_ntuple = rt.TFile(args.data_ntuple)
    weight_ntuple = rt.TFile(args.weight_ntuple)

    data_tree = data_ntuple.Get(args.data_tree)
    weight_tree = weight_ntuple.Get(args.weight_tree)

    # Add friend to associate events
    # NOTE: We need to build index first before adding as friend. See
    #  https://root.cern.ch/doc/master/classTTreeIndex.html
    # under "TreeIndex and Friend Trees" section for more info.
    data_tree.BuildIndex("runNumber", "eventNumber")
    weight_tree.AddFriend(data_tree)

    for var, bin_range, up_y_min, up_y_max, down_y_min, down_y_max in \
        zip(args.vars, args.bin_ranges, args.up_y_min, args.up_y_max,
            args.down_y_min, args.down_y_max):
        plot_ratio(weight_tree, args.output_path,
                   var, args.ff_weight, var,
                   bin_range,
                   up_y_min, up_y_max,
                   down_y_min, down_y_max)