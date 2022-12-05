import numpy as np
import math
from matplotlib import pyplot as plt
from matplotlib import cm
from CustomLibs import Rows_Support_Function as RSF
from CustomLibs import KSP_const as KSP
MAX = 0


def get_earth(x0, y0, z0, R, layers=18j, color='bone'):
    global MAX
    MAX = max(MAX, x0 + R, x0 - R, y0 + R, y0 - R, z0 + R, z0 - R)
    u, v = np.mgrid[0:2 * np.pi:layers, 0:np.pi:layers]
    x = np.cos(u) * np.sin(v) * R + x0
    y = np.sin(u) * np.sin(v) * R + y0
    z = np.cos(v) * R + z0

    ax.plot_surface(x, y, z, cmap=color)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    return x, y, z


def get_moon(R, self_R, SOI, latitude=0.0, longitude=0.0, layers=18j, color='bone', SOI_DISPLAY=False):
    global MAX
    x0, y0, z0 = RSF.get_xyz(math.radians(longitude), math.radians(latitude), R)

    MAX = max(MAX, x0 + self_R, x0 - self_R, y0 + self_R, y0 - self_R, z0 + self_R, z0 - self_R)
    u, v = np.mgrid[0:2 * np.pi:layers, 0:np.pi:layers]

    x = np.cos(u) * np.sin(v) * self_R + x0
    y = np.sin(u) * np.sin(v) * self_R + y0
    z = np.cos(v) * self_R + z0

    ax.plot_surface(x, y, z, cmap=color)
    if SOI_DISPLAY:
        get_moonSOI(R, SOI, latitude=latitude, longitude=longitude, layers=10j)


def get_trajectory(vertices, color):
    x = [v[0] for v in vertices]
    y = [v[1] for v in vertices]
    z = [v[2] for v in vertices]
    ax.plot(x, y, z, c=color)


def get_area():
    global MAX
    MAX += MAX // 4
    FIELD = [
        [MAX, MAX, MAX],
        [MAX, MAX, -MAX],
        [MAX, -MAX, MAX],
        [-MAX, MAX, MAX],
        [-MAX, -MAX, MAX],
        [-MAX, MAX, -MAX],
        [MAX, -MAX, -MAX],
        [-MAX, -MAX, -MAX]
    ]

    x = [v[0] for v in FIELD]
    y = [v[1] for v in FIELD]
    z = [v[2] for v in FIELD]
    ax.scatter(x, y, z)


def calculate_launch_phase_1(T, h0, R, M0, Lambda, V_R_n, V_C_n, deltaT, current_h, current_longitude, current_latitude, FUEL_MASS, absT):
    altitude = current_h - 600_000
    if V_R_n >= 0:
        if T == 0:
            V_R_n__plus = 0
            current_h = h0
        else:
            g = (KSP.G * KSP.KERBAL_MASS) / (current_h ** 2)
            p = RSF.get_atm(altitude)
            Tn = T - deltaT
            V_R_n__plus = V_R_n + ((R - (M0 - Lambda * Tn) * g - ((5.76) * 0.2 * p * 0.5 * (V_R_n ** 2)) + (Lambda * V_R_n)) / (M0 - Lambda * Tn)) * deltaT
            current_h += (deltaT * (V_R_n + V_R_n__plus) / 2)
            deltaC = deltaT * (V_C_n) / 2
            deltaLong = 360 * deltaC / (math.pi * 2 * current_h)
            current_longitude += deltaLong

        if (FUEL_MASS - Lambda * T) > 0:
            return {"T": T,
                    "absT": absT,
                    "V_R_n": V_R_n__plus,
                    "V_C_n": V_C_n,
                    "V_n": (V_C_n ** 2 + V_R_n__plus ** 2) ** 0.5,
                    "Altitude": current_h - 600_000,
                    "current_h": current_h,
                    "current_long": current_longitude,
                    "current_lat": current_latitude,
                    "MASS": (M0 - Lambda * T),
                    "FUEL_MASS": (FUEL_MASS - Lambda * T)}
        else:
            raise RSF.Custom_error("ФАЗА 1\nТопливо кончилось\n")

    else:
        raise RSF.Custom_error("Тяговооруженность ниже 1, это штука не полетит не истратив впустую топливо")


