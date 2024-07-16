class CRL1(Device):
    x = Cpt(EpicsMotor, "X1}Mtr")
    y = Cpt(EpicsMotor, "Y1}Mtr")
    z = Cpt(EpicsMotor, "Z}Mtr")

class CRL2(Device):
    x = Cpt(EpicsMotor, "X2}Mtr")
    y = Cpt(EpicsMotor, "Y2}Mtr")
    z = Cpt(EpicsMotor, "Z}Mtr")
    

crl1 = CRL1("XF:12ID1-OP{CRL-Ax:", name="crl")
crl2 = CRL2("XF:12ID1-OP{CRL-Ax:", name="crl")



pos1_y1 = 8.73
pos1_x1 = 4.16
pos1_z1 = 0


# pos2_y1 = 8.79
# pos2_x1 = 3.86
# pos2_z1 = 100

# 14.4keV June 2024, FWHM = 12um
pos2_y1 = 8.95
pos2_x1 = 3.45
pos2_z1 = 180

# # 14.4keV June 2024, FWHM = 15.2um
# pos2_y1 = 8.91
# pos2_x1 = 3.59
# pos2_z1 = 140

# # 14.4keV June 2024, FWHM = 18.2um
# pos2_y1 = 8.88
# pos2_x1 = 3.71
# pos2_z1 = 100

# # 14.4keV June 2024, FWHM = 40.4um
# pos2_y1 = 8.86
# pos2_x1 = 3.81
# pos2_z1 = 70

# pos1_x2 = 2.6
# pos1_y2 = 0.373
# pos1_z2 = 150

# pos2_x2 = 2.87
# pos2_y2 = 0.303
# pos2_z2 = 75

# pos2_x2 = 3.13
# pos2_y2 = 0.243
# pos2_z2 = 0

###  14.4 keV Dec 2023
pos1_x2 = 2.8114
pos1_y2 = 0.46
pos1_z2 = 150


# pos2_x2 = 3.0514
# pos2_y2 = 0.38
# pos2_z2 = 75

# pos2_x2 = 3.2914
# pos2_y2 = 0.32
# pos2_z2 = 0

pos2_x2 = 3.5364
pos2_y2 = 0.26
pos2_z2 = -75


slope_x1 = (pos1_x1-pos2_x1)/(pos1_z1-pos2_z1) 
slope_y1 = (pos1_y1-pos2_y1)/(pos1_z1-pos2_z1)
slope_x2 = (pos2_x2-pos1_x2)/(pos2_z2-pos1_z2) 
slope_y2 = (pos2_y2-pos1_y2)/(pos2_z2-pos1_z2)


def crl_calc(z):
    x1 = pos1_x1 + slope_x1*(z-pos1_z1)
    y1 = pos1_y1 + slope_y1*(z-pos1_z1)
    x2 = pos1_x2 + slope_x2*(z-pos1_z2)
    y2 = pos1_y2 + slope_y2*(z-pos1_z2)
    print(x1,y1,x2,y2,z)


def crl_go(z):
    x1 = pos1_x1 + slope_x1*(z-pos1_z1)
    y1 = pos1_y1 + slope_y1*(z-pos1_z1)
    x2 = pos1_x2 + slope_x2*(z-pos1_z2)
    y2 = pos1_y2 + slope_y2*(z-pos1_z2)
  #  yield from bps.mov(crl1.x,x1,crl1.y,y1)
    yield from bps.mov(crl2.x,x2,crl2.y,y2)
    yield from bps.mov(crl1.z,z)
    




