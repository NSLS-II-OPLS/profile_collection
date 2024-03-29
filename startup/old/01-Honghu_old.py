# pull various motors into the global name space


##Copied from 76-GID in /nsls2/xf12id1/user/2021_c2/..../honghu




def cfn(name):
    # This takes the reflectivity
    yield from bps.mv(geo.stblx2,0.2)

    yield from bps.mv(flow3,3.2) # need to change back to 3.1
    yield from bps.mv(geo.det_mode,1)
    
    # sets sample height at alpha=0.08
    yield from sample_height_set()

    print('Sleeping time before reflectivity')
    yield from bps.sleep(10)
    yield from bps.mv(flow3,2.7)
    
    # takes the reflectivity
    yield from fast_scan(name)

    # sets sample height at alpha=0.08 so that it is ready for GID
    yield from bps.mv(abs2,6)
    yield from mabt(0.08,0.08,0)
    
    print('Start the height scan before GID')
    yield from sample_height_set()

    # This takes the GID
    yield from bps.mv(geo.det_mode,2)
    alphai = 0.11
    yield from gid_scan(md={'sample_name': name+'_GID'},
                        exp_time = 1,
                        detector = pilatus100k,
                        alphai = alphai,
                        attenuator=1)

    yield from bps.mvr(geo.stblx2,2)
    yield from sample_height_set()
    yield from bps.mv(geo.det_mode,2)
    alphai = 0.11
    yield from gid_scan(md={'sample_name': name+'_fresh1_GID'},
                        exp_time = 1,
                        detector = pilatus100k,
                        alphai = alphai,
                        attenuator=1)

    yield from bps.mvr(geo.stblx2,-4)
    yield from sample_height_set()
    yield from bps.mv(geo.det_mode,2)
    alphai = 0.11
    yield from gid_scan(md={'sample_name': name+'_fresh2_GID'},
                        exp_time = 1,
                        detector = pilatus100k,
                        alphai = alphai,
                        attenuator=1)
    
    yield from bps.mv(flow3,2.7)
    yield from bps.mv(geo.stblx2,0.2)



# gid_dets = [pilatus300k, quadem]
# @bpp.stage_decorator(gid_dets)
def gid_cfn_cal(md=None, exp_time=1, detector = 'pilatus300k', alphai = 0.1, attenuator=2):
    # Bluesky command to record metadata
    base_md = {'plan_name': 'gid',
               'detector': detector, 
               'energy': energy.energy.position,
               'alphai': alphai,
            # ...
           }

    base_md.update(md or {})
    bec.disable_plots()
    yield from bps.open_run(md=base_md)

    # Creation of a fignal to record the attenuation
    yield from bps.mv(abs2, attenuator)# to avoid pilatus saturation
    attenuation = calculate_att_comb([np.sum(current_att_thickness[0:attenuator+1])], ['Mo'], energy.energy.position)
    attenuation_factor_signal = Signal(name='attenuation', value = attenuation[0])

    # Set and record the exposure time to 0.1 for the precount
    exposure_time = Signal(name='exposure_time', value = exp_time)
    yield from det_exposure_time_pilatus(exp_time, exp_time)

    # Move to the good geometry position
    yield from mabt(alphai, 0, 0) # gid poistion with beam stop
    yield from bps.sleep(5)

    # yield from bps.mv(abs2, 0)
    # yield from bps.mv(abs2, 3)# to avoid pilatus saturation
    # yield from bps.mv(attenuation_factor_signal, 1)

    # yield from bps.mvr(geo.stblx2, -1) # move stable X2
    
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)


    yield from bps.mv(abs2, 6)
    yield from mabt(alphai, 0, -1) # gid poistion without beam stop
    yield from bps.sleep(5)

    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)


    yield from bps.mv(abs2, 6)
    yield from mabt(alphai, 0, -2) # gid poistion without beam stop
    yield from bps.sleep(5)
    yield from bps.mv(shutter,1)
    yield from bps.sleep(0.5) # add this because the QuadEM I0
    yield from bps.trigger_and_read(gid_dets + [geo] + [attenuation_factor_signal] + [exposure_time], name='primary')
    yield from bps.mv(shutter,0)

    # Bluesky command to stop recording metadata
    yield from close_run()
    bec.enable_plots()
    # yield from bps.mv(abs2, 5)
    print('The gid is over')
                       


