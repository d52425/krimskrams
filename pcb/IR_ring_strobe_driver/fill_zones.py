import sys, wx
app = wx.App()
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
filler = pcbnew.ZONE_FILLER(b)
print("fill rc:", filler.Fill(b.Zones()))
b.Save(sys.argv[1])
