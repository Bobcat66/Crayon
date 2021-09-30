import re
import sys

execRegex = re.compile(r'(?<=##\{).{1,}(?=\}##)') #Defines execute command
printRegex = re.compile(r"(?<=displayOut\(\').{1,}(?=\'\))")
addRegex = re.compile(r"(?<=add\()[\d,\-,\+,\.]{1,}(?=\))")
statementRegex = re.compile(r"(?<=\$)[^\$]{1,}") #Statements must begin with '$'
varRegex = re.compile(r"(VAR\(([A-Za-z]+)\))") # VAR(<variable name>)
setVarRegex = re.compile(r"(?<=setVar\()NAME=([A-Za-z]{1,}),VALUE=([^\)]{1,})(?=\))") #setVar(NAME=<variable name>,VALUE=<variable value>)


variables = []

class Variable():
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value

def initialize(codeVar):
    runOne = execRegex.search(codeVar)
    if not runOne == None:
        parseStatements(runOne.group(0))

def variableParse(codeVar):
    """
    parses variables
    """
    variableTagList = varRegex.findall(codeVar) #returns a list of tuples. variableTag[0] is equivalent to group(0), variableTag[1] is equivalent to group(1), etc.
    output = codeVar
    for variableTag in variableTagList:
        for variable in variables:
            if variable.name == variableTag[1]:
                output = output.replace(variableTag[0], variable.value)
    return output






def parseStatements(codeVar):
    """
    Detects individual statements in an execute command
    """
    statements = statementRegex.findall(codeVar)
    for statement in statements:
        varParseStatement = variableParse(statement)
        execute(varParseStatement)


def execute(codeVar):
    """
    Executes parsed statements
    """
    printCommand(codeVar)
    exitCommand(codeVar)
    addCommand(codeVar)
    howSayCrayon(codeVar)
    setVar(codeVar)

def addCommand(codeVar):
    """
    performs addition
    """
    addRun = addRegex.search(codeVar)
    if addRun == None:
        return
    addNums = re.split(r'\+', addRun.group(0))
    addFloats = []
    for ele in addNums:
        addFloats.append(float(ele))
    output = 0
    for ele in addFloats:
        output += ele
    if not output == 0:
        print(output)
    

def printCommand(codeVar):
    #Defines print statement
    printRun = printRegex.search(codeVar)
    if printRun == None:
        return
    print(printRun.group(0))

def exitProg(exitCause):
    """
    Defines exit
    """
    sys.exit(f"Crayon Process Terminated: {exitCause}")

def exitCommand(codeVar):
    if 'EXIT' in codeVar:
        exitProg("EXIT_COMMAND")

def howSayCrayon(codeVar):
    if 'HOW_SAY_CRAYON' in codeVar:
        print("Here is how you say Crayon: KRAE-OHN")

def setVar(codeVar):
    varSetRun = setVarRegex.search(codeVar)
    if varSetRun == None:
        return
    variables.append(Variable(name=varSetRun.group(1), value=varSetRun.group(2)))