def cfn_3():

    # name_cfn = { 1: 'AuNR_5_19_stock',
    #              2: 'AuNR_5_19_T6K',
    #              3: 'AuNR_5_19_E6K',
    # }
    # name_cfn = { 1: 'AuNR_5_19_stock_10mMNaCl', # add 20.2uL 1M NaCl @9:35pm 06/30/21
    #              2: 'AuNR_5_19_T6K_10mMNaCl',
    #              3: 'AuNR_5_19_E6K_10mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_5_19_stock_100mMNaCl', # add 36.6uL 5M NaCl @11:35pm 06/30/21
    #              2: 'AuNR_5_19_T6K_100mMNaCl',
    #              3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_10_30_E6K', # add 2ml @7:32pm 07/01/21
    #              2: 'AuNR_10_30_T6K',
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_10_30_E6K_10mMNaCl', # add 20.2uL 1M NaCl @8:53pm 07/01/21
    #              2: 'AuNR_10_30_T6K_10mMNaCl',
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_10_30_E6K_100mMNaCl', # add 36.6uL 5M NaCl @10.43pm 07/01/21
    #              2: 'AuNR_10_30_T6K_100mMNaCl',
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { #1: 'AuNR_10_30_E6K_100mMNaCl', # add 36.6uL 5M NaCl @10.43pm 07/01/21
    #              2: 'AuNR_10_30_T6K_100mMNaCl_LowConc',  #remove 1340 ul solution and then add 1340 100mMNaCl to make the NP conc as the E6K
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_5_19_E2K', # add 2ml, 12 nM @12:51 am 07/02/21
    #              2: 'AuNR_5_19_T2K', # add 2ml, 12 nM @12:51 am 07/02/21
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_5_19_E2K_10mMNaCl', # add 20.2uL 1M NaCl @2am 07/02/21
    #              2: 'AuNR_5_19_T2K_10mMNaCl', # add 20.2uL 1M NaCl @2am 07/02/21
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_5_19_E2K_100mMNaCl', # add 36.6uL 5M NaCl @3:05am 07/02/21
    #              2: 'AuNR_5_19_T2K_100mMNaCl', # add 36.6uL 5M NaCl @3:05am 07/02/21
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # }
    # name_cfn = { 1: 'AuNR_5_19_E2KS6k_10mMNaCl', # add 2ml, 10 nM and 20.2uL 1M NaCl @5:04am 07/02/21
    #              2: 'AuNR_5_19_E6kS2k_10mMNaCl', # add 2ml, 10 nM and 20.2uL 1M NaCl @5:04am 07/02/21
    #              #3: 'AuNR_5_19_E6K_100mMNaCl',
    # } 
    name_cfn = { 1: 'AuNR_5_19_E2KS6k_100mMNaCl', # add 36.6uL 5M NaCl @6:10am 07/02/21
                 2: 'AuNR_5_19_E6kS2k_100mMNaCl', # add 36.6uL 5M NaCl @6:10am 07/02/21
                 #3: 'AuNR_5_19_E6K_100mMNaCl',
    }  

    yield from bps.mv(geo.det_mode,1)
    # x2_pos1 = -47.6 # -11.3-38.1
    # tilt1 = 0
    # x2_pos2 = -10 #  -11.3-0.2
    # tilt2 = 0
    # x2_pos2 = -9 # for AuNR_10_30_T6K_100mMNaCl_LowConc
    # tilt2 = 0
    # x2_pos3 = -11.3+38.1-0.5
    # tilt3 = -0.4
    # x2_pos1 = -50.8
    # tilt1 = 0
    # x2_pos2 = -12.5-0.2  
    # tilt2 = 0
    # x2_pos1 = -46.4
    # tilt1 = 0
    # x2_pos2 = -8.5 
    # tilt2 = 0

    x2_pos1 = -46.4
    tilt1 = 0

    x2_pos2 = -8
    tilt2 = 0

    yield from cfn_ref(name_cfn[1],x2_pos1,tilt1)
    yield from cfn_gid(name_cfn[1])
    yield from cfn_ref(name_cfn[2],x2_pos2,tilt2)
    yield from cfn_gid(name_cfn[2])

    #yield from cfn_ref(name_cfn[3],x2_pos3,tilt3)
    #yield from cfn_gid(name_cfn[3])



def cfn_1():
    '''
    XR and GID run for one sample cell
    '''
    # name_cfn = { 2: 'AuNR_10_50_T6K', # @11:14am 07/01/21
    # }
    # name_cfn = { 2: 'AuNR_10_50_T6K_10mMNaCl', # add 20.2uL 1M NaCl @ 12pm 07/01/21
    # }
    # name_cfn = { 2: 'AuNR_10_50_T6K_100mMNaCl', # add 36.6uL 5M NaCl @ 12:45pm 07/01/21
    # }

    # name_cfn = { 2: 'AuNR_10_40_T6K', # @1:27 pm 07/01/21
    # }
    #name_cfn = { 2: 'AuNR_10_40_T6K_10mMNaCl', # add 20.2uL 1M NaCl @2:04 pm 07/01/21
    #}
    name_cfn = { 2: 'AuNR_10_40_T6K_100mMNaCl', # add 36.6uL 5M NaCl @4:31 pm 07/01/21
    }


    yield from bps.mv(geo.det_mode,1)
    x2_pos2 = -9.0 #-11.3+2+0.3
    tilt2 = -0.4
    yield from cfn_ref(name_cfn[2],x2_pos2,tilt2)
    yield from cfn_gid(name_cfn[2])


# def cfn_gid(name):

#     # sets sample height at alpha=0.08 so that it is ready for GID
    
#     print('Start the height scan before GID')
#     gid_dets = [pilatus300k, quadem]
#     @bpp.stage_decorator(gid_dets)
#     if _dx2 == 0:
#         yield from bps.mv(shutter,1)
#         yield from ih_set()  #Align the spectrometer  height
#         yield from tth_set() #Align the spectrometer rotation angle
#         yield from sample_height_set_fine()
#     yield from bps.mv(geo.det_mode,2)
#     alphai = 0.1
#     yield from gid_scan(md={'sample_name': name+'_GID_pos_' + str(_dx2)+'_exp_' + str(_exp_time)+'s'},
#                         exp_time = _exp_time,
#                         detector = 'pilatus300k',
#                         alphai = alphai,
#                         attenuator=0)


def cfn_ref(name,xpos,tiltx):
    '''Conduct reflectivity measurments'''
    print("file name=",name)
    yield from bps.mv(geo.stblx2,xpos)  #move the  Sample Table X2 to xpos
    yield from bps.mv(tilt.x,tiltx)  #move the  Sample tilt 
    yield from bps.mv(shutter,1) # open shutter
    yield from ih_set()  #Align the spectrometer  height
    yield from tth_set() #Align the spectrometer rotation angle
    yield from sample_height_set_coarse() #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from sample_height_set_fine()   #scan the detector arm height from -0.2 to 0.2 with 21 points
    yield from bps.mv(shutter,1) # open shutter
    # yield from astth_set()   #Align the detector arm rotation angle# comment out as it might affect OFFSET
    yield from fast_scan(name)

def cfn_20210718_night():
    yield from he_on()
    for run_num in range(3):
        yield from bps.mv(shutter,1) # open shutter
        yield from cfn_20210718_night_one_scan(run_num)
        yield from bps.mv(shutter,0) # close shutter
        yield from bps.sleep(3600 * 2 ) # 
 


def cfn_20210718_night_one_scan(run_num):
    #yield from he_on()
    yield from one_ref("S1, 1ul_DSPEP_P14_run=%s"%(run_num),-57+run_num, tiltx=0,detector=pilatus100k)
    yield from one_ref("S2, 2ul_DSPEP_Px_run=%s"%(run_num), -10+run_num, tiltx=0,detector=pilatus100k)
    yield from one_ref("S3, 4ul_DSPEP_P38_run=%s"%(run_num), 36+run_num, tiltx=0,detector=pilatus100k)     
    #yield from he_off()

def cfn_20210719_pm_one_scan( ):
    yield from he_on()
    sam = 'S1, DNA-DSPEP_1-5_P34'
    yield from one_ref(sam,-56 , tiltx=0,detector=pilatus100k)

    yield from bps.mv(geo.stblx2,  -56 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-56 + 1, stth = 17.5, exp_time=60, attenuator=0, beta1=0, beta_off=0.13 ) 
    yield from one_gid( name=sam, xpos=-56 + 1 , stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13 ) 


    sam = 'S2, DNA-DSPEP_1-10_Px'
    yield from one_ref(sam, -9, tiltx=0,detector=pilatus100k)

    yield from bps.mv(geo.stblx2,  -9 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13 ) 
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13 )   

    sam = 'S3, DNA-DSPEP_1-1_P36'
    yield from one_ref( sam, 37 , tiltx=0,detector=pilatus100k)     

    yield from bps.mv(geo.stblx2,  37 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13 ) 
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13 ) 

