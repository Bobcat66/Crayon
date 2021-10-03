import re
import sys


execRegex = re.compile(r'(?<=##{).{1,}(?=}##)') #Defines execute command
printRegex = re.compile(r"(?<=displayOut\(\').{1,}(?=\'\))")
addRegex = re.compile(r"(?<=add\()[\d,\-,\+,\.]{1,}(?=\))")
statementRegex = re.compile(r"(?<=\$)[^\$]{1,}") #Statements must begin with '$'
varRegex = re.compile(r"(VAR\(([A-Za-z]+)\))") # VAR(<variable name>)
setVarRegex = re.compile(r"(?<=setVar\()NAME=([A-Za-z]{1,}),VALUE=([^\)]{1,})(?=\))") #setVar(NAME=<variable name>,VALUE=<variable value>)
embedExecRegex = re.compile(r"(EMBED{([^}]+)}EMBED)") #Example statement: $displayOut('Your Name is: EMBED{userInput('What is your name?')}EMBED')
inputRegex = re.compile(r"(?<=userInput\(\').+(?=\'\))") #Input MUST HAVE a string
ifRegex = re.compile(r"(?<=if\()CONDITION=(True|False),TRIGGER=([A-Za-z0-9]+)(?=\))")#Example statement: $if(CONDITION=TRUE,TRIGGER=01)
evalRegex = re.compile(r"eval\('([^']+)'='([^']+)'\)")#Example statement: $eval('Hello'='Hello')
trigExecRegex = re.compile(r"TRIG\{(.+)\}TRIG\[([A-Za-z0-9]+)\]")#Example: TRIG{<code goes here>}TRIG[<Trigger Name>]
notIfRegex = re.compile(r"(?<=notIf\()CONDITION=(True|False),TRIGGER=([A-Za-z0-9]+)(?=\))")#opposite of if, disables trigger if CONDITION is TRUE, activates it if CONDITION is FALSE
arithRegex = re.compile(r"arith\((-?[0-9]*.?[0-9]+)([+,\-,*,/])(-?[0-9]*.?[0-9]+)\)") #syntax: arith(<number 1><operator><number 2>)
comparRegex = re.compile(r"compare\((-?[0-9]*.?[0-9]+)(<|>)(-?[0-9]*.?[0-9]+)\)") #syntax: compare(<number 1><operator><number 2>)
gotoRegex = re.compile(r"GOTO\(([0-9]+)\)")

variables = []

triggers = []

linecount = 0
def executeProgram(lines):
    global linecount
    """
    Initializes all elements in a list
    (for GOTO statements)
    Takes dictionary as input
    """
    totalLines = len(lines)
    while linecount < totalLines:
        initialize(lines.get(linecount))
        linecount += 1

    

class Trigger():
    def __init__(self, name=None, value=False):
        self.name = name
        self.value = value

class Variable():
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value

def initialize(codeVar):
    """
    Handles execution commands such as ## and TRIG
    """
    runOne = execRegex.search(codeVar) #Executes ##
    if runOne is not None:
        parseStatements(runOne.group(0))

    runTwo = trigExecRegex.search(codeVar) #Executes TRIG
    if runTwo is not None:
        for trigger in triggers:
            if trigger.name == runTwo.group(2) and trigger.value is True:
                parseStatements(runTwo.group(1))

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

def embedParse(codeVar):
    """
    Parses Embedded Code
    """
    embedList = embedExecRegex.findall(codeVar)
    output = codeVar
    for embed in embedList:
        embedOutput = embedExecute(embed[1])
        if embedOutput is not None:
            output = output.replace(embed[0], embedOutput)
    return output




def parseStatements(codeVar):
    """
    Detects individual statements in an execute command
    """
    statements = statementRegex.findall(codeVar)
    for statement in statements:
        varParseStatement = variableParse(statement)
        embedStatement = embedParse(varParseStatement)
        execute(embedStatement)

