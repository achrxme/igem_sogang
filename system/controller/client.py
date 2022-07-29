import socket

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
        print(msg)
        return msg    #return str

    elif order == 'get_pos':
        #receive
        rcv_data = client_socket.recv(64)
        print("[client] : recv suc/fail")
        rcv_msg = rcv_data.decode()
        client_socket.close()

        rcv_dx, rcv_dy = extract_dx_dy(rcv_msg)
        return rcv_dx, rcv_dy  #return int, int

    elif order == 'get_world_pos' :

        #receive
        rcv_data1 = client_socket.recv(64)
        rcv_data2 = client_socket.recv(64)
        rcv_data3 = client_socket.recv(64)
        rcv_data4 = client_socket.recv(64)
        rcv_data5 = client_socket.recv(64)
        rcv_data6 = client_socket.recv(64)
        rcv_data7 = client_socket.recv(64)

        print("[client] : recv suc/fail")

        rcv_msg1 = rcv_data1.decode()
        rcv_msg2 = rcv_data2.decode()
        rcv_msg3 = rcv_data3.decode()
        rcv_msg4 = rcv_data4.decode()
        rcv_msg5 = rcv_data5.decode()
        rcv_msg6 = rcv_data6.decode()
        rcv_msg7 = rcv_data7.decode()

        client_socket.close()

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

        return return_x, return_x

    else :
        print('unexpected order')
        return 'unexpected order'  # return 'unexpected order'
