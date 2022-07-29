import cv2
import numpy as np

REPEAT_NUM = 10

def get_center_of_red_circle():

    cap = cv2.VideoCapture(0)

    if cap.isOpened():

        valid_idx = 0
        x = []
        y = []
        radii = []

        while True:
            ret, frame = cap.read()
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            #빨간색 부분 : 1 / 나머지 부분 : 0 으로 변환
            red_area =  cv2.inRange(frame_hsv, (-5,100,100), (5, 255, 255))
            #noise 제거
            unnoise_red = cv2.GaussianBlur(red_area, (0,0), 1.0)

            min_rad = 10 #0으로 두면 사용하지 않음
            max_rad = 45
            threshold = 30 #작으면 오류가 높음, 크면 검출률이 떨어짐
            
            circles = cv2.HoughCircles(unnoise_red, cv2.HOUGH_GRADIENT, 1, 20, param1=120, param2=threshold, 
                                        minRadius=min_rad, maxRadius=max_rad)

            circled_red_copy = unnoise_red.copy() #원을 그릴 도화지
            if circles is not None:

                cx, cy, radius = circles[0][0] #원의 정보 저장(중심점 좌표, 반지름)(하나만 가져감)
                print(cx, cy, radius)
                x.append(cx)
                y.append(cy)
                radii.append(radius)
                valid_idx +=1 

                    #cv2.circle(circled_red_copy, (int(cx),int(cy)), int(radius), (0,0,255),2) #원 그리기
            else :
                pass
                #print('no circles')

            if valid_idx == REPEAT_NUM:
                break
            
            if ret :
                cv2.imshow('camera', circled_red_copy)
                if cv2.waitKey(1) != -1:
                    break
            else :
                print('ERROR : no frmae')
                break

    else :
        print('ERROR : no camera')

    cap.release()

    return x, y, radii

#dx, dy = get_pos.get_pos() 으로 호출, 실행하면 됨

def get_pos():
    while(1):
        success_idx = 0

        result_x, result_y, result_radii = get_center_of_red_circle()
        aver_x = np.mean(result_x)
        aver_y = np.mean(result_y)
        aver_radii = np.mean(result_radii)

        #test whethe function get wrong circle or not
        for i in range(REPEAT_NUM):
            if aver_x - result_x[i] < 5 and aver_y - result_y[i] < 5 :
                success_idx += 1
            else :
                print('we should repeat again')
        
        if success_idx == REPEAT_NUM:
            break

    
    print('END : ' ,aver_x, aver_y)

    dx, dy = scale_adjust(aver_x, aver_y, aver_radii)

    print(dx, dy)

    int_dx = int(dx)
    int_dy = int(dy)

    return int_dx, int_dy

def get_scale_coef(measured_radii):
    actual_radii = 10 #reference, mm, it should be changed for real red dot sticker
    scale_coef = actual_radii / measured_radii

    return scale_coef


def scale_adjust(aver_x, aver_y, aver_radii):
    center_offset_x = 650
    center_offset_y = 450

    centered_x = aver_x - center_offset_x #center change
    centered_y = aver_y - center_offset_y

    scale_coefficient = get_scale_coef(aver_radii)

    scaled_x = scale_coefficient * centered_x  #scale adjustment
    scaled_y = scale_coefficient * centered_y

    return scaled_x, scaled_y

get_pos()