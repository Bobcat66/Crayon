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
ifRegex = re.compile(r"(?<=if\()CONDITION=(TRUE|FALSE),TRIGGER=([A-Za-z0-9]+)(?=\))")#Example statement: $if(CONDITION=TRUE,TRIGGER=01)
evalRegex = re.compile(r"eval\('([^']+)'='([^']+)'\)")#Example statement: $eval('Hello'='Hello')
trigExecRegex = re.compile(r"TRIG\{(.+)\}TRIG\[([A-Za-z0-9]+)\]")#Example: TRIG{<code goes here>}TRIG[<Trigger Name>]
notIfRegex = re.compile(r"(?<=notIf\()CONDITION=(TRUE|FALSE),TRIGGER=([A-Za-z0-9]+)(?=\))")#opposite of if, disables trigger if CONDITION is TRUE, activates it if CONDITION is FALSE




variables = []

triggers = []

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
    if not runOne == None:
        parseStatements(runOne.group(0))

    runTwo = trigExecRegex.search(codeVar) #Executes TRIG
    if not runTwo == None:
        for trigger in triggers:
            if trigger.name == runTwo.group(2):
                if trigger.value == True:
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
        if not embedOutput == None:
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
    if not inputRegex.search(codeVar) == None:
        output = inputCommand(codeVar)
    if not evalRegex.search(codeVar) == None:
        output = evalCommand(codeVar)
    return output

def inputCommand(codeVar):
    """
    User input function
    Embeddable = YES
    """
    inputSearch = inputRegex.search(codeVar)
    if inputSearch == None:
        return None
    else:
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

def evalCommand(codeVar):
    """
    Evaluates a statement as true or false
    Is embeddable
    """
    evalSearch = evalRegex.search(codeVar)
    if evalSearch == None:
        return None
    else:
        if evalSearch.group(1) == evalSearch.group(2):
            return 'TRUE'
        else:
            return 'FALSE'

def ifCommand(codeVar):
    """
    Takes a boolean and executes code if it is true
    """
    ifSearch = ifRegex.search(codeVar)
    if not ifSearch == None:
        triggerExists = False
        for trigger in triggers:
            if trigger.name == ifSearch.group(2):
                if ifSearch.group(1) == 'TRUE':
                    trigger.value == True
                elif ifSearch.group(1) == 'FALSE':
                    trigger.value == False
                triggerExists == True
        if not triggerExists:
            if ifSearch.group(1) == 'TRUE':
                newTrig = Trigger(name=ifSearch.group(2), value=True)
            elif ifSearch.group(1) == 'FALSE':
                newTrig = Trigger(name=ifSearch.group(2), value=False)
            triggers.append(newTrig)

def notIfCommand(codeVar):
    """
    Takes a boolean and executes code if it is false,
    opposite of if command
    """
    notIfSearch = notIfRegex.search(codeVar)
    if not notIfSearch == None:
        triggerExists = False
        for trigger in triggers:
            if trigger.name == notIfSearch.group(2):
                if notIfSearch.group(1) == 'TRUE':
                    trigger.value == False
                elif notIfSearch.group(1) == 'FALSE':
                    trigger.value == True
                triggerExists == True
        if not triggerExists:
            if notIfSearch.group(1) == 'TRUE':
                newTrig = Trigger(name=notIfSearch.group(2), value=False)
            elif notIfSearch.group(1) == 'FALSE':
                newTrig = Trigger(name=notIfSearch.group(2), value=True)
            triggers.append(newTrig)
        