def launch_p1(h0=0, h_purpose=10_000, launch_latitude=0.0, launch_longitude=0.0, color="red", THRUST=0, START_MASS=0, BURN_RATE=0, deltaT=0, FUEL_MASS=0, DRAW=True, absT=0):
    global MAX
    current_h = h0
    T = 0
    V_R_n = 0
    V_C_n = 175

    DATA = []
    trajectory = []

    current_latitude = launch_latitude
    current_longitude = launch_longitude

    if h_purpose - 600_000 > 25_000: raise RSF.Custom_error(
        "ФАЗА 1\nДалее ты 100% перелетишь нужную высоту и траектория будет неэффективной")
    if h_purpose - 600_000 < 3000: raise RSF.Custom_error(
        "ФАЗА 1\nХерня какая-то, слишком маленькая высота подъема, такую даже не рассматриваем")

    while current_h < h_purpose + deltaT:
        result = calculate_launch_phase_1(T=T,
                                          h0=h0,
                                          R=THRUST,
                                          M0=START_MASS,
                                          Lambda=BURN_RATE,
                                          V_R_n=V_R_n,
                                          V_C_n=V_C_n,
                                          deltaT=deltaT,
                                          current_h=current_h,
                                          current_longitude=current_longitude,
                                          current_latitude=current_latitude,
                                          FUEL_MASS=FUEL_MASS,
                                          absT=absT)

        T += deltaT
        absT += deltaT

        V_R_n = result["V_R_n"]
        current_h = result["current_h"]
        current_longitude = result["current_long"]

        if current_h - 600_000 < 0: raise RSF.Custom_error("ФАЗА 1\nТы умудрился врезаться в землю")

        point = RSF.get_xyz(math.radians(current_longitude), math.radians(current_latitude), current_h)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)

        DATA.append(result)

    if DRAW: get_trajectory(trajectory, color)
    return DATA


def launch_p2(phase_1_h, phase_1_V_R, phase_1_V_C, phase_1_lat, phase_1_long, phase_1_MF, R, BURN_RATE, thrust_angle, Duration, deltaT, color, FUEL_MASS, DRAW, SPACESHIP, absT):
    global MAX

    trajectory = []
    DATA = []
    current_h = phase_1_h
    V_R_n = phase_1_V_R
    V_C_n = phase_1_V_C
    current_lat = phase_1_lat
    current_long = phase_1_long
    M0 = phase_1_MF
    T = 0
    if Duration < 5: raise RSF.Custom_error("ФАЗА 2\nОчевидно слишком маленькое время работы двигателя")
    while T < Duration + deltaT:
        result = calculate_phase_2(h0=current_h,
                                   current_h=current_h,
                                   T=T,
                                   deltaT=deltaT,
                                   V_R_n=V_R_n,
                                   V_C_n=V_C_n,
                                   thrust_angle=thrust_angle,
                                   R=R,
                                   M0=M0,
                                   Lambda=BURN_RATE,
                                   current_long=current_long,
                                   current_lat=current_lat,
                                   FUEL_MASS=FUEL_MASS,
                                   SPACESHIP=SPACESHIP,
                                   absT=absT)

        V_R_n = result["V_R_n"]
        V_C_n = result["V_C_n"]
        current_h = result["current_h"]
        current_long = result["current_long"]

        if result["FUEL_MASS"] < 0: raise RSF.Custom_error("ФАЗА 2\nНе хватит топлива")
        if current_h - 600_000 < 0: raise RSF.Custom_error("ФАЗА 2\nТы умудрился врезаться в землю")
        if thrust_angle >= 80: raise RSF.Custom_error("ФАЗА 2\nТы фактически изменяешь смысл фазы, без этого")
        if thrust_angle <= 10: raise RSF.Custom_error(
            "ФАЗА 2\nЗачем поворачиваться на такой маленький угол? Просто подлети выше и развернись нормально")

        T += deltaT
        absT += deltaT

        point = RSF.get_xyz(math.radians(current_long), math.radians(current_lat), current_h)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)

        DATA.append(result)
    if DRAW: get_trajectory(trajectory, color)
    return DATA


