import math
import test_client

from i611_MCS import *
from i611_extend import *
from i611_io import *
from teachdata import *
from rbsys import *
from i611_common import *
from i611shm import *

pi = math.pi

z_safety = 50

off_data = {'there': [0, 0, 0], 'closed_incub_door': [0, -10, -10], 'incub_plate_1': [20, -20, -10], 'incub_plate_2': [-20, -20, -10],
            'on_micro': [10, 0, -20], 'on_plate_sol_1': [-100, 50, -20], 'to_PBS': [-30, 10, 0], 'pipet_handle_1': [10, 10, -10],
            'pipet_tip': [10, -10, -10], 'del_tip': [10, -30, 0], 'to_trypsin': [0, 10, 0], 'to_conical': [-10, 10, 0],
            'to_medium': [-20, 10, 0], 'on_plate_sol_2': [20, 0, -20], 'on_plate_sol_3': [60, 0, -20], 'pipet_handle_2': [30, 10, -10]}

posture = {'centri_ver': [-145, -90, -145], 'centri_hor': [145, 0, -90], 'suction_ver': [110, -90, -110], 'suction_hor': [90, 0, -90],
           'work_ver': [-150, -90, 110], 'work_hor': [45, 0, -90], 'plate_ver': [0, -90, -90], 'plate_hor': [0, 0, -90],
           'pipet_ver': [35, -90, -165], 'pipet_hor': [-40, 0, -90], 'micro_ver': [90, -90, 90], 'micro_hor': [-90, 0, -90],
           'incub_ver': [-70, -90, -155], 'incub_hor': [-135, 0, -90], 'plate_cap_grip': [90, 0, -180], 'order': ['rz', 'ry', 'rx']}


def main():

    rb = i611Robot()
    _BASE = Base()
    rb.open()
    IOinit(rb)

    m_basic = MotionParam(lin_speed=60, jnt_speed=20)
    rb.motionparam(m_basic)

    x_list, y_list = test_client.order_classify('get_world_pos')

    pos_centri = Position(x_list[0], y_list[0], z_safety, posture['centri_hor'][0],
                        posture['centri_hor'][1], posture['centri_hor'][2])
    pos_suction = Position(x_list[1], y_list[1], z_safety, posture['suction_hor'][0],
                           posture['suction_hor'][1], posture['suction_hor'][2])
    pos_worktable = Position(x_list[2], y_list[2], z_safety, posture['work_hor'][0],
                           posture['work_hor'][1], posture['work_hor'][2])
    pos_plate_sol = Position(x_list[3], y_list[3], z_safety, posture['plate_hor'][0],
                            posture['plate_hor'][1], posture['plate_hor'][2])
    pos_pipette = Position(x_list[4], y_list[4], z_safety, posture['pipet_hor'][0],
                            posture['pipet_hor'][1], posture['plate_hor'][2])
    pos_micro= Position(x_list[5], y_list[5], z_safety, posture['micro_hor'][0],
                           posture['micro_hor'][1], posture['micro_hor'][2])
    pos_incub = Position(x_list[6], y_list[6], z_safety, posture['incub_hor'][0],
                         posture['incub_hor'][1], posture['incub_hor'][2])

    rb.move(pos_centri)
    rb.move(pos_suction)
    rb.move(pos_worktable)

    rb.close()
                    
    
if __name__ == '__main__':
    main()
