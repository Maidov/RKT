import math


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


class Custom_error(Exception):
    def __init__(self, text):
        self.txt = text


class Teue_error(Exception):
    def __init__(self, text):
        self.txt = text


def get_xyz(vi, fi, R):
    fi = math.pi / 2 - fi
    x = math.cos(vi) * math.sin(fi) * R
    y = math.sin(vi) * math.sin(fi) * R
    z = math.cos(fi) * R
    return [x, y, z]


def formalize_data(DATA, title):
    max_key = 0
    for key in DATA.keys():
        length = len(key)
        max_key = max(max_key, length)
    output = "\n------->  " + str(title) + "  <-------\n\n"
    for key in DATA.keys():
        output += str(key) + ":   " + (" " * (max_key - len(key))) + str(DATA[key]) + "\n"
    return output


def get_atm(altitude):
    if altitude < 2500: p = 1
    elif (2500 <= altitude) and (altitude < 5000): p = 0.681
    elif (5000 <= altitude) and (altitude < 7500): p = 0.450
    elif (7500 <= altitude) and (altitude < 10_000): p = 0.287
    elif (10_000 <= altitude) and (altitude < 15_000): p = 0.177
    elif (15_000 <= altitude) and (altitude < 20_000): p = 0.066 + 0.015
    elif (20_000 <= altitude) and (altitude < 25_000): p = 0.025 + 0.015
    elif (25_000 <= altitude) and (altitude < 30_000): p = 0.010 + 0.006
    elif (30_000 <= altitude) and (altitude < 40_000): p = 0.004 + 0.006
    elif (40_000 <= altitude) and (altitude < 50_000): p = 0.001 + 0.002
    elif altitude >= 50_000 and altitude < 70_000: p = 0
    else: p = 0
    p = p * 1.23
    return p


def get_table(first_column_key, other_column_keys, FLIGHT_DATA):
    output = str(first_column_key)
    for other_key in other_column_keys:
        output += " " + str(other_key)
    output += "\n"
    for DATA in FLIGHT_DATA:
        for condition in DATA:
            output += str(toFixed(condition[first_column_key], 3)).replace(".", ",")
            for other_key in other_column_keys:
                output += " " + str(toFixed(condition[other_key], 3)).replace(".", ",")
            output += "\n"
    return output


