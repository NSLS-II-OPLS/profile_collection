# Borrowed from SMI's profile: https://github.com/NSLS-II-SMI/profile_collection/blob/e745b5d476ff2005977cf070b69ba3e9cc3a850d/startup/16-electrometers.py#L111-L118

from nslsii.ad33 import QuadEMV33
#from ophyd.quadem import TetrAMM

quadem = QuadEMV33("XF:12ID1-BI{EM:1}EM1:", name="quadem")
quadem.conf.port_name.put("EM180")
quadem.stage_sigs["acquire_mode"] = 2

for i in [1, 2, 3, 4]:
    getattr(quadem, f"current{i}").mean_value.kind = "normal"

# for i in [1,2,3]:
for i in [2,3]:
    getattr(quadem, f"current{i}").mean_value.kind = "hinted"

    
quadem.integration_time.put(0.0004)
quadem.values_per_read.put(500)
#for continuous reading
quadem.acquire_mode.put(2)
#for diamond mode
quadem.geometry.put(0)


quadem1_cl = EpicsSignal("XF:12ID1-BI{EM:1}EM1:ComputeCurrentOffset1.PROC", name="quadem1_clear")
quadem2_cl = EpicsSignal("XF:12ID1-BI{EM:1}EM1:ComputeCurrentOffset2.PROC", name="quadem2_clear")
quadem3_cl = EpicsSignal("XF:12ID1-BI{EM:1}EM1:ComputeCurrentOffset3.PROC", name="quadem3_clear")





def quadem_clear():
    yield from bps.mv(quadem1_cl,1)
    yield from bps.mv(quadem2_cl,1)
    yield from bps.mv(quadem3_cl,1)





#tetramm = QuadEMV33("XF:12ID1-BI{EM:2}", name="tetramm")
#tetramm.conf.port_name.put("TeTrAMM")
#tetramm.acquire_mode.put(2)
#tetramm.stage_sigs["acquire_mode"] = 2

#for i in [1, 2, 3, 4]:
#    getattr(tetramm, f"current{i}").mean_value.kind = "normal"

#for i in [1,2,3]:
#    getattr(tetramm, f"current{i}").mean_value.kind = "hinted"

#bpm = QuadEMV33("XF:12ID1-BI{EM:2}", name="bpm")


#This is for the siddons box for the DBPM

class XBPM4(Device):
    """
    XBPM are diamond windows that generate current when the beam come through. It is used to know the position
    of the beam at the bpm postion as well as the amount of incoming photons. 3 bpms are available at SMI: bpm1
    is position upstream, bpm2 after the focusing mirrons and bpm3 downstream
    :param Device: ophyd device
    """
    ch1 = Cpt(EpicsSignal, 'Current1:MeanValue_RBV')
    ch2 = Cpt(EpicsSignal, 'Current2:MeanValue_RBV')
    ch3 = Cpt(EpicsSignal, 'Current3:MeanValue_RBV')
    ch4 = Cpt(EpicsSignal, 'Current4:MeanValue_RBV')
    sumX = Cpt(EpicsSignal, 'SumX:MeanValue_RBV')
    sumY = Cpt(EpicsSignal, 'SumY:MeanValue_RBV')
    posX = Cpt(EpicsSignal, 'PosX:MeanValue_RBV')
    posY = Cpt(EpicsSignal, 'PosY:MeanValue_RBV')


#ben commented this out on 9/20/21 due to errors
bpm = XBPM4("XF:12ID1-BI{EM:2}", name="bpm")


bpm.ch1.kind = 'hinted'
bpm.ch2.kind = 'hinted'
bpm.ch3.kind = 'hinted'
bpm.ch4.kind = 'hinted'


bpm.posX.kind = 'normal'
bpm.posY.kind = 'normal'
