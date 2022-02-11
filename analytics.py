import re

sample = '''
Wordle 215 4/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
🟩🟩🟩🟩🟩
-
Wordle 216 6/6

🟩⬛⬛⬛⬛
🟩🟩⬛⬛⬛
🟩🟩🟨🟩⬛
🟩🟩🟩🟩🟩
'''.split("-")[0].strip()
print(sample)

def is_wordle_share(msg: str):
    return re.match('Wordle \d\d\d .\/\d\n\n[⬛⬜🟩🟨]{5}', msg)

# isWordlePost = 
# print(isWordlePost)
# if isWordlePost is not None:
#     # break up string by line
#     wordlePost = sample.split('\n')
    
#     wPostNumber = wordlePost[0][7:10]
#     # cast the score to an int
#     wPostScore = wordlePost[0][11]
#     if wPostScore == 'X':
#         wPostScore = 7
#     else:
#         wPostScore = int(wPostScore)
    
#     attemptArrayInt = []
#     attemptSet = []

#     i = 2
#     while i < len(wordlePost):
#         # word row count stats
#         countB = wordlePost[2].count('⬛') + wordlePost[2].count('⬜')
#         countY = wordlePost[2].count('🟨')
#         countG = wordlePost[2].count('🟩')

#         arrayRes = []
#         for c in wordlePost[i]:
#             if c == '⬛' or c == '⬜':
#                 arrayRes.append(0)
#             elif c == '🟨':
#                 arrayRes.append(1)
#             elif c == '🟩':
#                 arrayRes.append(2)
#         print(arrayRes, countB, countY, countG)
#         # attemptRow = WordAttempt(arrayRes, countB, countY, countG)
#         # attemptSet.append(attemptRow)
#         # attemptArrayInt.append(arrayRes)
#         i+= 1
