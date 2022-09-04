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
test_height = 500


def main():
    data = Teachdata("teach_data")

    rb = i611Robot()
    _BASE = Base()
    rb.open()
    IOinit(rb)

    m_basic = MotionParam( lin_speed = 25, jnt_speed = 15)  
    rb.motionparam(m_basic)


    off_data = {'there':[0, 0, 0], 'incub_plate_1':[131.1, -95.9, 13.1], 'incub_plate_2':[131.5, -74.3, -85.9], 'incub_plate_3':[89.6, -129.1, -86.2], 'incub_closed_handle':[290.5, -57.6, 42.5],
                'pipet_thick_handle':[102, 142, -70.2], 'pipet_thick_tip':[39.9, 334, 37.2], 'pipet_thin_handle':[-110, 59, -75.7], 'pipet_thin_tip':[-40, -220, -32], 'remove_tip':[-17.8, -219.9, 55.9],
                'PBS_cap':[103.2, 203.4, 65], 'medium_cap':[4, 203.4, 58], 'conical_cap':[-96.5, 203.4, 65], 'trypsin_cap':[102.2, 104.4, 65],
                'above_PBS':[78.8,70, 20], 'above_medium':[-28, 70, 20], 'above_conical':[-121.2, 70, 20], 'above_trypsin':[77.5, -39.7, -36],
                'plate_1_cap':[93.8, 287.9, 52.4], 'plate_2_cap':[-55.9, 287.9, 59], 'plate_3_cap':[-205, 287.9, 54.5],
                'grip_plate_1':[93.4, 52.5, -196.3], 'grip_plate_2':[-59.2, 57.9, -187.4], 'grip_plate_3':[-207.4, 57.9, -195.6],  
                'above_plate_1': [71.4, 48.4, -10], 'above_plate_2':[-89, 75, -10], 'above_plate_3':[-241.9, 48.4, -10],
                'before_suction_on':[-33.8, -62.5, -184.8], 'before_suction_off':[-33.8, 21.5, -166.1]
                }

    posture = {'incub_ver':[-180, 90, -135], 'pipet_thick_ver' : [-45, 90, -45], 'pipet_thick_hor':[90, 0, 90], 'plate_ver':[-90, 90, 180], 'plate_hor':[180, 0, 90],
                'tip_remove_ver':[-75, 90, 135], 'pipet_thin_ver':[0, 90, 180], 'pipet_thin_hor':[-90, 0 , 90], 'front_top':[180, 0, 180], 'back_top':[0,0,180]}

    grip_code = {'basic_grip' : '111', 'basic_release' : '000', 'pipet_half_grip':'001', 'pipet_release' : '010', 'pipet_hold' : '100', 'half_release' : '101',
                    'cap_open_grip' : '110'}
    grip_test_code = {'success' : '1', 'fail' : '0'}

    get_world_test_pos = Position(0, -500, test_height, posture['back_top'][0], posture['back_top'][1], posture['back_top'][2])

    rb.home()
    rb.move(get_world_test_pos)

    pos_x, pos_y = client.order_classify('get_world_pos')

    pos_incub_marker = Position(pos_x[0], pos_y[0], test_height, posture['front_top'][0], posture['front_top'][1], posture['front_top'][2])
    pos_pipet_thick_marker = Position(pos_x[1], pos_y[1], test_height, posture['front_top'][0], posture['front_top'][1], posture['front_top'][2])
    pos_solution_marker = Position(pos_x[2], pos_y[2], test_height, posture['front_top'][0], posture['front_top'][1], posture['front_top'][2])
    pos_plate_marker = Position(pos_x[3], pos_y[3], test_height, posture['front_top'][0], posture['front_top'][1], posture['front_top'][2])
    pos_suction_marker = Position(pos_x[4], pos_y[4], test_height, posture['front_top'][0], posture['front_top'][1], posture['front_top'][2])
    pos_pipet_thin_marker = Position(pos_x[5], pos_y[5], test_height, posture['front_top'][0], posture['front_top'][1], posture['front_top'][2])
    pos_tip_remove_marker = Position(pos_x[6], pos_y[6], test_height, posture['front_top'][0], posture['front_top'][1], posture['front_top'][2])


    def adjust_world(pos_align):

        repeat_idx = 0

        while(1):
            rb.move(pos_align)

            idx, off_x, off_y = client.order_classify('adjust_world_pos')

            print(idx, off_x, off_y)

            if abs(off_x) < 1 and abs(off_y) < 1:
                rb.home()
                break
            else :
                pos_x[idx-1] = pos_x[idx-1] + off_x
                pos_y[idx-1] = pos_y[idx-1] + off_y

                pos_align.replace(x = pos_x[idx-1], y = pos_y[idx-1])

                repeat_idx += 1
            
            if repeat_idx > 5:
                rb.home()
                break

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
    
    def grip(mode, pos_align, offset_name, approach, return_or_not, test_or_not) :
        
        test_hight = 50
        pos_precise = offset_position(pos_align,offset_name,0)

        while(1) :

            if approach == '+x' :
                rb.move(pos_precise.offset(dx = off_data[offset_name][0]-300))
                rb.line(pos_precise)
            elif approach == '-x' :
                rb.move(pos_precise.offset(dx = off_data[offset_name][0]+300))
                rb.line(pos_precise)
            elif approach == '+y' :
                rb.move(pos_precise.offset(dy = off_data[offset_name][1]-300))
                rb.line(pos_precise)
            elif approach == '-y' :
                rb.move(pos_precise.offset(dy = off_data[offset_name][1]+300))
                rb.line(pos_precise)
            elif approach == '-z':
                rb.move(pos_precise.offset(dz = off_data[offset_name][2]+20))
                rb.line(pos_precise)
            elif approach == 'incub':
                rb.move(pos_precise.offset(dx = off_data[offset_name][0]-150, dy = off_data[offset_name][1]+150))
                rb.line(pos_precise)
            else :
                rb.move(pos_precise)
            
            if mode == 'grip' :
                dout(16, grip_code['basic_grip'])
                rb.sleep(2)
            elif mode == 'release' :
                dout(16, grip_code['basic_release'])
                rb.sleep(2)
            elif mode == 'half_release':
                dout(16, grip_code['half_release'])
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
            if approach == '+x' :
                rb.line(pos_precise.offset(dx = off_data[offset_name][0]-300))
            elif approach == '-x' :
                rb.line(pos_precise.offset(dx = off_data[offset_name][0]+300))
            elif approach == '+y' :
                rb.line(pos_precise.offset(dy = off_data[offset_name][1]-300))
            elif approach == '-y' :
                rb.line(pos_precise.offset(dy = off_data[offset_name][1]+300))
            elif approach == '-z':
                rb.line(pos_precise.offset(dz = off_data[offset_name][2]+20))
            elif approach == 'incub':
                rb.line(pos_precise.offset(dx = off_data[offset_name][0]-150, dy = off_data[offset_name][1]+150))
            rb.move(pos_align)
           
    def incubator_motion(mode, radii) :

        dout(16, grip_code['basic_release'])

        incub_handle_posture = posture_change(pos_incub_base, 'front_top', 1)

        pos_closed_handle = offset_position(incub_handle_posture, 'incub_closed_handle', 0)
        

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

            rb.line(pos_opened_handle.offset(dx = 220, dy = 20, dz = 100))
            rb.move(pos_opened_handle.offset(dx = 220, dy = -40, dz = 100))
            rb.move(pos_opened_handle.offset(dx = 50, dy = -80, dz = 100))

            rb.line(pos_opened_handle.offset(dx = 50, dy = -80, dz = 200))
            rb.line(pos_opened_handle.offset(dx = 100, dy = -80, dz = 200))


        else :
            rb.move(pos_opened_handle.offset(dx=-50, dy=-50))
            rb.line(pos_closed_handle)

        print('done')
        
    def plate_open(mode, offset_name) :
        
        dout(16, grip_code['basic_release'])
        
        plate_open_posture = posture_change(pos_plate_base, 'front_top', 0)
        target_positon = offset_position(plate_open_posture, offset_name, 0)

        cap_release_position = target_positon.offset(dy=-150, dz = -120)
    
        if mode == 'open' :
            grip('grip',plate_open_posture, offset_name, '-z', 1, 0)
            grip('release', cap_release_position, 'there', '-z', 0, 0)
            rb.line(cap_release_position.offset(dz = 50))
        elif mode == 'close' :
            grip('grip', cap_release_position, 'there', '-z', 1, 0)
            grip('release',plate_open_posture, offset_name, '-z', 0, 0)
            rb.line(cap_release_position.offset(dz = 20))
        else :
            print('ERROR !')
        
        rb.move(plate_open_posture)
   
    def cap_open(mode, solution_name) :
        rb.home()

        dout(16, grip_code['basic_release'])
        rb.move(pos_solution_base)
        new_posture = posture_change(pos_solution_base, 'front_top', 1)
        rb.move(new_posture.offset(dz = 200))

        if solution_name == 'PBS':
            print('PBS mode')
            pos_solution_cap = offset_position(new_posture, 'PBS_cap', 0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'TRYPSIN':
            print('trypsin mode')
            pos_solution_cap = offset_position(new_posture, 'trypsin_cap',0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'CONICAL':
            print('conical tube mode')
            pos_solution_cap = offset_position(new_posture, 'conical_cap', 0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'MEDIUM':
            print('medium mode')
            pos_solution_cap = offset_position(new_posture, 'medium_cap', 0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 3
        
        pos_front_state_cap = posture_change(pos_solution_cap, 'front_top', 0)
        pos_back_state_cap = posture_change(pos_solution_cap, 'back_top', 0)

        if mode == 'open':
            
            rb.move(pos_front_state_cap)
            rb.sleep(10)

            dout(16, grip_code['cap_open_grip'])
 
            rb.move(pos_back_state_cap)
            rb.move(pos_front_state_cap)

            dout(16, grip_code['basic_release'])
            rb.sleep(1)
            dout(16, grip_code['basic_grip'])

            rb.move(pos_back_state_cap.offset(dz=30))

            rb.move(pos_solution_base)

            grip('release', pos_cap_release, 'there', 0, 0, 0)

            rb.line(pos_cap_release.offset(dz=100))
        
        if mode == 'close':
            grip('grip',pos_cap_release, 'there',0,0,0)
            rb.move(pos_solution_cap.offset(dz=20))
            rb.line(pos_solution_cap.offset(dz=5))
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
            rb.line(pos_solution_cap.offset(dz=20))

        rb.home()

    def cap_open_3(mode, solution_name) :
        rb.home()

        dout(16, grip_code['basic_release'])
        rb.move(pos_solution_base)
        new_posture = posture_change(pos_solution_base, 'front_top', 1)
        rb.move(new_posture.offset(dz = 200))

        if solution_name == 'PBS':
            print('PBS mode')
            pos_solution_cap = offset_position(new_posture, 'PBS_cap', 0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'TRYPSIN':
            print('trypsin mode')
            pos_solution_cap = offset_position(new_posture, 'trypsin_cap',0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'CONICAL':
            print('conical tube mode')
            pos_solution_cap = offset_position(new_posture, 'conical_cap', 0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 2
        elif solution_name == 'MEDIUM':
            print('medium mode')
            pos_solution_cap = offset_position(new_posture, 'medium_cap', 0)
            pos_cap_release = pos_solution_cap.offset(dy=-50, dz=-50)
            repeat_time = 3

        joint_solution_cap = rb.Position2Joint(pos_solution_cap)
        print('before replace : ', joint_solution_cap.jnt2list())

        if mode == 'open':

            rb.move(pos_solution_cap)

            joint_solution_cap_2 = joint_solution_cap.replace(j6 = 40)
            print('after replace : ', joint_solution_cap_2.jnt2list())

            rb.move(joint_solution_cap_2)
        
        if mode == 'close':
            pass

        rb.home()

    def pipette_motion(pos_fluid, off_fluid, pos_goal, off_goal, pipet_type, init_or_not, mid_or_not, fin_or_not):

        if pipet_type == 'thin':
            pipet_posture = posture_change(pos_pipet_thin_base, 'pipet_thin_ver', 0)
            pos_pipet_handle = offset_position(pipet_posture, 'pipet_thin_handle', 0)
            near_handle_offset = 50
            hanle_out_offset = 50
            pos_pipet_tip = offset_position(pipet_posture, 'pipet_thin_tip', 0)
        elif pipet_type == 'thick':
            pipet_posture = posture_change(pos_pipet_thick_base, 'pipet_thick_ver', 0)
            pos_pipet_handle = offset_position(pipet_posture, 'pipet_thick_handle', 0)
            near_handle_offset = -50
            hanle_out_offset = -50
            pos_pipet_tip = offset_position(pipet_posture, 'pipet_thick_tip', 0)
        else:
           print('type error')

        handle_up_offset = 20


        if init_or_not == 1 :
            print('----- get the pipet -----')

            dout(16, grip_code['pipet_release'])
            rb.sleep(1)

            rb.move(pipet_posture)
            rb.move(pos_pipet_handle.offset(dx=near_handle_offset))
            rb.line(pos_pipet_handle)

            print('----- half grip pipet -----')
            dout(16, grip_code['pipet_half_grip'])
            rb.sleep(1)

            rb.line(pos_pipet_handle.offset(dz = handle_up_offset))
            rb.line(pos_pipet_handle.offset(dy = hanle_out_offset, dz = handle_up_offset))
            rb.move(pipet_posture.offset(dz = 100))


            print('----- tip -----')

            rb.move(pos_pipet_tip.offset(dz = 100))
            rb.line(pos_pipet_tip)
            rb.line(pos_pipet_tip.offset(dz = 100))
            rb.move(pipet_posture)

            if pipet_type == 'thin':
                off_data['pipet_thin_tip'][1] -= 9
            elif pipet_type == 'thick':
                off_data['pipet_thick_tip'][1] -= 18

        if mid_or_not == 1:
            

            print('----- suck up the fluid -----')
            if pos_fluid == pos_plate_higher:
                second_posture = posture_change(pos_plate_higher, 'plate_ver', 0)
            elif pos_fluid == pos_solution_higher:
                second_posture = posture_change(pos_solution_higher, 'plate_ver', 0)

            rb.home()
            rb.move(second_posture)
            
            near_above_fluid = second_posture.offset(dz = off_data[off_fluid][2])
            rb.move(near_above_fluid)
            above_fluid = offset_position(near_above_fluid, off_fluid, 1)
            rb.line(above_fluid.offset(dz = -100))

            rb.sleep(2)
            dout(16, grip_code['pipet_release'])
            rb.sleep(1)

            rb.line(above_fluid)
            rb.move(second_posture)

            print('----- release fluid -----')

            if pos_goal == pos_plate_higher:
                third_posture = posture_change(pos_plate_higher, 'plate_ver', 0)
            elif pos_goal == pos_solution_base:
                third_posture = posture_change(pos_solution_higher, 'plate_ver', 0)

            rb.move(third_posture.offset(dy = -30))

            above_goal = offset_position(third_posture, off_goal, 1)
            
            rb.sleep(1)
            rb.line(above_goal.offset(dz=-10))

            dout(16, grip_code['pipet_hold'])
            rb.sleep(1)

            rb.line(above_goal)
            rb.move(third_posture)

        if fin_or_not == 1 :

            print('----- remove tip -----')

            dout(16, grip_code['basic_release'])
            four_posture = posture_change(pos_tip_remove_base, 'pipet_thin_ver', 1)

            rb.line(four_posture.offset(dz = -70))
            pos_del_tip = offset_position(four_posture, 'remove_tip', 0)

            rb.line(pos_del_tip.offset(dz = -100))
            rb.line(pos_del_tip)
            rb.line(pos_del_tip.offset(dz = -100))
            
            rb.move(four_posture.offset(dz = -100))
            rb.move(four_posture)

            print('----- release pipet ------')

            rb.move(pipet_posture.offset(dz = 100))
            rb.move(pos_pipet_handle.offset(dy = hanle_out_offset, dz = handle_up_offset))
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


        rb.home()

    rb.home()

    pos_incub_base = pos_incub_marker.offset(dx= -100, dy = +100, dz = -200)
    pos_pipet_thick_base = pos_pipet_thick_marker.offset(dz = -200)
    pos_solution_base = pos_solution_marker.offset(dz = -200)
    pos_plate_base = pos_plate_marker.offset(dz = -200)
    pos_suction_base =pos_suction_marker.offset(dz = -200)
    pos_pipet_thin_base = pos_pipet_thin_marker.offset(dx = 100, dz = -200)
    pos_tip_remove_base = pos_tip_remove_marker.offset(dx = 100, dz = -150)

    pos_plate_higher = pos_plate_marker.offset(dz = -100)
    pos_solution_higher = pos_solution_marker.offset(dy = -100 ,dz = -100)


    rb.home()  

    cap_open_3('open', 'CONICAL')



    

if __name__ == '__main__':
        main()
