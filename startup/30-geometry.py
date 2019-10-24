import numpy as np

from ophyd import PseudoPositioner
from ophyd import PseudoSingle
from ophyd import EpicsSignal
import warnings

# from ophyd import EpicsMotor
from ophyd.pseudopos import pseudo_position_argument, real_position_argument
from ophyd import Component as Cpt
import bluesky.plans as bp
import bluesky.plan_stubs as bps

from ophyd.positioner import SoftPositioner


class EpicsMotor(SoftPositioner):
    def __init__(self, prefix, **kwargs):
        super().__init__(**kwargs, init_pos=0)
        self.prefix = prefix


class EpicsMotorWithLimits(EpicsMotor):
    # low_limit = Cpt(EpicsSignal, ".LLM")
    # high_limit = Cpt(EpicsSignal, ".HLM")
    ...


too_small = 1.0e-10


class Geometry(PseudoPositioner):
    # angles
    alpha = Cpt(PseudoSingle, "")
    beta = Cpt(PseudoSingle, "")
    stth = Cpt(PseudoSingle, "")

    # input motors
    th = Cpt(EpicsMotor, "{XtalDfl-Ax:Th}Mtr", doc="Θ 3-circle theta for mono")
    #
    phi = Cpt(EpicsMotor, "{XtalDfl-Ax:Phi}Mtr", doc="Φ-stage sets bragg angle")
    #    phi = Cpt(EpicsMotor, '{XtalDfl-Ax:M7}Mtr', labels=['geo'])
    chi = Cpt(EpicsMotor, "{XtalDfl-Ax:Chi}Mtr", doc="Χ, beam steering")
    tth = Cpt(EpicsMotor, "{XtalDfl-Ax:Tth}Mtr", doc="2Θ, spectrometer rotation")
    ih = Cpt(EpicsMotor, "{XtalDfl-Ax:IH}Mtr", doc="input height")
    ir = Cpt(EpicsMotorWithLimits, "{XtalDfl-Ax:IR}Mtr", doc="input rotation")

    # Sample Motors
    sh = Cpt(EpicsMotor, "bogus", doc="Sample vertical translation")
    astth = Cpt(EpicsMotor, "bogus", doc="Sample rotation")
    tblx2 = Cpt(EpicsMotor, "bogus", doc="Table 2 X")
    # output motors
    orb = Cpt(EpicsMotor, "bogus", doc="β, output arm rotation")
    oh = Cpt(EpicsMotor, "bogus", doc="output arm vertical rotation")

    def __init__(self, prefix, **kwargs):
        self.wlength = 0.77086  # x-ray wavelength, A
        self.s_l1 = 278  # distance crystal to input arm elevator, mm
        self.s_l2 = 850  # distance crystal to sample center, mm
        self.s_13 = 600  # distance sample to output elevator, mm
        self.s_qtau = 1.9236  # monochromator reciprocal lattice vector, 1/A
        #        self.s_Eta = 0.000722 # inc beam upward tilt from mirror (rad)
        self.s_Eta = 0.000  # inc beam upward tilt from mirror (rad)
        self.s_trck = 0  # whether to track sample table
        super().__init__(prefix, **kwargs)
        self.phi.settle_time = 0.5
        self.ih.settle_time = 0.5

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        """Calculate a RealPosition from a given PseudoPosition
           based on the s_motors method

        Parameters
        ----------
        pseudo_pos : PseudoPosition
            The pseudo position input

        Returns
        -------
        real_position : RealPosition
            The real position output
        """
        # by convention in this function:
        #  - angles in degrees are not prefixed by underscores
        #  - angles in radians are prefixed by underscores

        if pseudo_pos.alpha > 90:
            msg = f"Unobtainable position: alpha({a}) is greater than 90 degrees"
            raise ValueError(msg)

        # get pseudo positions in radians
        _alpha = np.deg2rad(pseudo_pos.alpha)
        _beta = np.deg2rad(pseudo_pos.beta)
        _stth = np.deg2rad(pseudo_pos.stth)

        cE = np.cos(self.s_Eta)
        sE = np.sin(self.s_Eta)

        # bragg is sin(theta_bragg)
        _lambda = self.wlength
        bragg = self.s_qtau * _lambda * 1.0 / (4.0 * np.pi)
        if np.fabs(bragg) > 1:
            msg = f"Unobtainable position: cannot find bragg angle, lambda ({_lambda}) too big"
            raise ValueError(msg)

        # calculate sin(phi)
        tmp = 2 * cE * bragg
        if np.fabs(tmp) < too_small:
            msg = (
                f"Unobtainable position: cannot find phi, denominator({tmp}) too small"
            )
            raise ValueError(msg)

        aphi = (2 * bragg * bragg - np.sin(_alpha) * sE - sE * sE) / tmp
        if np.fabs(aphi) > 1:
            msg = f"Unobtainable position: cannot find phi, lambda ({_lambda}) too big"
            raise ValueError(msg)

        _phi = np.arcsin(aphi)  # radians

        # calculate chi
        tmp = 2 * bragg * np.cos(_phi)
        if np.fabs(tmp) < too_small:
            msg = (
                f"Unobtainable position: cannot find chi, denominator({tmp}) too small"
            )
            raise ValueError(msg)

        # not an angle
        achi = (np.sin(_alpha) + sE) / tmp
        if np.fabs(achi) > 1:
            msg = f"Unobtainable position: cannot find chi, alpha({_alpha}) too big or phi({phi}) too small"
            raise ValueError(msg)

        _chi = np.arcsin(achi)  # as radians

        _th = 0

        tmp = cE - 2 * bragg * np.sin(_phi)
        if np.fabs(tmp) < too_small:
            msg = f"Unobtainable position: cannot find tth"
            raise ValueError(msg)

        # maybe use atan2(y, x), instead of atan(y/x) ?
        _tth = np.arctan(2 * bragg * np.cos(_phi) * np.cos(_chi) / tmp)

        ih = -self.s_l1 * np.tan(_alpha)

        # 'th', 'phi', 'chi', 'tth', 'ih', and 'ir'

        sh = self.s_l2 * np.sin(_alpha)  # + correction
        tblx2 = self.s_l2 * np.sin(_tth) * np.cos(_chi)
        # todo check degree vs radian
        oh = sh + self.s_13 * np.tan(_beta)
        # actually output theta
        _astth = _tth + _stth
        return self.RealPosition(
            th=np.rad2deg(_th),
            phi=np.rad2deg(_phi),
            chi=np.rad2deg(_chi),
            tth=np.rad2deg(_tth),
            ih=ih,
            ir=np.rad2deg(_alpha),
            orb=pseudo_pos.beta,
            sh=sh,
            tblx2=tblx2,
            astth=np.rad2deg(_astth),
            oh=oh,
        )

    @real_position_argument
    def inverse(self, real_pos):
        """Calculate a PseudoPosition from a given RealPosition

        Parameters
        ----------
        real_position : RealPosition
            The real position input

        Returns
        -------
        pseudo_pos : PseudoPosition
            The pseudo position output
        """

        bragg = self.s_qtau * self.wlength * 1.0 / (4.0 * np.pi)
        if np.fabs(bragg) > 1:
            msg = f"Unobtainable position: cannot find bragg angle, lambda ({_lambda}) too big"
            raise ValueError(msg)

        phi = real_pos.phi * (np.pi / 180.0)
        chi = real_pos.chi * (np.pi / 180.0)

        tmp = 2 * bragg * np.cos(phi) * np.sin(chi) - np.sin(self.s_Eta)
        if np.fabs(tmp) > 1:
            msg = f"Unobtainable position: cannot find alpha"
            raise ValueError(msg)

        _alpha = np.arcsin(tmp) * (180.0 / np.pi)

        stth = real_pos.astth - real_pos.tth

        return self.PseudoPosition(alpha=_alpha, beta=real_pos.orb, stth=stth)

    def move_ab(self, val):
        warnings.warn("use `yield from bps.mv(goe, val)` instead")
        return (yield from bps.mv(self.alpha, val))


