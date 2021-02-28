""""
Author: Martin SAVESKI
Date: May 2009
License: MIT
AI Agent for Connect Four
ConFour.py
* Evaluation Function - optimized using hash table
* Alpha Beta Pruning Search Algorithm
* Iterative Deepening Search Algorithm
"""

from utils.Con4Utils import *
from utils import c4_math
from time import gmtime

table = [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]]

# table =[]
# for line in open("input.txt"):
#    line=line.strip()
#    table.append([int(c) for c in line])
# print table

# table.reverse()


def d(s):
    return {int(x): int(y) for (x, y) in [z.split(' ') for z in s.split('\n')]}


i4 = [int(i) for i in c4_math.ev_table.split('\n')]
i5 = d(c4_math.v_5ki)
i6 = d(c4_math.v_6ki)
i7 = d(c4_math.v_7ki)


# for li in open("eval/5ki.txt"):
#     tok = li.split()
#     l5[int(tok[0])] = int(tok[1])
# l6 = {}
# for li in open("eval/6ki.txt"):
#     tok = li.split()
#     l6[int(tok[0])] = int(tok[1])
# l7 = {}
# for li in open("eval/7ki.txt"):
#     tok = li.split()
#     l7[int(tok[0])] = int(tok[1])


# Evaluation Method, uses the hash tables to evaluate lines
def t_hash(t):
    resp = 0

    for x in range(6):
        i = 0
        for y in range(0, 7, -1):
            i += (10 ** y) * t[x][6 - y]
        resp += i7[i]

    # resp += i7[1000000*t[0][0] + 100000*t[0][1] + 10000*t[0][2] + 1000*t[0][3] + 100*t[0][4] + 10*t[0][5] + t[0][6]]
    # resp += i7[1000000*t[1][0] + 100000*t[1][1] + 10000*t[1][2] + 1000*t[1][3] + 100*t[1][4] + 10*t[1][5] + t[1][6]]
    # resp += i7[1000000*t[2][0] + 100000*t[2][1] + 10000*t[2][2] + 1000*t[2][3] + 100*t[2][4] + 10*t[2][5] + t[2][6]]
    # resp += i7[1000000*t[3][0] + 100000*t[3][1] + 10000*t[3][2] + 1000*t[3][3] + 100*t[3][4] + 10*t[3][5] + t[3][6]]
    # resp += i7[1000000*t[4][0] + 100000*t[4][1] + 10000*t[4][2] + 1000*t[4][3] + 100*t[4][4] + 10*t[4][5] + t[4][6]]
    # resp += i7[1000000*t[5][0] + 100000*t[5][1] + 10000*t[5][2] + 1000*t[5][3] + 100*t[5][4] + 10*t[5][5] + t[5][6]]

    for y in range(7):
        i = 0
        for x in range(0, 6, -1):
            i += (10 ** x) * t[5 - x][y]
        resp += i6[i]

    # resp += i6[100000*t[0][0] + 10000*t[1][0] + 1000*t[2][0] + 100*t[3][0] + 10*t[4][0] + t[5][0]]
    # resp += i6[100000*t[0][1] + 10000*t[1][1] + 1000*t[2][1] + 100*t[3][1] + 10*t[4][1] + t[5][1]]
    # resp += i6[100000*t[0][2] + 10000*t[1][2] + 1000*t[2][2] + 100*t[3][2] + 10*t[4][2] + t[5][2]]
    # resp += i6[100000*t[0][3] + 10000*t[1][3] + 1000*t[2][3] + 100*t[3][3] + 10*t[4][3] + t[5][3]]
    # resp += i6[100000*t[0][4] + 10000*t[1][4] + 1000*t[2][4] + 100*t[3][4] + 10*t[4][4] + t[5][4]]
    # resp += i6[100000*t[0][5] + 10000*t[1][5] + 1000*t[2][5] + 100*t[3][5] + 10*t[4][5] + t[5][5]]
    # resp += i6[100000*t[0][6] + 10000*t[1][6] + 1000*t[2][6] + 100*t[3][6] + 10*t[4][6] + t[5][6]]

    resp += i6[100000*t[0][0] + 10000*t[1][1] + 1000*t[2][2] + 100*t[3][3] + 10*t[4][4] + t[5][5]]
    resp += i6[100000*t[0][1] + 10000*t[1][2] + 1000*t[2][3] + 100*t[3][4] + 10*t[4][5] + t[5][6]]
    resp += i6[100000*t[5][1] + 10000*t[4][2] + 1000*t[3][3] + 100*t[2][4] + 10*t[1][5] + t[0][6]]
    resp += i6[100000*t[5][0] + 10000*t[4][1] + 1000*t[3][2] + 100*t[2][3] + 10*t[1][4] + t[0][5]]

    resp += i5[10000*t[1][0] + 1000*t[2][1] + 100*t[3][2] + 10*t[4][3] + t[5][4]]
    resp += i5[10000*t[0][2] + 1000*t[1][3] + 100*t[2][4] + 10*t[3][5] + t[4][6]]
    resp += i5[10000*t[4][0] + 1000*t[3][1] + 100*t[2][2] + 10*t[1][3] + t[0][4]]
    resp += i5[10000*t[5][2] + 1000*t[4][3] + 100*t[3][4] + 10*t[2][5] + t[1][6]]

    resp += i4[27*t[0][3] + 9*t[1][4] + 3*t[2][5] + t[3][6]]
    resp += i4[27*t[2][0] + 9*t[3][1] + 3*t[4][2] + t[5][3]]
    resp += i4[27*t[3][0] + 9*t[2][1] + 3*t[1][2] + t[0][3]]
    resp += i4[27*t[5][3] + 9*t[4][4] + 3*t[3][5] + t[2][6]]
    return resp


