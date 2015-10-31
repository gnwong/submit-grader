# server.py (server) 
#
# (c) 2015 George Wong
# 

from __future__ import print_function
import subprocess
import random, socket, time


####

ALLOWED_MODES = \
  [
  "sample"
  ]

PORT_NUMBER  = 4242
ALLOW_CONN   = 5
NUM_TESTS    = 50

####


def update_file(name, data, score):
  fp = open("scores/" + name + ".dat", "a+")
  # TODO
  fp.close()
  return

def run_test(name, data):
  return subprocess.check_output(["./" + name, str(data)])

def verify_info(info):
  fp = open("userlist.txt","r")
  valid = 0
  for line in fp:
    if line.split()[0].strip() == info[1]:
      if line.split()[2].strip() == info[3]:
        valid = 1
  fp.close()
  return valid > 0


if __name__ == "__main__":

  ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ssocket.bind((socket.gethostname(), PORT_NUMBER))
  ssocket.listen( ALLOW_CONN )

  print("Listening on " + str(socket.gethostname() + ":" + str(PORT_NUMBER)))

  while True:
    try:
      connection, address = ssocket.accept()
      print("Received connection from " + str(address))
      if (connection.recv(2048) != "HELO"):
        print("Unauthorized connection attempt. Aborting!")
        connection.close()
        continue
      connection.send("EHLO")

      # Get submitter information
      INFO = []
      INFO.append(connection.recv(2048))
      connection.send("ACK")
      INFO.append(connection.recv(2048))
      connection.send("ACK")
      INFO.append(connection.recv(2048))
      connection.send("ACK")
      INFO.append(connection.recv(2048))

      # Verify submitter information
      valid = verify_info(INFO)
      if valid:
        connection.send("GOOD")
      else:
        connection.send("BAD")
        print("Unallowed submitter: " + INFO[0])
        connection.close()
        continue

      # Get full submitter information & exercise number
      INFO.append(connection.recv(4096))
      mode = connection.recv(1024)
      if mode in ALLOWED_MODES:
        connection.send("ACK")
      else:
        connection.send("NO")
        print("Unallowed mode requested: " + str(mode))
        connection.close()
        continue

      # Run NUM_TESTS tests of the code
      connection.send(str(NUM_TESTS))
      numcorrect = 0
      for i in range(NUM_TESTS):
        rand = random.randint(0,100)
        time.sleep(0.01)
        connection.send(str(rand))
        time.sleep(0.01)
        ser_res = str(run_test(mode, rand)).rstrip()
        time.sleep(0.01)
        cli_res = str(connection.recv(1024)).rstrip()
        time.sleep(0.01)
        print(ser_res, cli_res)
        if (ser_res == cli_res):
          numcorrect += 1
          connection.send("valid")
        else:
          connection.send("bad")

      connection.close()
      update_file(INFO[1], INFO, numcorrect)
      print("Connection closed for " + str(address))
    except:
      pass
