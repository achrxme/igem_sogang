import re

x_result = [10, 9, -3, 245 ,-24, 42, 15]
y_result = [20, -200, 351, 244, -42, 6, 57]

str_x1 = str(x_result[0])
str_x2 = str(x_result[1])
str_x3 = str(x_result[2])
str_x4 = str(x_result[3])
str_x5 = str(x_result[4])
str_x6 = str(x_result[5])
str_x7 = str(x_result[6])

str_y1 = str(y_result[0])
str_y2 = str(y_result[1])
str_y3 = str(y_result[2])
str_y4 = str(y_result[3])
str_y5 = str(y_result[4])
str_y6 = str(y_result[5])
str_y7 = str(y_result[6])
          
str_xy1 = 'x' + str_x1 + 'y' + str_y1 + 'q'
str_xy2 = 'x' + str_x2 + 'y' + str_y2 + 'q'
str_xy3 = 'x' + str_x3 + 'y' + str_y3 + 'q'
str_xy4 = 'x' + str_x4 + 'y' + str_y4 + 'q'
str_xy5 = 'x' + str_x5 + 'y' + str_y5 + 'q'
str_xy6 = 'x' + str_x6 + 'y' + str_y6 + 'q'
str_xy7 = 'x' + str_x7 + 'y' + str_y7 + 'q'

str_xy_array = str_xy1 + 'w' + str_xy2 + 'w' + str_xy3 + 'w' + str_xy4 + 'w' + str_xy5  + 'w' + str_xy6 + 'w' + str_xy7 + 'w'

def extract_dx_dy(rcv_str_dx_dy):

    #print('str : ', rcv_str_dx_dy)

    idx_x = rcv_str_dx_dy.find('x')
    idx_y = rcv_str_dx_dy.find('y')
    idx_end = rcv_str_dx_dy.find('q')

    idx_data_x = idx_x+1
    idx_data_y = idx_y+1

    str_x = rcv_str_dx_dy[idx_data_x:idx_data_y-1]
    str_y = rcv_str_dx_dy[idx_data_y:idx_end]

    int_x = int(str_x)
    int_y = int(str_y)

    print(int_x, int_y)

    return int_x, int_y

def divide_string(rcv_str):

    idx = [0, 0, 0, 0, 0, 0, 0]
    i=0

    for m in re.finditer('w', rcv_str):
        idx[i] = m.start()
        i +=1
    
    str1 = rcv_str[0:idx[0]]
    str2 = rcv_str[idx[0]+1:idx[1]]
    str3 = rcv_str[idx[1]+1:idx[2]]
    str4 = rcv_str[idx[2]+1:idx[3]]
    str5 = rcv_str[idx[3]+1:idx[4]]
    str6 = rcv_str[idx[4]+1:idx[5]]
    str7 = rcv_str[idx[5]+1:idx[6]]

    return str1, str2, str3, str4, str5, str6, str7

rcv_msg1, rcv_msg2, rcv_msg3, rcv_msg4, rcv_msg5, rcv_msg6, rcv_msg7 = divide_string(str_xy_array)

rcv_x1, rcv_y1 = extract_dx_dy(rcv_msg1)
rcv_x2, rcv_y2 = extract_dx_dy(rcv_msg2)
rcv_x3, rcv_y3 = extract_dx_dy(rcv_msg3)
rcv_x4, rcv_y4 = extract_dx_dy(rcv_msg4)
rcv_x5, rcv_y5 = extract_dx_dy(rcv_msg5)
rcv_x6, rcv_y6 = extract_dx_dy(rcv_msg6)
rcv_x7, rcv_y7 = extract_dx_dy(rcv_msg7)
