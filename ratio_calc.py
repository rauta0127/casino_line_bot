import poker_chart
import time
from tqdm import tqdm

count = 10000

answers = []

for i in tqdm(range(count)):
    answer = poker_chart.main()[4]
    answers.append(answer)

print ('Count: {}'.format(count))
print ('R counts: {}, (ratio {}%)'.format(answers.count('R'), int(answers.count('R')*100/count)))
print ('RF counts: {}, (ratio {}%)'.format(answers.count('RF'), int(answers.count('RF')*100/count)))
print ('C counts: {}, (ratio {}%)'.format(answers.count('C'), int(answers.count('C')*100/count)))
print ('C2 counts: {}, (ratio {}%)'.format(answers.count('C2'), int(answers.count('C2')*100/count)))
print ('F counts: {}, (ratio {}%)'.format(answers.count('F'), int(answers.count('F')*100/count)))