def found_eccentric_anomaly(M):
    # E - sinE = M
    # E = M + sinE
    E0 = math.radians(360 / 2)
    E = 0
    diff = 1.0
    eps = 0.001
    while math.fabs(diff) >= eps:
        E = M + math.sin(E0)
        diff = E - E0
        E0 = E
    return (int(E // eps)) * eps


def get_vector_angle(vector):
    tan = vector[1] / vector[0]
    meta = math.atan(tan)
    return math.degrees(meta)


def to_moon_system(orbitalV, moon_long, meta):
    ultra = meta + moon_long
    V_R_n = orbitalV * math.cos(math.radians(ultra))
    V_C_n = orbitalV * math.sin(math.radians(ultra))
    return [V_R_n, V_C_n]


def get_autopilot_full(filename, ALT1, T2, ANGL2, transfer_burn, start_angle, start_transfer, final_t, final_burn_t):
    file = open(filename, "w")
    ALT1 = str(toFixed(ALT1, 4))
    T2 = str(toFixed(T2, 4))
    ANGL2 = str(toFixed(ANGL2, 4))
    transfer_burn = str(toFixed(transfer_burn, 4))
    start_angle = str(toFixed(start_angle, 4))
    start_transfer = str(toFixed(start_transfer, 4))
    final_t = str(toFixed(final_t, 4))
    final_burn_t = str(toFixed(final_burn_t, 4))
    autopilot = """
                    set ALT1 to """ + ALT1 + """.
                    set ANGL2 to 90 - """ + ANGL2 + """.
                    set T2 to """ + T2 + """.
                    set transfer_burn to """ + transfer_burn + """.
                    set start_angle to """ + start_angle + """.
                    set start_transfer to """ + start_transfer + """.
                    set final_t to """ + final_t + """. 
                    set final_burn_t to """ + final_burn_t + """.
                    set eps to 0.5.
                    set G to (6.6743) * ((10) ^ (-11)).
                    set KERBAL_MASS to (5.2915158) * (10 ^ 22).

                    function DoSafeStage{
                        wait until stage:ready.
                        stage.
                    }
                    
                    
                    function Do1stPhase {
                        lock steering to up.
                        lock throttle to 1.
                        DoSafeStage.
                            until altitude > (ALT1 - (ALT1 / 10)){
                        }
                    }
                    
                    
                    function Do2ndPhase {
                        lock throttle to 1.
                        set mysteer to heading(90, ANGL2).
                        lock steering to mysteer.
                        wait T2.
                        lock throttle to 0.
                    }
                    
                    
                    function set_sasMode {
                        UNLOCK STEERING.
                        SET NAVMODE TO "Surface".
                        WAIT 0.5.                                  // so sas has time to recognize navball change
                        SAS on.
                        SET NAVMODE TO "Orbit".
                        WAIT 1.                                       // so sas has time to recognize navball change
                        SET SASMODE TO "Prograde".
                    }
                    
                    
                    function Do3rdPhase {
                        set_sasMode.
                        wait until altitude > (apoapsis - apoapsis/83.33).
                        sas off.
                    }
                    
                    
                    function Do4thPhase {
                        set apo to apoapsis.
                        set t0 to time:seconds.
                        print t0.
                        lock steering to heading(90, 0).
                        lock throttle to 1.
                        print ((G * KERBAL_MASS) / (apo + 600000))^0.5.
                        print ship:velocity:orbit:sqrmagnitude^0.5.
                        wait until ((ship:velocity:orbit:sqrmagnitude^0.5) > (((G * KERBAL_MASS) / (apo + 600000))^0.5)).
                        lock throttle to 0.
                        unlock steering.
                        unlock throttle.
                        wait 10.
                        DoSafeStage.
                        wait 10.
                        DoSafeStage.
                        wait 2.
                        DoSafeStage.
                    }
                    
                    
                    function Do5thPhase {
                        set_sasMode.
                        wait 5.
                        lock throttle to 1.
                        wait transfer_burn.
                        lock throttle to 0.
                        unlock throttle.
                        sas off.
                    }
                    
                    
                    function Do6thPhase {
                        set_sasMode.
                        wait 1.
                        set sasMode to "Retrograde".
                        wait 5.
                        lock throttle to 1.
                        wait final_burn_t.
                        lock throttle to 0.
                        sas off.
                        unlock steering.
                        unlock throttle.
                    
                    }
                    
                    
                    function main {
                        set T to time:seconds.
                        Do1stPhase.
                        Do2ndPhase.
                        Do3rdPhase.
                        Do4thPhase.
                        WARPTO(T + start_transfer - transfer_burn).
                        until (time:seconds - T) > (start_transfer - (transfer_burn / 2)){
                            print((time:seconds - T) - (start_transfer - (transfer_burn / 2))).
                        }
                        print((time:seconds - T) - (start_transfer- (transfer_burn / 2))).
                        Do5thPhase.
                        wait 10.
                        WARPTO(T + final_t - 10).
                        until (time:seconds - T) > (final_t){
                            print((time:seconds - T) - (final_t)).
                        }
                        Do6thPhase.
                    }
                    
                    
                    print ship:velocity:orbit:sqrmagnitude^0.5.
                    until (((mun:longitude - ship:longitude) > start_angle - eps) and ((mun:longitude - ship:longitude) < start_angle + eps)) {
                        print mun:longitude - ship:longitude - start_angle.
                        wait 1.
                    }
                    main."""
    file.write(autopilot)
    file.close()


def get_autopilot_orbit(filename, START_ANGLE, start_trunsfer_t, transfer_burn, final_t, final_burn_t):
    file = open(filename, "w")
    autopilot = """
    // Програмные данные
    set transfer_burn to """ + str(toFixed(transfer_burn, 4)) +""". //время работы двигателя для переходной орбиты
    set start_angle to """ + str(toFixed(START_ANGLE, 4)) +""". // угол между местом старта и муной
    set start_transfer to """ + str(toFixed(start_trunsfer_t, 4)) +""". //Время когда кончается фаза LEO и начинается переходная орбита
    set final_t to """ + str(toFixed(final_t, 4)) +""". // полупериод переходной орбиты, время когда мы будем на пике гепотетической переходной орбиты
    set final_burn_t to """ + str(toFixed(final_burn_t, 4)) +""". //Длительность последнего маневра
    set eps to 0.5. // градус погрешности

function DoSafeStage{
    wait until stage:ready.
    stage.
}


function set_sasMode {
    UNLOCK STEERING.
    SET NAVMODE TO "Surface".
    WAIT 0.5.                                  // so sas has time to recognize navball change
    SAS on.
    SET NAVMODE TO "Orbit".
    WAIT 1.                                       // so sas has time to recognize navball change
    SET SASMODE TO "Prograde".
}


function Do5thPhase {
    set_sasMode.
    wait 5.
    lock throttle to 1.
    wait transfer_burn.
    lock throttle to 0.
    unlock throttle.
    sas off.
}


function Do6thPhase {
    set_sasMode.
    wait 1.
    set sasMode to "Retrograde".
    wait 5.
    lock throttle to 1.
    wait final_burn_t.
    lock throttle to 0.
    sas off.
    unlock steering.
    unlock throttle.

}


function main {
    set T to time:seconds.
    WARPTO(T + start_transfer - transfer_burn).
    until (time:seconds - T) > (start_transfer - (transfer_burn / 2)){
        print((time:seconds - T) - (start_transfer - (transfer_burn / 2))).
    }
    print((time:seconds - T) - (start_transfer- (transfer_burn / 2))).
    print mun:longitude - ship:longitude.
    Do5thPhase.
    wait 10.
    WARPTO(T + final_t - 10).
    until (time:seconds - T) > (final_t){
        print((time:seconds - T) - (final_t)).
    }
    Do6thPhase.
}


print ship:velocity:orbit:sqrmagnitude^0.5.
until (((mun:longitude - ship:longitude) > start_angle - eps) and ((mun:longitude - ship:longitude) < start_angle + eps)) {
    print mun:longitude - ship:longitude - start_angle.
    wait 1.
}
main.
    """
    file.write(autopilot)
    file.close()
