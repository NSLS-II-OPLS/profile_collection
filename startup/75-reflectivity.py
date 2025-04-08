# global attenuation_factor_signal, attenuator_name_signal, default_attenuation # exposure_time, 
# attenuator_name_signal = Signal(name='attenuator_name', value='abs1',kind='normal')


# attenuation_factor_signal = Signal(name='attenuation', value=1e-7,kind='normal')
# default_attenuation = Signal(name='default-attenuation', value=1e-7)
import time
def reflection_scan_full(scan_param, md=None, detector=lambda_det, tilt_stage=False, stth_corr_par=None, usekibron = False, trough = None, auto_atten = False, compress = False, target_pressure=0):

    """
    Macros to set all the parameters in order to record all the required information for further analysis,
    such as the attenuation factors, detector='lambda_det'
    :param detector: A string which is the detector name
    :type detector: string, can be either 'lambda_det' or 'pilatus100k'
    """
    try:
        # Tom's way of checking to see if all lists are the same length
        N = None
        for k, v in scan_param.items():
            if N is None:
                N = len(v)
            if N != len(v):
                raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

        unhinted_ref() ## change all hinted settings to 'normal'
        
        #XF:12ID1-ES{Det:Lambda}ROI1:MinX
        # Bluesky command to record metadata
        base_md = {'plan_name': 'reflection_scan',
                'cycle': RE.md['cycle'],
                'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
                'detectors': [detector.name, quadem.name],
                'energy': energy.energy.position,
                # 'rois': [detector.roi1.min_xyz.min_x.get(), ### before TRANS (rot270)
                #             detector.roi1.min_xyz.min_y.get(),
                #             detector.roi2.min_xyz.min_y.get(),
                #             detector.roi3.min_xyz.min_y.get(),
                #             detector.roi2.size.x.get(),
                #             detector.roi2.size.y.get()],

                'rois': [detector.roi1.min_xyz.min_x.get(), ### after TRANS1 (rot270), 2025/03/27, HZ
                         detector.roi2.min_xyz.min_x.get(),
                         detector.roi3.min_xyz.min_x.get(),
                         detector.roi2.min_xyz.min_y.get(),
                         detector.roi2.size.x.get(),
                         detector.roi2.size.y.get()],
                'geo_param': [geo.L1.get(), geo.L2.get(), geo.L3.get(), geo.L4.get()],
                'slit_s1': [S1.top.position - S1.bottom.position, S1.outb.position - S1.inb.position],
                'slit_s2': [S2.vg.position, S2.hg.position],
                'x2': [geo.stblx2.position],
                'tilt stage': tilt_stage,
                }
        base_md.update(md or {})
        bec.disable_plots()
        # Bluesky command to start the document
        # moved this line so we get a single UID per sub-scan
        yield from bps.open_run(md=base_md)
        x2_nominal= geo.stblx2.position
        blocky_nominal= block.y.position ## add blocky pos (HZ, 06102022)

        for i in range(N):
            # yield from bps.open_run(md=base_md)
            print('%sst set starting'%i)
            yield from bps.sleep(3) 
    #      print(scan_param)
            yield from reflection_scan(scan_param,i, detector=detector, md=md, tilt_stage=tilt_stage, auto_atten=auto_atten, usekibron = usekibron, trough = trough, compress = compress, target_pressure=target_pressure, x2_nominal=x2_nominal,blocky_nominal=blocky_nominal)                      
            print('%sst set done'%i)
            # yield from bps.close_run()


        # Bluesky command to stop recording metadata
        #moved this to inside the loop
        yield from bps.close_run()
        bec.enable_plots()
        # puts in absorber to protect the detctor      
        yield from bps.mv(abs2, 6)
        quadem.averaging_time.put(1)
        print('The reflectivity scan is over')
    finally:
        hinted_ref() ## change hinted settings

print(f'Loading {__file__}')
all_area_dets = [quadem, lambda_det, AD1, AD2, o2_per, chiller_T, ls]
#all_area_dets = [quadem, bpm, lambda_det, AD1, AD2, o2_per, chiller_T]




@bpp.stage_decorator(all_area_dets)