def embedExecute(codeVar):
    """
    Executes embedded code
    """
    output = None
    if inputRegex.search(codeVar) is not None:
        output = inputCommand(codeVar)
    if evalRegex.search(codeVar) is not None:
        output = evalCommand(codeVar)
    if arithRegex.search(codeVar) is not None:
        output = arithCommand(codeVar)
    if comparRegex.search(codeVar) is not None:
        output = compareCommand(codeVar)
    return output

def inputCommand(codeVar):
    """
    User input function
    Embeddable = YES
    """
    inputSearch = inputRegex.search(codeVar)
    if inputSearch is None:
        return None
    
    output = input(inputSearch.group(0))
    return output
    
def execute(codeVar):
    """
    Executes parsed statements
    """
    printCommand(codeVar)
    exitCommand(codeVar)
    addCommand(codeVar)
    howSayCrayon(codeVar)
    setVar(codeVar)
    ifCommand(codeVar)
    notIfCommand(codeVar)


def addCommand(codeVar):
    """
    performs addition
    """
    addRun = addRegex.search(codeVar)
    if addRun is None:
        return
    addNums = re.split(r'\+', addRun.group(0))
    addFloats = []
    for ele in addNums:
        addFloats.append(float(ele))
    output = 0
    for ele in addFloats:
        output += ele
    print(output)
    

def printCommand(codeVar):
    #Defines print statement
    printRun = printRegex.search(codeVar)
    if printRun is None:
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
    if varSetRun is None:
        return
    variables.append(Variable(name=varSetRun.group(1), value=varSetRun.group(2)))

def evalCommand(codeVar):
    """
    Evaluates a statement as true or false
    Is embeddable
    """
    evalSearch = evalRegex.search(codeVar)
    if evalSearch is None:
        return None
    if evalSearch.group(1) == evalSearch.group(2):
        return 'True'
    return 'False'

def ifCommand(codeVar):
    """
    Takes a boolean and executes code if it is true
    """
    ifSearch = ifRegex.search(codeVar)
    if ifSearch is not None:
        triggerExists = False
        for trigger in triggers:
            if trigger.name == ifSearch.group(2):
                trigger.value == bool(ifSearch.group(1))
                triggerExists == True
        if not triggerExists:
            newTrig = Trigger(name=ifSearch.group(2), value=bool(ifSearch.group(1)))
            triggers.append(newTrig)

def notIfCommand(codeVar):
    """
    Takes a boolean and executes code if it is false,
    opposite of if command
    """
    notIfSearch = notIfRegex.search(codeVar)
    if notIfSearch is not None:
        triggerExists = False
        for trigger in triggers:
            if trigger.name == notIfSearch.group(2):
                trigger.value = not bool(notIfSearch.group(1))
                triggerExists == True
        if not triggerExists:
            newTrig = Trigger(name=notIfSearch.group(2), value=not bool(notIfSearch.group(1)))
            triggers.append(newTrig)

def arithCommand(codeVar):
    """
    Performs Arithmetic
    Is Embeddable
    """
    arithSearch = arithRegex.search(codeVar)
    if arithSearch.group(2) == '+':
        return str(float(arithSearch.group(1)) + float(arithSearch.group(3)))
    elif arithSearch.group(2) == '-':
        return str(float(arithSearch.group(1)) - float(arithSearch.group(3)))
    elif arithSearch.group(2) == '*':
        return str(float(arithSearch.group(1)) * float(arithSearch.group(3)))
    elif arithSearch.group(2) == '/':
        return str(float(arithSearch.group(1)) / float(arithSearch.group(3)))

def compareCommand(codeVar):
    """
    Compares the value of two numbers
    Is Embeddable
    """
    compareSearch = comparRegex.search(codeVar)
    if compareSearch.group(2) == "<":
        return str(float(compareSearch.group(1)) < float(compareSearch.group(3)))
    elif compareSearch.group(2) == ">":
        return str(float(compareSearch.group(1)) > float(compareSearch.group(3)))
        