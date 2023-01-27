import flask
from flask import Flask ,request
import logging
import json
import math
from datetime import datetime



def get_log_ind(req):
    ind_logger = logging.getLogger("independent-logger")
    ind_logger.setLevel(logging.DEBUG)
    if not getattr(ind_logger, 'handler_set', None):
       indfileHandler = logging.FileHandler('independent.log')
       indformatter = logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req}")
       indfileHandler.setFormatter(indformatter)
       ind_logger.addHandler(indfileHandler)
    return ind_logger

def get_log_req(req):
    req_logger = logging.getLogger("request-logger")
    req_logger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler('requests.log')
    formatter = logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request # {req}")
    fileHandler.setFormatter(formatter)
    req_logger.addHandler(fileHandler)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request # {req}")
    console.setFormatter(formatter)
    req_logger.addHandler(console)
    return req_logger

def get_log_stack(req):
    stack_logger = logging.getLogger("stack-logger")
    stack_logger.setLevel(logging.INFO)
    stackfileHandler = logging.FileHandler('stack.log')
    stackformatter = logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req}")
    stackfileHandler.setFormatter(stackformatter)
    stack_logger.addHandler(stackfileHandler)
    return stack_logger
def valid_oprator(opr):
    res = opr.lower()
    if res == "plus" or res == "minus" or res == "times" or res == "divide" or res == "pow" or res == "abs" or res == "fact":
        return res
    else:
        return "error"
def calc2(numbers , op,isStack):
    if isStack:
        num1 = numbers.pop()
        num2 = numbers.pop()
    else:
        num1 = numbers[0]
        num2 = numbers[1]
    if op == "plus" :
        return num1 + num2
    elif op == "minus":
        return num1 - num2
    elif op == "times":
        return num1 * num2
    elif op == "divide":
        if num2 == 0:
            return "Error while performing operation Divide: division by 0"
        return int(num1 / num2)
    elif op == "pow" :
        return int(math.pow(num1,num2))
def calc1(numbers,op) :
    if op == "abs" :
        num1 = numbers.pop()
        if num1 < 0:
            return num1 * -1
        else:
            return num1
    else:
        num1 = numbers.pop()
        if num1 < 0:
            return "Error while performing operation Factorial: not supported for the negative number"
        return math.factorial(num1)
def valid_numbers(numbers,op,is_stack):
    if op == "plus" or op == "minus" or op == "times" or op == "divide" or op == "pow" :

        if len(numbers) < 2 :
                return "Error: Not enough arguments to perform the operation " + op
        elif len(numbers) > 2 and is_stack == False:
                return "Error: Too many arguments to perform the operation " + op
        else:
            return "valid"
    else:

        if len(numbers) > 1 and is_stack == False :
                return "Error: Too many arguments to perform the operation " + op
        elif len(numbers) < 1 :
                return "Error: Not enough arguments to perform the operation " + op
        else:
            return "valid"


