# for water 9.7 keV
def night():
    yield from xr_checks()
#    yield from xr_scan1("water_slit_0.04-0.1")
    yield from xr_scan2("water_slit_0.04_3")
    yield from shclose()

def day():
    yield from shopen()
    yield from bps.mv(x2,-43)
    yield from xr_checks()
    yield from xr_scan2("POPC_0.18mg-ml_Run3")
    yield from shclose()

#yield from mov("XF:12ID1-ES{Det:Lambda}cam1:OperatingMode",2)

def ref_s1():
#sample/position 1
        yield from bps.mv(x2,-57)
        yield from xr_checks_all()
        yield from xr_scan2("PFDA_100ppm_DI_1")

def ref_s2():
#sample/position 2
        yield from bps.mv(x2,-9)
        yield from xr_checks()
     #   yield from xr_scan2("PFDA_100ppm_0.1MCaCl_1")
     #   yield from xr_scan2("PFOS_300ppm_0.03MCaCl_1")
        yield from xr_scan2("PFDA_10ppm_DI_1")

def ref_s3():
#sample/position 3
        yield from bps.mv(x2,-9+38)
        yield from xr_checks_all()
        yield from xr_scan2("PFOS_5000ppm_0.1MCaCl_1")


def gid_s2():
        yield from gid_scan1("test_3")




def xr_checks(detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(shutter,1) # open shutter
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_ih()  #Align the spectrometer  height
    yield from check_tth() #Align the spectrometer rotation angle
    #yield from check_sh_coarse(0.05,detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from check_sh_fine(0.05,detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affec


def xr_checks_all(detector=lambda_det):
    yield from bps.mv(geo.det_mode,1)
    yield from bps.mv(shutter,1) # open shutter
    yield from det_exposure_time_new(detector, 1.0, 1.0)
    yield from check_ih()  #Align the spectrometer  height
    yield from check_tth() #Align the spectrometer rotation angle
    yield from check_sh_coarse(0.05,detector=detector) #scan the detector arm height (sh) from -1 to 1 with 41 points
    yield from check_sh_fine(0.05,detector=detector)   #scan the detector arm height from -0.2 to 0.2 with 21 points
    #yield from bps.mv(shutter,1) # open shutter
    #yield from check_astth(detector=detector)   #Align the detector arm rotation angle# comment out as it might affec



def xr_scan1(name):
    #9.7kev
    alpha_start_list =   [ 0.04, 0.16, 0.30, 0.50,  0.8,  1.3,  2.5]
    alpha_stop_list =    [ 0.16, 0.30, 0.50, 0.80,  1.3,  2.5,  5.1]
    number_points_list = [    7,   8,    6,     7,    6,   13,    7]
    auto_atten_list =    [    6,   5,    4,     3,    2,    1,    0] 
    s2_vg_list =         [  0.03, 0.03,  0.05,   0.05,  0.1,  0.1,  0.1] 
    exp_time_list =      [    4,   4,    4,     4,    4,    4,   4 ]
    precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1,  0.1]
    wait_time_list=      [    4,   4,    4,     4,    4,    4,   4 ]
    x2_offset_list=      [    0,   0,    0,     0,    0,    0.5,   1.0]


    scan_p={"start":alpha_start_list,
        "stop":alpha_stop_list,
        "n":number_points_list,
        "atten":auto_atten_list,
        "s2vg":s2_vg_list,
        "exp_time":exp_time_list,
        "pre_time":precount_time_list,
        "wait_time":wait_time_list,
        "x2_offset":x2_offset_list}

    print(scan_p)
    yield from bps.mv(geo.det_mode,1)
    yield from reflection_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=lambda_det, 
        tilt_stage=False,)


def xr_scan2(name):
  
  #9.7kev
    alpha_start_list =   [ 0.04, 0.16, 0.30, 0.50,  0.8,  1.3,  2.5]
    alpha_stop_list =    [ 0.16, 0.30, 0.50, 0.80,  1.3,  2.5,  4.0]
    number_points_list = [    7,   8,    6,     7,    6,   13,    8]
    auto_atten_list =    [    6,   5,    4,     3,    2,    1,    0] 
    s2_vg_list =         [  0.04, 0.04,  0.04,   0.04,  0.04,  0.04,  0.04] 
    exp_time_list =      [    4,   4,    4,     4,    4,    4,   4 ]
    precount_time_list=  [  0.1, 0.1,  0.1,   0.1,  0.1,  0.1,  0.1]
    wait_time_list=      [    4,   4,    4,     4,    4,    4,   4 ]
    x2_offset_list=      [    0,   0,    0,     0,    0,    0,   0 ]



    scan_p={"start":alpha_start_list,
        "stop":alpha_stop_list,
        "n":number_points_list,
        "atten":auto_atten_list,
        "s2vg":s2_vg_list,
        "exp_time":exp_time_list,
        "pre_time":precount_time_list,
        "wait_time":wait_time_list,
        "x2_offset":x2_offset_list}

    print(scan_p)
    yield from bps.mv(geo.det_mode,1)


    yield from reflection_scan_full(scan_param=scan_p,
        md={'sample_name': name},
        detector=lambda_det, 
        tilt_stage=False,)
    yield from mabt(0.2,0.2,0)


# print_summary(gid_scan1('bob'))

def gid_scan1(name):
    det_saxs_y_list         = [0,0]
    det_saxs_y_offset_list  = [0,1]
    stth_list               = [16,16]
    exp_time_list           = [10,10]
    x2_offset_list          = [0,0]
    atten_2_list            = [0,0]
    wait_time_list          = [5,5]

    scan_dict={"det_saxs_y":det_saxs_y_list,
        "det_saxs_y_offset":det_saxs_y_offset_list,
        "stth":stth_list,
        "exp_time":exp_time_list,
        "x2_offset":x2_offset_list,
        "atten_2":atten_2_list,
        "wait_time":wait_time_list,}


#mode 3 is for GID with no beam stop, mode 2 is for GID mode with the beam stop
    yield from bps.mv(geo.det_mode,3)
    print("calling GID_stitch")
    yield from gid_scan_stitch(scan_dict,
                                md={'sample_name': name}, 
                                detector = pilatus300k,
                                alphai = 0.1)


    
