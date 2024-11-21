import subprocess
import threading

proc = subprocess.Popen(["python", "trace_selector_main.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
def printOutput():
    i = 0
    print("---STDOUT---")
    while (line := proc.stdout.readline()) != "":
        print(i, line.replace("\n", ""))
        i += 1
    print("---STDOUT---")
t = threading.Thread(target=printOutput)
t.start()
