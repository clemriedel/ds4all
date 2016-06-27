import csv
import pandas as pd

input_file = csv.DictReader(open("NSF_ZFull_journalism.csv"))

text = [] 
number = []

for row in input_file:
    text.append(row["Abstract"])
    number.append(row["AwardedAmountToDate"])

number_cleaned=[]
for amount in number: 
    number_cleaned.append(float(
            str(amount).replace("$", "").replace(",", "").replace(".00", "")
                                )/1e6
                          )
df = pd.DataFrame({'M$':number_cleaned, 'NSF - Journalism':text})

df.to_csv('NSF_journalism.csv', index = False)