def calculate_phase_2(h0, current_h, T, deltaT, V_R_n, V_C_n, thrust_angle, R, M0, Lambda, current_long, current_lat, FUEL_MASS, SPACESHIP, absT):
    V_n = (V_R_n ** 2 + V_C_n ** 2) ** 0.5
    altitude = current_h - 600_000

    if V_n >= 0:
        if T == 0:
            Drag_R_loss = KSP.AIR_DRAG_CONSTANT * ((V_R_n) ** 2) * (SPACESHIP["LENGTH"] * SPACESHIP["HEIGHT"]) * math.sin(
                math.radians(thrust_angle)) * RSF.get_atm(altitude)
            V_R_n__plus = V_R_n - Drag_R_loss
            V_C_n__plus = V_C_n
            current_h = h0
        else:
            g = (KSP.G * KSP.KERBAL_MASS) / (current_h ** 2)

            p = RSF.get_atm(altitude)
            Tn = T - deltaT

            R_R = R * math.cos(math.radians(thrust_angle))
            R_C = R * math.sin(math.radians(thrust_angle))

            drag_angle_rad = math.atan(V_C_n / V_R_n)
            turn_angle = thrust_angle - math.degrees(drag_angle_rad)

            if turn_angle > 10:
                S = SPACESHIP["HEIGHT"] * SPACESHIP["WIDTH"]
            elif ((10 >= turn_angle) and (turn_angle >= -2.0)):
                S = SPACESHIP["HEIGHT"] * SPACESHIP["WIDTH"] / 2
            else:
                S = SPACESHIP["LENGTH"] * SPACESHIP["WIDTH"] * 1.5
            F_air = (S * 0.2 * p * 0.5 * (V_n ** 2))

            F_air_R = F_air * math.cos(drag_angle_rad)
            F_air_C = F_air * math.sin(drag_angle_rad)
            Strange_thing = Lambda * V_n
            S_T_R = Strange_thing * math.cos(drag_angle_rad)
            S_T_C = Strange_thing * math.sin(drag_angle_rad)
            V_R_n__plus = V_R_n + ((R_R - (M0 - Lambda * Tn) * g - F_air_R + S_T_R) / (M0 - Lambda * Tn)) * deltaT
            V_C_n__plus = V_C_n + ((R_C - F_air_C + S_T_C) / (M0 - Lambda * Tn)) * deltaT

            deltaC = deltaT * (V_C_n__plus + V_C_n) / 2
            deltaLong = 360 * deltaC / (math.pi * 2 * current_h)

            current_long += deltaLong
            current_h += (deltaT * (V_R_n + V_R_n__plus) / 2)

        return {"T": T,
                "absT": absT,
                "V_R_n": V_R_n__plus,
                "V_C_n": V_C_n__plus,
                "V_n": (V_R_n__plus ** 2 + V_C_n__plus ** 2) ** 0.5,
                "Altitude": current_h - 600_000,
                "current_h": current_h,
                "current_long": current_long,
                "current_lat": current_lat,
                "MASS": (M0 - Lambda * T),
                "FUEL_MASS": (FUEL_MASS - Lambda * T)}




    else:
        raise RSF.Custom_error("Тяговооруженность ниже 1, это штука не полетит не истратив впустую топливо")


def launch_p3(phase_2_h, phase_2_V_R, phase_2_V_C, phase_2_lat, phase_2_long, phase_2_MF, deltaT, FUEL_MASS, DRAW, color, absT, GOAL, EPSILON, FREE_MOD):
    global MAX

    trajectory = []
    DATA = []
    current_h = phase_2_h
    V_R_n = phase_2_V_R
    V_C_n = phase_2_V_C
    current_lat = phase_2_lat
    current_long = phase_2_long
    M0 = phase_2_MF
    T = 0
    if V_R_n < 0: "ФАЗА 3\nТы уже пдаешь "
    while True:
        result = calculate_phase_3(h0=current_h,
                                   current_h=current_h,
                                   T=T,
                                   deltaT=deltaT,
                                   V_R_n=V_R_n,
                                   V_C_n=V_C_n,
                                   M0=M0,
                                   current_long=current_long,
                                   current_lat=current_lat,
                                   FUEL_MASS=FUEL_MASS,
                                   absT=absT)

        V_R_n = result["V_R_n"]
        V_C_n = result["V_C_n"]
        current_h = result["current_h"]
        current_long = result["current_long"]
        absT += deltaT
        T += deltaT

        if result["FUEL_MASS"] < 0: raise RSF.Custom_error("ФАЗА 3\nНе хватит топлива");
        if current_h - 600_000 < 0: raise RSF.Custom_error("ФАЗА 3\nТы умудрился врезаться в землю");

        point = RSF.get_xyz(math.radians(current_long), math.radians(current_lat), current_h)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)

        DATA.append(result)
        if V_R_n < 0:
            break
        elif math.fabs((V_C_n ** 2 + V_R_n ** 2) ** 0.5) > 10_000:
            break
        elif T > 500:
            raise RSF.Custom_error(
                "Достигнут лимит просчета траектории 3ей фазы, скорее всего ваша траектория не является возможной в рамках понимания 3ей фазы,"
                "если вы уверены, что она возможна, то поменяйте параметр в проверке исключения 3ей фазы")

    if DRAW: get_trajectory(trajectory, color)
    if not FREE_MOD:
        if not ((DATA[-1]["Altitude"] <= GOAL + EPSILON) and (DATA[-1]["Altitude"] >= GOAL - EPSILON)):
            raise RSF.Custom_error(
                "ФАЗА 3\nТакими маневрами не попасть на нужную орбиту, нужна наивысшая точка в эпсилон (eps=" + str(
                    EPSILON) + ") окрестности " + str(GOAL) + ", а пик этой траектории на " + str(DATA[-1][
                                                                                                      "Altitude"]) + "\n\n Если вы хотите отключить это предупреждение установите FREE_MOD = True")
    return DATA