def reflection_scan(scan_param, i, detector=lambda_det, md={}, tilt_stage=False,x2_nominal=0,blocky_nominal=0, usekibron = False, auto_atten = False, trough = None, compress = False, target_pressure=0):

    alpha_start =   scan_param["start"][i]
    alpha_stop =    scan_param["stop"][i]
    number_points = scan_param["n"][i]
    atten_2 =       scan_param["atten"][i]
    s2_vg =         scan_param["s2vg"][i]
    exp_time =      scan_param["exp_time"][i]
    precount_time=  scan_param["pre_time"][i]
    wait_time =     scan_param["wait_time"][i]
    x2_offset_start =     scan_param["x2_offset_start"][i]
    x2_offset_stop =     scan_param["x2_offset_stop"][i]
    block_offset   =     scan_param["beam_block_offset"][i]



# setting up so that if alpha is moved negative that there is an extra wait
    alpha_old=5
    print(alpha_start,"----",alpha_stop,atten_2)
    for alpha in np.linspace(alpha_start, alpha_stop, number_points):
        # Move to the good geometry position
        if tilt_stage:
             yield from nab(alpha, alpha)
        else:
            if alpha >= alpha_old:
                yield from mabt(alpha, alpha, 0)

                # if alpha-alpha_old < 0.05: ## added by HZ 2022-10-17 due to low geometry resolution
                #     yield from mabt(alpha-0.1, alpha-0.1, 0)
                #     yield from bps.sleep(1)
                #     yield from mabt(alpha, alpha, 0)
                # else:
                #     yield from mabt(alpha, alpha, 0)

            else:
                yield from mabt(alpha-0.1, alpha-0.1, 0)
                yield from bps.sleep(1)
                yield from mabt(alpha, alpha, 0)
            
            ### this is a quick patch for loss the incident angle. 2024/11/22
            yield from bps.sleep(5)
            if abs(geo.ia.user_setpoint.value-alpha)>0.001:
                print(f'Target ia {alpha}, current ia {geo.ia.user_setpoint.value}.')
                yield from bps.mv(geo.ia, alpha)

            if abs(geo.oa.user_setpoint.value-alpha)>0.001:
                print(f'Target oa {alpha}, current ia {geo.oa.user_setpoint.value}.')
                yield from bps.mv(geo.oa, alpha)

        #yield from mabt(geo.alpha=0,geo.samchi=x,geo.beta=2*x)
        fraction  = (alpha-alpha_start)/(alpha_stop-alpha_start)
        x2_fraction =fraction*(x2_offset_stop-x2_offset_start) + x2_offset_start ## Need to add x2_offset_start (HZ)

        yield from bps.mv(S2.vg,s2_vg)
        if abs(x2_fraction)>0:
            yield from bps.mv(geo.stblx2,x2_nominal+x2_fraction)
            yield from bps.sleep(5) # Wait for vibration going away for Kibron troughs (HZ)
        # yield from bps.mv(block.y,x2_nominal+x2_fraction+block_offset) # large trough
        # yield from bps.mv(block.y,blocky_nominal+x2_fraction+block_offset) # small trough, multiple slits
        if x2_offset_stop != x2_offset_start: 
            yield from bps.sleep(2) # sleep every time after x2 move (HZ)
        yield from bps.sleep(wait_time)    
        # REMOVED FOR MOLTEN SALTS
        #if alpha <= alpha_old:
        #    yield from bps.sleep(10) 
        #    print("wating an extra 10 sec")  
        alpha_old =alpha


        #Attenuator MODE
        # Set the absorber time to the define exp_time for the measurement
        # AUTO MODE FIGURES OUT THE APPROPIRAE ATTENUATOR BY DOING TESTS WITH HIGH ATTENUATOR NUMBERS
        if atten_2 == "auto":
            yield from calc_att_auto(alpha, precount_time=precount_time,detector=detector)
        # CALC MODE FIGURES OUT THE APPROPIRAE ATTENUATOR USING A FORMULA
        elif atten_2 == "calc":
            att = calc_att_from_ai(alpha)
            yield from bps.mv(abs2, atten_2)
        # THE ATTENUATOR NUMBER IS GIVEN BUT THE OUTPUT ON THE ATTENUATO VALU IS INCORRECT
        else:            
            if isinstance(atten_2,int):
                att=atten_2
                yield from bps.mv(abs2, att)    
        
        # else:
        #     print('The absorber should be auto, calc, or int. Here will use auto.')
        #     yield from calc_att_auto(alphai, precount_time=1)
        #set metadata
        # IF NOT EQUAL TO AUTO SETTING THE META DATA, THIS CHOOSES THE att_bar data structure to use
        #  THIS IS INCORRECT SINCE ATTENUATOR VALUES ARE NOT KNOWN.
        
        if atten_2 != "auto":
            yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][att])
            yield from bps.mv(attenuator_name_signal, att_bar1['name'][att])

    
        if not auto_atten:
        ##### to use the new attenbank #### 
            yield from bps.mv(abs2, atten_2)  
            yield from bps.mv(attenuator_name_signal, f'att{atten_2}')
            if att_fact_selected != None:
                yield from bps.mv(attenuation_factor_signal, att_fact_selected[f'att{atten_2}'])


        # start_time = time.time()
        yield from bps.mv(shutter, 1)
        # print(time.time()-start_time)
        yield from det_set_exposure([quadem], exposure_time=precount_time, exposure_number = 1)
        # print(time.time()-start_time)
        # yield from bps.trigger_and_read([quadem]+
        #                                     [geo] + 
        #                                     [S2] +
        #                                     [attenuation_factor_signal] +
        #                                     [attenuator_name_signal] +
        #                                     [exposure_time_signal],name='precount')



        # yield from bps.trigger_and_read([quadem],name='precount')
        if auto_atten:
            print('Start running automate attenuator')
            yield from automate_attenuator() ## set the abs2 based an automatica attenuation macro.
            atten_2 = abs2.position
            # yield from bps.mv(abs2, atten_2)  
            yield from bps.mv(attenuator_name_signal, f'att{int(atten_2)}')
            if att_fact_selected != None:
                yield from bps.mv(attenuation_factor_signal, att_fact_selected[f'att{int(atten_2)}'])
        else:
            yield from bps.trigger_and_read([quadem],name='precount')
        # yield from det_set_exposure([detector, quadem], exposure_time=exp_time, exposure_number = 1)
    
        yield from bps.mv(shutter, 1)
        yield from bps.trigger_and_read(all_area_dets +
                                            [geo] + 
                                            [S2] +
                                            [attenuation_factor_signal] +
                                            [attenuator_name_signal] +
                                            [exposure_time_signal],
                                            name='primary')
        # print(time.time()-start_time)
        yield from bps.mv(shutter, 0)
        # print(time.time()-start_time)
        
    

