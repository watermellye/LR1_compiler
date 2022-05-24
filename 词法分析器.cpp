#include <bits/stdc++.h>

#include <regex>
using namespace std;

void err(string s) {
    cout << "\nERROR: " << s << endl;
    exit(0);
}

int cnt;  // 当前终结符标号到哪里。
map<string, int> word;
string wordList[] = {"!=", "(",  ")", "*",  "+", ",",  "-",    "/",  "+=",  "-=",    "*=",     "/=",   "%=",    "^=", "&=", "|=", ";",
                     "<",  "<=", "=", "==", ">", ">=", "else", "if", "int", "float", "return", "void", "while", "{",  "}",  "||", "&&"};

void init() {
    cnt = 70;
    for (auto i : wordList) word[i] = ++cnt;
}

ofstream program("intermediate\\processed_sourceCode.txt");
ofstream iden("intermediate\\names.txt");
// string newProgram = "";

//查找保留字
int searchReserve(string s) {
    auto iter = word.find(s);
    return (iter != word.end()) ? iter->second : -1;  //若成功查找，则返回种别码；否则返回100，代表查找不成功，即为标识符
}

// 分析子程序，算法核心
// 输入：待分析字符串和当前指针
// 输出：当前提出的字符群token以及其属于的类型syn
void Scanner(string resProgram, int &pointer) {
    int syn = 0;
    string token = "";
    char ch;  //作为判断使用
    ch = resProgram[pointer];
    while (ch == ' ') ch = resProgram[++pointer];  //过滤空格，防止程序因识别不了空格而结束
    if (isalpha(resProgram[pointer]) || isdigit(resProgram[pointer])) {
        if (isalpha(resProgram[pointer])) {                                                                       //开头为字母，后跟字母或数字
            while (isalpha(resProgram[pointer]) || isdigit(resProgram[pointer])) token += resProgram[pointer++];  //收集，然后下移
            syn = searchReserve(token);                                                                           // 查表，若是保留字或已出现过的终结符，返回种别码；
            if (syn == -1) {
                iden << token << endl;
                token = "identifier";
            }
            // 若无，说明是标识符。
        } else {
            while (isdigit(resProgram[pointer])) token += resProgram[pointer++];  //开头为数字，后跟数字。
            syn = searchReserve(token);
            if (syn == -1) {
                iden << token << endl;
                token = "number";
            }
        }

        // word[token] = syn = ++cnt;  // 否则，加入终结符表。
    } else {  // 开头为其它字符
        token = resProgram[pointer];
        token += resProgram[pointer + 1];
        if ((syn = searchReserve(token)) != -1) {  // != <= == >=
            pointer += 2;
        } else {
            token = resProgram[pointer];
            if ((syn = searchReserve(token)) != -1) {  // ( ) * + , - / ; < >
                pointer += 1;
            } else
                err("unknown character " + to_string(int(token[0])) + " " + token);
        }
    }
    program << token << endl;
    // newProgram += char(syn);
}

//编译预处理，取出无用的字符和注释
string filterResource(string r) {
    r = regex_replace(r, regex("(\\s){2,}"), " ");  // 删除多余空格

    // 虽然注释也可以通过正则去掉，但是还是手动写了。
    string filStr = "";
    for (int i = 0; i <= r.length(); i++) {
        if (r[i] == '/' && r[i + 1] == '/')  // 单行注释去除[注释符//, 回车换行]
            while (r[i] != '\n') i++;
        if (r[i] == '/' && r[i + 1] == '*') {  // 多行注释去除[/* , */]
            i += 2;
            while (i + 1 < r.length() && (r[i] != '*' || r[i + 1] != '/')) ++i;
            if (i + 1 >= r.length()) err("没有找到 */");
            i += 2;
        }
        filStr += r[i];
    }

    filStr = regex_replace(filStr, regex("[\n\t\v\r]"), "");  // 过滤无用字符

    return filStr;
}

int main() {
    // 读入程序
    ifstream t("input\\源程序.txt");
    string str((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());

    //对源程序进行过滤
    string resProgram = filterResource(str);

    init();           // 加载保留字表、界符运算符表
    int pointer = 0;  // 源程序指针
    while (pointer < resProgram.length()) {
        Scanner(resProgram, pointer);
        if (!resProgram[pointer]) break;
    }

    for (auto i : word) {
        printf("%03d  ", i.second);
        cout << i.first << endl;
    }
    return 0;
}