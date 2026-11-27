#!/usr/bin/env python3
"""Generate the IR ring strobe driver KiCad project (schematic + PCB).

GPIO (3.3V) -> 100R -> Nch MOSFET gate (10k pull-down) -> low-side switch
of the +12V line feeding the FRS5CC LED ring via JST-XH. Bulk 1000uF/25V
(+10uF ceramic) sits on the +12V node next to the switch so the pulse
current comes from the capacitors, not the boost converter.

Board: 30x30mm, 2-layer. Passives are through-hole (axial resistors,
leaded ceramic) except Q1 (SOT-23). Schematic is emitted as text in the
KiCad 7.0 dialect (KiCad 10 reads it and migrates on save); the PCB is
built with the pcbnew API. Run with the KiCad-bundled python:

    KICAD_SHARE=<kicad share dir> <kicad python3> build_design.py

Then fill zones / DRC / gerbers with kicad-cli:

    kicad-cli pcb drc --refill-zones --save-board IR_ring_strobe.kicad_pcb
    kicad-cli pcb export gerbers --output gerber/ IR_ring_strobe.kicad_pcb
    kicad-cli pcb export drill --output gerber/ IR_ring_strobe.kicad_pcb
"""
import json 
import math 
import os 
import re 
import uuid 

HERE =os .path .dirname (os .path .abspath (__file__ ))
PROJ ="IR_ring_strobe"
KICAD_SHARE =os .environ .get ("KICAD_SHARE","/usr/share/kicad")
SYM_DIR =os .path .join (KICAD_SHARE ,"symbols")
FP_DIR =os .path .join (KICAD_SHARE ,"footprints")


def U ():
    return str (uuid .uuid4 ())


def fmt (v ):
    s =("%.4f"%v ).rstrip ("0").rstrip (".")
    return s if s not in ("-0","")else "0"






LOCAL_Q_NMOS_GSD =r'''(symbol "Q_NMOS_GSD" (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
        (property "Reference" "Q" (at 5.08 1.27 0)
          (effects (font (size 1.27 1.27)) (justify left))
        )
        (property "Value" "Q_NMOS_GSD" (at 5.08 -1.27 0)
          (effects (font (size 1.27 1.27)) (justify left))
        )
        (property "Footprint" "" (at 5.08 2.54 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (property "Datasheet" "~" (at 0 0 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (property "ki_keywords" "transistor NMOS N-MOS N-MOSFET" (at 0 0 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (property "ki_description" "N-MOSFET transistor, gate/source/drain" (at 0 0 0)
          (effects (font (size 1.27 1.27)) hide)
        )
        (symbol "Q_NMOS_GSD_0_1"
          (polyline
            (pts
              (xy 0.254 0)
              (xy -2.54 0)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.254 1.905)
              (xy 0.254 -1.905)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 -1.27)
              (xy 0.762 -2.286)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 0.508)
              (xy 0.762 -0.508)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 2.286)
              (xy 0.762 1.27)
            )
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 2.54 2.54)
              (xy 2.54 1.778)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 2.54 -2.54)
              (xy 2.54 0)
              (xy 0.762 0)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 0.762 -1.778)
              (xy 3.302 -1.778)
              (xy 3.302 1.778)
              (xy 0.762 1.778)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 1.016 0)
              (xy 2.032 0.381)
              (xy 2.032 -0.381)
              (xy 1.016 0)
            )
            (stroke (width 0) (type default))
            (fill (type outline))
          )
          (polyline
            (pts
              (xy 2.794 0.508)
              (xy 2.921 0.381)
              (xy 3.683 0.381)
              (xy 3.81 0.254)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (polyline
            (pts
              (xy 3.302 0.381)
              (xy 2.921 -0.254)
              (xy 3.683 -0.254)
              (xy 3.302 0.381)
            )
            (stroke (width 0) (type default))
            (fill (type none))
          )
          (circle (center 1.651 0) (radius 2.794)
            (stroke (width 0.254) (type default))
            (fill (type none))
          )
          (circle (center 2.54 -1.778) (radius 0.254)
            (stroke (width 0) (type default))
            (fill (type outline))
          )
          (circle (center 2.54 1.778) (radius 0.254)
            (stroke (width 0) (type default))
            (fill (type outline))
          )
        )
        (symbol "Q_NMOS_GSD_1_1"
          (pin input line (at -5.08 0 0) (length 2.54)
            (name "G" (effects (font (size 1.27 1.27))))
            (number "1" (effects (font (size 1.27 1.27))))
          )
          (pin passive line (at 2.54 -5.08 90) (length 2.54)
            (name "S" (effects (font (size 1.27 1.27))))
            (number "2" (effects (font (size 1.27 1.27))))
          )
          (pin passive line (at 2.54 5.08 270) (length 2.54)
            (name "D" (effects (font (size 1.27 1.27))))
            (number "3" (effects (font (size 1.27 1.27))))
          )
        )
      )'''


