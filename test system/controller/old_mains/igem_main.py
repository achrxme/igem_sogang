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

    m_basic = MotionParam( lin_speed = 25, jnt_speed = 10)
    rb.motionparam(m_basic)

    pos_centri = data.get_position("pos6", 0)

    pos_pipet_thin = data.get_position("pos6", 1)
    pos_pipet_thin_for_ver = pos_pipet_thin.offset(dx = 120)

    pos_tip_remove= data.get_position("pos6", 2)

    pos_plate_sol = data.get_position("pos6", 3)
    pos_plate_sol_for_ver =  pos_plate_sol.offset(dy = -100)

    pos_pipet_thick = data.get_position("pos6", 4)

    pos_micro = data.get_position("pos6", 5)
    pos_micro_for_ver = pos_micro.offset(dx = -150)

    pos_incub = data.get_position("pos6", 6)
    pos_incub_for_ver = pos_incub.offset(dy = 200)

    off_data = {'there':[0, 0, 0], 'pipet_thin_handle':[-91.23, -5.17, -68.3], 'pipet_thick_handle':[0, 0, 0], 'pipet_thin_tip':[-43.22, -281, -25], 'pipet_thick_tip':[0,0,0], 'remove_tip':[-88.9, -281.56, 169.45],
                'above_plate_1' : [0, 0, 0], 'above_plate_2' : [0, 0, 0], 'above_plate_3' : [-262.71, -20, 0.18], 'above_PBS' : [0, 0, 0], 'above_medium' : [0,0,0], 'above_trypsin' : [-127.81, -12, -125.61], 'above_conical' : [0, 0, 0],
                'grip_plate_1' : [0, 0, 0], 'grip_plate_2' : [0, 0, 0], 'grip_plate_3' : [-214, -13.47, -35],
                'incub_closed_handle': [115, -25.41, 0], 'incub_opened_handle':[-153.05, 36.77, 0], 'incub_2nd_open':[14.66, -23.38, 125], 'incub_opened_door':[-296.7, -73.88, 125],
                'incub_plate_1' : [-13, -263, -112.07], 'incub_plate_2':[0, 0, 0], 'incub_plate_3' : [0, 0, 0]}

    posture = {'incub_ver':[-180, 90, -135], 'micro_ver' : [-56, 90, -56], 'micro_hor':[90, 0, 90], 'plate_sol_ver':[-90, 90, 180], 'plate_sol_hor':[180, 0, 90],
                'tip_remove_ver':[-74, 90, 146], 'pipet_thin_ver':[-18, 90, 162], 'pipet_thin_hor':[-85, 0 , 90], 'front_top':[180, 0, 180], 'back_top':[0,0,180]}

    grip_code = {'basic_grip' : '111', 'basic_release' : '000', 'pipet_half_grip':'001', 'pipet_release' : '010', 'pipet_hold' : '100'}
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
        
        test_hight = 50
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
                rb.sleep(1)

                if test_result == grip_test_code['success'] : break
                elif test_result == grip_test_code['fail'] :

                    print('Ops! gripper misses target !')

                    pos_test = pos_precise.offset(dz = test_hight)

                    posture_change(pos_test, 'front_top', 1)

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

        dout(16, grip_code['basic_release'])

        incub_handle_posture = posture_change(pos_incub, 'front_top', 1)

        pos_closed_handle = offset_position(incub_handle_posture, 'incub_closed_handle', 0)
        
        incub_2nd_open = offset_position(incub_handle_posture, 'incub_2nd_open', 0)
        incub_opened_door = offset_position(incub_handle_posture, 'incub_opened_handle',0)

        if mode == 'open':

            rb.move(pos_closed_handle.offset(dz = 100))

            rb.sleep(1)
            rb.line(pos_closed_handle)

            repeat_num = 14
            for i in range(1, repeat_num+1) :
                rb.move(pos_closed_handle.offset(
                    dx=-(radii*(math.cos(pi/4)-math.cos(pi/4+pi/32*i))),
                    dy=(radii*(math.sin(pi/4+pi/32*repeat_num)-math.sin(pi/4)))))
                
            pos_opened_handle = pos_closed_handle.offset(dx = -(radii*(math.cos(pi/4)-math.cos(pi/4+pi/32*repeat_num))),
                                                        dy = (radii*(math.sin(pi/4+pi/32*repeat_num)-math.sin(pi/4))))

            rb.move(pos_opened_handle)
            rb.line(pos_opened_handle.offset(dy = 20))
            rb.line(pos_opened_handle.offset(dy = 20, dz = 100))

            rb.line(pos_opened_handle.offset(dx = 250, dy = 20, dz = 100))
            rb.move(pos_opened_handle.offset(dx = 250, dy = -40, dz = 50))
            rb.move(pos_opened_handle.offset(dx = 50, dy = -80, dz = 50))

        else :
            rb.move(pos_opened_handle.offset(dx=-50, dy=-50))
            rb.line(pos_closed_handle)

        print('done')
        
    def plate_open(mode, pos_align, offset_name) :

        plate_open_posture = posture_change(pos_align, 'front_top', 1)

        target_positon = offset_position(plate_open_posture, offset_name, 0)
        if pos_align == pos_plate_sol:
            plate_cap_position = target_positon.offset(dy=-200, dz = -50)
        elif pos_align == pos_micro:
            plate_cap_position = target_positon.offset(dx=-200, dz = -50)
        else:
            print('sorry, that position is not defined')
        

        if mode == 'open' :

            grip('grip', plate_open_posture, offset_name, 1, 1, 0)
            grip('release', plate_cap_position, 'there', 1, 0, 0)
        elif mode == 'close' :
            grip('grip', plate_cap_position, 'there', 1, 1, 0)
            grip('release', plate_open_posture,offset_name,1,0,0)
        else :
            print('ERROR !')
        
        rb.move(pos_align)
    
    def cap_open(mode, solution_name) :
        rb.home()

        print('posture change')
        new_posture = posture_change(pos_plate_sol, 'front_top', 0)

        if solution_name == 'PBS':
            print('PBS mode')
            pos_solution = offset_position(new_posture, 'above_PBS', 0)
            pos_cap = pos_solution.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'TRYPSIN':
            print('trypsin mode')
            pos_solution = offset_position(new_posture, 'above_trypsin',0)
            pos_cap = pos_solution.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'CONICAL':
            print('conical tube mode')
            pos_solution = offset_position(new_posture, 'above_conical', 0)
            pos_cap = pos_solution.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'MEDIUM':
            print('medium mode')
            pos_solution = offset_position(new_posture, 'above_medium', 0)
            pos_cap = pos_solution.offset(dy=-50, dz=-50)
            repeat_time = 2

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
            hanle_out_offset = 50
            pos_pipet_tip = offset_position(pipet_posture, 'pipet_thin_tip', 0)
        elif pipet_type == 'thick':
            pipet_posture = pos_pipet_thick_ver.copy()
            pos_pipet_handle = offset_position(pipet_posture, 'pipet_thick_handle', 0)
            near_handle_offset = -50
            hanle_out_offset = -50
            pos_pipet_tip = offset_position(pipet_posture, 'pipet_thick_tip', 0)
        else:
           print('type error')

        handle_up_offset = 25


        if init_or_not == 1 :
            print('----- get the pipet -----')

            dout(16, grip_code['pipet_release'])
            rb.sleep(1)

            rb.move(pipet_posture)
            rb.move(pos_pipet_handle.offset(dx=near_handle_offset))
            rb.line(pos_pipet_handle)
            rb.line(pos_pipet_handle.offset(dz = handle_up_offset))
            rb.line(pos_pipet_handle.offset(dy = hanle_out_offset, dz = handle_up_offset))
            rb.move(pipet_posture.offset(dz = 100))

            print('----- tip -----')

            dout(16, grip_code['pipet_hold'])
            rb.sleep(1)

            rb.move(pos_pipet_tip.offset(dz = 150))
            rb.line(pos_pipet_tip)
            rb.line(pos_pipet_tip.offset(dz = 150))
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
                second_posture = pos_plate_sol_ver_above
            elif pos_fluid == pos_pipet_thick:
                second_posture = pos_pipet_thick_ver_above
            rb.move(second_posture)
                
            above_fluid = offset_position(second_posture, off_fluid, 1)
            rb.line(above_fluid.offset(dz = -105))

            rb.sleep(2)
            dout(16, grip_code['pipet_release'])
            rb.sleep(1)

            rb.line(above_fluid)
            rb.move(second_posture)

            print('----- release fluid -----')

            if pos_goal == pos_plate_sol:
                third_posture = pos_plate_sol_ver_above
            elif pos_goal == pos_pipet_thick:
                third_posture = pos_pipet_thick_ver_above
            rb.move(second_posture)
            
            above_goal = offset_position(third_posture, off_goal, 1)
            rb.line(above_goal.offset(dz=-42))

            rb.sleep(2)

            dout(16, grip_code['pipet_hold'])
            rb.sleep(1)

            rb.line(above_goal)
            rb.move(third_posture)

        if fin_or_not == 1 :

            print('----- remove tip -----')

            four_posture = pos_tip_remove_ver.copy()
            pos_del_tip = offset_position(four_posture, 'remove_tip', 0)

            rb.line(pos_del_tip.offset(dz = -40))

            dout(16, grip_code['pipet_release'])
            rb.sleep(1)

            rb.line(pos_del_tip)
            rb.line(pos_del_tip.offset(dz = -40))

            print('----- release pipet ------')

            rb.move(pipet_posture)

            rb.line(pos_pipet_handle.offset(dy = hanle_out_offset, dz = handle_up_offset))
            rb.line(pos_pipet_handle.offset(dz = handle_up_offset))
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
        rb.move(pos_pipet_thin)
        rb.move(pos_plate_sol)
        rb.move(pos_pipet_thin)

    pos_incub_ver = posture_change(pos_incub_for_ver,'incub_ver', 0)
    pos_micro_ver = posture_change(pos_micro_for_ver, 'micro_ver', 0)
    pos_micro_hor = posture_change(pos_micro, 'micro_hor', 0)
    pos_pipet_thick_ver = posture_change(pos_pipet_thick, 'plate_sol_ver', 0)
    pos_plate_sol_ver = posture_change(pos_plate_sol_for_ver, 'plate_sol_ver', 0)
    pos_plate_sol_hor = posture_change(pos_plate_sol_for_ver, 'plate_sol_hor', 0)
    pos_tip_remove_ver = posture_change(pos_tip_remove, 'tip_remove_ver', 0)
    pos_pipet_thin_ver = posture_change(pos_pipet_thin_for_ver, 'pipet_thin_ver', 0)
    pos_pipet_thin_hor = posture_change(pos_pipet_thin_for_ver, 'pipet_thin_hor', 0)
    pos_centri_hor = posture_change(pos_centri, 'pipet_thin_hor',0)

    pos_test_incub = posture_change(pos_incub, 'front_top',0)
    pos_test_micro = posture_change(pos_micro, 'front_top',0)
    pos_test_pipet_thick = posture_change(pos_pipet_thick, 'front_top',0)
    pos_test_plate_sol = posture_change(pos_plate_sol, 'front_top',0)
    pos_test_tip_remove = posture_change(pos_tip_remove, 'front_top',0)
    pos_test_pipet_thin = posture_change(pos_pipet_thin, 'front_top',0)
    pos_test_centri = posture_change(pos_centri, 'front_top',0)

    pos_incub_back_top = posture_change(pos_incub, 'front_top', 0)
    pos_pipet_thick_ver_above =  pos_pipet_thick_ver.offset(dz=250)
    pos_plate_sol_ver_above = pos_plate_sol_ver.offset(dz = 120)

    #rb.move(pos_plate_sol_ver)
    #rb.sleep(10)

    #rb.move(pos_plate_sol_ver)

    #rb.move(pos_centri)
    #rb.sleep(7)
    #rb.move(pos_incub_back_top)

    #rb.move(pos_pipet_thick_ver_above)

    rb.move(pos_plate_sol_ver)
    dout(16, grip_code['basic_release'])
    pipette_motion(pos_pipet_thick, 'above_trypsin', pos_plate_sol, 'above_plate_3', 'thin', 1, 0, 0)


    #rb.home()
    #dout(16, grip_code['basic_release'])
    #rb.sleep(1)

    #rb.sleep(5)
    #incubator_motion('open', 190)
    
    #rb.move(pos_incub_ver)

    #dout(16, grip_code['basic_release'])
    #rb.move(pos_incub_ver.offset(dx=-150, dy=-150, dz = off_data['incub_plate_1'][2]))
    #grip('grip', pos_incub_ver, 'incub_plate_1',0, 0, 0)
    #rb.line(pos_incub_ver.offset(dx=-150, dy=-150, dz = off_data['incub_plate_1'][2]))
    #rb.move(pos_incub_ver)


    

    rb.close()

if __name__ == '__main__':
        main()
