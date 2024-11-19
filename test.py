import subprocess
import threading
import time
import os

env = os.environ.copy()
proc = subprocess.Popen(["python", r"C:\Users\abril\Andreas Eigene Dateien\Programmieren\VS Code\Git\trace_selector\trace_selector_main.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, text=True)

def readStdout():
    while (line := proc.stdout.readline().strip("\n")) != "":
        print(line)
    print("Fertig")

#threading.Thread(target=readStdout, daemon=True).start()
print("Schreibe")
proc.stdin.write("Hallo Welt\n")
proc.stdin.write("Hallo Welt 2\n")
proc.stdin.flush()
proc.stdin.write("\n")
proc.stdin.flush()
readStdout()
print("Schreibe Ende")

#time.sleep(20)

exit()