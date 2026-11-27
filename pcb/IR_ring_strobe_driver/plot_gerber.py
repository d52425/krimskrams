import os, wx
app = wx.App()
import pcbnew
b = pcbnew.LoadBoard("IR_ring_strobe.kicad_pcb")
os.makedirs("gerber", exist_ok=True)
pc = pcbnew.PLOT_CONTROLLER(b)
po = pc.GetPlotOptions()
po.SetOutputDirectory("gerber")
po.SetPlotFrameRef(False)
po.SetUseGerberProtelExtensions(True)
po.SetUseGerberX2format(False)
po.SetScale(1)
po.SetMirror(False)
po.SetUseAuxOrigin(False)
for name, lid in [("F.Cu", pcbnew.F_Cu), ("B.Cu", pcbnew.B_Cu),
                  ("F.SilkS", pcbnew.F_SilkS), ("B.SilkS", pcbnew.B_SilkS),
                  ("F.Mask", pcbnew.F_Mask), ("B.Mask", pcbnew.B_Mask),
                  ("F.Paste", pcbnew.F_Paste), ("B.Paste", pcbnew.B_Paste),
                  ("Edge.Cuts", pcbnew.Edge_Cuts)]:
    pc.SetLayer(lid)
    pc.OpenPlotfile(name, pcbnew.PLOT_FORMAT_GERBER, name)
    print(name, pc.PlotLayer())
pc.ClosePlot()
