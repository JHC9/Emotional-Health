import csv

headers = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
emocent = [0.0, 0.0, 0.045454545454545456, 0.8409090909090909, 0.0, 0.0, 0.11363636363636363]

with open('my_file.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)  # Write the headers
    writer.writerow(emocent)  # Write the data under the corresponding headers

