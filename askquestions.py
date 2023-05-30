import awnserQuestion
import readCSVfile

df = readCSVfile.readCSV()

question = input(" waar ik je mee helpen:\n")

print(awnserQuestion.answer_question(df, question=question))