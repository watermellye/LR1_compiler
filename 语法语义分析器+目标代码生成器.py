import json

start_symbol = ""  # 初始符号
symbol = set()  # 所有符号集合
terminal_symbol = set()  # 终结符集合
non_terminal_symbol = set()  # 非终结符集合

产生式 = []  # {'left': "S'", 'right': ['S']}
项目 = []  # {'left': "S'", 'right': ['S'], 'point': 0}
新项目 = []  # {'left': "S'", 'right': ['S'], 'point': 0, "origin": 0, "accept": "#"}
首项 = {}  # 每个非终结符B的形如B→·C的产生式的序号 首项['S']={2, 5}

closure = []  # 每个项目的闭包 closure[0]={0, 2, 5, 7, 10}
closureSet = []  # 项目集族 closureSet[0]={0, 2, 5, 7, 10}

goto = []  # go[状态i][符号j] 该数组依次存储了不同内容，分别为：
# = Closure{项目x, 项目y}
# = {项目x, 项目y, 项目z}
# = 状态k
# 进入Action/Goto环节后，go函数会被转换为goto函数
# goto[状态i][符号j]=0:accept / +x:移进字符和状态x（sx）/ -x:用产生式x归约（rx）/ 无定义:err

first = {}  # first['F']={'(', 'a', 'b', '^'}
first_empty = []  # first集中含有空的非终结符集合 {"E'", "T'", "F'"}

gotoFile = open(r'output\\goto.txt', 'w', encoding="utf-8")
firstFile = open(r'output\\first.txt', 'w', encoding="utf-8")
productionFile = open(r'output\\production.txt', 'w', encoding="utf-8")
closureFile = open(r'output\\closure.txt', 'w', encoding="utf-8")
lrFile = open(r'output\\lr.txt', 'w', encoding="utf-8")
analyzeFile = open(r'output\\analyze.txt', 'w', encoding="utf-8")
xmjzFile = open(r'output\\xmjz.txt', 'w', encoding="utf-8")
emitFile = open(r'output\\emit.txt', 'w', encoding="utf-8")
varFile = open(r'output\\var.txt', 'w', encoding="utf-8")
object_codeFile = open(r'output\\object_code.asm', 'w', encoding="utf-8")


# 传入项目集(列表，内含项目编号)，推得其closure；判断是否已存在
# 若不存在，命名新项目集族，并求Goto。
def find_Goto(i):
    global symbol, closure
    # print(i)
    for j in closureSet[i]:
        # print("  ", j)
        item = 新项目[j]
        try:
            nowCharacter = item["right"][item["point"]]
            if nowCharacter in goto[i]:
                goto[i][nowCharacter].append(j + len(terminal_symbol))
            else:
                goto[i][nowCharacter] = [j + len(terminal_symbol)]
        except:
            pass
    for j in symbol:
        if j in goto[i]:  # goto(i, j)
            newSet = set()
            for itemOrd in goto[i][j]:
                newSet |= closure[itemOrd]
            print("Goto(I%d,%s) = Closure(" % (i, j), goto[i][j], ') =', newSet, "={", end=" ", file=gotoFile)
            for k in newSet:
                print(新项目[k]["left"], "->", ''.join(新项目[k]["right"]), ",", 新项目[k]["accept"], end=" ", sep="", file=gotoFile)
            print("}", end=" ", file=gotoFile)
            # print("len(ClosureSet)=", len(closureSet))
            if newSet in closureSet:
                goto[i][j] = closureSet.index(newSet)
            else:
                closureSet.append(newSet)
                goto.append({})
                goto[i][j] = len(closureSet) - 1
            print('= I', goto[i][j], sep="", file=gotoFile)
    print(i, closureSet[i], file=xmjzFile)


# 求项目i的Closure
def find_closure(i, ini):
    # print("find_closure", i)
    global closure
    # if len(closure[i]) > 0:
    #    return closure[i]

    item = 新项目[i]
    try:
        nowCharacter = item["right"][item["point"]]
        beta = ""
        alpha = item["accept"]
        fir = set()
        try:
            beta = item["right"][(item["point"] + 1):]
            beta += [alpha]
            for sym in beta:
                fir |= first[sym]
                if sym not in first_empty:
                    break
        except:
            fir = set(alpha)
        if nowCharacter in 首项:
            for j in 首项[nowCharacter]:
                if j not in closure[ini] and 新项目[j]["accept"] in fir:
                    # print(j)
                    closure[i].add(j)
                    closure[ini].add(j)
                    closure[i] |= find_closure(j, ini)
    except:
        closure[i].add(i)
        return {i}
    return closure[i]