def extract_symbol (libfile ,name ):
    """Return the (symbol "name" ...) block text from a library file.

    KiCad 10 split libraries (<Lib>.kicad_symdir/<Symbol>.kicad_sym, one
    file per root symbol, subunits inside) are resolved as well.
    """
    if name .startswith ("Q_NMOS_GSD"):
        txt =LOCAL_Q_NMOS_GSD 
        start =txt .index ('(symbol "%s"'%name )
        depth ,i =0 ,start 
        while True :
            c =txt [i ]
            if c =="(":
                depth +=1 
            elif c ==")":
                depth -=1 
                if depth ==0 :
                    break 
            i +=1 
        return txt [start :i +1 ]
    p =os .path .join (SYM_DIR ,libfile )
    if os .path .exists (p ):
        txt =open (p ,encoding ="utf-8").read ()
    else :
        base =libfile [:-len (".kicad_sym")]if libfile .endswith (".kicad_sym")else libfile 
        root =re .sub (r"_\d+_\d+$","",name )
        txt =open (os .path .join (SYM_DIR ,base +".kicad_symdir",
        root +".kicad_sym"),encoding ="utf-8").read ()
    start =txt .index ('(symbol "%s"'%name )
    depth ,i =0 ,start 
    while True :
        c =txt [i ]
        if c =="(":
            depth +=1 
        elif c ==")":
            depth -=1 
            if depth ==0 :
                break 
        i +=1 
    return txt [start :i +1 ]


def symbol_pins (libfile ,name ):
    """Pins of subunit _1_1: {number: (x, y)} in symbol coords (y up)."""
    block =extract_symbol (libfile ,name +"_1_1")
    pins ={}
    for m in re .finditer (
    r'\(pin\s+\S+\s+\S+\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+\d+\)'
    r'.*?\(number\s+"(\d+)"',block ,re .S ):
        pins [m .group (3 )]=(float (m .group (1 )),float (m .group (2 )))
    return pins 


def _rot (ox ,oy ,rot ):
    if rot ==90 :
        return (oy ,-ox )
    if rot ==180 :
        return (-ox ,-oy )
    if rot ==270 :
        return (-oy ,ox )
    return (ox ,oy )


def pin_file_pos (pins ,num ,pos ,rot =0 ):
    px ,py =pins [num ]
    ox ,oy =_rot (px ,-py ,rot )
    return (round (pos [0 ]+ox ,2 ),round (pos [1 ]+oy ,2 ))


def place_by_pin (pins ,num ,target ,rot =0 ):
    px ,py =pins [num ]
    ox ,oy =_rot (px ,-py ,rot )
    return (round (target [0 ]-ox ,2 ),round (target [1 ]-oy ,2 ))