def calculate_phase_3(h0, current_h, T, deltaT, V_R_n, V_C_n, M0, current_long, current_lat, FUEL_MASS, absT):
    V_n = (V_R_n ** 2 + V_C_n ** 2) ** 0.5
    altitude = current_h - 600_000

    if V_n >= 0:
        if T == 0:
            V_R_n__plus = V_R_n
            V_C_n__plus = V_C_n
            current_h = h0
        else:
            g = (KSP.G * KSP.KERBAL_MASS) / (current_h ** 2)

            p = RSF.get_atm(altitude)

            S = 5.76
            F_air = (S * 0.2 * p * 0.5 * (V_n ** 2))

            drag_angle_rad = math.atan(V_C_n / V_R_n)
            F_air_R = F_air * math.cos(drag_angle_rad)
            F_air_C = F_air * math.sin(drag_angle_rad)
            V_R_n__plus = V_R_n + ((- (M0) * g - F_air_R) / (M0)) * deltaT
            V_C_n__plus = V_C_n + ((- F_air_C) / (M0)) * deltaT

            deltaC = deltaT * (V_C_n__plus + V_C_n) / 2
            deltaLong = 360 * deltaC / (math.pi * 2 * current_h)

            current_long += deltaLong
            current_h += (deltaT * (V_R_n + V_R_n__plus) / 2)

        return {"T": T,
                "absT": absT,
                "V_R_n": V_R_n__plus,
                "V_C_n": V_C_n__plus,
                "V_n": (V_R_n__plus ** 2 + V_C_n__plus ** 2) ** 0.5,
                "Altitude": current_h - 600_000,
                "current_h": current_h,
                "current_long": current_long,
                "current_lat": current_lat,
                "MASS": (M0),
                "FUEL_MASS": FUEL_MASS}


def launch_p4(V0, absT, lat_0, long_0, R, M0, FUEL_MASS, I, BURNING_RATE, deltaT, color, DRAW):
    global MAX
    V = ((KSP.KERBAL_MASS * KSP.G) / R) ** 0.5
    period = (2 * math.pi * R) / V
    needed_deltaV = V - V0
    I *= 9.816
    possible_deltaV = I * math.log((M0 / (M0 - FUEL_MASS)), math.e)
    deltaFUEL = M0 - (M0 / math.exp(needed_deltaV / I))
    BURNING_TIME = deltaFUEL / BURNING_RATE
    DATA = []
    trajectory = []
    midV = (V + V0) / 2
    ExecTIME = BURNING_TIME - BURNING_TIME % deltaT
    T = 0

    if possible_deltaV > needed_deltaV:
        while T < ExecTIME:
            current_long = long_0 + ((360 * T * midV) / (2 * math.pi * R))

            point = RSF.get_xyz(math.radians(current_long), math.radians(lat_0), R)
            MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
            trajectory.append(point)

            result = {"absT": absT,
                      "R": R,
                      "current_lat": lat_0,
                      "current_long": current_long,
                      "Altitude": R - 600_000,
                      "MASS": M0 - deltaFUEL,
                      "FUEL_MASS": FUEL_MASS - deltaFUEL,
                      "V_n": V,
                      "period": period,
                      "BURNING_TIME": BURNING_TIME,
                      "V_C_n": V,
                      "V_R_n": 0,
                      "orbitalV": V
                      }
            DATA.append(result)

            T += deltaT
            absT += deltaT

        if DRAW: get_trajectory(trajectory, color)
        return DATA
    else:
        raise RSF.Custom_error("ФАЗА 4\nНе хватит deltaV, ложная траектория")


