
#for reading in the A/D and making isotherm plots

AD1 = EpicsSignal("XF:12ID1:TrufA1", name="analog/digital 1")
AD2 = EpicsSignal("XF:12ID1:TrufA2", name="analog/digital 2")
#AD3 = EpicsSignal("XF:12ID1-ECAT:EL3164-00-AI3", name="analog/digital 3")
#AD4 = EpicsSignal("XF:12ID1-ECAT:EL3164-00-AI4", name="analog/digital 4")

import matplotlib.pyplot as plt 
import json
import time


def isotherm(wait_time=1, clear='no',color='b--',file='tmp',read='no'):
    directory ='/home/xf12id1/data/isotherms/'
    
    if clear == 'yes':
                plt.close()
                plt.axis([0,.0011,0,.0011])
                plt.xlabel('area')
                plt.ylabel('pressure')
    pressure=[]
    area=[]
    shutter_orig= shutter.get()
    for n in range(100):
        if read != 'no':
            g=open('/home/xf12id1/data/isotherms/tmp','r+')
            [area2,pressure2]=json.load(g)
            plt.plot(area2,pressure2,color)
            break
        if shutter.value == shutter_orig:
            pressure.append(AD1.get())
            area.append(AD2.get())
            time.sleep(wait_time)
        else:
            plt.plot(area,pressure,color)
            plt.show()
            filename= directory+file
            f=open(filename,'w')
            json.dump([area,pressure],f)
            break