def calc_att_from_ai(alphai):
    if alphai<0.15:
        return 6
    elif 0.13<alphai<0.16:
        return 5
    elif 0.16<alphai<0.25:
        return 4
    elif 0.25<alphai<0.40:
        return 3
    elif 0.4<alphai<0.6:
        return 2
    elif 0.6<alphai<1.0:
        return 1
    elif alphai>1.0:
        return 0

# THIS DOES A PRECOUNT WITH A HIGH ATTUNATOR VALUE TO DETERMINE THE BEST ATTENUATOR TO USE
def calc_att_auto(alphai, precount_time=1,detector=lambda_det):
    # Move the default attenuator in for the pre-count based on the value of attenuation define in default_attenuation
    def_att = yield from put_default_absorbers(energy.energy.position,
                                               default_attenuation=default_attenuation.get())
    # Set the exposure time to for the pre-count
    yield from det_exposure_time(precount_time, precount_time)
    # Take the pre-count data
    yield from bps.mv(shutter, 1)
    ret = yield from bps.trigger_and_read(area_dets, name='precount')
    yield from bps.mv(shutter, 0)
    if ret is None:
        print('No count on the detector')
    else:
        # Read the maximum count on a pixel from the detector
        i_max = ret['%s_stats4_max_value'%detector.name]['value']
        # look at the maximum count of the pre-count and adjust the default attenuation, can do multiple iterations
        while (i_max < 100 or i_max > 40000) and default_attenuation.get() < 1:
            if i_max > 40000:
                # If i_max to high, attenuate more
                yield from bps.mv(default_attenuation, default_attenuation.get() / 10)
            elif i_max < 100:
                # If i_max to low, attenuate less
                yield from bps.mv(default_attenuation, default_attenuation.get() * 10)
            else:
                print('You should not be there!')
                break   
            ret = yield from bps.trigger_and_read(area_dets,
                                                    name='precount')
            yield from bps.mv(shutter, 0)
                                    
            # Re-read the maximum count on a pixel from the detector
            i_max = ret['%s_stats4_max_value'%detector.name]['value']                    
        # Adjust the absorbers to avoid saturation of detector
        best_at, attenuation_factor, best_att_name = yield from calculate_and_set_absorbers(energy=energy.energy.position,
                                                                                            i_max=i_max,
                                                                                            att=def_att,
                                                                                            precount_time=precount_time)
        
        # Upload the attenuation factor for the metadata

        yield from bps.mv(attenuation_factor_signal, attenuation_factor)
        yield from bps.mv(attenuator_name_signal, best_att_name)


