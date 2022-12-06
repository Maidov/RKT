from matplotlib import pyplot as plt
from CustomLibs import Rows_Lib as row
import math



# ---> Physical constants
DELTA_T = 0.01
PHASE_3_GOAL = 80000
EPSILON = 50
TRANSFER_APO = row.KSP.MOON_RADIUS - row.KSP.MOON_SELF_RADIUS - 1_000_000
# ---> Technical parametrs
LAUNCH_PAD = {"latitude": - (0),
              "longitude": - (74 + 34 / 60 + 31 / (60 * 60)),
              "h": row.KSP.EARTH_RADIUS + 68
              }
LYNX_ENGINE = {"THRUST": 374.194 * 10 ** 3,
               "THRUST VACUUM": 400 * 10 ** 3,
               "BURNING RATE": 131.531,
               "IMPULSE VACUUM": 370
               }
TERRIER_ENGINE = {"THRUST VACUUM": 60 * 10 ** 3,
                  "BURNING RATE": 17.728,
                  "IMPULSE VACUUM": 345
                  }
PRI_MAT_01 = {"HEIGHT": 13.6,
              "WIDTH": 2.4,
              "LENGTH": 2.4,
              "FIRST STAGE": {"ENGINE": LYNX_ENGINE,
                              "FUEL MASS": 15_700,
                              "START MASS": 22_230},
              "SECOND STAGE": {"ENGINE": TERRIER_ENGINE,
                               "FUEL MASS": 640,
                               "START MASS": 1_970
                               }
              }
