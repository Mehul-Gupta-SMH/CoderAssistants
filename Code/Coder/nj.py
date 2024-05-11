from Code.Coder.ToolBox.SQLTB import instFunctions as SQLTB

functionList = [functionName for functionName in dir(SQLTB) if not functionName.startswith("__")]


print({eval("SQLTB."+functionName) : eval("SQLTB."+functionName+".__doc__") for functionName in functionList})