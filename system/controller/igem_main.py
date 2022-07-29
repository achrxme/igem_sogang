import math

from i611_MCS import *
from i611_extend import *
from i611_io import *
from teachdata import *
from rbsys import *
from i611_common import *
from i611shm import *

import client

pi = math.pi

def main():
    data = Teachdata("teach_data")

    rb = i611Robot()
    _BASE = Base()
    rb.open()
    IOinit(rb)

    m_basic = MotionParam( lin_speed = 60, jnt_speed = 20 )
    rb.motionparam(m_basic)

    pos_centri = data.get_position("pos6", 0)
    pos_suction = data.get_position("pos6", 1)
    pos_worktable= data.get_position("pos6", 2)
    pos_plate_sol = data.get_position("pos6", 3)
    pos_pipette = data.get_position("pos6", 4)
    pos_micro = data.get_position("pos6", 5)
    pos_incub = data.get_position("pos6", 6)

    off_data = {'there':[0, 0, 0], 'closed_incub_door':[0,-10,-10], 'incub_plate_1':[20,-20,-10],'incub_plate_2':[-20,-20,-10],
                'on_micro': [10, 0, -20], 'on_plate_sol_1' : [-100, 50, -20], 'to_PBS' : [-30, 10, 0], 'pipet_handle_1':[10,10,-10],
                'pipet_tip' : [10,-10,-10], 'del_tip' : [10, -30, 0], 'to_trypsin' : [0, 10, 0], 'to_conical' :[-10, 10, 0],
                'to_medium': [-20, 10, 0], 'on_plate_sol_2': [20, 0, -20], 'on_plate_sol_3': [60, 0, -20], 'pipet_handle_2':[30,10,-10]}

    posture = {'centri_ver' : [-145, -90, -145], 'centri_hor' :[145, 0, -90], 'suction_ver':[110,-90,-110], 'suction_hor':[90, 0, -90],
                'work_ver' : [-150, -90, 110], 'work_hor' : [45, 0, -90], 'plate_ver' : [0, -90, -90], 'plate_hor' : [0, 0, -90],
                'pipet_ver' : [35, -90, -165], 'pipet_hor' : [-40, 0, -90], 'micro_ver' : [90, -90, 90], 'micro_hor' : [-90, 0, -90],
                'incub_ver' : [-70, -90, -155], 'incub_hor' : [-135, 0, -90], 'plate_cap_grip' : [90, 0, -180], 'order' : ['rz', 'ry', 'rx']}

    def posture_change(pos_origin, new_posture_name, move_or_not) :
        dumm_posture = pos_origin.copy()
        new_posture = dumm_posture.replace(rz=posture[new_posture_name][0], ry=posture[new_posture_name][1], rx=posture[new_posture_name][2])

        if move_or_not == 1 :
            rb.move(new_posture)
        return new_posture
    
    def offset_position(pos_origin, offset_name, move_or_not) :
        new_position = pos_origin.offset(dx=off_data[offset_name][0], dy=off_data[offset_name][1], dz=off_data[offset_name][2])

        if move_or_not == 1 :
            rb.move(new_position)
        return new_position
    
    def grip(mode, pos_align, offset_name, return_or_not, test_or_not, special) :
        pos_precise = offset_position(pos_align,offset_name,0)
        while(1) :
            rb.move(pos_precise)
            
            if mode == 'grip' :
                print('grip something')
                test_result = client.order_classify('grip_test')
                rb.sleep(0.5)
            elif mode == 'release' :
                print('release something')
                rb.sleep(0.5)
            else : print('ERROR !')

            if return_or_not == 1 :
                rb.move(pos_align)
            
            if test_or_not == 0 : break
            else :
                if test_result == 'success' : break
                elif test_result == 'fail' :
                    print('Ops! gripper misses target !')

                    pre_dx, pre_dy = client.order_classify('get_pos')
                    print('position is adjusted by')
                    print(pre_dx)
                    print(pre_dy)
                    
                    pos_precise = pos_precise.offset(dx=pre_dx, dy=pre_dy)
                    rb.move(pos_align)
                else : print('ERROR !')
            
        if special and pos_align == pos_micro :
            rb.move(pos_precise.offset(dx = -50))
            print('close the gripper')
            rb.line(pos_precise.offset(dx = 20))
            rb.line(pos_precise.offset(dx = -50))



    def incubator_motion(mode, radii) :

        posture_change(pos_incub,'incub_hor',1)

        pos_closed_door = offset_position(pos_incub, 'closed_incub_door',0)
        pos_opened_door = pos_closed_door.offset(dx = -radii*1.4142)

        if mode == 'open' :
            grip('grip',pos_closed_door,'there', 0, 0, 0)
            for i in range(1,9) :
                rb.move(pos_closed_door.offset(
                    dx=-(radii*(math.cos(pi/4)-math.cos(pi/4+pi/16*i))),
                    dy=(radii*(math.sin(pi/4+pi/16*i)-math.sin(pi/4)))
                ))
            rb.move(pos_opened_door)
            grip('release', pos_opened_door,'there',0,0,0)

            rb.line(pos_opened_door.offset(dz=300))
            rb.line(pos_closed_door.offset(dz=150))
            rb.move(pos_closed_door)
        else :
            rb.line(pos_closed_door.offset(dz=150))
            rb.line(pos_opened_door.offset(dz=300))
            rb.move(pos_opened_door.offset(dx = -30, dy = 30, dz = 50))
            rb.line(pos_opened_door.offset(dx = -30, dy = - 100))
            rb.line(pos_closed_door)
        
        rb.move(pos_incub)

    def plate_open(mode, pos_align, offset_name) :

        rb.move(pos_align)
        target_positon = offset_position(pos_align,offset_name,0)
        if pos_align == pos_plate_sol:
            plate_cap_position = target_positon.offset(dy=-200)
        elif pos_align == pos_micro:
            plate_cap_position = target_positon.offset(dx=-200)
        else:
            print('sorry, that position is not defined')

        if mode == 'open' :
            grip('grip', pos_align, offset_name, 1, 1, 0)
            grip('release', plate_cap_position, 'there', 1, 0, 0)
        elif mode == 'close' :
            grip('grip', plate_cap_position, 'there', 1, 1, 0)
            grip('release', pos_align,offset_name,1,0,0)
        else :
            print('ERROR !')
        
        rb.move(pos_align)
    
    def cap_open(mode, solution_name) :
        rb.home()

        print('posture change')
        new_posture = posture_change(pos_plate_sol, 'plate_cap_grip', 0)

        if solution_name == 'PBS':
            print('PBS mode')
            pos_solution = offset_position(new_posture, 'to_PBS', 0)
            pos_cap = pos_solution.offset(dy=-20, dz=-20)
            repeat_time = 2
        elif solution_name == 'TRYPSIN':
            print('trypsin mode')
            pos_solution = offset_position(new_posture, 'to_trypsin',0)
            pos_cap = pos_solution.offset(dy=-20, dz=-10)
            repeat_time = 1
        elif solution_name == 'CONICAL':
            print('conical tube mode')
            pos_solution = offset_position(new_posture, 'to_conical', 0)
            pos_cap = pos_solution.offset(dy=-20, dz=-15)
            repeat_time = 1
        elif solution_name == 'MEDIUM':
            print('medium mode')
            pos_solution = offset_position(new_posture, 'to_medium', 0)
            pos_cap = pos_solution.offset(dy=-20, dz=-15)
            repeat_time = 1

        joint_solution = rb.Position2Joint(pos_solution)

        if mode == 'open':
            rb.move(pos_solution)
            for i in range(repeat_time):
                print('raw grip')
                rb.move(joint_solution.offset(dj6=0))
                rb.move(joint_solution.offset(dj6=175))
                print('raw release')
                rb.move(joint_solution.offset(dj6=-170))
                print('raw grip')
                rb.move(joint_solution.offset(dj6=0))
                print('raw release')
            print('raw grip')
            rb.move(pos_solution.offset(dz=30))
            grip('release', pos_cap, 'there', 0, 0, 0)
            rb.line(pos_cap.offset(dz=20))
        
        if mode == 'close':
            grip('grip',pos_cap, 'there',0,0,0)
            rb.move(pos_solution.offset(dz=20))
            rb.line(pos_solution.offset(dz=5))
            for i in range(repeat_time) :
                print('raw grip')
                rb.move(joint_solution.offset(0))
                rb.move(joint_solution.offset(dj6=-175))
                print('raw release')
                rb.move(joint_solution.offset(dj6=170))
                print('raw grip')
                rb.move(joint_solution.offset(dj6=0))
                print('raw release')
            rb.line(pos_solution.offset(dz=20))

        rb.home()

    def pipette_motion(pos_fluid, off_fluid, pos_goal, off_goal, pipet_type, init_or_not, mid_or_not, fin_or_not):
        pipet_posture = posture_change(pos_pipette, 'pipet_ver', 0)
        pos_pipet_handle = offset_position(pipet_posture, 'pipet_handle_1', 0)
        if pipet_type == '1000ml':
            pos_pipet_handle = offset_position(pipet_posture, 'pipet_handle_2', 0)
        
        if init_or_not == 1 :
            print('----- get the pipet -----')

            rb.move(pipet_posture)
            rb.move(pos_pipet_handle.offset(dx=-5))
            rb.line(pos_pipet_handle)
            rb.line(pos_pipet_handle.offset(dz = 10))

            print('----- tip -----')
            pos_pipet_tip = offset_position(pipet_posture, 'pipet_tip', 1)
            off_data['pipet_tip'][0] += 30
            rb.line(pos_pipet_tip.offset(dz = -10))
            rb.line(pos_pipet_tip)
        if mid_or_not == 1:
            rb.move(pipet_posture)
            print('hold the pipette, half')

            print('----- suck up the fluid -----')
            if pos_fluid == pos_plate_sol :
                second_posture = posture_change(pos_fluid,'plate_ver',1)
            elif pos_fluid == pos_worktable :
                second_posture = posture_change(pos_fluid, 'work_ver',1)
            above_fluid = offset_position(second_posture, off_fluid, 1)
            rb.line(above_fluid.offset(dz = -5))
            print('unhold the pipette')
            rb.line(above_fluid.offset(dz = 20))
            rb.move(second_posture)

            print('----- release fluid -----')
            if pos_goal == pos_plate_sol : 
                third_posture = posture_change(pos_goal, 'plate_ver', 1)
            elif pos_goal == pos_worktable :
                third_posture = posture_change(pos_goal, 'plate_ver', 1)
            above_goal = offset_position(third_posture, off_goal, 1)
            rb.line(above_goal.offset(dz=-5))
            print('fully hold the pipette')
            rb.line(above_goal.offset(dz= 20))
            rb.move(third_posture)

        if fin_or_not == 1 :

            print('----- remove tip -----')

            four_posture = posture_change(pos_worktable, 'work_ver', 1)
            pos_del_tip = offset_position(four_posture, 'del_tip', 1)
            rb.line(pos_del_tip.offset(dz = 20))
            rb.line(pos_del_tip)
            rb.move(pipet_posture)

            print('----- release pipet ------')
            rb.move(pos_pipet_handle.offset(dz=20))
            rb.line(pos_pipet_handle)
            rb.line(pos_pipet_handle.offset(dx=-10))

            rb.move(pos_pipette)

    def pipette_mix(mix_base, offset_name, repeat, amplitude):
        pos_mix_1 = offset_position(mix_base, offset_name, 0)
        pos_mix_2 = pos_mix_1.offset(dy=amplitude, dz = -0.5*amplitude)
        for i in range(repeat) :
            print('hold the pipette, half')
            rb.move(pos_mix_1)
            print('unhold the pipette')
            rb.move(pos_mix_2)
            print('fully hold the pipette')

        rb.move(mix_base)

    def mix(mix_base, repeat, amplitude):
        mix_left = mix_base.offset(dx = amplitude/2)
        mix_right = mix_base.offset(dx = -amplitude/2)
        mix_front = mix_base.offset(dy = amplitude/2)
        mix_back = mix_base.offset(dy = -amplitude/2)
        rb.move(mix_base)

        m_mix = MotionParam(jnt_speed = 20)
        rb.motionparam(m_mix)

        for i in range(repeat) :
            rb.move(mix_left)
            rb.move(mix_right)
        
        rb.move(mix_base)
        
        for i in range(repeat) :
            rb.move(mix_front)
            rb.move(mix_back)

        rb.motionparam(m_basic)
        
        rb.move(mix_base)

    def suction():
        print('----suction motion----')
        rb.move(pos_suction)
        rb.move(pos_plate_sol)
        rb.move(pos_suction)

    pos_incub_ver = posture_change(pos_incub,'incub_ver', 0)
    pos_micro_ver = posture_change(pos_micro, 'micro_ver', 0)
    pos_plate_sol_ver = posture_change(pos_plate_sol, 'plate_ver',0)

    rb.home()
    
    
    print('============= opencv test  ==============')

    grip('grip',pos_plate_sol,'there',0,1,0)

    rb.close()

if __name__ == '__main__':
        main()