def cfn_20210719_pm_np_one_scan( ):
    yield from he_on()
    sam = 'S1, DNA-DSPEP_1-5_NP_P32_run1'
    yield from one_ref(sam,-56 , tiltx=0,detector=pilatus100k)

    yield from bps.mv(geo.stblx2,  -56 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-56+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-56+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-56+1, stth = 17.5, exp_time=60, attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=-56+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 

    sam = 'S2, DNA-DSPEP_1-10_NP_Px_run1'
    yield from one_ref(sam, -9, tiltx=0,detector=pilatus100k)

    yield from bps.mv(geo.stblx2,  -9 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-9+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-9+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3)   

    sam = 'S3, DNA-DSPEP_1-1_NP_P35_run1'
    yield from one_ref( sam, 37 , tiltx=0,detector=pilatus100k)     

    yield from bps.mv(geo.stblx2,  37 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=37+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=37+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 
    #yield from he_off()


def cfn_20210719_night_npsalt_one_scan( ):
    yield from he_on()
    sam = 'S1, DNA-DSPEP_1-5_NPsalt_P34_run1'
    yield from one_ref(sam,-56 , tiltx=0,detector=pilatus100k)

    yield from bps.mv(geo.stblx2,  -56 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-56+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-56+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-56+1, stth = 17.5, exp_time=60, attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=-56+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 

    sam = 'S2, DNA-DSPEP_1-10_NPsalt_Px_run1'
    yield from one_ref(sam, -9, tiltx=0,detector=pilatus100k)

    yield from bps.mv(geo.stblx2,  -9 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-9+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-9+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3)   

    sam = 'S3, DNA-DSPEP_1-1_NPsalt_P42_run1'
    yield from one_ref( sam, 37 , tiltx=0,detector=pilatus100k)     

    yield from bps.mv(geo.stblx2,  37 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=37+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=37+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 
    yield from bps.mv(abs2, 6)


def cfn_20210719_night_npsalt_gid_scan( ):
    yield from he_on()
    sam = 'S1, DNA-DSPEP_1-5_NPsalt_P34_run2'
    yield from bps.mv(geo.stblx2,  -56 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-56+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-56+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-56+1, stth = 17.5, exp_time=60, attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=-56+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 

    sam = 'S2, DNA-DSPEP_1-10_NPsalt_Px_run2'
    yield from bps.mv(geo.stblx2,  -9 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=-9+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-9+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=-9+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3)   

    sam = 'S3, DNA-DSPEP_1-1_NPsalt_P42_run2'
    yield from bps.mv(geo.stblx2,  37 + 1 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=37+0.5, stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=37+0.75, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=37+1, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 
    yield from bps.mv(abs2, 6)



def cfn_20210720_night():
    yield from he_on()
    for run_num in range(3):
        #yield from shopen()
        yield from bps.mv(shutter,1) # open shutter
        yield from cfn_20210720_night_npsalt_one_scan( run_num )
        yield from bps.mv(shutter,0) # close shutter
        #yield from shclose()
        #yield from bps.sleep(3600 * .5 ) # 
    yield from he_off()

def cfn_20210720_night_npsalt_one_scan( run_num ):

    ''''
    Need to add tth and ih check before GID
    '''
    yield from he_on()

    sam = 'S1, DNA-DSPEP_1-5_NPsalt_P34_run%i'%(3+run_num)
    start_pos = -57 + run_num
    yield from one_ref(sam, start_pos , tiltx=0,detector=pilatus100k)    
    yield from bps.mv(geo.stblx2,  start_pos + .5 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=start_pos + .25 , stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=start_pos + .25, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=start_pos + .75, stth = 17.5, exp_time=60, attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=start_pos + .75, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 

    sam = 'S2, DNA-DSPEP_1-10_NPsalt_Px_run%i'%(3+run_num)
    start_pos = -10 + run_num
    yield from one_ref(sam, start_pos , tiltx=0,detector=pilatus100k)    
    yield from bps.mv(geo.stblx2,  start_pos + .5 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=start_pos + .25 , stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=start_pos + .25, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=start_pos + .75, stth = 17.5, exp_time=60, attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=start_pos + .75, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 

    sam = 'S3, DNA-DSPEP_1-1_NPsalt_P42_run%i'%(3+run_num)    
    start_pos = 36 + run_num
    # yield from one_ref(sam, start_pos , tiltx=0,detector=pilatus100k)    
    yield from bps.mv(geo.stblx2,  start_pos + .5 )
    yield from sample_height_set_fine(detector=pilatus100k)
    yield from one_gid( name=sam, xpos=start_pos + .25 , stth = 0, exp_time=1, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=start_pos + .25, stth = 0, exp_time=5, attenuator=0, beta1=0, beta_off= 0.4, det_mode=2)
    yield from one_gid( name=sam, xpos=start_pos + .75, stth = 17.5, exp_time=60, attenuator=0, beta1=0, beta_off=0.13, det_mode=3) 
    yield from one_gid( name=sam, xpos=start_pos + .75, stth = 17.5, exp_time=60,attenuator=0, beta1=2, beta_off=0.13, det_mode=3) 