app = Flask(__name__)
print("server up....")
stack = []
req_num = 0
req_logger = get_log_req(req_num)
ind_logger = get_log_ind(req_num)
stack_logger = get_log_stack(req_num)
@app.route('/independent/calculate', methods = ['POST'])
def ind_clc():
    global req_num
    req_num += 1
    reponse = {}
    st_code = 200

    time1 = datetime.now()
    info_message = f"Incoming request | # {req_num} | resource: /independent/calculate | HTTP Verb POST"
    req_logger.handlers[0].setFormatter(logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.handlers[1].setFormatter(logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    ind_logger.handlers[0].setFormatter(logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.info(info_message)



    final_data = json.loads(request.data.decode())
    num_arr = final_data["arguments"]
    op = final_data["operation"]
    final_op = valid_oprator(op)
    if final_op == "error":
        reponse["error-message"] = "Error: unknown operation: " + op
        ind_message = "Server encountered an error ! message: error-message: Error: unknown operation: " + op
        ind_logger.error(ind_message)
        st_code = 409
    else:
        valid_n = valid_numbers(num_arr, final_op,False)
        if valid_n != "valid":
            reponse["error-message"] = valid_n
            ind_message = "Server encountered an error ! message: error-message: " + valid_n
            ind_logger.error(ind_message)
            st_code = 409
        else:
            if len(num_arr) == 2:
                res = calc2(num_arr, final_op,False)
                if res == "Error while performing operation Divide: division by 0":
                    reponse["error-message"] = res
                    ind_message = "Server encountered an error ! message: error-message: " + res
                    ind_logger.error(ind_message)
                    st_code = 409
                else:
                    reponse["result"] = res
                    sarr = [str(a) for a in num_arr]
                    ind_message_info = f"Performing operation {final_op}. Result is {res}"
                    ind_message_debug =f"Performing operation: {final_op}({', '.join(sarr)}) = {res}"
                    ind_logger.info(ind_message_info)
                    ind_logger.debug(ind_message_debug)
            else:
                res = calc1(num_arr, final_op)
                if res == "Error while performing operation Factorial: not supported for the negative number":
                    reponse["error-message"] = res
                    ind_message = "Server encountered an error ! message: error-message: " + res
                    ind_logger.error(ind_message)
                    st_code = 409
                else:
                    reponse["result"] = res
                    sarr = [str(a) for a in num_arr]
                    ind_message_info = f"Performing operation {final_op}. Result is {res}"
                    ind_message_debug = f"Performing operation: {final_op}({', '.join(sarr)}) = {res}"
                    ind_logger.info(ind_message_info)
                    ind_logger.debug(ind_message_debug)

    time2 = datetime.now()
    timedif = time2-time1
    debug_message =f"request  # {req_num} duration: {timedif.total_seconds()*1000}ms"
    req_logger.debug(debug_message)


    return flask.make_response(json.dumps(reponse),st_code)

@app.route('/stack/size', methods = ['GET'])
def stack_size():
    global req_num
    req_num += 1
    time1 = datetime.now()
    req_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.handlers[1].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    stack_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    info_message = f"Incoming request | # {req_num} | resource: /stack/size | HTTP Verb GET"
    req_logger.info(info_message)
    stack_info_message =f"Stack size is {len(stack)}"
    stack_logger.info(stack_info_message)
    print_arr = []
    for num in stack:
        print_arr.insert(0, num)
    stack_debug_message =f"Stack content (first == top): {print_arr}"
    stack_logger.debug(stack_debug_message)
    reponse = {}
    reponse["result"] = len(stack)

    time2 = datetime.now()
    timedif = time2 - time1
    debug_message = f"request  # {req_num} duration: {timedif.total_seconds() * 1000}ms"
    req_logger.debug(debug_message)
    return flask.make_response(json.dumps(reponse),200)

@app.route('/stack/arguments', methods = ['PUT'])
def push_args():
    global req_num
    req_num += 1
    time1 = datetime.now()
    req_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.handlers[1].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    stack_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    info_message = f"Incoming request | # {req_num} | resource: /stack/arguments | HTTP Verb PUT"
    req_logger.info(info_message)

    reponse = {}
    data = json.loads(request.data.decode())
    num_arr = data["arguments"]
    print_arr =[]
    cur_stack_size = len(stack)
    for num in num_arr :
        stack.append(num)
        print_arr.insert(0,num)
    reponse["result"] = len(stack)
    stack_info_message = f"Adding total of {len(num_arr)} argument(s) to the stack | Stack size: {len(stack)}"
    stack_logger.info(stack_info_message)
    stack_debug_message = f"Adding arguments: {num_arr} | Stack size before {cur_stack_size} | stack size after {len(stack)}"
    stack_logger.debug(stack_debug_message)
    time2 = datetime.now()
    timedif = time2 - time1
    debug_message = f"request  # {req_num} duration: {timedif.total_seconds() * 1000}ms"
    req_logger.debug(debug_message)
    return flask.make_response(json.dumps(reponse),200)
@app.route('/stack/operate', methods = ['GET'])
def oper():
    global req_num
    req_num += 1
    time1 = datetime.now()
    req_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.handlers[1].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    stack_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    info_message = f"Incoming request |# {req_num} | resource: /stack/operate | HTTP Verb GET"
    req_logger.info(info_message)


    reponse = {}
    st_code = 200
    op = request.args.to_dict().get("operation")
    final_op = valid_oprator(op)
    if final_op == "error":
        reponse["error-message"] = "Error: unknown operation: " + op
        st_code = 409
        stack_erorr_message = "Server encountered an error ! message: " + "Error: unknown operation: " + op
        stack_logger.error(stack_erorr_message)
    else:
        valid_n = valid_numbers(stack, final_op,True)
        if valid_n != "valid":
            reponse["error-message"] = valid_n
            st_code = 409
            stack_erorr_message = "Server encountered an error ! message: " + valid_n
            stack_logger.error(stack_erorr_message)
        else:
            debug_arr =[]
            if len(stack) >= 2 and (final_op == "plus" or final_op == "minus" or final_op == "times" or final_op == "divide" or final_op == "pow") :
                debug_arr.append(stack[len(stack)-2])
                debug_arr.append(stack[len(stack)-1])
                res = calc2(stack, final_op,True)
                if res == "Error while performing operation Divide: division by 0":
                    reponse["error-message"] = res
                    st_code = 409
                    stack_erorr_message = "Server encountered an error ! message: " + res
                    stack_logger.error(stack_erorr_message)
                else:
                    reponse["result"] = res
                    stack_info_message = f"Performing operation {final_op}. Result is {res} | stack size: {len(stack)}"
                    stack_logger.info(stack_info_message)
                    sarr = [str(a) for a in debug_arr]
                    stack_debug_message = f"Performing operation: {final_op}({', '.join(sarr)}) = {res}"
                    stack_logger.debug(stack_debug_message)
            else:
                debug_arr.append(stack[len(stack) - 1])
                res = calc1(stack, final_op)
                if res == "Error while performing operation Factorial: not supported for the negative number":
                    reponse["error-message"] = res
                    st_code = 409
                    stack_erorr_message = "Server encountered an error ! message: " + res
                    stack_logger.error(stack_erorr_message)
                else:
                    reponse["result"] = res
                    stack_info_message = f"Performing operation {final_op}. Result is {res} | stack size: {len(stack)}"
                    stack_logger.info(stack_info_message)
                    sarr = [str(a) for a in debug_arr]
                    stack_debug_message = f"Performing operation: {final_op}({', '.join(sarr)}) = {res}"
                    stack_logger.debug(stack_debug_message)

    time2 = datetime.now()
    timedif = time2 - time1
    debug_message = f"request  # {req_num} duration: {timedif.total_seconds() * 1000}ms"
    req_logger.debug(debug_message)

    return flask.make_response(json.dumps(reponse), st_code)

@app.route('/stack/arguments', methods = ['DELETE'])
def delete_items():
    global req_num
    req_num += 1
    time1 = datetime.now()
    req_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.handlers[1].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    stack_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    info_message = f"Incoming request | # {req_num} | resource: /stack/arguments | HTTP Verb DELETE"
    req_logger.info(info_message)

    reponse = {}
    st_code = 200
    num_to_del = int(request.args.to_dict().get("count"))
    if num_to_del > len(stack):
        reponse["error-message"] = f"Error: cannot remove {num_to_del} from the stack. It has only {len(stack)} arguments"
        stack_error_message = f"Server encountered an error ! message: " + reponse["error-message"]
        stack_logger.error(stack_error_message)
        st_code = 409
    else:
        for i in range(0,num_to_del) :
            stack.pop()
        reponse["result"] = len(stack)
        stack_info_message = f"Removing total {num_to_del} argument(s) from the stack | Stack size: {len(stack)}"
        stack_logger.info(stack_info_message)

    time2 = datetime.now()
    timedif = time2 - time1
    debug_message = f"request  # {req_num} duration: {timedif.total_seconds() * 1000}ms"
    req_logger.debug(debug_message)
    return flask.make_response(json.dumps(reponse), st_code)

@app.route('/logs/level', methods = ['GET'])
def get_level():
    global req_num
    req_num += 1
    time1 = datetime.now()
    req_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.handlers[1].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    stack_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    info_message = f"Incoming request |# {req_num} | resource: /logs/level | HTTP Verb GET"
    req_logger.info(info_message)
    name = request.args.to_dict().get("logger-name")
    time2 = datetime.now()
    timedif = time2 - time1
    debug_message = f"request  # {req_num} duration: {timedif.total_seconds() * 1000}ms"
    req_logger.debug(debug_message)
    if name == "request-logger" or name == "stack-logger" :
        return "Success: INFO"
    elif name == "independent-logger":
        return "Success: DEBUG"
    else:
        return "Failure: no such logger exists"


@app.route('/logs/level', methods=['PUT'])
def set_level():
    global req_num
    req_num += 1
    time1 = datetime.now()
    req_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    req_logger.handlers[1].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    stack_logger.handlers[0].setFormatter(
        logging.Formatter(f"%(asctime)s %(levelname)s: %(message)s | request #{req_num}"))
    info_message = f"Incoming request |# {req_num} | resource: /logs/level | HTTP Verb PUT"
    req_logger.info(info_message)
    name = request.args.to_dict().get("logger-name")
    level = request.args.to_dict().get("logger-level")
    time2 = datetime.now()
    timedif = time2 - time1
    debug_message = f"request  # {req_num} duration: {timedif.total_seconds() * 1000}ms"
    req_logger.debug(debug_message)
    if level != "ERROR" and level != "INFO" and level != "DEBUG" :
        return "Failure: no such level exsits!"
    if name == "request-logger" :
        req_logger.setLevel(level)
        return "Success:" + level
    elif name == "stack-logger" :
        stack_logger.setLevel(level)
        return "Success:" + level
    elif name == "independent-logger":
        ind_logger.setLevel(level)
        return "Success:" + level
    else:
        return "Failure: no such logger exsits!"








if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=9285)
