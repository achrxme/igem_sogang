import socket, threading

import keras_model_def
import grip_test
import get_pos
import get_world_pos

model = keras_model_def.keras_model_def()

def binder(client_socket, addr):

  print('Connected by', addr)
  try:
    while True:
      #receive
      data = client_socket.recv(64)
      msg = data.decode()
     
      if msg == 'grip_test' :

        test_result = grip_test.grip_test(model)
        print(test_result)

        #send
        data = test_result.encode()
        client_socket.send(data)
        break

      elif msg == 'get_pos' :

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
 