PARTS ={
"J1":("Connector_Generic","Conn_01x03","IN 12V/GND/STROBE",
"TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal"),
"J2":("Connector_Generic","Conn_01x02","RING OUT",
"TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal"),
"Q1":("Device","Q_NMOS_GSD","MTN2306AN3/AO3400A",
"Package_TO_SOT_SMD:SOT-23"),
"R1":("Device","R","100",
"Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
"R2":("Device","R","10k",
"Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
"C1":("Device","C_Polarized","1000uF/25V",
"Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"),
"C2":("Device","C","10uF",
"Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"),
}
VAL_OF ={r :v [2 ]for r ,v in PARTS .items ()}
FP_OF ={r :v [3 ]for r ,v in PARTS .items ()}

PINS ={}
lib_blocks =[]
_seen =set ()
for _ref ,(lib ,sym ,_val ,_fp )in PARTS .items ():
    if (lib ,sym )in _seen :
        continue 
    _seen .add ((lib ,sym ))
    block =extract_symbol (lib +".kicad_sym",sym )
    block =block .replace ('(symbol "%s"'%sym ,
    '(symbol "%s:%s"'%(lib ,sym ),1 )
    lib_blocks .append (block )
    PINS [sym ]=symbol_pins (lib +".kicad_sym",sym )




PLAN ={
"J1":("1",(30 ,50 ),0 ),
"J2":("2",(102 ,50 ),180 ),
"C1":("1",(56 ,64 ),0 ),
"C2":("1",(64 ,64 ),0 ),
"Q1":("3",(84 ,78 ),0 ),
"R1":("2",(68 ,83.08 ),90 ),
"R2":("1",(64 ,90 ),0 ),
}
POS ={}
PINPOS ={}
for ref ,(anch ,target ,rot )in PLAN .items ():
    sym =PARTS [ref ][1 ]
    pos =place_by_pin (PINS [sym ],anch ,target ,rot )
    POS [ref ]=(pos ,rot )
    for num in PINS [sym ]:
        PINPOS [(ref ,num )]=pin_file_pos (PINS [sym ],num ,pos ,rot )

wires =[]
junctions =[]
labels =[]


def wire (a ,b ):
    wires .append ((a [0 ],a [1 ],b [0 ],b [1 ]))


def stub_label (a ,b ,text ):
    wire (a ,b )
    junctions .append (a )
    labels .append ((text ,b [0 ],b [1 ]))


def PP (ref ,pinnum ):
    return PINPOS [(ref ,pinnum )]



wire (PP ("J1","1"),PP ("J2","2"))
wire ((56 ,50 ),PP ("C1","1"));junctions .append ((56 ,50 ))
wire ((64 ,50 ),PP ("C2","1"));junctions .append ((64 ,50 ))
wire (PP ("C1","2"),(56 ,78 ));labels .append (("GND",56 ,78 ))
wire (PP ("C2","2"),(64 ,78 ));labels .append (("GND",64 ,78 ))
stub_label ((84 ,50 ),(84 ,45 ),"+12V")

wire (PP ("J1","2"),(38 ,52.54 ));labels .append (("GND",38 ,52.54 ))
wire (PP ("J1","3"),(38 ,55.08 ));labels .append (("STROBE",38 ,55.08 ))

wire (PP ("J2","1"),(102 ,78 ))
wire ((102 ,78 ),PP ("Q1","3"))

wire (PP ("Q1","2"),(84 ,94 ));labels .append (("GND",84 ,94 ))

wire (PP ("Q1","1"),PP ("R1","2"))
wire (PP ("R1","1"),(52 ,83.08 ))
wire ((52 ,83.08 ),(52 ,92 ));labels .append (("STROBE",52 ,92 ))
wire ((64 ,83.08 ),PP ("R1","2"))
wire ((64 ,83.08 ),PP ("R2","1"));junctions .append ((64 ,83.08 ))
wire (PP ("R2","2"),(64 ,102 ));labels .append (("GND",64 ,102 ))


def _on_segment (p ,a ,b ):
    (px ,py ),(ax ,ay ),(bx ,by )=p ,a ,b 
    cross =(bx -ax )*(py -ay )-(by -ay )*(px -ax )
    if abs (cross )>0.01 :
        return False 
    dot =(px -ax )*(px -bx )+(py -ay )*(py -by )
    return dot <-0.001 


split_wires =[]
for (x1 ,y1 ,x2 ,y2 )in wires :
    cuts =[(jx ,jy )for (jx ,jy )in junctions 
    if _on_segment ((jx ,jy ),(x1 ,y1 ),(x2 ,y2 ))]
    cuts .sort (key =lambda p :(p [0 ]-x1 )**2 +(p [1 ]-y1 )**2 )
    pts =[(x1 ,y1 )]+cuts +[(x2 ,y2 )]
    for a ,b in zip (pts ,pts [1 :]):
        split_wires .append ((a [0 ],a [1 ],b [0 ],b [1 ]))
wires =split_wires 

sheet_uuid =U ()
sch =[]
sch .append ('(kicad_sch (version 20230121) (generator eeschema)')
sch .append ('  (uuid %s)'%sheet_uuid )
sch .append ('  (paper "A4")')
sch .append ('  (title_block (title "IR LED ring strobe driver - GPIO to '
'MOSFET 12V pulse switch") (date "2026-11-27") (rev "B"))')
sch .append ('  (lib_symbols')
for b in lib_blocks :
    sch .append ('    '+b .replace ('\n','\n    '))
sch .append ('  )')
for ref in ("J1","J2","C1","C2","Q1","R1","R2"):
    lib ,sym =PARTS [ref ][0 ],PARTS [ref ][1 ]
    pos ,r =POS [ref ]
    sch .append ('  (symbol (lib_id "%s:%s") (at %.2f %.2f %d) (unit 1) '
    '(in_bom yes) (on_board yes) (dnp no) (uuid %s)'
    %(lib ,sym ,pos [0 ],pos [1 ],r ,U ()))
    sch .append ('    (property "Reference" "%s" (at %.2f %.2f 0) '
    '(effects (font (size 1.27 1.27))))'
    %(ref ,pos [0 ],pos [1 ]-2.54 ))
    sch .append ('    (property "Value" "%s" (at %.2f %.2f 0) '
    '(effects (font (size 1.27 1.27))))'
    %(VAL_OF [ref ],pos [0 ],pos [1 ]+2.54 ))
    sch .append ('    (property "Footprint" "%s" (at %.2f %.2f 0) '
    '(effects (font (size 1.27 1.27)) hide))'
    %(FP_OF [ref ],pos [0 ],pos [1 ]))
    sch .append ('    (property "Datasheet" "" (at %.2f %.2f 0) '
    '(effects (font (size 1.27 1.27)) hide))'%(pos [0 ],pos [1 ]))
    for num in sorted (PINS [sym ]):
        sch .append ('    (pin "%s" (uuid %s))'%(num ,U ()))
    sch .append ('    (instances (project "%s" (path "/%s" '
    '(reference "%s") (unit 1))))'%(PROJ ,sheet_uuid ,ref ))
    sch .append ('  )')
for (x1 ,y1 ,x2 ,y2 )in wires :
    sch .append ('  (wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) '
    '(stroke (width 0) (type default)) (uuid %s))'
    %(x1 ,y1 ,x2 ,y2 ,U ()))
for (x ,y )in junctions :
    sch .append ('  (junction (at %.2f %.2f) (diameter 0) (color 0 0 0 0) '
    '(uuid %s))'%(x ,y ,U ()))
for (text ,x ,y )in labels :
    sch .append ('  (global_label "%s" (shape input) (at %.2f %.2f 0) '
    '(effects (font (size 1.27 1.27)) (justify left)) (uuid %s))'
    %(text ,x ,y ,U ()))
sch .append ('  (sheet_instances (path "/" (page "1")))')
sch .append (')')
with open (os .path .join (HERE ,PROJ +".kicad_sch"),"w")as f :
    f .write ("\n".join (sch )+"\n")
print ("schematic written")



import pcbnew 
MM =pcbnew .FromMM 

board =pcbnew .BOARD ()
nets ={}
for name in ("+12V","GND","STROBE","DRAIN","GATE"):
    ni =pcbnew .NETINFO_ITEM (board ,name )
    board .Add (ni )
    nets [name ]=ni .GetNetCode ()


def load_fp (lib ,name ):
    return pcbnew .FootprintLoad (os .path .join (FP_DIR ,lib +".pretty"),name )


def add_fp (lib ,name ,ref ,value ,pos ,rot =0 ,netmap =None ):
    fp =load_fp (lib ,name )
    fp .SetReference (ref )
    fp .SetValue (value )
    fp .SetPosition (pcbnew .VECTOR2I (MM (pos [0 ]),MM (pos [1 ])))
    fp .SetOrientationDegrees (rot )
    board .Add (fp )
    if netmap :
        for pad in fp .Pads ():
            n =netmap .get (pad .GetNumber ())
            if n :
                pad .SetNetCode (nets [n ])
    return fp 


def pad_pos (fp ,num ):
    for pad in fp .Pads ():
        if pad .GetNumber ()==num :
            p =pad .GetPosition ()
            return (pcbnew .ToMM (p .x ),pcbnew .ToMM (p .y ))
    raise KeyError (num )


def track (a ,b ,w ,net ,layer =pcbnew .F_Cu ):
    t =pcbnew .PCB_TRACK (board )
    t .SetStart (pcbnew .VECTOR2I (MM (a [0 ]),MM (a [1 ])))
    t .SetEnd (pcbnew .VECTOR2I (MM (b [0 ]),MM (b [1 ])))
    t .SetWidth (MM (w ))
    t .SetLayer (layer )
    t .SetNetCode (nets [net ])
    board .Add (t )


def via (pos ,net ):
    v =pcbnew .PCB_VIA (board )
    v .SetPosition (pcbnew .VECTOR2I (MM (pos [0 ]),MM (pos [1 ])))
    v .SetViaType (pcbnew .VIATYPE_THROUGH )
    v .SetDrill (MM (0.3 ))
    v .SetWidth (MM (0.6 ))
    v .SetNetCode (nets [net ])
    board .Add (v )






j1 =add_fp ("TerminalBlock_Phoenix",
"TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal",
"J1",VAL_OF ["J1"],(5.6 ,11.5 ),270 ,
{"1":"+12V","2":"GND","3":"STROBE"})
j1 .Reference ().SetPosition (pcbnew .VECTOR2I (MM (5.6 ),MM (24.8 )))
j2 =add_fp ("TerminalBlock_Phoenix",
"TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal",
"J2",VAL_OF ["J2"],(24.4 ,16.75 ),90 ,
{"1":"DRAIN","2":"+12V"})
j2 .Reference ().SetPosition (pcbnew .VECTOR2I (MM (24.4 ),MM (21.8 )))
c1 =add_fp ("Capacitor_THT","CP_Radial_D10.0mm_P5.00mm",
"C1",VAL_OF ["C1"],(15 ,9.7 ),90 ,
{"1":"+12V","2":"GND"})
c1 .Reference ().SetPosition (pcbnew .VECTOR2I (MM (22.2 ),MM (3.2 )))
c2 =add_fp ("Capacitor_THT","C_Disc_D5.0mm_W2.5mm_P2.50mm",
"C2",VAL_OF ["C2"],(13.75 ,15.9 ),0 ,
{"1":"+12V","2":"GND"})
c2 .Reference ().SetPosition (pcbnew .VECTOR2I (MM (19.6 ),MM (18.9 )))
for _p in c1 .Pads ():
    if _p .GetNumber ()=="2":
        _p .SetLocalZoneConnection (pcbnew .ZONE_CONNECTION_FULL )
q1 =add_fp ("Package_TO_SOT_SMD","SOT-23",
"Q1",VAL_OF ["Q1"],(15 ,20.6 ),0 ,
{"1":"GATE","2":"GND","3":"DRAIN"})
q1 .Reference ().SetPosition (pcbnew .VECTOR2I (MM (18.4 ),MM (20.6 )))
r1 =add_fp ("Resistor_THT","R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
"R1",VAL_OF ["R1"],(11.19 ,24.2 ),0 ,
{"1":"STROBE","2":"GATE"})
r1 .Reference ().SetPosition (pcbnew .VECTOR2I (MM (21.2 ),MM (24.2 )))
r2 =add_fp ("Resistor_THT","R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
"R2",VAL_OF ["R2"],(11.19 ,27.9 ),0 ,
{"1":"GATE","2":"GND"})
r2 .Reference ().SetPosition (pcbnew .VECTOR2I (MM (21.2 ),MM (27.9 )))
for i ,(hx ,hy )in enumerate ([(2.5 ,2.5 ),(27.5 ,2.5 ),(2.5 ,27.5 ),(27.5 ,27.5 )]):
    h =add_fp ("MountingHole","MountingHole_2.2mm_M2",
    "H%d"%(i +1 ),"",(hx ,hy ),0 )
    h .Reference ().SetVisible (False )

for _nm ,_fp in (("J1",j1 ),("J2",j2 )):
    _bb =_fp .GetCourtyard (pcbnew .F_CrtYd ).BBox ()
    print (_nm ,"courtyard x %.2f..%.2f y %.2f..%.2f"%(
    pcbnew .ToMM (_bb .GetLeft ()),pcbnew .ToMM (_bb .GetRight ()),
    pcbnew .ToMM (_bb .GetTop ()),pcbnew .ToMM (_bb .GetBottom ())),
    "pads",{p .GetNumber ():(round (pcbnew .ToMM (p .GetPosition ().x ),2 ),
    round (pcbnew .ToMM (p .GetPosition ().y ),2 ))
    for p in _fp .Pads ()})


track (pad_pos (j1 ,"1"),(10 ,11.5 ),1.0 ,"+12V")
track ((10 ,11.5 ),(10 ,9.7 ),1.0 ,"+12V")
track ((10 ,9.7 ),pad_pos (c1 ,"1"),1.0 ,"+12V")
track ((10 ,11.5 ),(10 ,15.9 ),0.8 ,"+12V")
track ((10 ,15.9 ),pad_pos (c2 ,"1"),0.8 ,"+12V")

track (pad_pos (c1 ,"1"),(15 ,6.4 ),1.0 ,"+12V",pcbnew .B_Cu )
track ((15 ,6.4 ),(22.4 ,6.4 ),1.0 ,"+12V",pcbnew .B_Cu )
track ((22.4 ,6.4 ),(22.4 ,13.25 ),1.0 ,"+12V",pcbnew .B_Cu )
track ((22.4 ,13.25 ),pad_pos (j2 ,"2"),1.0 ,"+12V",pcbnew .B_Cu )

q1d =pad_pos (q1 ,"3")
track (q1d ,(20 ,20.6 ),1.0 ,"DRAIN")
track ((20 ,20.6 ),(20 ,16.75 ),1.0 ,"DRAIN")
track ((20 ,16.75 ),pad_pos (j2 ,"1"),1.0 ,"DRAIN")


track (pad_pos (q1 ,"2"),(16.6 ,23.3 ),0.6 ,"GND")
via ((16.6 ,23.3 ),"GND")

track (pad_pos (j1 ,"3"),(5.6 ,24.2 ),0.4 ,"STROBE")
track ((5.6 ,24.2 ),pad_pos (r1 ,"1"),0.4 ,"STROBE")

q1g =pad_pos (q1 ,"1")
r1p2 =pad_pos (r1 ,"2")
track (r1p2 ,(12.9 ,24.2 ),0.4 ,"GATE")
track ((12.9 ,24.2 ),(12.9 ,q1g [1 ]),0.4 ,"GATE")
track ((12.9 ,q1g [1 ]),q1g ,0.4 ,"GATE")
track ((12.9 ,24.2 ),(12.9 ,27.9 ),0.4 ,"GATE")
track ((12.9 ,27.9 ),pad_pos (r2 ,"1"),0.4 ,"GATE")

for p in [(28.5 ,8 ),(1.8 ,20.5 )]:
    via (p ,"GND")


for a ,b in [((0 ,0 ),(30 ,0 )),((30 ,0 ),(30 ,30 )),
((30 ,30 ),(0 ,30 )),((0 ,30 ),(0 ,0 ))]:
    s =pcbnew .PCB_SHAPE (board )
    s .SetShape (pcbnew .SHAPE_T_SEGMENT )
    s .SetStart (pcbnew .VECTOR2I (MM (a [0 ]),MM (a [1 ])))
    s .SetEnd (pcbnew .VECTOR2I (MM (b [0 ]),MM (b [1 ])))
    s .SetLayer (pcbnew .Edge_Cuts )
    s .SetWidth (MM (0.1 ))
    board .Add (s )


for layer in (pcbnew .F_Cu ,pcbnew .B_Cu ):
    z =pcbnew .ZONE (board )
    z .SetLayer (layer )
    z .SetNetCode (nets ["GND"])
    z .SetLocalClearance (MM (0.25 ))
    z .SetMinThickness (MM (0.25 ))
    chain =pcbnew .SHAPE_LINE_CHAIN ()
    for (cx ,cy )in [(0.3 ,0.3 ),(29.7 ,0.3 ),(29.7 ,29.7 ),(0.3 ,29.7 )]:
        chain .Append (MM (cx ),MM (cy ))
    chain .SetClosed (True )
    z .Outline ().AddOutline (chain )
    board .Add (z )





def silk (text ,pos ,size =0.9 ):
    t =pcbnew .PCB_TEXT (board )
    t .SetText (text )
    t .SetPosition (pcbnew .VECTOR2I (MM (pos [0 ]),MM (pos [1 ])))
    t .SetLayer (pcbnew .F_SilkS )
    t .SetTextSize (pcbnew .VECTOR2I (MM (size ),MM (size )))
    t .SetTextThickness (MM (size *0.15 ))
    board .Add (t )


def silk_rot (text ,pos ,size =0.8 ):
    t =pcbnew .PCB_TEXT (board )
    t .SetText (text )
    t .SetPosition (pcbnew .VECTOR2I (MM (pos [0 ]),MM (pos [1 ])))
    t .SetLayer (pcbnew .F_SilkS )
    t .SetTextSize (pcbnew .VECTOR2I (MM (size ),MM (size )))
    t .SetTextThickness (MM (size *0.15 ))
    t .SetTextAngleDegrees (90 )
    board .Add (t )


def silk_b (text ,pos ,size =0.9 ):
    t =pcbnew .PCB_TEXT (board )
    t .SetText (text )
    t .SetPosition (pcbnew .VECTOR2I (MM (pos [0 ]),MM (pos [1 ])))
    t .SetLayer (pcbnew .B_SilkS )
    t .SetMirrored (True )
    t .SetTextSize (pcbnew .VECTOR2I (MM (size ),MM (size )))
    t .SetTextThickness (MM (size *0.15 ))
    board .Add (t )


silk_b ("IR RING STROBE",(7.5 ,22.5 ),1.0 )
silk_rot ("+12V",(10.2 ,11.5 ))
silk_rot ("GND",(10.2 ,15 ))
silk_rot ("STR",(10.2 ,18.5 ))
silk_rot ("R+",(19.3 ,13.25 ))
silk_rot ("R-",(19.3 ,16.75 ))
silk ("MAX 18V",(9.0 ,21.4 ),0.9 )

board .Save (os .path .join (HERE ,PROJ +".kicad_pcb"))
print ("pcb written")

pro ={
"board":{"design_settings":{"defaults":{}},"layer_presets":[],"viewports":[]},
"boards":[],
"cvpcb":{"equivalence_files":[]},
"erc":{"erc_exclusions":[],"meta":{"version":0 },"pin_map":[],"rule_severities":{}},
"libraries":{"pinned_footprint_libs":[],"pinned_symbol_libs":[]},
"meta":{"filename":PROJ +".kicad_pro","version":1 },
"net_settings":{"classes":[{"bus_width":12 ,"clearance":0.2 ,"diff_pair_gap":0.25 ,
"diff_pair_via_gap":0.25 ,"diff_pair_width":0.2 ,
"microvia_diameter":0.3 ,"microvia_drill":0.1 ,"name":"Default",
"pcb_color":"rgba(0, 0, 0, 0.000)","schematic_color":"rgba(0, 0, 0, 0.000)",
"track_width":0.25 ,"via_diameter":0.6 ,"via_drill":0.3 ,
"wire_width":6 }],"meta":{"version":3 },"net_colors":None ,"netclass_assignments":None ,"netclass_patterns":[]},
"pcbnew":{"last_paths":{"gencad":"","idf":"","netlist":"","plot":"","pos_files":"","specctra_dsn":"","step":"","svg":"","vrml":""},"page_layout_descr_file":""},
"schematic":{"annotate_start_num":0 ,"drawing":{},"legacy_lib_dir":"","legacy_lib_list":[],"meta":{"version":1 },"pin_symbol_size":0 ,"text_offset_ratio":0.08 },
"text_variables":{},
}
open (os .path .join (HERE ,PROJ +".kicad_pro"),"w").write (json .dumps (pro ,indent =1 ))


sym_libs =["Device","Connector_Generic","Connector"]
fp_libs =["TerminalBlock_Phoenix","Capacitor_THT",
"Package_TO_SOT_SMD","Resistor_THT","TestPoint","MountingHole"]
with open (os .path .join (HERE ,"sym-lib-table"),"w")as f :
    f .write ("(sym_lib_table\n  (version 7)\n")
    for n in sym_libs :
        f .write ('  (lib (name "%s") (type "KiCad") (uri "${KICAD10_SYMBOL_DIR}/%s.kicad_symdir") (options "") (descr ""))\n'%(n ,n ))
    f .write (")\n")
with open (os .path .join (HERE ,"fp-lib-table"),"w")as f :
    f .write ("(fp_lib_table\n  (version 7)\n")
    for n in fp_libs :
        f .write ('  (lib (name "%s") (type "KiCad") (uri "${KICAD10_FOOTPRINT_DIR}/%s.pretty") (options "") (descr ""))\n'%(n ,n ))
    f .write (")\n")

with open (os .path .join (HERE ,"netlist.txt"),"w")as f :
    f .write ("Expected nets (design intent):\n")
    f .write ("+12V : J1.1 C1.1 C2.1 J2.2\n")
    f .write ("GND  : J1.2 C1.2 C2.2 Q1.2(S) R2.2\n")
    f .write ("DRAIN: J2.1 Q1.3(D)\n")
    f .write ("GATE : Q1.1(G) R1.2 R2.1\n")
    f .write ("STROBE: J1.3 R1.1\n")
print ("project written")
