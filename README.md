# portrix

Portrix is a small tool to create a portmatrix out of a text file.

-------
Usage
-------
usage: portrix.py [-h] -i INPUTFILE [-o OUTPUTFILE]

optional arguments:
  -h, --help            					show this help message and exit
  -o OUTPUTFILE, --outputfile OUTPUTFILE 	Output file name

required arguments:
  -i INPUTFILE, --inputfile INPUTFILE 		Input file name

--------
Examples
--------
-------------
Input
-------------
```
fw01	fw02	22,443
_Internet	fw01	4443
client01	_Internet	80,443,8081-8090
client02	fw02	443
fw02	client03	3389
```
-------------
Output
-------------
```
;_Internet;client01;client02;client03;fw01;fw02
_Internet;XX;;;;4443, ;
client01;80, 443, 8081-8090, ;XX;;;;
client02;;;XX;;;443, 
client03;;;;XX;;
fw01;;;;;XX;22, 443, 
fw02;;;;3389, ;;XX
```

|           | _Internet            | client01 | client02 | client03 | fw01   | fw02      | 
|-----------|----------------------|----------|----------|----------|--------|-----------| 
| _Internet | XX                   |          |          |          | 4443,  |           | 
| client01  | 80, 443, 8081-8090,  | XX       |          |          |        |           | 
| client02  |                      |          | XX       |          |        | 443,      | 
| client03  |                      |          |          | XX       |        |           | 
| fw01      |                      |          |          |          | XX     | 22, 443,  | 
| fw02      |                      |          |          | 3389,    |        | XX        | 
