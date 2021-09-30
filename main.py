
import crayon

fileOpen = input("Enter file directory: ")
with open(fileOpen, 'r') as f:
    fileLines = f.readlines()
    for line in fileLines:
        crayon.initialize(line)


