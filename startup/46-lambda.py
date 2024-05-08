print(f'Loading {__file__}')

from ophyd import Component as Cpt
from ophyd import ROIPlugin, TransformPlugin, EpicsSignal, EpicsSignalRO
from ophyd.areadetector.base import EpicsSignalWithRBV as SignalWithRBV
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector import ADComponent as ADCpt, DetectorBase
from nslsii.ad33 import StatsPluginV33, SingleTriggerV33


class Lambda750kCam(CamBase):
    """
    support for X-Spectrum Lambda 750K detector
    
    https://x-spectrum.de/products/lambda-350k750k/
    """
    _html_docs = ['Lambda750kCam.html']

    config_file_path = ADCpt(EpicsSignal, 'ConfigFilePath')
    firmware_version = ADCpt(EpicsSignalRO, 'FirmwareVersion_RBV')
    operating_mode = ADCpt(SignalWithRBV, 'OperatingMode')
    serial_number = ADCpt(EpicsSignalRO, 'SerialNumber_RBV')
    temperature = ADCpt(SignalWithRBV, 'Temperature')


class LambdaDetector(DetectorBase):
    _html_docs = ['lambda.html']
    cam = Cpt(Lambda750kCam, 'cam1:')

class Lambda(SingleTriggerV33, LambdaDetector):
    # MR20200122: created all dirs recursively in /nsls2/jpls/data/lambda/
    # from 2020 to 2030 with 777 permissions, owned by xf12id1 user.
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix="TIFF1:",
               write_path_template="/nsls2/data/smi/legacy/xf12id1/data/lambda/%Y/%m/%d/",
               read_path_template="/nsls2/data/smi/legacy/xf12id1/data/lambda/%Y/%m/%d/",
               root='/nsls2/data/smi/legacy/xf12id1/data') 

    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')

    stats1 = Cpt(StatsPluginV33, 'Stats1:', read_attrs=['total'])
    stats2 = Cpt(StatsPluginV33, 'Stats2:', read_attrs=['total'])
    stats3 = Cpt(StatsPluginV33, 'Stats3:', read_attrs=['total'])
    stats4 = Cpt(StatsPluginV33, 'Stats4:', read_attrs=['total'])

    stats5 = Cpt(StatsPluginV33, 'Stats5:', read_attrs=['total']) # HZ for total counts from the whole AD


    trans1 = Cpt(TransformPlugin, 'Trans1:')

    low_thr = Cpt(EpicsSignal, 'cam1:LowEnergyThreshold')
    hig_thr = Cpt(EpicsSignal, 'cam1:HighEnergyThreshold')
    oper_mode = Cpt(EpicsSignal, 'cam1:OperatingMode')

lambda_det = Lambda('XF:12ID1-ES{Det:Lambda}', name='lambda_det')
lambda_det.tiff.kind = 'hinted'



lambda_det.roi1.kind = 'hinted'
lambda_det.stats1.kind = 'hinted'
lambda_det.stats1.total.kind = 'hinted'

lambda_det.roi2.kind = 'hinted'
lambda_det.stats2.kind = 'hinted'
lambda_det.stats2.total.kind = 'hinted'

lambda_det.roi3.kind = 'hinted'
lambda_det.stats3.kind = 'hinted'
lambda_det.stats3.total.kind = 'hinted'

lambda_det.stats4.total.kind = 'hinted'
lambda_det.stats4.kind = 'hinted'
lambda_det.stats4.max_value.kind = 'hinted'

lambda_det.stats5.kind = 'hinted'
lambda_det.stats5.total.kind = 'hinted'
lambda_det.stats5.max_value.kind = 'hinted' ## HZ


# Impose Stats4 to be ROI4 if in the future we need to exclude bad pixels
def set_defaut_stat_roi():
    yield from bps.mv(lambda_det.stats1.nd_array_port, 'ROI1')
    yield from bps.mv(lambda_det.stats2.nd_array_port, 'ROI2')
    yield from bps.mv(lambda_det.stats3.nd_array_port, 'ROI3')
    yield from bps.mv(lambda_det.stats4.nd_array_port, 'ROI4')

    # yield from bps.mv(lambda_det.stats4.nd_array_port, 'LAMBDA1') # HZ for total counts from the whole AD

# Define the region of interest if required
# lambda_det.roi1.size.x.get() = 31
# lambda_det.roi1.min_xyz.size_x.get() = 100


# def det_exposure_time(exp_t, meas_t=1):
#     yield from bps.mov(
#         lambda_det.cam.acquire_time, exp_t,
#         lambda_det.cam.acquire_period, exp_t+0.2,
#         lambda_det.cam.num_images, int(meas_t/exp_t))


