import sys

f = open("test.csv", "w")
f.write(sys.argv[1])
f.close()