def calc_Hohmann_Transfer(pere_R, apo_R, long_0, lat_0, M0, FUEL_MASS, BURNING_RATE, absT, exc, period, T, a, Mu):
    M = (T / period) * 360
    CoOl_ThInG = int(M // 180)
    E = math.degrees(RSF.found_eccentric_anomaly(math.radians(M)))
    R = a * (1 - (exc * math.cos(math.radians(E))))
    fi_from_arccos = (((a * (1 - (exc ** 2))) / R) - 1) / exc
    if fi_from_arccos > 1: fi_from_arccos = 1
    if fi_from_arccos < -1: fi_from_arccos = -1
    fi = math.degrees(math.acos(fi_from_arccos))
    if CoOl_ThInG:
        current_long = long_0 + 360 - fi
    else:
        current_long = long_0 + fi
    V = (Mu * ((2 / R) - (1 / a))) ** 0.5
    result = {"T": T,
              "absT": absT,
              "current_lat": lat_0,
              "current_long": current_long,
              "MASS": M0 - BURNING_RATE * T,
              "FUEL_MASS": FUEL_MASS - BURNING_RATE * T,
              "period": period,
              "orbitalV": V,
              "current_h": R,
              "R": R,
              "apo_R": apo_R,
              "pere_R": pere_R
              }
    return result


def burn_Hohmann_Transfer(pere_R, apo_R, V0, long_0, lat_0, I, M0, FUEL_MASS, BURNING_RATE, deltaT, absT, DRAW, color, quality):
    global MAX
    a = (pere_R + apo_R)/2
    exc = 1 - (pere_R/a)
    b = a * ((1 - (exc**2))**0.5)
    Mu = KSP.G * KSP.KERBAL_MASS
    V = (Mu * ((2 / pere_R) - (1 / a)))**0.5
    needed_deltaV = V - V0
    period = 2 * math.pi * (a**3 / Mu)**0.5
    trajectory = []
    DATA = []
    I *= 9.816
    deltaFUEL = M0 - (M0 / math.exp(needed_deltaV / I))
    BURNING_TIME = deltaFUEL / BURNING_RATE
    ExecTIME = BURNING_TIME - BURNING_TIME % deltaT
    T = 0
    calc_detailing = int(1 / (int(quality) / 100))
    deltaT = deltaT * calc_detailing
    flag = 0

    while T < ExecTIME:
        result = calc_Hohmann_Transfer(pere_R=pere_R,
                                       apo_R=apo_R,
                                       long_0=long_0,
                                       lat_0=lat_0,
                                       M0=M0,
                                       FUEL_MASS=FUEL_MASS,
                                       BURNING_RATE=BURNING_RATE,
                                       absT=absT,
                                       exc=exc,
                                       period=period,
                                       T=T,
                                       a=a,
                                       Mu=Mu)

        R = result["R"]
        current_long = result["current_long"]

        point = RSF.get_xyz(math.radians(current_long), math.radians(lat_0), R)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)

        flag += 1
        T += deltaT
        absT += deltaT
        DATA.append(result)
    if T != ExecTIME:
        result = calc_Hohmann_Transfer(pere_R=pere_R,
                                       apo_R=apo_R,
                                       long_0=long_0,
                                       lat_0=lat_0,
                                       M0=M0,
                                       FUEL_MASS=FUEL_MASS,
                                       BURNING_RATE=BURNING_RATE,
                                       absT=absT,
                                       exc=exc,
                                       period=period,
                                       T=BURNING_TIME,
                                       a=a,
                                       Mu=Mu)

        R = result["R"]
        current_long = result["current_long"]

        point = RSF.get_xyz(math.radians(current_long), math.radians(lat_0), R)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)
        DATA.append(result)

    if DRAW: get_trajectory(trajectory, color)
    return DATA


