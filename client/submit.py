# submit.py (client) 
#
# (c) 2015 George Wong
# 

from __future__ import print_function
import subprocess
import socket
import sys


####

SERVER_ADDR = ""
SERVER_PORT = 4242

####


def run_test(name, data):
  return subprocess.check_output(["./" + name, str(data)])

if __name__ == "__main__":
  
  STUDENT = {
    "name"  : "",
    "netid" : "",
    "nid"   : "",
    "cc"    : "",
    "full"  : ""
  }

  print("")

  ## Ensure we have a meaningful program to run
  if len(sys.argv) < 2:
    print("Please run this program with the proper arguments:")
    print("  python submit.py <sample>\n")
    exit(-3)

  ## Get the student info 
  try:
    fp = open("my.info","r")
    for line in fp:
      STUDENT["full"] += line
      if line.strip()[:5].lower() == "name:":
        STUDENT["name"] = line.strip()[5:].strip()
      elif line.strip()[:7].lower() == "net id:":
        STUDENT["netid"] = line.strip()[7:].strip()
      elif line.strip()[:11].lower() == "nyu id(n#):":
        STUDENT["nid"] = line.strip()[11:].strip()
      elif line.strip()[:18].lower() == "confirmation code:":
        STUDENT["cc"] = line.strip()[18:].strip()
    fp.close()
  except:
    print("Unable to open my.info file. Quitting!\n")
    exit(-1)
  # Validate
  valid = 1
  if len(STUDENT["name"]) < 1:
    valid = 0
    print("No name found")
  if len(STUDENT["netid"]) < 1:
    valid = 0
    print("No net id found")
  if len(STUDENT["nid"]) < 1:
    valid = 0
    print("No N# found")
  if len(STUDENT["cc"]) < 1:
    print("No confirmation code found")
    valid = 0
  if valid == 0:
    print(" + Please check your my.info file!\n")

  ## Attempt to establish connection with server
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((SERVER_ADDR, SERVER_PORT))
  s.send("HELO")
  s.recv(64)
  s.send(STUDENT["name"])
  s.recv(64)
  s.send(STUDENT["netid"])
  s.recv(64)
  s.send(STUDENT["nid"])
  s.recv(64)
  s.send(STUDENT["cc"])
  r = s.recv(1024)
  if r != "GOOD":
    print("Server does not like your credentials. Please")
    print("verify your informsation and try again.\n")
    exit(-2)
  s.send(STUDENT["full"])
  s.send(sys.argv[1])
  if s.recv(1024) != "ACK":
    print("Bad test name. Please ensure you are following the")
    print("correct naming convention!\n")
    exit(-3)

  # Run tests
  tests_passed = 0
  ntests = int(s.recv(1024))
  for i in range(ntests):
    arg = int(s.recv(1024))
    out = run_test(sys.argv[1],arg)
    s.send(out)
    valid = s.recv(1024)
    if valid == "valid": tests_passed += 1

  ## Notify submitter of result
  s.close()
  print('Tests passed: {0:d} of {1:d}\n'.format(tests_passed, ntests))
