import socket
import re

def extract_dx_dy(rcv_str_dx_dy):

    idx_x = rcv_str_dx_dy.find('x')
    idx_y = rcv_str_dx_dy.find('y')
    idx_end = rcv_str_dx_dy.find('q')

    idx_data_x = idx_x+1
    idx_data_y = idx_y+1

    str_x = rcv_str_dx_dy[idx_data_x:idx_data_y-1]
    str_y = rcv_str_dx_dy[idx_data_y:idx_end]

    int_x = int(str_x)
    int_y = int(str_y)

    return int_x, int_y

def divide_string(rcv_str):

    idx = [0, 0, 0, 0, 0, 0, 0]
    i=0

    for m in re.finditer('w', rcv_str):
        idx[i] = m.start()
        i += 1
    
    str1 = rcv_str[0:idx[0]]
    str2 = rcv_str[idx[0]+1:idx[1]]
    str3 = rcv_str[idx[1]+1:idx[2]]
    str4 = rcv_str[idx[2]+1:idx[3]]
    str5 = rcv_str[idx[3]+1:idx[4]]
    str6 = rcv_str[idx[4]+1:idx[5]]
    str7 = rcv_str[idx[5]+1:idx[6]]

    return str1, str2, str3, str4, str5, str6, str7

def extract_idx_x_y(rcv_str_idx_x_y):

    idx_idx = 0
    idx_x = rcv_str_idx_x_y.find('x')
    idx_y = rcv_str_idx_x_y.find('y')
    idx_end = rcv_str_idx_x_y.find('q')

    idx_data_x = idx_x+1
    idx_data_y = idx_y+1

    idx = rcv_str_idx_x_y[idx_idx:idx_data_x-1]
    off_x = rcv_str_idx_x_y[idx_data_x:idx_data_y-1]
    off_y = rcv_str_idx_x_y[idx_data_y:idx_end]

    int_idx = int(idx)
    int_off_x = int(off_x)
    int_off_y = int(off_y)


    #print(idx, off_x, off_y)

    return int_idx, int_off_x, int_off_y

def order_classify(order):
    HOST = '192.168.0.14'
    PORT = 9999
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    send_msg = order
    send_data = send_msg.encode()
    
    #send
    print("[client] : send msg")
    client_socket.send(send_data)

    if order == 'grip_test':
        #receive
        rcv_data = client_socket.recv(64)
        print("[client] : recv suc/fail")
        rcv_msg = rcv_data.decode()
        client_socket.close()

        msg = rcv_msg

        return msg    #return str

    elif order == 'get_pos':
        #receive
        rcv_data = client_socket.recv(64)
        print("[client] : recv from server")
        rcv_msg = rcv_data.decode()

        client_socket.close()

        rcv_dx, rcv_dy = extract_dx_dy(rcv_msg)
        return rcv_dx, rcv_dy  #return int, int

    elif order == 'get_world_pos' : 

        rcv_data = client_socket.recv(1024)

        print("[client] : recv from server")
        rcv_msg = rcv_data.decode()

        client_socket.close()

        rcv_msg1, rcv_msg2, rcv_msg3, rcv_msg4, rcv_msg5, rcv_msg6, rcv_msg7= divide_string(rcv_msg)
         
        rcv_x1, rcv_y1 = extract_dx_dy(rcv_msg1)
        rcv_x2, rcv_y2 = extract_dx_dy(rcv_msg2)
        rcv_x3, rcv_y3 = extract_dx_dy(rcv_msg3)
        rcv_x4, rcv_y4 = extract_dx_dy(rcv_msg4)
        rcv_x5, rcv_y5 = extract_dx_dy(rcv_msg5)
        rcv_x6, rcv_y6 = extract_dx_dy(rcv_msg6)
        rcv_x7, rcv_y7 = extract_dx_dy(rcv_msg7)

        return_x = []
        return_x.append(rcv_x1)
        return_x.append(rcv_x2)
        return_x.append(rcv_x3)
        return_x.append(rcv_x4)
        return_x.append(rcv_x5)
        return_x.append(rcv_x6)
        return_x.append(rcv_x7)

        return_y = []
        return_y.append(rcv_y1)
        return_y.append(rcv_y2)
        return_y.append(rcv_y3)
        return_y.append(rcv_y4)
        return_y.append(rcv_y5)
        return_y.append(rcv_y6)
        return_y.append(rcv_y7)

        return return_x, return_y

    elif order == 'adjust_world_pos':
        rcv_data = client_socket.recv(1024)

        print("[client] : recv from server")
        rcv_msg = rcv_data.decode()

        

        client_socket.close()

        idx, off_x, off_y = extract_idx_x_y(rcv_msg)

        return idx, off_x, off_y


    else :
        print('unexpected order')
        return 'unexpected order'  # return 'unexpected order'
