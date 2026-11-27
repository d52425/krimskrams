#!/usr/bin/env python3
"""Draw the system wiring diagram: P4 -> boost module -> strobe driver
board -> FRS5CC IR LED ring. Output: wiring_diagram.png (PIL, Noto CJK)."""
from PIL import Image ,ImageDraw ,ImageFont 

FB ="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FR ="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

W ,H =1800 ,1100 
img =Image .new ("RGB",(W ,H ),"white")
d =ImageDraw .Draw (img )

RED =(200 ,40 ,30 )
BLK =(30 ,30 ,30 )
ORG =(230 ,110 ,0 )
BOXF =(247 ,247 ,247 )
BOXT =(40 ,40 ,40 )


def font (path ,size ):
    return ImageFont .truetype (path ,size )


def box (x ,y ,w ,h ,title ,sub =None ):
    d .rounded_rectangle ([x ,y ,x +w ,y +h ],radius =14 ,fill =BOXF ,
    outline =BOXT ,width =3 )
    d .text ((x +w /2 ,y +34 ),title ,font =font (FB ,30 ),fill =BOXT ,
    anchor ="ma")
    if sub :
        d .text ((x +w /2 ,y +74 ),sub ,font =font (FR ,22 ),fill =(90 ,90 ,90 ),
        anchor ="ma")


def term (x ,y ,label ,side ="r",color =BLK ):
    """Terminal dot on a box edge; label drawn inside the box."""
    d .ellipse ([x -9 ,y -9 ,x +9 ,y +9 ],fill =color ,outline =BOXT ,width =2 )
    if side =="r":
        d .text ((x +18 ,y ),label ,font =font (FB ,23 ),fill =BOXT ,anchor ="lm")
    else :
        d .text ((x -18 ,y ),label ,font =font (FB ,23 ),fill =BOXT ,anchor ="rm")


def wire (pts ,color ,width =5 ):
    d .line (pts ,fill =color ,width =width ,joint ="curve")


def wlabel (x ,y ,text ,color ):
    d .text ((x ,y ),text ,font =font (FB ,24 ),fill =color ,anchor ="ma")


d .text ((W /2 ,36 ),"IRリング ストロボ結線図",font =font (FB ,46 ),
fill =BOXT ,anchor ="ma")
d .text ((W /2 ,102 ),"ESP32-P4 → 昇圧 12V → ストロボドライバ → LEDリング",
font =font (FR ,25 ),fill =(90 ,90 ,90 ),anchor ="ma")


box (50 ,300 ,300 ,300 ,"ESP32-P4 ボード","（PoE 給電）")
box (520 ,300 ,340 ,300 ,"昇圧モジュール","（写真のもの）")
box (1030 ,300 ,340 ,300 ,"ストロボドライバ基板","（30×30mm）")
box (1540 ,300 ,230 ,300 ,"IR LEDリング","FRS5CC")


term (350 ,390 ,"5V","l",RED )
term (350 ,470 ,"GND","l")
term (350 ,550 ,"GPIO","l",ORG )

term (520 ,390 ,"IN+","r",RED )
term (520 ,470 ,"IN−","r")
term (860 ,390 ,"OUT+","l",RED )
term (860 ,470 ,"OUT−","l")
d .text ((690 ,520 ),"ボリュームで",font =font (FR ,22 ),fill =(90 ,90 ,90 ),
anchor ="ma")
d .text ((690 ,550 ),"12.0V に調整",font =font (FB ,22 ),fill =(90 ,90 ,90 ),
anchor ="ma")

term (1030 ,400 ,"+12V","r",RED )
term (1030 ,475 ,"GND","r")
term (1030 ,550 ,"STROBE","r",ORG )
term (1370 ,400 ,"RING+","l",RED )
term (1370 ,500 ,"RING−","l")

term (1540 ,400 ,"+","r",RED )
term (1540 ,500 ,"−","r")
d .ellipse ([1615 ,415 ,1695 ,495 ],outline =(230 ,120 ,0 ),width =10 )


wire ([(350 ,390 ),(520 ,390 )],RED )
wlabel (435 ,352 ,"+5V",RED )
wire ([(350 ,470 ),(520 ,470 )],BLK )
wire ([(860 ,390 ),(950 ,390 ),(950 ,400 ),(1030 ,400 )],RED )
wlabel (945 ,330 ,"12.0V",RED )
wire ([(860 ,470 ),(950 ,470 ),(950 ,475 ),(1030 ,475 )],BLK )
wire ([(350 ,550 ),(350 ,770 ),(1030 ,770 ),(1030 ,550 )],ORG )
wlabel (690 ,782 ,"STROBE（GPIO パルス 3.3V）",ORG )
wire ([(1370 ,400 ),(1540 ,400 )],RED )
wire ([(1370 ,500 ),(1540 ,500 )],BLK )
wlabel (1455 ,522 ,"FETでスイッチ",(90 ,90 ,90 ))

notes =[
"・GND は全て共通（昇圧は非絶縁）。STROBE の基準もこの GND。",
"・リングをつなぐ前に、昇圧モジュールの出力が 12.0V になっているか確認する。",
"・FRS5CC は CDS をバイパス（ショート）して「12V が来れば点灯」にしておくこと。",
]
for i ,n in enumerate (notes ):
    d .text ((60 ,880 +i *52 ),n ,font =font (FR ,24 ),fill =BOXT ,anchor ="la")

img .save ("/home/hatch/workspace/goals/esp32-p4-ir-tracker/files/pcb/"
"IR_ring_strobe_driver/wiring_diagram.png")
print ("saved")
