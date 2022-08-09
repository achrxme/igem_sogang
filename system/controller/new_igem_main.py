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

    m_basic = MotionParam( lin_speed = 50, jnt_speed = 12 )
    rb.motionparam(m_basic)

    pos_centri = data.get_position("pos6", 0)
    pos_pipet_thin_origin = data.get_position("pos6", 1)
    pos_pipet_thin = pos_pipet_thin_origin.offset(dx = 120)

    pos_tip_remove= data.get_position("pos6", 2)
    pos_plate_sol = data.get_position("pos6", 3)
    pos_pipet_thick = data.get_position("pos6", 4)
    pos_micro = data.get_position("pos6", 5)
    pos_incub = data.get_position("pos6", 6)

    off_data = {'there':[0, 0, 0], 'pipet_thin_handle':[-92.76, -12.26, -56.6], 'pipet_thick_handle':[0, 0, 0], 'pipet_thin_tip':[-22.7, -279.11, -24.78], 'pipet_thick_tip':[0, 0, 0], 'del_tip':[0, 0, 0]}

    posture = {'incub_ver':[-180, 90, -120], 'micro_ver' : [-56, 90, -56], 'micro_hor':[90, 0, 90], 'plate_sol_ver':[-90, 90, 180], 'plate_sol_hor':[180, 0, 90],
                'tip_remove_ver':[-74, 90, 146], 'pipet_thin_ver':[-18, 90, 162], 'pipet_thin_hor':[-85, 0 , 90], 'front_top':[180, 0, 180], 'back_top':[0,0,180]}

    grip_code = {'basic_grip' : '111', 'basic_release' : '000', 'pipet_half_grip':'001',
                    'pipet_release' : '010', 'pipet_hold' : '100'}
    grip_test_code = {'success' : '1', 'fail' : '0'}

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
                dout(16, grip_code['basic_grip'])
                rb.sleep(2)
            elif mode == 'release' :
                dout(16, grip_code['basic_release'])
                rb.sleep(2)
            else : print('ERROR !')

            if test_or_not == 0 : break
            else :
                rb.move(pos_align)
                test_result = din(0)
                rb.sleep(0.5)
                if test_result == grip_test_code['success'] : break
                elif test_result == grip_test_code['fail'] :

                    print('Ops! gripper misses target !')

                    pre_dx, pre_dy = client.order_classify('get_pos')

                    pos_precise = pos_precise.offset(dx=pre_dx, dy=pre_dy)
                    rb.move(pos_align)
                else : print('ERROR !')

        if return_or_not == 1:
            rb.move(pos_align)
           
        if special and pos_align == pos_micro :
            rb.move(pos_precise.offset(dx = -50))
            print('close the gripper')
            rb.line(pos_precise.offset(dx = 20))
            rb.line(pos_precise.offset(dx = -50))

    def incubator_motion(mode, radii) :

        new_incub = posture_change(pos_incub,'incub_grip',1)

        pos_closed_door = offset_position(new_incub, 'closed_incub_door',0)
        pos_opened_door = pos_closed_door.offset(dx = -radii*1.4142)

        if mode == 'open' :
            for i in range(1,9) :
                rb.move(pos_closed_door.offset(
                    dx=-(radii*(math.cos(pi/4)-math.cos(pi/4+pi/16*i))),
                    dy=(radii*(math.sin(pi/4+pi/16*i)-math.sin(pi/4)))
                ))
            rb.move(pos_opened_door)

            rb.line(pos_opened_door.offset(dz=50))
            rb.move(pos_closed_door)
        else :
            rb.move(pos_opened_door.offset(dx=-50, dy=-50))
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
                dout(16, grip_code['basic_grip'])
                rb.sleep(1)
                rb.move(joint_solution.offset(dj6=0))
                rb.move(joint_solution.offset(dj6=175))
                dout(16, grip_code['basic_release'])
                rb.sleep(1)
                rb.move(joint_solution.offset(dj6=-170))
                dout(16, grip_code['basic_grip'])
                rb.sleep(1)
                rb.move(joint_solution.offset(dj6=0))
                dout(16, grip_code['basic_release'])
                rb.sleep(1)

            dout(16, grip_code['basic_grip'])
            rb.sleep(1)

            rb.move(pos_solution.offset(dz=30))
            grip('release', pos_cap, 'there', 0, 0, 0)
            rb.line(pos_cap.offset(dz=20))
        
        if mode == 'close':
            grip('grip',pos_cap, 'there',0,0,0)
            rb.move(pos_solution.offset(dz=20))
            rb.line(pos_solution.offset(dz=5))
            for i in range(repeat_time) :
                dout(16, grip_code['basic_grip'])
                rb.sleep(1)
                rb.move(joint_solution.offset(0))
                rb.move(joint_solution.offset(dj6=-175))
                dout(16, grip_code['basic_release'])
                rb.sleep(1)
                rb.move(joint_solution.offset(dj6=170))
                dout(16, grip_code['basic_grip'])
                rb.sleep(1)
                rb.move(joint_solution.offset(dj6=0))
                dout(16, grip_code['basic_release'])
                rb.sleep(1)
            rb.line(pos_solution.offset(dz=20))

        rb.home()

    def pipette_motion(pos_fluid, off_fluid, pos_goal, off_goal, pipet_type, init_or_not, mid_or_not, fin_or_not):

        if pipet_type == 'thin':
            pipet_posture = pos_pipet_thin_ver.copy()
            pos_pipet_handle = offset_position(pipet_posture, 'pipet_thin_handle', 0)
            near_handle_offset = 50
            pos_pipet_tip = offset_position(pipet_posture, 'pipet_thin_tip', 0)
        elif pipet_type == 'thick':
            pipet_posture = pos_pipet_thick_ver.copy()
            pos_pipet_handle = offset_position(pipet_posture, 'pipet_thick_handle', 0)
            near_handle_offset = -50
            pos_pipet_tip = offset_position(pipet_posture, 'pipet_thick_tip', 0)
        else:
           print('type error')


        if init_or_not == 1 :
            print('----- get the pipet -----')

            rb.move(pipet_posture)
            rb.move(pos_pipet_handle.offset(dx=near_handle_offset))
            rb.line(pos_pipet_handle)
            rb.line(pos_pipet_handle.offset(dz = 20))
            rb.line(pos_pipet_handle.offset(dy = 30, dz = 20))
            rb.move(pipet_posture)

            print('----- tip -----')

            rb.move(pos_pipet_tip.offset(dz = 120))
            rb.line(pos_pipet_tip)
            rb.line(pos_pipet_tip.offset(dz = 120))
            rb.move(pipet_posture)

            if pipet_type == 'thin':
                off_data['pipet_thin_tip'][1] -= 9
            elif pipet_type == 'thick':
                off_data['pipet_thick_tip'][1] -= 18

        if mid_or_not == 1:
            
            print('----- half grip pipet -----')
            dout(16, grip_code['pipet_half_grip'])
            rb.sleep(1)

            print('----- suck up the fluid -----')
            if pos_fluid == pos_plate_sol:
                second_posture = posture_change(pos_plate_sol, 'plate_sol_ver',1)
            elif pos_fluid == pos_pipet_thick:
                second_posture = posture_change(pos_pipet_thick, 'micro_ver',1)
                
            above_fluid = offset_position(second_posture, off_fluid, 1)
            rb.line(above_fluid.offset(dz = -5))

            dout(16, grip_code['pipet_release'])
            rb.sleep(1)

            rb.line(above_fluid.offset(dz = 20))
            rb.move(second_posture)

            print('----- release fluid -----')

            if pos_goal == pos_plate_sol:
                third_posture = posture_change(pos_plate_sol, 'plate_sol_ver',1)
            elif pos_goal == pos_pipet_thick:
                third_posture = posture_change(pos_pipet_thick, 'micro_ver',1)
            
            above_goal = offset_position(third_posture, off_goal, 1)
            rb.line(above_goal.offset(dz=-5))

            dout(16, grip_code['pipet_hold'])
            rb.sleep(1)

            rb.line(above_goal.offset(dz= 20))
            rb.move(third_posture)

        if fin_or_not == 1 :

            print('----- remove tip -----')

            four_posture = pos_tip_remove_ver.copy()
            pos_del_tip = offset_position(four_posture, 'del_tip', 0)
            rb.line(pos_del_tip.offset(dz = -20))
            rb.line(pos_del_tip)
            rb.line(pos_del_tip.offset(dz = -20))

            print('----- release pipet ------')

            rb.move(pipet_posture)
            
            rb.line(pos_pipet_handle.offset(dy=30, dz=20))
            rb.line(pos_pipet_handle)
            rb.line(pos_pipet_handle.offset(dz=20))
            

            rb.line(pos_pipet_handle.offset(dy = 10))
            rb.line(pos_pipet_handle.offset(dz = 10))
            rb.line(pos_pipet_handle)
            rb.move(pos_pipet_handle.offset(dx=near_handle_offset))

            rb.move(pipet_posture)

    def pipette_mix(mix_base, offset_name, repeat, amplitude):
        pos_mix_1 = offset_position(mix_base, offset_name, 0)
        pos_mix_2 = pos_mix_1.offset(dy=amplitude, dz = -0.5*amplitude)

        for i in range(repeat) :
            rb.move(mix_base)
            dout(16, grip_code['pipet_half_grip'])
            rb.sleep(1)
            rb.move(pos_mix_1)
            dout(16, grip_code['pipet_release'])
            rb.sleep(1)
            rb.move(pos_mix_2)
            dout(16, grip_code['pipet_hold'])
            rb.sleep(1)

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
    pos_micro_hor = posture_change(pos_micro, 'micro_hor', 0)
    pos_pipet_thick_ver = posture_change(pos_pipet_thick, 'micro_ver', 0)
    pos_plate_sol_ver = posture_change(pos_plate_sol, 'plate_sol_ver', 0)
    pos_plate_sol_hor = posture_change(pos_plate_sol, 'plate_sol_hor', 0)
    pos_tip_remove_ver = posture_change(pos_tip_remove, 'tip_remove_ver', 0)
    pos_pipet_thin_ver = posture_change(pos_pipet_thin, 'pipet_thin_ver', 0)
    pos_pipet_thin_hor = posture_change(pos_pipet_thin, 'pipet_thin_hor', 0)

    pos_test_incub = posture_change(pos_incub, 'front_top',0)
    pos_test_micro = posture_change(pos_micro, 'front_top',0)
    pos_test_pipet_thick = posture_change(pos_pipet_thick, 'front_top',0)
    pos_test_plate_sol = posture_change(pos_pipet_thin, 'front_top',0)
    pos_test_tip_remove = posture_change(pos_tip_remove, 'front_top',0)
    pos_test_pipet_thin = posture_change(pos_pipet_thin, 'front_top',0)
    pos_test_centri = posture_change(pos_centri, 'front_top',0)

    rb.home()

    pipette_motion(pos_plate_sol, 'there', pos_plate_sol, 'there', 'thin',1,0,0)
    pipette_motion(pos_plate_sol, 'there', pos_plate_sol, 'there', 'thin',1,0,1)

    rb.close()

if __name__ == '__main__':
        main()