# THIS IS THE OLD WAY OF SETTING THE COUNTING TIMES
def reflection_scan_full_old(scan_param, md=None, detector=lambda_det, tilt_stage=False, stth_corr_par=None, usekibron = False, trough = None, compress = False, target_pressure=0):
    """
    Macros to set all the parameters in order to record all the required information for further analysis,
    such as the attenuation factors, detector='lambda_det'
    :param detector: A string whiyield from bps.mv(abs2, atten_2)  ch is the detector name
    :type detector: string, can be either 'lambda_det' or 'pilatus100k'
    """
    # Tom's way of checking to see if all lists are the same length
    N = None
    for k, v in scan_param.items():
        if N is None:
            N = len(v)
        if N != len(v):
            raise ValueError(f"the key {k} is length {len(v)}, expected {N}")

    unhinted_ref() ## change all hinted settings to 'normal'
    
    #XF:12ID1-ES{Det:Lambda}ROI1:MinX
    # Bluesky command to record metadata
    base_md = {'plan_name': 'reflection_scan',
               'cycle': RE.md['cycle'],
               'proposal_number': RE.md['proposal_number'] + '_' + RE.md['main_proposer'],
               'detector': detector.name, 
               'energy': energy.energy.position,
               'rois': [detector.roi1.min_xyz.min_x.get(),
                        detector.roi1.min_xyz.min_y.get(),
                        detector.roi2.min_xyz.min_y.get(),
                        detector.roi3.min_xyz.min_y.get(),
                        detector.roi2.size.x.get(),
                        detector.roi2.size.y.get()],
               'geo_param': [geo.L1.get(), geo.L2.get(), geo.L3.get(), geo.L4.get()],
               'slit_s1': [S1.top.position - S1.bottom.position, S1.outb.position - S1.inb.position],
               'slit_s2': [S2.vg.position, S2.hg.position],
               'x2': [geo.stblx2.position],
               'tilt stage': tilt_stage,
               }
    base_md.update(md or {})
    #  global attenuation_factor_signal, attenuator_name_signal, default_attenuation # exposure_time, 
    #  attenuator_name_signal = Signal(name='attenuator_name', value='abs1',kind='normal')
    #  attenuation_factor_signal = Signal(name='attenuation', value=1e-7,kind='normal')
    # exposure_time = Signal(name='exposure_time', value=1)
    #default_attenuation = Signal(name='default-attenuation', value=1e-7)
    # Disable the plot during the reflectivity scan
    bec.disable_plots()
    # Bluesky command to start the document
    # moved this line so we get a single UID per sub-scan
    yield from bps.open_run(md=base_md)
    x2_nominal= geo.stblx2.position
    blocky_nominal= block.y.position ## add blocky pos (HZ, 06102022)

    for i in range(N):
        # yield from bps.open_run(md=base_md)
        print('%sst set starting'%i)
        yield from bps.sleep(3) 
  #      print(scan_param)
        yield from reflection_scan_old(scan_param,i, detector=detector, md=md, tilt_stage=tilt_stage, usekibron = usekibron, trough = trough, compress = compress, target_pressure=target_pressure, x2_nominal=x2_nominal,blocky_nominal=blocky_nominal)                      
        print('%sst set done'%i)
        # yield from bps.close_run()


    # Bluesky command to stop recording metadata
    #moved this to inside the loop
    yield from bps.close_run()
    bec.enable_plots()
    # puts in absorber to protect the detctor      
    yield from bps.mv(abs2, 5)
    quadem.averaging_time.put(1)
    print('The reflectivity scan is over')
    hinted_ref() ## change hinted settings

