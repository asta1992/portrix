#!/usr/bin/python3
import sys
import argparse
import requests


class Rule:
    fromsystem = ""
    tosystem = ""
    port = ""

    def __init__(self, fromsystem, tosystem, ports):
        self.fromsystem = fromsystem
        self.tosystem = tosystem
        self.port = self.extractports(ports)

    def extractports(self, ports):
        port = ""
        for s in ports.split(","):
            s = s.replace(" ", "")
            s = s.replace("\n", "")
            port = port + s + ", "
        return port[0:-2]


class Exporter:
    outputfile = ""

    def __init__(self, outputfile):
        self.outputfile = outputfile

    def exporttocsv(self, portmatrix):
        csvstring = self.createoutput(portmatrix)
        try:
            with open(self.outputfile, "w") as text_file:
                text_file.write(csvstring)
        except FileNotFoundError:
            print("ERROR: No such outputfile or directory: " + str(self.outputfile))

    def exporttostdout(self, portmatrix):
        print(self.createoutput(portmatrix))

    def createoutput(self, portmatrix):
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


class Reader:
    inputfile = ""

    def __init__(self, inputfile):
        self.inputfile = inputfile

    def createrulesfromfile(self):
        rulelist = []
        try:
            with open(self.inputfile) as file:
                for line in file:
                    splittedline = line.split("\t")
                    rule = Rule(splittedline[0], splittedline[1], splittedline[2])
                    rulelist.append(rule)
            return rulelist
        except FileNotFoundError:
            print("ERROR: No such inputfile or directory: " + str(self.inputfile))
            sys.exit()


class Matrix:

    def getallsystems(self, rulelist):
        allsystems = set()
        for rule in rulelist:
            allsystems.add(rule.fromsystem)
            allsystems.add(rule.tosystem)
        return sorted(allsystems, key=lambda s: s.lower())

    def creatematrix(self, rulelist):
        allsystems = self.getallsystems(rulelist)

        n = len(allsystems) + 1
        x = 1
        y = 1
        portmatrix = [[""] * n for _ in range(n)]
        for system in allsystems:
            portmatrix[0][x] = system
            portmatrix[y][0] = system
            x += 1
            y += 1
            portmatrix[y - 1][x - 1] = "XX"

        for rule in rulelist:
            row = allsystems.index(rule.fromsystem) + 1
            column = allsystems.index(rule.tosystem) + 1
            if portmatrix[row][column] == "XX":
                print("\n--- Rule to same System are not possible: " + str(rule.fromsystem) + "\t" + str(
                    rule.tosystem) + "\t" + str(rule.port) + "\n")
            else:
                portmatrix[row][column] = portmatrix[row][column] + rule.port + ", "

        return portmatrix


class FortiConnector:
    url = ""
    port = 443
    insecure = True
    token = ""
    rulelist = []

    def __init__(self, url, port, insecure, token):
        self.url = url
        self.port = port
        self.insecure = insecure
        self.token = token

    def getruleset(self):

        endpoint = self.url + ":" + str(self.port) + "/api/v2/cmdb/firewall/policy"
        headers = {"Authorization": "Bearer " + self.token}

        if self.insecure:
            resp = requests.get(endpoint, headers=headers, verify=False)
        else:
            resp = requests.get(endpoint, headers=headers)

        if resp.status_code != 200:
            print("ERROR: Bad request please check input parameter: \n" + "responce code: " + str(resp.status_code) +
                  "\nurl: " + self.url + "\nport: " + self.port +
                  "\ninsecure: " + self.insecure + "\ntoken: " + self.token)

        return self.parse_rules(resp.json()['results'])

    def parse_rules(self, json_rules):
        policyset_list = []
        for policyset in json_rules:
            if policyset['action'] == "accept" and policyset['status'] == "enable":
                for srcaddr in policyset['srcaddr']:
                    for dstaddr in policyset['dstaddr']:
                        service_string = ""
                        for service in policyset['service']:
                            service_string += service['name'] + ","

                        rule = Rule(policyset['srcintf'][0]['name'] + ":" + srcaddr['name'],
                                    policyset['dstintf'][0]['name'] + ":" + dstaddr['name'],
                                    service_string[:-1])

                        policyset_list.append(rule)
        return policyset_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser_name', help='Choose between file and fortigate api input')
    subparser_file = subparsers.add_parser('file')
    subparser_forti = subparsers.add_parser('fortigate')

    # Forti options
    subparser_forti.add_argument('-u', '--url', help='URL to fortigate REST API', required=True)
    subparser_forti.add_argument('-p', '--port', help='Port to fortigate REST API (Default: 443)', type=int,
                                 default=443)
    subparser_forti.add_argument('-k', '--insecure', help='disable tls check', action='store_true')
    subparser_forti.add_argument('-t', '--token', help='Bearer token', required=True)
    subparser_forti.add_argument('-o', '--outputfile', help='Output file name (Default: stdout)', required=False)

    # File options
    subparser_file.add_argument('-i', '--inputfile', help='Input file name', required=True)
    subparser_file.add_argument('-o', '--outputfile', help='Output file name (Default: stdout)', required=False)

    args = parser.parse_args()
    rulelist = []

    if args.subparser_name == "file":
        reader = Reader(args.inputfile)
        rulelist = reader.createrulesfromfile()
    elif args.subparser_name == "fortigate":
        forticonnector = FortiConnector(args.url, args.port, args.insecure, args.token)
        rulelist = forticonnector.getruleset()
    else:
        parser.print_help()
        subparser_file.print_help()
        subparser_forti.print_help()
        sys.exit(1)

    exporter = Exporter(args.outputfile)

    matrix = Matrix()
    portmatrix = matrix.creatematrix(rulelist)
    if args.outputfile:
        exporter.exporttocsv(portmatrix)
    else:
        exporter.exporttostdout(portmatrix)