geo = Geometry("XF:12ID1-ES", name="geo")
[setattr(getattr(geo, k), "kind", "hinted") for k in geo.RealPosition._fields]


def phi_track(alpha_ini, alpha_stop, num_alpha):
    # for eta in range(eta_start, eta_stop, nb_eta):
    # eta

    dif = np.zeros((2, num_alpha))
    for i, alpha in enumerate(range(0, num_alpha, 1)):
        alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)
        print(i, alpha_ini, alpha_re)
        yield from bps.mv(geo, alpha_re)
        yield from bp.rel_scan([quadem], geo.phi, -0.01, 0.01, 40)
        print(peaks.cen["quadem_current2_mean_value"] - geo.ca(alpha_re).phi)
        dif[0, i] = alpha_re

        dif[1, i] = peaks.cen["quadem_current2_mean_value"] - geo.ca(alpha_re).phi

    print(dif)
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(dif[0, :], dif[1, :])
    plt.show()


def ih_track(alpha_ini, alpha_stop, num_alpha):
    # for ih in range(alpha_ini,alpha_stop, nb_alpha):

    dif = np.zeros((3, num_alpha))
    for i, alpha in enumerate(range(0, num_alpha, 1)):
        alpha_re = alpha_ini + (i * (alpha_stop - alpha_ini) / num_alpha)
        print(i, alpha_ini, alpha_re)
        yield from bps.mv(geo, alpha_re)
        yield from bp.rel_scan([quadem], geo.phi, -0.010, 0.010, 20)
        yield from bps.mv(geo.phi, peaks.cen["quadem_current2_mean_value"])
        dif[2, i] = peaks.cen["quadem_current2_mean_value"] - geo.ca(alpha_re).phi
        yield from bp.rel_scan([quadem], geo.ih, -0.5, 0.5, 20)
        # is the next line corrct, geo.ca.
        print(peaks.cen["quadem_current3_mean_value"] - geo.ca(alpha_re).ih)
        dif[0, i] = alpha_re
        dif[1, i] = peaks.cen["quadem_current3_mean_value"] - geo.ca(alpha_re).ih

    print(dif)
    import matplotlib.pyplot as plt

    plt.figure()
    plt.subplot(211)
    plt.title("IH_track")
    plt.plot(dif[0, :], dif[1, :])
    plt.subplot(212)
    plt.title("Phi_track")
    plt.plot(dif[0, :], dif[2, :])
    plt.show()