#print(f'Loading {__file__}')
all_area_dets = [quadem, lambda_det, AD1, AD2, o2_per, chiller_T]
#all_area_dets = [quadem, bpm, lambda_det, AD1, AD2, o2_per, chiller_T]



@bpp.stage_decorator(all_area_dets)
def reflection_scan_old(scan_param, i, detector='lambda_det', md={}, tilt_stage=False,x2_nominal=0,blocky_nominal=0, usekibron = False, trough = None, compress = False, target_pressure=0):
        
    alpha_start =   scan_param["start"][i]
    alpha_stop =    scan_param["stop"][i]
    number_points = scan_param["n"][i]
    atten_2 =       scan_param["atten"][i]
    s2_vg =         scan_param["s2vg"][i]
    exp_time =      scan_param["exp_time"][i]
    precount_time=  scan_param["pre_time"][i]
    wait_time =     scan_param["wait_time"][i]
    x2_offset_start =     scan_param["x2_offset_start"][i]
    x2_offset_stop =     scan_param["x2_offset_stop"][i]
    block_offset   =     scan_param["beam_block_offset"][i]



# setting up so that if alpha is moved negative that there is an extra wait
    alpha_old=5
    print(alpha_start,"----",alpha_stop,atten_2)
    for alpha in np.linspace(alpha_start, alpha_stop, number_points):
        # Move to the good geometry position
        if tilt_stage:
             yield from nab(alpha, alpha)
        else:
            if alpha >= alpha_old:
                yield from mabt(alpha, alpha, 0)

                # if alpha-alpha_old < 0.05: ## added by HZ 2022-10-17 due to low geometry resolution
                #     yield from mabt(alpha-0.1, alpha-0.1, 0)
                #     yield from bps.sleep(1)
                #     yield from mabt(alpha, alpha, 0)
                # else:
                #     yield from mabt(alpha, alpha, 0)

            else:
                yield from mabt(alpha-0.1, alpha-0.1, 0)
                yield from bps.sleep(1)
                yield from mabt(alpha, alpha, 0)



        #yield from mabt(geo.alpha=0,geo.samchi=x,geo.beta=2*x)
        fraction  = (alpha-alpha_start)/(alpha_stop-alpha_start)
        x2_fraction =fraction*(x2_offset_stop-x2_offset_start) + x2_offset_start ## Need to add x2_offset_start (HZ)
        # Set the exposure time to the define exp_time for the measurement
        yield from det_set_exposure(detectors_all, expo_time=exp_time, expo_number = 1)
        #   yield from det_exposure_time(exp_time, exp_time)
        # yield from bps.mv(exposure_time, exp_time)
        yield from bps.mv(S2.vg,s2_vg)
        if abs(x2_fraction)>0:
            yield from bps.mv(geo.stblx2,x2_nominal+x2_fraction)
            yield from bps.sleep(5) # Wait for vibration going away for Kibron troughs (HZ)
        # yield from bps.mv(block.y,x2_nominal+x2_fraction+block_offset) # large trough
        # yield from bps.mv(block.y,blocky_nominal+x2_fraction+block_offset) # small trough, multiple slits
        if x2_offset_stop != x2_offset_start: 
            yield from bps.sleep(2) # sleep every time after x2 move (HZ)
        yield from bps.sleep(wait_time)    
        # REMOVED FOR MOLTEN SALTS
        #if alpha <= alpha_old:
        #    yield from bps.sleep(10) 
        #    print("wating an extra 10 sec")  
        alpha_old =alpha


        #Attenuator MODE
        # Set the absorber time to the define exp_time for the measurement
        # AUTO MODE FIGURES OUT THE APPROPIRAE ATTENUATOR BY DOING TESTS WITH HIGH ATTENUATOR NUMBERS
        if atten_2 == "auto":
            yield from calc_att_auto(alpha, precount_time=precount_time,detector=detector)
        # CALC MODE FIGURES OUT THE APPROPIRAE ATTENUATOR USING A FORMULA
        elif atten_2 == "calc":
            att = calc_att_from_ai(alpha)
            yield from bps.mv(abs2, atten_2)
        # THE ATTENUATOR NUMBER IS GIVEN BUT THE OUTPUT ON THE ATTENUATO VALU IS INCORRECT
        else:            
            if isinstance(atten_2,int):
                att=atten_2
                yield from bps.mv(abs2, att)
                
            # else:
            #     print('The absorber should be auto, calc, or int. Here will use auto.')
            #     yield from calc_att_auto(alphai, precount_time=1)
        #set metadata
        # IF NOT EQUAL TO AUTO SETTING THE META DATA, THIS CHOOSES THE att_bar data structure to use
        #  THIS IS INCORRECT SINCE ATTENUATOR VALUES ARE NOT KNOWN.
        if atten_2 != "auto":
            yield from bps.mv(attenuation_factor_signal, att_bar1['attenuator_aborp'][att])
            yield from bps.mv(attenuator_name_signal, att_bar1['name'][att])

        # ToDo: is that really usefull now
       # if alpha == alpha_start:
       #     print("first point in the scan")
       #     yield from bps.mv(shutter, 1)
       #     yield from bps.trigger_and_read(all_area_dets, name='precount')
       #     yield from bps.mv(shutter, 0)
       #     yield from bps.sleep(wait_time)
       #     print("finished dummy count")

        yield from bps.mv(shutter, 1)
    #    yield from bps.sleep(2)
        yield from det_exposure_time(1,1)
        yield from bps.mv(exposure_time, 1)
        quadem.averaging_time.put(precount_time)
        yield from bps.trigger_and_read([quadem], name='precount')
        quadem.averaging_time.put(exp_time)
        yield from det_exposure_time(exp_time, exp_time)
        yield from bps.mv(exposure_time, exp_time)

        if usekibron:
            if trough is None:
                print('Trough is not defined; it should be set to Kibron.')
                raise ValueError('Trough is not defined!')
            else:
                if compress: # to use compression mode
                    trough.update() # to update the kibron parameters
                    if target_pressure - trough.pressure.get() > 0.5:
                        print(f'Target pressure is {target_pressure} mN/m')
                        print(f'Current pressure is {trough.pressure.get()} mN/m')
                        print('Need to compress!')
                        trough.runPressureManual(target_pressure = target_pressure, target_speed = 10)


                        #### codes below does not work due to opening a new run

                        # yield from bps.unstage(lambda_det)
                        # yield from det_exposure_time(1,1)
                        # yield from sample_height_set_fine_o(detector=lambda_det)
                        # yield from bps.stage(lambda_det)
                        # yield from mabt(alpha, alpha, 0)
                        # yield from bps.sleep(wait_time)


            yield from bps.mv(shutter, 1)
            yield from det_exposure_time(1,1)
            yield from bps.mv(exposure_time, 1)
            quadem.averaging_time.put(precount_time)
            yield from bps.trigger_and_read([quadem], name='precount')
            quadem.averaging_time.put(exp_time)
            yield from det_exposure_time(exp_time, exp_time)
            yield from bps.mv(exposure_time, exp_time)
            
            trough.update() # to update the kibron parameters
            yield from bps.sleep(2) 

            yield from bps.trigger_and_read(all_area_dets +
                                [trough] + 
                                [geo] + 
                                [S2] +
                                [attenuation_factor_signal] +
                                [attenuator_name_signal] +
                                [exposure_time],
                                name='primary')
        
        
        else: ## Normal mode without kibron trough

            yield from bps.mv(shutter, 1)
            yield from det_exposure_time(1,1)
            yield from bps.mv(exposure_time, 1)
            quadem.averaging_time.put(precount_time)
            yield from bps.trigger_and_read([quadem], name='precount')
            quadem.averaging_time.put(exp_time)
            yield from det_exposure_time(exp_time, exp_time)
            yield from bps.mv(exposure_time, exp_time)

            yield from bps.trigger_and_read(all_area_dets +
                                            [geo] + 
                                            [S2] +
                                            [attenuation_factor_signal] +
                                            [attenuator_name_signal] +
                                            [exposure_time],
                                            name='primary')
        #THIS IS WHERE WE COULD PUT IN A WARNING IF THE INTENSITY IS TOO HIGH OR LOW

        yield from bps.mv(shutter, 0)
        


