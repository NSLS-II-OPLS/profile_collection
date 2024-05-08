from ophyd import Signal

exposure_time_signal = Signal(name='expo_time', value=1)

def det_set_exposure(detectors, exposure_time, exposure_period = None, exposure_number = 1):
    '''
    To see the exposure time for a list of detectors
    exposure_time   (float): exposure time for one frame
    exposure_period (float): the period for multiple frames; default is exposure_time+0.1
    exposure_number (int):   total frame number for multiple frames; default is 1 (single frame)
    '''
   # print("set_exposure",detectors,exposure_time)
    if exposure_period == None:
        exposure_period = exposure_time+0.1

    yield from bps.mov(exposure_time_signal, exposure_time)

    for det in detectors:

        # if det in [pilatus100k, pilatus300k, lambda_det]:
        if det in [pilatus100k, pilatus100kA, pilatus300k, lambda_det, pilatus1m]:

            try:
                yield from bps.mov(
                det.cam.acquire_time, exposure_time,
                det.cam.acquire_period, exposure_period,
                det.cam.num_images, exposure_number
                )
            except:
                print(f'{det.name} is not connected properly.')

        elif det == xs:
            yield from bps.mov(
                det.settings.acquire_time, exposure_time,
                det.settings.num_images, exposure_number
                )

        elif det == quadem:
            yield from bps.mov(
                det.averaging_time, exposure_time
                )

        else:
            print('An unknown detector was selected!')


def det_test(detectors=None):
    '''
    test all the all detectors
    '''
    if detectors is None:
        detectors = [quadem, lambda_det, pilatus100k, xs, pilatus1m]
    yield from det_set_exposure(detectors, exposure_time=1, exposure_number = 1)
    for det in detectors:
        print(f'Currently running {det.name}...')
        yield from bp.count([det])
        yield from bps.sleep(0.1)  


detectors_all = [quadem, lambda_det, pilatus300k, pilatus100kA, pilatus1m, xs]

