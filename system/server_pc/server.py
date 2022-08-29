import socket, threading

#import keras_model_def
import get_pos
import get_world_pos


def binder(client_socket, addr):

  print('Connected by', addr)

  try:
    while True:
      #receive
      data = client_socket.recv(64)
      msg = data.decode()

      if msg == 'get_pos' :

        dx, dy = get_pos.get_pos()
        str_dx = str(dx)
        str_dy = str(dy)
        str_dx_dy = 'x' + str_dx + 'y' + str_dy + 'q'

        #send
        data = str_dx_dy.encode()
        client_socket.send(data)
        break
      
      elif msg == 'get_world_pos' :

          x_result, y_result = get_world_pos.get_world_pos()
          
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

          str_xy_array = str_xy1 + 'w' + str_xy2 + 'w' + str_xy3 + 'w' + str_xy4 + 'w' + str_xy5 + 'w' + str_xy6 + 'w' + str_xy7 + 'w'

          data = str_xy_array.encode()
          client_socket.send(data)

          break

      elif msg == 'adjust_world_pos' :

        idx, off_x, off_y = get_world_pos.adjust_world_pos()

        str_idx = str(idx)
        str_off_x = str(off_x)
        str_off_y = str(off_y)

        str_idx_x_y = str_idx + 'x' + str_off_x + 'y' + str_off_y + 'q'
        
        data = str_idx_x_y.encode()
        client_socket.send(data)

        break
      
      elif msg == "GUI_home":
        data = msg.encode()
        client_socket.send(data)
        break
      elif msg == "GUI_plate":
        data = msg.encode()
        client_socket.send(data)
        break
      else :
        print('[server] undefined order : ', msg)
        break  
        
  except:
    print("except : " , addr)
  finally:
   client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 9999))
server_socket.listen()
 
try:
  print("[SERVER START]")

  while True:
    client_socket, addr = server_socket.accept()
    th = threading.Thread(target=binder, args = (client_socket,addr))
    th.start()
except:
  print("[ERROR] server is not connected")
finally:
  server_socket.close()
 
