from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
import json
import re
import uuid 
import io
import sys
import opcode

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/submit-cp', methods=['POST'])
def submitCp():
    data = request.get_json()
    csvFileName = "/tmp/algoData"+str(uuid.uuid4())+".csv"
    with open (csvFileName, 'w', newline='') as f:
        fieldnames = ['event', 'arg', 'line', 'lasti', 'opcode', 'localObjects']
        writer = csv.writer(f)
        writer.writerow(fieldnames)
    def show_trace(frame, event, arg):
        frame.f_trace_opcodes = True
        code = frame.f_code
        offset = frame.f_lasti
        print(f"| {event:10} | {str(arg):>4} |", end=' ')
        print(f"{frame.f_lineno:>4} | {frame.f_lasti:>6} |", end=' ')
        print(f"{opcode.opname[code.co_code[offset]]:<18} | {str(frame.f_locals):<35} |")
        localObjects = {} 
        for key, value in frame.f_locals.items(): 
            localObjects[key] = str(value) 
        localObjects = json.dumps(localObjects) 
        with open(csvFileName, 'a', newline='') as f: 
            writer = csv.DictWriter(f, fieldnames=fieldnames) 
            writer.writerow({'event': event, 'arg': arg, 'line': frame.f_lineno, 'lasti': frame.f_lasti, 'opcode': opcode.opname[code.co_code[offset]], 'localObjects': localObjects}) 
        return show_trace

    testCaseSplit = data['testCase'].splitlines()
    testCaseString = ''
    for line in testCaseSplit:
        testCaseString += line + '\n' 
    user_input = testCaseString
    saved_stdin = sys.stdin
    sys.stdin = io.StringIO(user_input)
    sys.settrace(show_trace)
    functionString = "def newFunction():\n"
    codeLines = data['code'].splitlines()
    for line in codeLines:
        functionString += '    '+line + '\n'

    functionString += 'newFunction()'
    exec(functionString)

    # print(functionString)
    sys.stdin = saved_stdin
    sys.settrace(None)
    visualList = []
    codeLines = data['code'].splitlines()
    with open(csvFileName, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # check if the line number is valid
            if 51<int(row['line']):
                # codeLinePrior = codeLines[int(row['line'])-3]
                codeLineAt = codeLines[int(row['line'])-52]
                row['codeLineAt'] = codeLineAt
                # row['codeLinePrior'] = codeLinePrior
                # convert row['localObjects'] string to dict
                # row['localObjects'] = json.loads(p.sub('\"', row['localObjects']))
            visualList.append(row)

    os.remove(csvFileName)  
    return {'visualList': visualList}

    


# @app.route('/submit-cp', methods=['POST'])
# def submitCp():
#     data = request.get_json()
    
#     csvFileName = "algoData"+str(uuid.uuid4())+".csv"
#     # create new python file
#     with open('newFile.py', 'w') as f:
        
#         f.write('import sys \n')
#         f.write('import io \n')
#         f.write('import opcode\n')
#         f.write('import uuid \n')
#         f.write('import csv \n')
#         f.write('import json \n')
#         f.write('csvFileName =')
#         f.write('\"'+csvFileName+'\"')
#         f.write(' \n')
#         f.write('with open (csvFileName, \'w\', newline=\'\') as f: \n')
#         f.write('      fieldnames = [\'event\', \'arg\', \'line\', \'lasti\', \'opcode\', \'localObjects\'] \n')
#         f.write('    writer = csv.writer(f) \n')
#         f.write('    writer.writerow(fieldnames) \n')
#         f.write('def show_trace(frame, event, arg):\n')
#         f.write('    frame.f_trace_opcodes = True\n')
#         f.write('    code = frame.f_code\n')
#         f.write('    offset = frame.f_lasti\n')
#         f.write('    print(f"| {event:10} | {str(arg):>4} |", end=\' \')\n')
#         f.write('    print(f"{frame.f_lineno:>4} | {frame.f_lasti:>6} |", end=\' \')\n')
#         f.write('    print(f"{opcode.opname[code.co_code[offset]]:<18} | {str(frame.f_locals):<35} |")\n')
#         f.write('    localObjects = {} \n')
#         f.write('    for key, value in frame.f_locals.items(): \n')
#         f.write('       localObjects[key] = str(value) \n')
#         f.write('    localObjects = json.dumps(localObjects) \n')
#         f.write('    with open(csvFileName, \'a\', newline=\'\') as f: \n')
#         f.write('       writer = csv.DictWriter(f, fieldnames=fieldnames) \n')
#         f.write('       writer.writerow({\'event\': event, \'arg\': arg, \'line\': frame.f_lineno, \'lasti\': frame.f_lasti, \'opcode\': opcode.opname[code.co_code[offset]], \'localObjects\': localObjects}) \n') 
#         f.write('    return show_trace\n')
#         f.write('user_input = "')
#         # split data['testCase'] based on line breaks
#         testCaseSplit = data['testCase'].splitlines()
#         testCaseString = ''
#         # add each line to user_input
#         for line in testCaseSplit:
#             testCaseString += line + '\\n'
#         f.write(testCaseString)
#         f.write('" \n')
#         f.write('saved_stdin = sys.stdin \n')
#         f.write('sys.stdin = io.StringIO(user_input) \n')
#         f.write('sys.settrace(show_trace) \n')
#         # convert data['code'] into a function and write it to file
#         f.write('def newFunction():\n')
#         codeLines = data['code'].splitlines()
#         for line in codeLines:
#             f.write('    ' + line + '\n')
#         f.write('newFunction() \n')
#         f.write('\n')
#         f.write('sys.settrace(None) \n')
#         f.write('sys.stdin = saved_stdin \n')

#     # run newFile.py
#     os.system('python3 newFile.py')

#     visualList = []
#     codeLines = data['code'].splitlines()
#     with open(csvFileName, 'r') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             # check if the line number is valid
#             if 31<int(row['line']):
#                 # codeLinePrior = codeLines[int(row['line'])-3]
#                 codeLineAt = codeLines[int(row['line'])-32]
#                 row['codeLineAt'] = codeLineAt
#                 # row['codeLinePrior'] = codeLinePrior
#                 # convert row['localObjects'] string to dict
#                 # row['localObjects'] = json.loads(p.sub('\"', row['localObjects']))
#             visualList.append(row)


#     return {'visualList': visualList}

if __name__ == '__main__':
    app.run()
