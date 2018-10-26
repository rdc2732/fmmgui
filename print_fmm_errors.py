import os
import string

fp = open("./FMM.txt","r")
lines = fp.read().splitlines()
fp.close()

for line in lines:
    stringdata = string.split(line,",")
    if len(stringdata) > 8:
        print stringdata
