import numpy as np

def nusseltCoefficient(Re):
    if Re < 1e3:
        coef = 64
        expo = 1
    elif 1e3 <= Re <=2e5:
        coef = 0.27
        expo = 0.63
    elif 2e5 < Re <= 2e6:
        coef = 0.021
        expo = 0.84
    else:
        raise ValueError(f"Renolds number is too large:{Re}")
    return coef, expo


def firctionFactor(
    rr,
    Re
):
    """
    :param rr: relative roughness
    :param Re: reynolds number
    :return:
    """
    a = 1/(1+(Re/2720)**9)
    b = 1/(1+(rr*Re/160)**2)
    c = (Re/64)**a
    d = (1.8*np.log10(Re/6.8))**(2*(1-a)*b)
    e = (2*np.log10(3.7/rr))**(2*(1-a)*(1-b))
    fr = 1/(c*d*e)
    return fr


def NTUHE(C_inside,C_outside,U_total,A_HE):
    if C_inside < C_outside:
        Cr = C_inside/C_outside
        C_min = C_inside
        NTU = U_total*A_HE/C_min
        CC = np.exp(-Cr*(1-np.exp(-NTU)))
        eff = (1-CC)/Cr # efficiency of heat exchanger
    else:
        Cr = C_outside/C_inside
        C_min = C_outside
        NTU = U_total*A_HE/C_min
        CC = 1-np.exp(-Cr*NTU)
        eff = 1-np.exp(-CC/Cr)
    return eff, NTU


def nusseltNumberIn(rr,Re,PrandtlNumber):
    Pr = PrandtlNumber
    fr = firctionFactor(rr,Re)
    if Re <= 2300:
        nu = 4.01
    else:
        nu = (fr/8)*(Re-1000)*Pr/(1+12.7*(fr/8)**0.5*(Pr**(2/3)-1))
    return fr, nu