def Hohmann_Transfer(pere_R, apo_R, long_0, lat_0, M0, FUEL_MASS, deltaT, absT, DRAW, color, quality, Duration, T0):
    global MAX
    a = (pere_R + apo_R)/2
    exc = 1 - (pere_R/a)
    Mu = KSP.G * KSP.KERBAL_MASS
    period = 2 * math.pi * (a**3 / Mu)**0.5
    trajectory = []
    DATA = []
    T = T0
    calc_detailing = int(1 / (int(quality) / 100))
    deltaT = deltaT * calc_detailing
    flag = 0

    while T < Duration:
        result = calc_Hohmann_Transfer(pere_R=pere_R,
                                       apo_R=apo_R,
                                       long_0=long_0,
                                       lat_0=lat_0,
                                       M0=M0,
                                       FUEL_MASS=FUEL_MASS,
                                       BURNING_RATE=0,
                                       absT=absT,
                                       exc=exc,
                                       period=period,
                                       T=T,
                                       a=a,
                                       Mu=Mu)

        R = result["R"]
        current_long = result["current_long"]

        point = RSF.get_xyz(math.radians(current_long), math.radians(lat_0), R)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)

        flag += 1
        T += deltaT
        absT += deltaT
        DATA.append(result)
    if T != Duration + deltaT:
        result = calc_Hohmann_Transfer(pere_R=pere_R,
                                       apo_R=apo_R,
                                       long_0=long_0,
                                       lat_0=lat_0,
                                       M0=M0,
                                       FUEL_MASS=FUEL_MASS,
                                       BURNING_RATE=0,
                                       absT=absT,
                                       exc=exc,
                                       period=period,
                                       T=Duration,
                                       a=a,
                                       Mu=Mu)

        R = result["R"]
        current_long = result["current_long"]

        point = RSF.get_xyz(math.radians(current_long), math.radians(lat_0), R)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)
        DATA.append(result)

    if DRAW: get_trajectory(trajectory, color)
    return DATA


def get_decard(MAX):
    get_trajectory([[MAX, 0, 0], [-MAX, 0, 0]], "red")
    get_trajectory([[0, MAX, 0], [0, -MAX, 0]], "chartreuse")
    get_trajectory([[0, 0, MAX], [0, 0, -MAX]], "blue")


def LEO(R, long_0, lat_0, Duration, deltaT, orbitalV, absT, M0, FUEL_MASS, color, DRAW, period):
    global MAX
    T = 0
    trajectory = []
    DATA = []
    if R < 670000: raise RSF.Custom_error("Выход на орбиту невозможен в атмосфере")
    while T < Duration + deltaT:
        current_long = long_0 + ((360 * T * orbitalV) / (2 * math.pi * R))

        result = {"T": T,
                  "absT": absT,
                  "current_lat": lat_0,
                  "current_long": current_long,
                  "Altitude": R - 600_000,
                  "MASS": M0,
                  "FUEL_MASS": FUEL_MASS,
                  "period": period,
                  "orbitalV":orbitalV,
                  "current_h":R
                  }

        absT += deltaT
        T += deltaT

        point = RSF.get_xyz(math.radians(current_long), math.radians(lat_0), R)
        MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
        trajectory.append(point)

        DATA.append(result)
    if DRAW: get_trajectory(trajectory, color)
    return DATA


def get_moon_trace(absT, deltaT, alfa, R, color, self_R, SOI, SOI_DISPLAY):
    global MAX
    trajectory = []
    T = 0
    flag = 0
    current_long = alfa
    while T < absT:
        current_long = alfa + ((360 * T * KSP.MOON_V) / (2 * math.pi * R))
        T += deltaT
        flag += 1
        if flag == 10:
            point = RSF.get_xyz(math.radians(current_long), math.radians(0), R)
            MAX = max(math.fabs(max(point)), math.fabs(min(point)), MAX)
            trajectory.append(point)
            flag = 0
    get_trajectory(trajectory, color)

    get_moon(R, self_R, SOI, latitude=0, longitude=current_long, layers=18j, color='bone', SOI_DISPLAY=SOI_DISPLAY)


def get_moonSOI(R, self_R, latitude=0.0, longitude=0.0, layers=15j):
    global MAX

    x0, y0, z0 = RSF.get_xyz(math.radians(longitude), math.radians(latitude), R)

    MAX = max(MAX, x0 + self_R, x0 - self_R, y0 + self_R, y0 - self_R, z0 + self_R, z0 - self_R)
    u, v = np.mgrid[0:2 * np.pi:layers, 0:np.pi:layers]

    x = np.cos(u) * np.sin(v) * self_R + x0
    y = np.sin(u) * np.sin(v) * self_R + y0
    z = np.cos(v) * self_R + z0

    norm = plt.Normalize(z.min(), z.max())
    colors = cm.viridis(norm(z))

    ax.plot_surface(x, y, z, facecolors=colors, shade=False).set_facecolor((0, 0, 0, 0))
    return x, y, z


def afterburner(M0, I, needed_deltaV, BURNING_RATE):
    I *= 9.816
    deltaFUEL = M0 - (M0 / math.exp(needed_deltaV / I))
    final_burn = deltaFUEL / BURNING_RATE
    return final_burn


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('xkcd:salmon')
ax.set_facecolor((0, 0, 0))
get_decard(MAX)
