print(f'Loading {__file__}')

from ophyd import Component as Cpt
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector import ADComponent as ADCpt, DetectorBase

from nslsii.ad33 import StatsPluginV33
from nslsii.ad33 import SingleTriggerV33


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
               write_path_template="/disk2/jpls_data/data/lambda/%Y/%m/%d/",
               read_path_template="/nsls2/jpls/data/lambda/%Y/%m/%d/",
               root='/nsls2/jpls/data')

    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')

    stats1 = Cpt(StatsPluginV33, 'Stats1:', read_attrs=['total'])
    stats2 = Cpt(StatsPluginV33, 'Stats2:', read_attrs=['total'])
    stats3 = Cpt(StatsPluginV33, 'Stats3:', read_attrs=['total'])
    stats4 = Cpt(StatsPluginV33, 'Stats4:', read_attrs=['total'])


lambda_det = Lambda('XF:12ID1-ES{Det:Lambda}', name='lambda_det')
lambda_det.tiff.kind = 'hinted'
lambda_det.stats1.kind = 'hinted'
lambda_det.stats1.total.kind = 'hinted'