with open("input\产生式.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip().replace('\n', ' ')
        # print(line)
        if line == "":
            continue
        line = line.split(':')
        if len(line) < 3:
            continue
        terminal_symbol.add(line[1])
        symbol.add(line[1])
        if line[2] == '$':
            产生式.append({"left": line[1], "right": [], "order": int(line[0])})
        else:
            产生式.append({"left": line[1], "right": line[2].split(' '), "order": int(line[0])})
            symbol |= (set(line[2].split(' ')))

start_symbol = 产生式[0]["left"]
symbol |= terminal_symbol
symbol -= {''}
terminal_symbol -= {''}
non_terminal_symbol = terminal_symbol
terminal_symbol = symbol - non_terminal_symbol
terminal_symbol |= {'#'}

# print(产生式)

# 求First集
for item in non_terminal_symbol:
    first[item] = set()
for item in terminal_symbol:
    first[item] = {item}

bfs = []
for item in 产生式:
    try:
        sym = item["right"][0]
        if sym in terminal_symbol:
            first[item["left"]].add(sym)
    except:
        first_empty.append(item["left"])
        bfs.append(item["left"])

import copy

proCopy = copy.deepcopy(产生式)
while len(bfs) > 0:
    sym = bfs.pop(-1)
    for i, item in zip(range(len(proCopy)), proCopy):
        if item["left"] == sym:
            proCopy[i]["right"] = []
        elif sym in item["right"]:
            proCopy[i]["right"].remove(sym)
            if len(proCopy[i]["right"]) == 0:
                if item["left"] not in first_empty:
                    first_empty.append(item["left"])
                    bfs.append(sym)

print(first_empty, file=firstFile)

f = 1
while f:
    f = 0
    for item in 产生式:
        for sym in item["right"]:
            if not first[item["left"]].issuperset(first[sym]):
                f = 1
                first[item["left"]] |= first[sym]
            if sym not in first_empty:
                break
    # print(first, "\n")

for item in non_terminal_symbol:
    print("%s\n%s" % (item, " ".join(list(first[item]))), " $" if item in first_empty else "", "\n", file=firstFile)

# 从产生式生成项目
for order, i in zip(range(len(产生式)), 产生式):
    for j in range(len(i["right"]) + 1):
        项目.append({"left": i["left"], "right": i["right"], "order": i["order"], "point": j, "origin": order, "isTer": (j == len(i["right"]))})

# 从项目生成带接受符号的项目
for i, item in zip(range(len(项目)), 项目):
    for sym in terminal_symbol:
        closure.append(set())
        新项目.append(copy.deepcopy(item))
        新项目[-1]["accept"] = sym

# 记录首项
for i, item in zip(range(len(新项目)), 新项目):
    if item["point"] == 0:
        if item["left"] in 首项:
            首项[item["left"]].add(i)
        else:
            首项[item["left"]] = {i}

print("项目：\n", 项目, "\n", file=productionFile)
print("新项目：\n", 新项目, "\n", file=productionFile)
print("原点在开头的产生式编号：\n", 首项, "\n", file=productionFile)

# print(新项目)

# 求每个项目的闭包
print("单个项目的闭包：", file=closureFile)
for i, item in zip(range(len(新项目)), 新项目):
    print("%-4d " % i, item, file=closureFile)
    closure[i].add(i)
    closure[i] = find_closure(i, i)
    if item["origin"] == 0 and item["accept"] == '#' and item["point"] == 0:
        closureSet.append(closure[i])
    print("  ", closure[i], file=closureFile)

# print(closureSet[0])
goto.append({})

print("Goto：", file=gotoFile)
i = 0
while (i < len(closureSet)):
    find_Goto(i)
    i += 1
    print(file=gotoFile)

print("LR(1)分析器：", file=lrFile)
ts = sorted(list(terminal_symbol - {start_symbol}))
nts = sorted(list(non_terminal_symbol - {start_symbol}))
print("   ", '  '.join(map(lambda x: (x + "  ")[:3], ts)), "", '  '.join(map(lambda x: (x + "  ")[:3], nts)), file=lrFile)
for i in range(len(closureSet)):
    print("%-3d" % i, end=" ", file=lrFile)
    for item in closureSet[i]:
        k = item
        item = 新项目[item]
        if item["isTer"] == True:
            if item["accept"] in goto[i]:
                print("Warning:", "%d号项目集族的\t%s\t符号冲突，冲突的产生式为\t%d\t" % (i, item["accept"], k), 新项目[k])
                '''
                print("项目集族为：")
                for t in closureSet[i]:
                    print(t, 新项目[t])
                    '''
            else:
                goto[i][item["accept"]] = -item["origin"]
    for j in ts:
        try:
            if goto[i][j] > 0:
                print("s%-3d" % goto[i][j], end=" ", file=lrFile)
            if goto[i][j] < 0:
                print("r%-3d" % -goto[i][j], end=" ", file=lrFile)
            if goto[i][j] == 0:
                print("acc ", end=" ", file=lrFile)
        except:
            print("    ", end=" ", file=lrFile)
    for j in nts:
        try:
            print("%-4d" % goto[i][j], end=" ", file=lrFile)
        except:
            print("    ", end=" ", file=lrFile)
    print(file=lrFile)

names = ""
with open('intermediate\\names.txt', encoding="utf-8") as f:
    names = f.read()
names = names.strip().replace(' ', "").split('\n')
names = names[::-1]
names = list(filter(lambda x: x != "", names))
# print(names)
inp = ""  # 分析栈
with open("intermediate\\processed_sourceCode.txt", encoding="utf-8") as f:
    inp = f.read()
inp = inp.strip().split('\n')
inp = list(filter(lambda x: x != "", inp))
inp += ['#']
print(inp, "的分析栈：", file=analyzeFile)
statusStack = [0]  # 状态栈
charStack = ['#']  # 输入栈
tempVarCnt = {}
midCode = {}  # 中间代码

pointer = 0
tree = []
for i in range(len(closureSet)):
    tree.append({})


def prin(num, typ, ss=0):
    if ss == 0:
        global attr
        ss = attr[typ]
    if type(num) == int:
        num = charStack[num]
    print(num, ".%s=" % typ, ss, sep="", file=analyzeFile)


def getAttr(nam, dom=None):
    global varStack
    if dom != None:
        if (nam, dom) in varStack:
            return varStack[nam, dom]
        else:
            return None
    global domain
    if (nam, domain) in varStack:
        return varStack[nam, domain]
    elif domain != 0 and (nam, 0) in varStack:
        return varStack[nam, 0]
    else:
        raise RuntimeError("Error: undefined variable %s" % nam)


def emit(*args):
    global emitCount
    # args = list(map(lambda x: str(x), args))
    args = list(args)
    lis = []
    if len(args) == 1:
        lis = [args[0], None, None, None]
    else:
        lis = args[:-1]
        for i in range(4 - len(args)):
            lis.append(None)
        lis.append(args[-1])
    if domain in midCode:
        midCode[domain].append({"form": copy.deepcopy(lis), "show_label": False})
    else:
        midCode[domain] = [{"form": copy.deepcopy(lis), "show_label": False}]
    print("(%-6s , %2d) (" % (str(domain), len(midCode[domain])), str(lis)[1:-1], ")", sep="", file=emitFile)


def getNumType(num):
    return str(type(num))[8:-2]


def newTempVar(typ):
    cnt = 0
    if domain in tempVarCnt:
        cnt = tempVarCnt[domain]
    cnt += 1
    tempVarCnt[domain] = cnt
    cnt = "$%d" % cnt
    varStack[cnt, domain] = {"type": typ, "is_temp": True}
    print("新增临时变量：name=%s, 作用域=%s, type=%s, 临时变量=%s" % (cnt, str(domain), typ, "True"), file=analyzeFile)
    return cnt


def getType(nam, dom=None):
    if nam == None:
        return None
    if type(nam) == str:
        return getAttr(nam, dom)["type"]
    else:
        return getNumType(nam)


def getDomain(nam):
    global domain
    global varStack
    if type(nam) == str:
        if (nam, domain) in varStack:
            return domain
        elif domain != 0 and (nam, 0) in varStack:
            return 0
        else:
            print("Error: undefined variable %s" % nam)
            a = []  # try catch 捕捉到错误，程序停止分析
            print(a[2])
    else:
        return domain


varStack = {}  # varStack[name,作用域] = {type:"int", is_temp=True, value=None}
funStack = {}  # funStack[过程名]= {code:四元式组, var=[接受的参数], ret_type="int"}
procedure = {0: {"type": "void", "param": []}}
procedureSequence = []
domain = 0  # 一个全局变量记录当前作用域，初始为int(0)，为全局；否则为过程名（string）
attrStack = []  # 每个栈里的符号的属性（不同类型的符号记录的属性不同），语义分析用

root = -1
cntNode = -1
nodeStack = []  # 语法树结点 nodeStack[cntNode]["name"]="123" nodeStack[cntNode]["children"]=[1, 2, 3]

print("%-10s %-10s %-10s" % (' '.join(map(lambda x: str(x), statusStack)), ' '.join(charStack), ' '.join(inp[pointer:])), file=analyzeFile)
while True:
    # print(attrStack)
    c = inp[pointer]
    try:
        # print(c)
        # print(statusStack[-1])
        num = goto[statusStack[-1]][c]
        if num == 0:
            print("Accepted", file=analyzeFile)
            tree[statusStack[-1]]["name"] = charStack[-1]
            root = statusStack[-1]
            break
        elif num > 0:  # 移进
            statusStack.append(num)
            # print(num, c)
            tree.append({})
            cntNode += 1
            tree[cntNode]["name"] = c
            nodeStack.append(cntNode)
            attrStack.append({})
            charStack.append(c)
            pointer += 1

            if c in ["identifier", "number"]:
                tree[cntNode]["children"] = [cntNode + 1]
                tree.append({})
                cntNode += 1
                nam = names.pop()
                tree[cntNode]["name"] = nam
                if c == "identifier":
                    attrStack[-1]["name"] = nam
                    print("用identifier归约:", file=analyzeFile)
                    prin(-1, "name", nam)

                elif c == "number":
                    attrStack[-1]["name"] = eval(nam)
                    # attrStack[-1]["type"] = str(type(attrStack[-1]["name"]))[8:-2]
                    print("用number归约:", file=analyzeFile)
                    prin(-1, "name", nam)
                    # prin(-1, "type", attrStack[-1]["type"])

        elif num < 0:
            item = 产生式[-num]  # 用 item 归约
            print("\n用%d号产生式归约:" % (item["order"]), item["left"], "→", " ".join(item["right"]), file=analyzeFile)
            order = item["order"]
            attr = {}
            # 归约前执行的

            if order in [117, 617]:
                attr["name"] = attrStack[-1]["name"]
                prin(-1, "name")
                varStack[attr["name"], domain] = {"type": attrStack[-2]["type"], "is_temp": False}
                print("读入新变量：name=%s, 作用域=%s, type=%s, 临时变量=%s" % (attr["name"], str(domain), str(attrStack[-2]["type"]), "False"), file=analyzeFile)
                if order == 617:
                    procedure[domain]["param"].append(attr["name"])
            elif order == 611:
                pass
            elif order == 118:
                attr["type"] = attrStack[-3]["type"]
                prin(-3, "type")
            elif order == 121:
                attr["name"] = attrStack[-1]["name"]
                prin(-1, "name")
            elif order in [122, 416, 414, 412, 407, 405, 403, 401, 132, 131]:
                attr["name"] = attrStack[-1]["name"]
                prin(-1, "name")
            elif order in [113, 724]:
                attr["name"] = attrStack[-3]["name"]  # a
                prin(-3, "name")
                attr["value"] = attrStack[-1]["name"]  # 5.123 "$1"
                prin(-1, "value")
                attr["type"] = getType(attr["value"])  # float
                prin(-1, "type", attr["type"])
                op = "="
                if order == 724:
                    op = attrStack[-2]["operator"]
                if op == "=":
                    op = ":="
                shouldType = getType(attr["name"])
                if shouldType != attr["type"]:
                    print("Warning: 类型不匹配。变量%s的类型为%s，赋值%s的类型为%s" % (attr["name"], shouldType, str(attr["value"]), attr["type"]))
                # if shouldType == "int":
                #    attr["value"] = int(attr["value"])
                varStack[attr["name"], getDomain(attr["name"])]["value"] = attr["value"]
                # print("(%s,%s).value=%s"%(attr["name"], str(domain), attr["value"]))
                print("(%s,%s).value=%s" % (attr["name"], str(domain), attr["value"]), file=analyzeFile)
                if op == ":=":
                    emit(op, attr["value"], attr["name"])
                elif op[-1] == "=":
                    emit(op[:-1], attr["name"], attr["value"], attr["name"])

            elif order == 602:
                domain = attrStack[-1]["name"]
                procedure[domain] = {"type": attrStack[-2]["type"], "param": []}
                procedureSequence.append(domain)
                midCode[domain] = []
                print("新函数：%s type=%s" % (domain, procedure[domain]["type"]), file=analyzeFile)
            elif order in [411, 413, 402, 404, 406]:
                op = attrStack[-2]["operator"]
                lop = attrStack[-3]["name"]
                ltype = getType(lop)
                rop = attrStack[-1]["name"]
                rtype = getType(rop)
                newTempType = "void"
                if ltype == rtype:
                    newTempType = ltype
                else:
                    newTempType = "float"
                    print("Warning: 类型不匹配。左操作数%s的类型为%s，右操作数%s的类型为%s" % (lop, ltype, rop, rtype))
                if order in [402, 404, 406]:
                    newTempType = "int"
                newTempName = newTempVar(newTempType)
                emit(op, lop, rop, newTempName)
                attr["name"] = newTempName
                prin("expression", "name", newTempName)
            elif order == 415:
                op = "!"
                rop = attrStack[-1]["name"]
                rtype = getType(rop)
                newTempType = "int"
                newTempName = newTempVar(newTempType)
                emit(op, rop, newTempName)
                attr["name"] = newTempName
                prin("!_expression", "name", newTempName)

            elif order in [511, 512, 513, 514]:
                attr["operator"] = charStack[-1]
                prin(-1, "operator", attr["operator"])
            elif order == 731:
                if procedure[domain]["type"] == "void":
                    raise TypeError(f'Error: 过程{domain}类型为{procedure[domain]["type"]}，不需要返回值。')
                typPro = procedure[domain]["type"]
                namExp = attrStack[-2]["name"]
                typExp = getType(namExp)
                if typPro != typExp:
                    print("Warning: 类型不匹配。函数%s的类型为%s，返回值%s的类型为%s" % (str(domain), typPro, namExp, typExp))
                emit("return", namExp)
            elif order == 732:
                if procedure[domain]["type"] != "void":
                    raise TypeError(f'Error: 过程{domain}类型为{procedure[domain]["type"]}，需要返回值。')
                emit("return")
            elif order == 141:
                # print(attrStack[-2]["name"])
                nam = attrStack[-4]["name"]
                if len(attrStack[-2]["name"]) != len(procedure[nam]["param"]):
                    raise IndexError(f'Error: 函数{nam}接受{len(procedure[nam]["param"])}个参数，传入{len(attrStack[-2]["name"])}个。')
                for index, name in enumerate(attrStack[-2]["name"]):
                    if getType(procedure[nam]["param"][index], nam) != getType(name):
                        print(f'Warning: 函数{nam}的第{index+1}个参数类型为{getType(procedure[nam]["param"][index], nam)}，传入了{getType(name)}')
                    emit("param", name, index, nam)
                typ = procedure[nam]["type"]
                if typ != "void":
                    newVarNam = newTempVar(typ)
                    emit("call", nam, newVarNam)
                    attr["name"] = newVarNam
                    prin("function_expression", "name", attr["name"])
                else:
                    emit("call", nam, None, None)
            elif order in [154, 152]:
                attr["name"] = []
                prin("expression_list", "name", attr["name"])
            elif order in [153, 151]:
                # print(attrStack[-1]["name"])
                # print(attrStack[-2]["name"])
                attr["name"] = [attrStack[-2]["name"]] + attrStack[-1]["name"]
                # print(attr["name"])
                prin("expression_list", "name", attr["name"])
            elif order in [723, 726]:  # 参照154
                attr["name"] = []
                prin("assignment_expression_list", "name", attr["name"])
            elif order in [725, 722]:  # 参照153
                attr["name"] = [attrStack[-2]["name"]] + attrStack[-1]["name"]
                prin("assignment_expression_list", "name", attr["name"])

            elif order in [201, 202, 203, 204, 205, 206, 207, 208, 209]:
                attr["operator"] = charStack[-1]
                prin(-1, "operator", attr["operator"])
            elif order in [501, 502, 503, 504, 505, 506, 507, 508]:
                attr["operator"] = charStack[-1]
                prin(-1, "operator", attr["operator"])
            elif order == 123:
                attr["name"] = attrStack[-2]["name"]
                prin(-2, "name")
            elif order == 751:
                emit("j=", attrStack[-2]["name"], 0, "unknown")
                attr["pos"] = len(midCode[domain])
                prin("M_selection_statement", "pos", attr["pos"])
            elif order in [742, 741, 743]:
                if order == 743:
                    emit("j", attrStack[-6]["pos"] + 1)
                midCode[domain][attrStack[-2]["pos"] - 1]["form"][3] = len(midCode[domain]) + 1
                prin("回填", "产生式序号", attrStack[-2]["pos"])
                prin("回填", "值", str(len(midCode[domain]) + 1))
                print("    Modify:(%-6s , %2d) (" % (str(domain), attrStack[-2]["pos"]), str(midCode[domain][attrStack[-2]["pos"] - 1]["form"])[1:-1], ")", sep="", file=emitFile)
            elif order == 752:
                emit("j", "unknown")
                midCode[domain][attrStack[-3]["pos"] - 1]["form"][3] = len(midCode[domain]) + 1
                prin("回填", "产生式序号", attrStack[-3]["pos"])
                prin("回填", "值", str(len(midCode[domain]) + 1))
                print("    Modify:(%-6s , %2d) (" % (str(domain), attrStack[-3]["pos"]), str(midCode[domain][attrStack[-3]["pos"] - 1]["form"])[1:-1], ")", sep="", file=emitFile)
                attr["pos"] = len(midCode[domain])
                prin("N_selection_statement", "pos", attr["pos"])
            elif order == 753:
                attr["pos"] = len(midCode[domain])
                prin("N_iteration_statement", "pos", attr["pos"])

            if item["right"] == []:  # 空
                charStack += [item["left"]]
                statusStack.append(goto[statusStack[-1]][item["left"]])

                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = [cntNode + 1]
                tree[cntNode]["name"] = item["left"]
                nodeStack.append(cntNode)

                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = []
                tree[cntNode]["name"] = ''

            else:
                k = len(item["right"])
                statusStack = statusStack[:-k]
                charStack = charStack[:-k] + [item["left"]]
                statusStack.append(goto[statusStack[-1]][item["left"]])
                # print(statusStack[-1])
                tree.append({})
                cntNode += 1
                tree[cntNode]["children"] = []

                for i in range(k):
                    nowNode = nodeStack.pop()
                    attrStack.pop()
                    tree[cntNode]["children"].append(nowNode)

                tree[cntNode]["children"] = tree[cntNode]["children"][::-1]
                tree[cntNode]["name"] = item["left"]
                nodeStack.append(cntNode)
            # 归约后执行的
            type_specifier = {301: "int", 302: "double", 303: "float", 304: "void"}
            if order in type_specifier:
                typ = type_specifier[order]
                attr["type"] = typ
                prin(-1, "type")
            elif order == 112:
                attr["type"] = attrStack[-1]["type"]
                prin(-1, "type")
            elif order == 601:
                print("%s函数结束，domain=0" % (domain), file=analyzeFile)
                domain = 0

            attrStack.append(attr)
    except Exception as e:
        print("error", file=analyzeFile)
        raise e
    print("%-10s \t\t %-10s \t\t %-10s" % (' '.join(map(lambda x: str(x), statusStack)), ' '.join(charStack), ' '.join(inp[pointer:])), file=analyzeFile)

var_cnt = 0
for item in varStack:
    varStack[item]["pos"] = var_cnt
    var_cnt += 4  # 目前只支持int和float，所以总是+4
    print(item, varStack[item], file=varFile)

# for domain in midCode:
#     if len(midCode[domain]) > 0:
#         midCode[domain][0]["show_label"] = True
for domain in midCode:
    for index, formula in enumerate(midCode[domain]):
        if formula["form"][0][0] == "j":
            try:
                midCode[domain][formula["form"][3] - 1]["show_label"] = True
            except:
                raise RuntimeError(f"{domain} {formula} 跳转定位错误。请检查函数是否缺少了return。")
json.dump(midCode, emitFile, ensure_ascii=False, indent=4)


def outp(now):
    # print(now)
    if not tree[now]:
        return {}
    di = {}
    di["name"] = tree[now]["name"].replace("_", "_  \n") + ' '

    di["children"] = []
    if ("children" not in tree[now]) or (not tree[now]["children"]):
        return di
    for child in tree[now]["children"]:
        di["children"].append(outp(child))

    # print(now, di)
    return di


# print(root)
outpTree = outp(cntNode)
# print(outpTree)

from pyecharts import options as opts
from pyecharts.charts import Tree

treeData = [outpTree]
c = (
    Tree().add(
        "",
        treeData,
        orient="TB",
        initial_tree_depth=-1,
        # collapse_interval=10,
        symbol_size=3,
        is_roam=True,
        edge_shape="polyline",
        # is_expand_and_collapse=False,
        label_opts=opts.LabelOpts(
            position="top",
            horizontal_align="right",
            vertical_align="middle",
            # rotate='15',
            font_size=15)).set_global_opts(title_opts=opts.TitleOpts(title="语法树")).render("output\语法树.html"))

object_code_data = ['.data', f's: .space {len(varStack) * 4}', 'fpconst_0: .float 0 # 一定有，方便float转bool用。']
object_code_text = ['.text', 'b main']
float_const_num = 0  # 当前的浮点常量数
float_const_list = []  # 当前已生成的浮点数索引

debug_object_code = True


def getLabel(float_num):
    global float_const_num
    global float_const_list
    if float_num in float_const_list:
        return f'fpconst_{float_const_list.index(float_num)+1}'
    float_const_num += 1
    float_const_list.append(float_num)
    object_code_data.append(f'fpconst_{float_const_num}: .float {float_num}')
    return f'fpconst_{float_const_num}'


def s2w(x):
    code = []
    if debug_object_code:
        code.append("# float->int")
    code += [f'cvt.w.s $f{x}, $f{x}', f'mfc1, $t{x}, $f{x}']
    return code


def w2s(x):
    code = []
    if debug_object_code:
        code.append("# int->float")
    code += [f'mtc1, $t{x}, $f{x}', f'cvt.s.w $f{x}, $f{x}']
    return code


def prepare_data(var, formula_type, x, some_hash):
    # 根据参数所属类型进行不同操作
    object_code = []
    if var == None:
        return object_code
    try:
        var_type = getType(var)
    except:
        return object_code
    #s = None
    if formula_type == "int":
        s = f'$t{x}'
    if formula_type == "float":
        s = f'$f{x}'
    if formula_type == "bool":
        if var_type == "int":
            s = f'$t{x}'
        if var_type == "float":
            s = f'$f{x}'

    if type(var) == str:  # 变量
        k = getAttr(var)["pos"]
        if var_type == "int":
            object_code.append(f'ld $t{x}, s+{k}' + (f' # int {var} -> $t{x}' if debug_object_code else ""))
        if var_type == "float":
            object_code.append(f'l.s $f{x}, s+{k}' + (f' # float {var} -> $f{x}' if debug_object_code else ""))
    else:  # 常数
        if var_type == "float":
            object_code.append(f'l.s $f{x}, {getLabel(var)}' + (f' # const float {var} -> $f{x}' if debug_object_code else ""))
        elif var_type == "int":
            object_code.append(f'addi $t{x}, $0, {var}' + (f' # const int {var} -> $t{x}' if debug_object_code else ""))
    if var_type == "float" and formula_type == "int":
        object_code += s2w(x)

    if var_type == "float" and formula_type == "bool":
        object_code += [
            f'# float->bool' if debug_object_code else "", f'l.s $f10, fpconst_0', f'c.eq.s $f{x}, $f10 # =0则flag为1', f'bc1t {some_hash}_1 # flag为1则跳转', f'addi $t{x}, $0, 1', f'b {some_hash}_2',
            f'{some_hash}_1:', f'addi $t{x}, $0, 0', f'{some_hash}_2:'
        ]
    if var_type == "int" and formula_type == "float":
        object_code += w2s(x)

    if var_type == "int" and formula_type == "bool":
        object_code.append(f'sne $t{x}, $t{x}, 0' + (f' # int->bool' if debug_object_code else ""))
    return object_code


def save_to_memory(reg_num, paramName, paramType=None):
    if paramType == None:
        paramType = getType(paramName)
    if paramType == "int":
        return [f'sw $t{reg_num}, s+{getAttr(paramName)["pos"]}' + (f' # $t{reg_num} -> int {paramName}' if debug_object_code else "")]
    if paramType == "float":
        return [f's.s $f{reg_num}, s+{getAttr(paramName)["pos"]}' + (f' # $f{reg_num} -> float {paramName}' if debug_object_code else "")]


def type_cast(src, des, reg_num):
    code = []
    if src == "float" and des == "int":
        code += s2w(reg_num)
    if src == "int" and des == "float":
        code += w2s(reg_num)
    return code


for domain in procedureSequence:
    for index, formula in enumerate(midCode[domain]):
        object_code = [""]
        if index == 0:
            object_code += [f'{domain}:']
            param_cnt = len(procedure[domain]["param"]) - 1
            for i, varName in enumerate(procedure[domain]["param"]):
                object_code += [f'lw $t1, {4*(param_cnt-i)}($sp)',
                                f'sw $t1, s+{getAttr(varName)["pos"]}']
            object_code += ['addi $sp, $sp, -4',
                            'sw, $ra, 0($sp)' + (f' # 保存返回地址' if debug_object_code else '')]

        index += 1
        form = formula["form"]
        op = form[0]
        #formula_type = None
        x = form[3]
        y = form[1]
        z = form[2]
        try:
            x_type = getType(x)
        except:
            x_type = None
        try:
            y_type = getType(y)
        except:
            y_type = None
        try:
            z_type = getType(z)
        except:
            z_type = None
        x_actual_type = None
        some_hash = f'{domain}_{index}'
        # 1. 确定formula_type
        if op == ":=":
            formula_type = x_type
            x_actual_type = x_type
        elif op in ['+', '-', '*', '/', "<", ">", "<=", ">=", "!=", "=="]:
            formula_type = "int" if (y_type == "int" and z_type == "int") else "float"
            if op in ['+', '-', '*', '/']:
                x_actual_type = formula_type
            if op in ["<", ">", "<=", ">=", "!=", "=="]:
                x_actual_type = "int"  # bool
        elif op in ['j=']:
            formula_type = "bool"  # 在我们的程序中，永远只和0比较。标记为bool后，会预先将操作数转为0/1。
        elif op in ["^", "&", "|"]:
            if y_type != "int":
                raise TypeError(f'Error: 四元式 {form} 中 {y} 的类型为 {y_type}')
            if z_type != "int":
                raise TypeError(f'Error: 四元式 {form} 中 {z} 的类型为 {z_type}')
            formula_type = "int"
            x_actual_type = "int"
        elif op in ["||", "&&", '!']:
            formula_type = "bool"
            x_actual_type = "int"  # bool
        if formula["show_label"] == True:
            object_code.append(f'{domain}_{index}:')
        if debug_object_code:
            object_code.append(f'# ({domain}, {index:2d}) ({str(form)[1:-1]})' + (f' type={formula_type}' if formula_type != None else ""))

        # 特殊指令
        if op == 'call':  # (call, funcName, -, -/varName)
            funcName = form[1]
            object_code += [
                f'jal {funcName}',
                f'addi $sp, $sp, {4*len(procedure[funcName]["param"])}' + (f' # 恢复sp' if formula_type != None else "")
            ]
            if procedure[funcName]["type"] != "void":
                varName = form[3]
                if varName != None:
                    srcType = procedure[funcName]["type"]
                    desType = getType(varName)
                    reg_num = 1
                    object_code.append(f'move, $t{reg_num}, $v0')  # 从$v0接收返回值
                    if srcType == "float":
                        object_code.append(f'mtc1, $t{reg_num}, $f{reg_num}')
                    type_cast(srcType, desType, reg_num)  # 若类型不同，强转
                    object_code += save_to_memory(reg_num, varName, desType)

        elif op == 'param':  # (param, operand, index, funcName)
            operand = form[1]
            index = form[2]
            funcName = form[3]
            desType = getType(procedure[funcName]["param"][index], funcName)
            reg_num = 1
            object_code += prepare_data(operand, desType, reg_num, some_hash)
            if desType == "float":
                object_code.append(f'mfc1 $t{reg_num} $f{reg_num}')
            object_code += ['addi $sp, $sp, -4',
                            f'sw, $t{reg_num}, 0($sp)' + (f' # PUSH {operand}' if formula_type != None else "")]
        elif op in ['return']:
            operand = form[3]
            if operand != None:  # 带返回值
                desType = procedure[domain]["type"]
                reg_num = 1
                object_code += prepare_data(operand, desType, reg_num, some_hash)
                if desType == "float":
                    object_code.append(f'mfc1 $t{reg_num} $f{reg_num}')
                object_code += [f'move $v0, $t{reg_num}' + (f' # RETURN {operand}' if formula_type != None else "")]
            object_code += [
                'lw $ra, 0($sp)',
                'addi $sp, $sp, 4',
                'jr $ra'
            ]
        else:
            # y对应$t1/$f1 z对应$t2/$f2 x对应$t3/$f3
            reg_num = {}  # 不直接在申明的时候赋值，是因为x/y/z可能为null，也可能相同。
            reg_num[x] = 3
            reg_num[y] = 1
            reg_num[z] = 2
            # 2. 根据参数所属类型进行不同准备操作
            object_code += prepare_data(y, formula_type, reg_num[y], some_hash)
            object_code += prepare_data(z, formula_type, reg_num[z], some_hash)
            code = ""
            reg = {}
            # reg[x] = f'{"f" if x_type == "float" else "t"}{reg_num[x]}'
            reg_type = '$f' if formula_type == "float" else '$t'  # int/bool
            reg[x] = f'{reg_type}{reg_num[x]}'
            reg[y] = f'{reg_type}{reg_num[y]}'
            reg[z] = f'{reg_type}{reg_num[z]}'

            # 3. 执行核心指令
            xx = reg[x]  # 简写
            yy = reg[y]
            zz = reg[z]

            if op == ":=":
                symbol_type = {"int": "e", "float": '.s'}
                code = f'mov{symbol_type[formula_type]} {xx}, {yy}' + (f' # {x} {op} {y}' if debug_object_code else f'')
            elif op in ["+", '-', '*', '/']:
                symbol = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}
                symbol_type = {"int": "", "float": '.s'}
                code = f'{symbol[op]}{symbol_type[formula_type]} {xx}, {yy}, {zz}' + (f' # {x} := {y} {op} {z}' if debug_object_code else f'')
            elif op in ['^', '&', '|']:
                symbol = {'^': 'xor', '&': 'and', '|': 'or'}
                code = f'{symbol[op]} {xx}, {yy}, {zz}' + (f' # {x} := {y} {op} {z}' if debug_object_code else f'')
            elif op in ["||", '&&']:  # formula_type == bool
                symbol = {'&&': 'and', '||': 'or'}
                code = f'{symbol[op]} $t{reg_num[x]}, $t{reg_num[y]}, $t{reg_num[z]}' + (f' # {x} := {y} {op} {z}' if debug_object_code else f'')
            elif op in ["<", '>', '<=', '>=', '!=', '==']:
                if formula_type == "int":
                    symbol = {'<': 'slt', '>': 'sgt', '<=': 'sle', '>=': 'sge', '!=': 'sne', '==': 'seq'}
                    code = f'{symbol[op]} {xx}, {yy}, {zz}' + (f' # {x} := {y} {op} {z}' if debug_object_code else f'')
                if formula_type == "float":
                    symbol = {'<': ['lt', 0], '>': ['le', 1], '<=': ['le', 0], '>=': ['lt', 1], '!=': ['eq', 1], '==': ['eq', 0]}
                    symbol_mean = {'lt': '<', 'le': '<=', 'eq': '=='}
                    code = []
                    if debug_object_code:
                        code.append(f'# {x} := {y} {op} {z}' if debug_object_code else f'')
                    code += [
                        f'c.{symbol[op][0]}.s {yy}, {zz} # f1{symbol_mean[symbol[op][0]]}f2则flag为1',
                        f'bc1t {some_hash}_1 # flag为1则跳转',
                        f'addi $t{reg_num[x]}, $0, {symbol[op][1]}',
                        f'b {some_hash}_2',
                        f'{some_hash}_1:',
                        f'addi $t{reg_num[x]}, $0, {1-symbol[op][1]}',
                        f'{some_hash}_2:',
                    ]
            elif op == "!":  # formula_type == bool
                code = f'xor $t{reg_num[x]}, $t{reg_num[y]}, 1' + (f' # {x} {op} {y}' if debug_object_code else f'')
            elif op in ['j']:
                code = f"b {domain}_{x}" + (f' # goto {domain}_{x}' if debug_object_code else f'')
            elif op in ['j=']:
                code = f'beq {yy}, {zz}, {domain}_{x}' + (f' # if {y} == {z} goto {domain}_{x}' if debug_object_code else f'')

            if type(code) == dict:
                code = code[formula_type]
            if type(code) == list:
                code = "\n".join(code)
            if len(code) > 0:
                object_code.append(code)

        # 4. 将运算结果（若有）存入内存
        if op in [':=', '+', '-', '*', '/', "^", "&", "|", "||", "&&", "<", ">", "<=", ">=", "!=", "==", "!"]:
            type_cast(x_actual_type, x_type, reg_num[x])  # 若类型不同，强转
            object_code += save_to_memory(reg_num[x], x, x_type)

        object_code_text += copy.deepcopy(object_code)
print('\n'.join(object_code_data), file=object_codeFile)
print('\n'.join(object_code_text), file=object_codeFile)
