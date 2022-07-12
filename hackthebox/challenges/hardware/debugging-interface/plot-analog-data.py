import csv
import matplotlib.pyplot as plt

with open('truc.csv') as csvfile:
  reader = csv.reader(csvfile)
  data = [float(row[0]) for row in reader]
  plt.plot(data)
  plt.show()