##################################################################
#####                 ИСПОЛНЯЕМАЯ ЧАСТЬ                      #####
##################################################################
def get_autopilot_and_staff(HIGH_PHASE_1, PHASE_2_THRUST_ANGLE, PHASE_2_DURATION, FREE_MOD=True, DRAW=True, ORBIT_START=False):
    if not(ORBIT_START):
        phase_1_data = row.launch_p1(h0=LAUNCH_PAD["h"],
                                     h_purpose=row.KSP.EARTH_RADIUS + HIGH_PHASE_1,
                                     launch_latitude=LAUNCH_PAD["latitude"],
                                     launch_longitude=LAUNCH_PAD["longitude"],
                                     color="red",
                                     THRUST=PRI_MAT_01["FIRST STAGE"]["ENGINE"]["THRUST"],
                                     START_MASS=PRI_MAT_01["FIRST STAGE"]["START MASS"],
                                     BURN_RATE=PRI_MAT_01["FIRST STAGE"]["ENGINE"]["BURNING RATE"],
                                     deltaT=DELTA_T,
                                     FUEL_MASS=PRI_MAT_01["FIRST STAGE"]["FUEL MASS"],
                                     DRAW=DRAW)
        phase_1_results = phase_1_data[-1]
        phase_2_data = row.launch_p2(phase_1_h=phase_1_results["current_h"],
                                     phase_1_V_R=phase_1_results["V_R_n"],
                                     phase_1_V_C=phase_1_results["V_C_n"],
                                     phase_1_lat=phase_1_results["current_lat"],
                                     phase_1_long=phase_1_results["current_long"],
                                     phase_1_MF=phase_1_results["MASS"],
                                     R=PRI_MAT_01["FIRST STAGE"]["ENGINE"]["THRUST"],
                                     BURN_RATE=PRI_MAT_01["FIRST STAGE"]["ENGINE"]["BURNING RATE"],
                                     thrust_angle=PHASE_2_THRUST_ANGLE,
                                     Duration=PHASE_2_DURATION,
                                     deltaT=DELTA_T,
                                     color="blue",
                                     FUEL_MASS=phase_1_results["FUEL_MASS"],
                                     DRAW=DRAW,
                                     SPACESHIP=PRI_MAT_01,
                                     absT=phase_1_results["absT"])
        phase_2_results = phase_2_data[-1]
        phase_3_data = row.launch_p3(phase_2_h=phase_2_results["current_h"],
                                     phase_2_V_R=phase_2_results["V_R_n"],
                                     phase_2_V_C=phase_2_results["V_C_n"],
                                     phase_2_lat=phase_2_results["current_lat"],
                                     phase_2_long=phase_2_results["current_long"],
                                     phase_2_MF=phase_2_results["MASS"],
                                     deltaT=DELTA_T,
                                     FUEL_MASS=phase_2_results["FUEL_MASS"],
                                     DRAW=DRAW,
                                     color="orange",
                                     absT=phase_2_results["absT"],
                                     GOAL=PHASE_3_GOAL,
                                     EPSILON=EPSILON,
                                     FREE_MOD=FREE_MOD)
        phase_3_results = phase_3_data[-1]
        phase_4_data = row.launch_p4(V0=phase_3_results["V_C_n"],
                                     absT=phase_3_results["absT"],
                                     lat_0=phase_3_results["current_lat"],
                                     long_0=phase_3_results["current_long"],
                                     R=phase_3_results["current_h"],
                                     M0=phase_3_results["MASS"],
                                     FUEL_MASS=phase_3_results["FUEL_MASS"],
                                     I=PRI_MAT_01["FIRST STAGE"]["ENGINE"]["IMPULSE VACUUM"],
                                     BURNING_RATE=PRI_MAT_01["FIRST STAGE"]["ENGINE"]["BURNING RATE"],
                                     deltaT=DELTA_T,
                                     color="pink",
                                     DRAW=DRAW)
        phase_4_results = phase_4_data[-1]
        LEO_data = row.LEO(R=phase_4_results["R"],
                           long_0=phase_4_results["current_long"],
                           lat_0=phase_4_results["current_lat"],
                           Duration=phase_4_results["period"] / 2,
                           deltaT=DELTA_T,
                           orbitalV=phase_4_results["orbitalV"],
                           absT=phase_4_results["absT"],
                           M0=phase_4_results["MASS"],
                           FUEL_MASS=phase_4_results["FUEL_MASS"],
                           color="red",
                           DRAW=DRAW,
                           period=phase_4_results["period"]
                           )
        LEO_result = LEO_data[-1]
        burn_Hohmann_transfer_data = row.burn_Hohmann_Transfer(apo_R=TRANSFER_APO,
                                                               pere_R=LEO_result["current_h"],
                                                               V0=LEO_result["orbitalV"],
                                                               long_0=LEO_result["current_long"],
                                                               lat_0=LEO_result["current_lat"],
                                                               I=PRI_MAT_01["SECOND STAGE"]["ENGINE"]["IMPULSE VACUUM"],
                                                               BURNING_RATE=PRI_MAT_01["SECOND STAGE"]["ENGINE"][
                                                                   "BURNING RATE"],
                                                               deltaT=DELTA_T,
                                                               absT=LEO_result["absT"],
                                                               DRAW=DRAW,
                                                               color="pink",
                                                               FUEL_MASS=PRI_MAT_01["SECOND STAGE"]["FUEL MASS"],
                                                               M0=PRI_MAT_01["SECOND STAGE"]["START MASS"],
                                                               quality=100)
        burn_Hohmann_transfer_result = burn_Hohmann_transfer_data[-1]
        hypothetically_Hohmann_transfer_data = row.Hohmann_Transfer(pere_R=burn_Hohmann_transfer_result["pere_R"],
                                                                    apo_R=burn_Hohmann_transfer_result["apo_R"],
                                                                    long_0=LEO_result["current_long"],
                                                                    lat_0=burn_Hohmann_transfer_result["current_lat"],
                                                                    M0=burn_Hohmann_transfer_result["MASS"],
                                                                    FUEL_MASS=burn_Hohmann_transfer_result["FUEL_MASS"],
                                                                    deltaT=DELTA_T,
                                                                    absT=burn_Hohmann_transfer_result["absT"],
                                                                    DRAW=DRAW,
                                                                    color="blue",
                                                                    quality=1,
                                                                    Duration=burn_Hohmann_transfer_result["period"] / 2 -
                                                                             burn_Hohmann_transfer_result["T"],
                                                                    T0=burn_Hohmann_transfer_result["T"])
        hypothetically_Hohmann_transfer_result = hypothetically_Hohmann_transfer_data[-1]

        ABS_T = hypothetically_Hohmann_transfer_result["absT"]
        MOON_START_POSITION = hypothetically_Hohmann_transfer_result["current_long"] - ABS_T * ((360 * row.KSP.MOON_V) / (2 * math.pi * row.KSP.MOON_RADIUS))
        START_ANGLE = (MOON_START_POSITION - LAUNCH_PAD["longitude"] - 360)

        final_burn = row.afterburner(M0=hypothetically_Hohmann_transfer_result["MASS"],
                                     I=PRI_MAT_01["SECOND STAGE"]["ENGINE"]["IMPULSE VACUUM"],
                                     BURNING_RATE=PRI_MAT_01["SECOND STAGE"]["ENGINE"]["BURNING RATE"],
                                     needed_deltaV=hypothetically_Hohmann_transfer_result["orbitalV"])

        row.RSF.get_autopilot_full("autopilot_full.ks", HIGH_PHASE_1, PHASE_2_DURATION, PHASE_2_THRUST_ANGLE,burn_Hohmann_transfer_result["T"], START_ANGLE, LEO_result["absT"], hypothetically_Hohmann_transfer_result["absT"], final_burn)

        print(row.RSF.formalize_data(phase_1_results, "PHASE 1"))
        print(row.RSF.formalize_data(phase_2_results, "PHASE 2"))
        print(row.RSF.formalize_data(phase_3_results, "PHASE 3"))
        print(row.RSF.formalize_data(phase_4_results, "PHASE 4"))
        print(row.RSF.formalize_data(LEO_result, "LEO"))
        print(row.RSF.formalize_data(burn_Hohmann_transfer_result, "Hohmann burn"))
        print(row.RSF.formalize_data(hypothetically_Hohmann_transfer_result, "Hohmann transfer"))

        flight = [phase_1_data, phase_2_data, phase_3_data, phase_4_data]
        table = row.RSF.get_table("absT", ["V_n", "V_R_n", "V_C_n"], flight)
        my_file = open("table.txt", "w")
        my_file.write(table)
        my_file.close()
    else:
        R = row.KSP.EARTH_RADIUS + HIGH_PHASE_1
        LONG_0 = PHASE_2_THRUST_ANGLE
        V = ((row.KSP.KERBAL_MASS * row.KSP.G) / R) ** 0.5
        period = (2 * math.pi * R) / V
        LEO_data = row.LEO(R=R,
                           long_0=LONG_0,
                           lat_0=LAUNCH_PAD["latitude"],
                           Duration=period / 2,
                           deltaT=DELTA_T,
                           orbitalV=V,
                           absT=0,
                           M0=PRI_MAT_01["FIRST STAGE"]["START MASS"],
                           FUEL_MASS=PRI_MAT_01["FIRST STAGE"]["FUEL MASS"],
                           color="red",
                           DRAW=DRAW,
                           period=period
                           )
        LEO_result = LEO_data[-1]
        burn_Hohmann_transfer_data = row.burn_Hohmann_Transfer(apo_R=TRANSFER_APO,
                                                               pere_R=LEO_result["current_h"],
                                                               V0=LEO_result["orbitalV"],
                                                               long_0=LEO_result["current_long"],
                                                               lat_0=LEO_result["current_lat"],
                                                               I=PRI_MAT_01["SECOND STAGE"]["ENGINE"]["IMPULSE VACUUM"],
                                                               BURNING_RATE=PRI_MAT_01["SECOND STAGE"]["ENGINE"][
                                                                   "BURNING RATE"],
                                                               deltaT=DELTA_T,
                                                               absT=LEO_result["absT"],
                                                               DRAW=DRAW,
                                                               color="pink",
                                                               FUEL_MASS=PRI_MAT_01["SECOND STAGE"]["FUEL MASS"],
                                                               M0=PRI_MAT_01["SECOND STAGE"]["START MASS"],
                                                               quality=100)
        burn_Hohmann_transfer_result = burn_Hohmann_transfer_data[-1]
        hypothetically_Hohmann_transfer_data = row.Hohmann_Transfer(pere_R=burn_Hohmann_transfer_result["pere_R"],
                                                                    apo_R=burn_Hohmann_transfer_result["apo_R"],
                                                                    long_0=LEO_result["current_long"],
                                                                    lat_0=burn_Hohmann_transfer_result["current_lat"],
                                                                    M0=burn_Hohmann_transfer_result["MASS"],
                                                                    FUEL_MASS=burn_Hohmann_transfer_result["FUEL_MASS"],
                                                                    deltaT=DELTA_T,
                                                                    absT=burn_Hohmann_transfer_result["absT"],
                                                                    DRAW=DRAW,
                                                                    color="blue",
                                                                    quality=1,
                                                                    Duration=burn_Hohmann_transfer_result["period"] / 2 -
                                                                             burn_Hohmann_transfer_result["T"],
                                                                    T0=burn_Hohmann_transfer_result["T"])
        hypothetically_Hohmann_transfer_result = hypothetically_Hohmann_transfer_data[-1]

        ABS_T = hypothetically_Hohmann_transfer_result["absT"]
        MOON_START_POSITION = hypothetically_Hohmann_transfer_result["current_long"] - ABS_T * ((360 * row.KSP.MOON_V) / (2 * math.pi * row.KSP.MOON_RADIUS))
        START_ANGLE = (MOON_START_POSITION - LONG_0 - 360)
        final_burn = row.afterburner(M0=hypothetically_Hohmann_transfer_result["MASS"],
                                     I=PRI_MAT_01["SECOND STAGE"]["ENGINE"]["IMPULSE VACUUM"],
                                     BURNING_RATE=PRI_MAT_01["SECOND STAGE"]["ENGINE"]["BURNING RATE"],
                                     needed_deltaV=hypothetically_Hohmann_transfer_result["orbitalV"])


        print(row.RSF.formalize_data(LEO_result, "LEO"))
        print(row.RSF.formalize_data(burn_Hohmann_transfer_result, "Hohmann burn"))
        print(row.RSF.formalize_data(hypothetically_Hohmann_transfer_result, "Hohmann transfer"))
        row.RSF.get_autopilot_orbit("autopilot_orbit.ks", START_ANGLE, LEO_result["absT"], burn_Hohmann_transfer_result["T"], hypothetically_Hohmann_transfer_result["absT"], final_burn)
    if DRAW:
        row.get_earth(x0=0,
                      y0=0,
                      z0=0,
                      R=row.KSP.EARTH_RADIUS - row.KSP.EARTH_RADIUS / 20,
                      layers=15j)
        row.get_moon_trace(absT=ABS_T,
                           deltaT=DELTA_T,
                           alfa=MOON_START_POSITION,
                           R=row.KSP.MOON_RADIUS,
                           self_R=row.KSP.MOON_SELF_RADIUS,
                           SOI=row.KSP.MOON_SOI_RADIUS,
                           SOI_DISPLAY=True,
                           color="white"
                           )
        row.get_area()
        row.get_decard(row.MAX)
        plt.axis('off')
        plt.show()
