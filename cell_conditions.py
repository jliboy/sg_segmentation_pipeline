#Determining protein expressed in cells
def protein(i):
    if i in range(0, 30):
        protein = 'mEGFP'
    elif i in range(30,60):
        protein = 'G3BP1wt'
    elif i in range(60,90):
        protein = 'F15A'
    elif i in range(90,120):
        protein = 'V11A'
    elif i in range(120,150):
        protein = 'Q18A'
    elif i in range(150,180):
        protein = 'H31A'
    elif i in range(180,210):
        protein = 'F33A'
    elif i in range(210,240):
        protein = 'R32A'
    elif i in range(240,270):
        protein = 'K123A'
    elif i in range(270,300):
        protein = 'F124A'
    elif i in range(300,330):
        protein = 'S149A'
    elif i in range(330,360):
        protein = 'Y125A'
    elif i in range(360,390):
        protein = 'S149E'
    elif i in range(390,420):
        protein = 'IDR2'
    elif i in range(420,450):
        protein = 'G3BP2A'
    elif i in range(450,480):
        protein = 'IDR3'
    elif i in range(480,510):
        protein = 'G3BP2B'
    else:
        protein = 'Unknown'
    
    return protein

#Fix ranges...
#Determining treatment for each cell
def treatment(i):
    if i in range(0,10) or i in range(110,120) or i in range(120,130) or i in range(230,240) or i in range(240,250) or i in range(350,360) or i in range(360,370) or i in range(470,480) or i in range(480,490) or i in range(30,40) or i in range(80,90) or i in range(150,160) or i in range(200,210) or i in range(270,280) or i in range(320,330) or i in range(390,400) or i in range(440,450):
        treatment = 'NaAs'
    elif i in range(10,20) or i in range(100,110) or i in range(130,140) or i in range(220,230) or i in range(250,260) or i in range(340,350) or i in range(370,380) or i in range(460,470) or i in range(490,500) or i in range(40,50) or i in range(70,80) or i in range(160,170) or i in range(190,200) or i in range(280,290) or i in range(310,320) or i in range(400,410) or i in range(430,440):
        treatment = 'Tg'
    elif i in range(20,30) or i in range(90,100) or i in range(140,150) or i in range(210,220) or i in range(260,270) or i in range(330,340) or i in range(380,390) or i in range(450,460) or i in range(500,510) or i in range(50,60) or i in range(60,70) or i in range(170,180) or i in range(180,190) or i in range(290,300) or i in range(300,310) or i in range(410,420) or i in range(420,430):
        treatment = 'MG132'
    else:
        treatment = 'Unknown'

    return treatment