def automate_attenuator(precount_time=1,detector=lambda_det, upper_limit=2e5, total_threshold=[1e4, 2e5], abs_range =[0, 6], exposure_time_limit=[10,30]):
    '''
    Developed by Juan and Honghu.
    Frist test with beam on 04/08/2025

    precount_time: Exposure time to get a frame based on the current attenuator for further calculation
    detector: Detector object to take the shot and calculate the intensity in ROI2 and ROI4
    upper_limit: Maximum intensity allowed for a pixel in ROI4
    total_threshold: Lower and upper bound for desired intensity in ROI2
    abs_range: Lower and upper bound for allowed attenuator
    exposure_time_limit: 0: exposure_time limit for using current attenuator to increase statistics
                         1: exposure_time limit for using lowest attenuator while protecting the samples

    
    '''
    # Set the exposure time to for the pre-count
    # yield from det_exposure_time(precount_time, precount_time)
    yield from det_set_exposure([detector,quadem], exposure_time=precount_time, exposure_number = 1)
    # Take the pre-count data
    yield from bps.mv(shutter, 1)
    ret = yield from bps.trigger_and_read([detector, quadem], name='precount')
    yield from bps.mv(shutter, 0)
    
    if ret is None:
        print('No count on the detector')
    else:
        # Read the maximum count on a pixel from the detector
        # i_total = ret['%s_stats2_total'%detector.name]['value'] # Total intensity of i2
        i_total = ret[f'{detector.name.split("_")[0]}_2']['value'] # Total intensity of i2
        print(f'Total intensity of ROI2 {i_total}')

        # i_max = ret['%s_stats5_max'%detector]['value'] # Maximum intensity of one pixel
        # i_max = ret['%s_stats4_max_value'%detector.name]['value'] # Maximum intensity of one pixel
        i_max = ret[f'{detector.name.split("_")[0]}_4']['value'] # Total intensity of i4
        print(f'Max pixel intensity of ROI4 {i_max}')

        # att_keys = list(att_fact_selected.keys())

        abs2_current_position = abs2.position
        print(f'Current abs2 position: {abs2_current_position:.2f}')

        if i_max > upper_limit: # check the max_int for a pixel
            abs_target_position = abs2_current_position+1 
            # TODO: keep the count rate per pixel less than 200k based on the lambda parameter; need to think about the exposure!
        elif i_total > total_threshold[1]: #check the roi intensity
            abs_target_position = abs2_current_position+1
        else:
            # check lower limit of abs_range
            if abs(abs2_current_position - abs_range[0]) < 0.1: # stay at the current
                abs_target_position = abs2_current_position
                print(f'Approaching the low limit of abs2')
                exp_time_target = int(np.ceil(total_threshold[0]/i_total)) # protect the sample while sacrefice the statistics

                if exp_time_target > exposure_time_limit[1]:
                    exp_time_target = exposure_time_limit[1]

                print(f'Target exposure time: {exp_time_target} s')

                yield from det_set_exposure([detector, quadem], exposure_time=exp_time_target, exposure_number = 1)

            elif  i_total > total_threshold[0]:
                abs_target_position = abs2_current_position
                print(f'To get better statistics')
                exp_time_target = int(total_threshold[1]/i_total)
                if exp_time_target > exposure_time_limit[0]:
                    exp_time_target = exposure_time_limit[0]
                print(f'Target exposure time: {exp_time_target} s')

                yield from det_set_exposure([detector, quadem], exposure_time=exp_time_target, exposure_number = 1)

            else:
                abs_target_position = abs2_current_position-1

        yield from bps.mv(abs2, abs_target_position)
        print(f'change the abs2 to a new pos {abs_target_position}')
        yield from bps.sleep(2)
