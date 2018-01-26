#!/usr/bin/env python

#----------------------------------------------------------------------------
# Name:         ListCtrl_edit.py
# Purpose:      Testing editing a ListCtrl
#
# Author:       Pim van Heuven
#
# Created:      2004/10/15
# Copyright:    (c) Pim Van Heuven
# Licence:      wxWindows license
#----------------------------------------------------------------------------

import os, sys
import csv
import wx
import wx.lib.mixins.listctrl as listmix
import pandas as pd

#---------------------------------------------------------------------------

_tickers_df = None

#---------------------------------------------------------------------------

def GetHoldings():
    tickerscrape_env = "TICKERSCRAPE_HOME"
    tickerscrape_home = None

    # Get the home directory of the application
    if tickerscrape_env in os.environ:
        tickerscrape_home = os.environ[tickerscrape_env]
    if not tickerscrape_home:
        if os.name == "posix":
            tickerscrape_home = "/opt/tickerscrape"
        elif os.name == "nt":
            tickerscrape_home = os.environ["APPDATA"] + "\\tickerscrape"
            
    try:
        os.stat(tickerscrape_home)
    except:
        try:
            os.mkdir(tickerscrape_home)
        except IOError as e:
            print(e)
            return None

    # Get the holdings table
    global _tickers_df
    _tickers_df = pd.read_csv(tickerscrape_home + "/tickers.csv")
    _tickers_df.fillna("", inplace=True)
    print(_tickers_df)
    
    # Save the holdings table
    df = _tickers_df.set_index("Ticker", inplace=False)
    df.to_csv(tickerscrape_home + "/tickers_out.csv")
    

class TestListCtrl(wx.ListCtrl,
                   listmix.ListCtrlAutoWidthMixin,
                   listmix.TextEditMixin):

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.Populate()
        listmix.TextEditMixin.__init__(self)


    def Populate(self):
        GetHoldings()
        
        # for normal, simple columns, you can add them like this:
        self.InsertColumn(0, "Ticker")
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "Shares")
        self.InsertColumn(3, "Cost Basis")
        self.InsertColumn(4, "Purchase Date")
        self.InsertColumn(5, "Len 1", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(6, "Len 2", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(7, "Len 3", wx.LIST_FORMAT_RIGHT)

        for key, row in _tickers_df.iterrows():
            index = self.InsertItem(self.GetItemCount(), row["Ticker"])
            self.SetItem(index, 2, str(row["Shares"]))
            self.SetItem(index, 3, str(row["Cost Basis"]))
            self.SetItem(index, 4, str(row["Purchase Date"]))
            self.SetItemData(index, key)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(4, wx.LIST_AUTOSIZE)

        self.currentItem = 0


    def SetStringItem(self, index, col, data):
        if col in range(3):
            wx.ListCtrl.SetItem(self, index, col, data)
            wx.ListCtrl.SetItem(self, index, 5+col, str(len(data)))
        elif col in [3, 4]:
            wx.ListCtrl.SetItem(self, index, col, data)
        else:
            try:
                datalen = int(data)
            except:
                return

            wx.ListCtrl.SetItem(self, index, col, data)

            data = self.GetItem(index, col-5).GetText()
            wx.ListCtrl.SetItem(self, index, col-5, data[0:datalen])



class TestListCtrlPanel(wx.Panel):
    def __init__(self, parent, log):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        self.log = log
        tID = wx.NewId()

        sizer = wx.BoxSizer(wx.VERTICAL)

        if wx.Platform == "__WXMAC__" and \
               hasattr(wx.GetApp().GetTopWindow(), "LoadDemo"):
            self.useNative = wx.CheckBox(self, -1, "Use native listctrl")
            self.useNative.SetValue(
                not wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") )
            self.Bind(wx.EVT_CHECKBOX, self.OnUseNative, self.useNative)
            sizer.Add(self.useNative, 0, wx.ALL | wx.ALIGN_RIGHT, 4)

        self.list = TestListCtrl(self, tID,
                                 style=wx.LC_REPORT
                                 | wx.BORDER_NONE
                                 #| wx.LC_SORT_ASCENDING            # Content of list as instructions is
                                 | wx.LC_HRULES | wx.LC_VRULES      # nonsense with auto-sort enabled
                                 )

        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)


    def OnUseNative(self, event):
        wx.SystemOptions.SetOption("mac.listctrl.always_use_generic", not event.IsChecked())
        wx.GetApp().GetTopWindow().LoadDemo("ListCtrl_edit")



#---------------------------------------------------------------------------

def runTest(frame, nb, log):
    win = TestListCtrlPanel(nb, log)
    return win

#---------------------------------------------------------------------------


if __name__ == '__main__':
    import sys,os
    import wxticker.run
    
    wxticker.run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])

