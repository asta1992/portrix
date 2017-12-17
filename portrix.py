#!/usr/bin/python3
import argparse
import sys

class Rule:
    fromSystem = ""
    toSystem = ""
    port = ""
    
    def __init__(self, fromSystem, toSystem, ports):
        self.fromSystem = fromSystem
        self.toSystem = toSystem
        self.port = self.extractPorts(ports)
    
    def extractPorts(self, ports):
        port = ""
        for s in ports.split(","):
            s = s.replace(" ", "")
            s = s.replace("\n", "")
            port = port + s + ", "
        return port[0:-2]



class Reader:
    inputFile = ""
    outputFile = ""

    
    def __init__(self, inputFile, outputFile):
        self.inputFile = inputFile
        self.outputFile = outputFile
        
    def createRulesFromFile(self):
        ruleList = []
        try:
            with open(self.inputFile) as file:
                for line in file:
                    splittedLine = line.split("\t")
                    rule = Rule(splittedLine[0], splittedLine[1], splittedLine[2])
                    ruleList.append(rule)
            return ruleList
        except FileNotFoundError:
            print("ERROR: No such inputfile or directory: " + str(self.inputFile))
            sys.exit()
            s
    def createOutput(self, portmatrix):
        output = ""
        row = 0
        column = 0
        for row in range(len(portmatrix)):
            for column in range(len(portmatrix)):
                output = output + str(portmatrix[row][column]) + ""
                if column < len(portmatrix) - 1:
                    output = output + ";"
                column = column + 1
            output = output + "\n"
            row = row + 1
        return output
    
    def exportToCSV(self, portmatrix):
        csvString = self.createOutput(portmatrix)
        try:
            with open(self.outputFile, "w") as text_file:
                text_file.write(csvString)
        except FileNotFoundError:
            print("ERROR: No such outputfile or directory: " + str(self.outputFile))
            
            
    def exportToStdout(self, portmatrix):
        print(self.createOutput(portmatrix))
      
      
        
class Matrix:

    def getAllSystems(self, ruleList):
        allSystems = set()
        for rule in ruleList:
            allSystems.add(rule.fromSystem)
            allSystems.add(rule.toSystem)
        return sorted(allSystems, key=lambda s: s.lower())
    
    def createMatrix(self, ruleList):
        allSystems = self.getAllSystems(ruleList)
        
        n = len(allSystems) + 1
        x = 1
        y = 1
        portmatrix = [[""] * n for _ in range(n)]
        for system in allSystems:
            portmatrix[0][x] = system
            portmatrix[y][0] = system
            x += 1
            y += 1
            portmatrix[y-1][x-1] = "XX"
        
        for rule in ruleList:
            row = allSystems.index(rule.fromSystem) + 1 
            column = allSystems.index(rule.toSystem) + 1
            if(portmatrix[row][column] == "XX"):
                print("\n--- Rule to same System are not possible: " + str(rule.fromSystem) + "\t" + str(rule.toSystem) + "\t" +  str(rule.port) + "\n")
            else:
                portmatrix[row][column] = portmatrix[row][column] + rule.port + ", "
                
        return portmatrix      
  
  
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required arguments')
    requiredNamed.add_argument('-i', '--inputfile', help='Input file name', required=True)
    parser.add_argument('-o', '--outputfile', help='Output file name')
    
    args = parser.parse_args()
    reader = Reader(args.inputfile, args.outputfile)
    ruleList = reader.createRulesFromFile();
    matrix = Matrix()
    portmatrix = matrix.createMatrix(ruleList)
    if args.outputfile:
        reader.exportToCSV(portmatrix)
    else:
        reader.exportToStdout(portmatrix)
    
   
    
    
    