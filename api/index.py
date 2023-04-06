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
    # get file path to tmp folder in root directory
    
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    csvFileName = "../../../tmp/algoData"+str(uuid.uuid4())+".csv"
    print('csvFileName: ', csvFileName)
    with open(csvFileName, 'w', newline='') as f:
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
            # if 62<int(row['line']):
            #     # codeLinePrior = codeLines[int(row['line'])-3]
            #     codeLineAt = codeLines[int(row['line'])-63]
            #     row['codeLineAt'] = codeLineAt
            #     row['codeLinePrior'] = codeLinePrior
            #     # convert row['localObjects'] string to dict
            row['localObjects'] = json.loads(p.sub('\"', row['localObjects']))
            visualList.append(row)

    os.remove(csvFileName)  
    return {'visualList': visualList}

if __name__ == '__main__':
    app.run()
