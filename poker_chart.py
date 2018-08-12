# -*- coding: utf-8 -*-
"""
@author: 
@brief: 
"""

import itertools
import random
import pandas as pd

suits = ['D', 'C', 'H', 'S']
nums = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
deck = list(itertools.product(suits, nums))
random.shuffle(deck)

positions = ['UTG', 'MP', 'CO', 'BUTTON']
statuses = ['OPENING_PLAYER', '1-2_LIMPERS', 'FACING_A_RAISE', 'FACING_A_3BET']
actions = ['R', 'RF', 'C', 'C2', 'F']
call2_desc = 'Call if a call has been made in front of you. Do not call if not.'


def dealing(hand_num):
    hands = deck[:2]
    return hands

def sorting(class_name):
    if class_name in ['TJ', 'TQ', 'TK', 'TA', 'JA', 'QK', 'QA', 'KA']:
        class_name = class_name[::-1]
    return class_name

def classing(hand_list):
    class_name = 'garbage hand'
    if hand_list[0][1] == hand_list[1][1]:
        class_name = '{}{}'.format(hand_list[0][1], hand_list[1][1])
    elif hand_list[0][0] == hand_list[1][0]:
        class_name = '{}{}'.format(hand_list[0][1], hand_list[1][1])
        class_name = ''.join(sorted(list(class_name), reverse=True))
        class_name = sorting(class_name)
        class_name = '{}s'.format(class_name)
    else:
        class_name = '{}{}'.format(hand_list[0][1], hand_list[1][1])
        class_name = ''.join(sorted(list(class_name), reverse=True))
        class_name = sorting(class_name)
    return class_name

def question(hand_list, position, status):
    hand = '{}, {}'.format(''.join(hand_list[0]), ''.join(hand_list[1]))
    q = 'Your hand: {hand}\n'\
        'positon: {position}\n'\
        'status: {status}'.format(hand=hand, position=position, status=status)
    return q

def answer(hand_class, position, status):
    action_df = pd.read_csv('shorthand_chart.csv')
    answer_series = action_df[(action_df['hand']==hand_class) & (action_df['status']==status) & (action_df['position']==position)]['action']
    if answer_series.empty:
        answer = 'F'
    else:
        answer = answer_series.values[0]
    return answer

#-------------------------- Main --------------------------
def main():
    hand_list = dealing(2)
    hand_class = classing(hand_list)
    position = positions[random.randrange(len(positions))]
    status = statuses[random.randrange(len(statuses))]
    question = question(hand_list, position, status)
    answer = answer(hand_class, position, status)
    print ('hands: {}'.format(hand_list))
    print ('class_name: {}'.format(hand_class))
    print ('q: {}'.format(question))
    print ('answer: {}'.format(answer))
    return hand_class, position, status, question, answer

if __name__ == '__main__':
    main()