# valid moves
order = [3, 2, 4, 1, 5, 0, 6]


# Use board[x][-1]
def valid_moves(i):
    global order
    moves = []
    for col in order:
        for row in range(6):
            if i[row][col] == 0:
                moves.append([row, col])
                break
    print(f"valid moves {moves}")
    return moves


# moves in slot x according to valid moves function
def move(intable, x, who):
    val = valid_moves(intable)
    intable[val[x][0]][val[x][1]] = who


# Alpha Beta Pruning Search Algorithm
def ab_prune(intable, depth):
    def ab(intable, depth, alpha, beta):
        values = []
        v = -10000000
        for a, s in valid_moves(intable):
            intable[a][s] = 1
            v = max(v, abmin(intable, depth - 1, alpha, beta))
            values.append(v)
            intable[a][s] = 0
        largest = max(values)
        dex = values.index(largest)
        return [dex, largest]

    def abmax(intable, depth, alpha, beta):
        moves = valid_moves(intable)
        if depth == 0 or not moves:
            return t_hash(intable)

        v = -10000000
        for a, s in moves:
            intable[a][s] = 1
            v = max(v, abmin(intable, depth - 1, alpha, beta))
            intable[a][s] = 0
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def abmin(intable, depth, alpha, beta):
        moves = valid_moves(intable)
        if depth == 0 or not moves:
            return t_hash(intable)

        v = 10000000
        for a, s in moves:
            intable[a][s] = 2
            v = min(v, abmax(intable, depth - 1, alpha, beta))
            intable[a][s] = 0
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    return ab(intable, depth, -10000000, +10000000)


# returns the minutes*60 + seconds in the actual time
def time():
    return ((gmtime()[4]) * 60) + gmtime()[5]


# Iterative Deepening Search Algorithm
def iter_deepening(intable):
    global order
    # order=[3,2,4,1,5,0,6]

    timeout = time() + 19
    depth = 1
    res = ab_prune(intable, depth)
    while True:
        t_start = time()
        if abs(res[1]) > 5000:  # terminal node
            print("Nearly done!")
            return res[0]
        tmp = res[0]
        # changing the order in considering moves
        while tmp != 0:
            order[tmp - 1], order[tmp] = order[tmp], order[tmp - 1]
            tmp -= 1
        depth += 1
        res = ab_prune(intable, depth)
        tEnd = time()
        runTime = tEnd - t_start
        if timeout < tEnd + (4 * runTime) or depth > 42:
            print("DEPTH", depth)
            return res[0]


# GAME
agent, player = 0, 0
first = input("Do you want to play first? (y/n) >> ")

# the player plays first
if first == 'y' or first == 'Y':
    draw(table)
    while valid_moves(table):

        # Begin loop

        n = input("n: ")
        hmove(table, n)
        # draw(table)
        if win(table) == 2:
            player += 1
            draw(table)
            break

        cStart = time()
        # print("Hmmm let me think ?!??!")
        move(table, iter_deepening(table), 1)
        draw(table)
        # print("After ", time() - cStart, " seconds thinking!")
        if win(table) == 1:
            agent += 1
            break


# The AI agent plays first
# else:
#     while valid_moves(table):
#         cStart = time()
#         print("Hmmm let me think ?!??!")
#         move(table, iter_deepening(table), 1)
#         draw(table)
#         print("After ", time() - cStart, " seconds thinking!")
#         if win(table) == 1:
#             agent += 1
#             break
#
#         n = input("n: ")
#         hmove(table, n)
#         draw(table)
#         if win(table) == 2:
#             player += 1
#             break

if agent == player:
    print("DRAW")
else:
    print("AI AGENT ", agent, " : ", player, " PLAYER")
