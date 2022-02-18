import mysql.connector
import pyperclip
from datetime import datetime

# MySQL <-> Python connection
mydb = mysql.connector.connect(host = "localhost", user = "root", passwd = "HugoSoderholm01", database = "neotide")
mycursor = mydb.cursor()

# Main funktion
def main():
    # Skapar korrekt lista av patienter
    patientlista = list(list_split(start(), 5))
    arrival_condition(patientlista)
    date_format(patientlista)

    # Läser in patienter i MySQL databasen (OBS! Hos patienter utan releasedate så lagras releasedate som 0000-00-00 i databasen)
    sql_command = "INSERT IGNORE INTO patient (patientnumber, arrivaldate, releasedate, ward, weight) VALUES (%s, %s, %s, %s, %s)"
    mycursor.executemany(sql_command, patientlista)
    mydb.commit()
    print(mycursor.rowcount, "was inserted")

# Block av kod som hanterar patienternas data (från datorns clipboard!) och snyggar till den
def start():
    patienter_kopia = pyperclip.paste()             # Sparar datorns clipboard i en strängvariabel
    templist = patienter_kopia.split("\r\n")        # Skapar en lista som hanterar och tar bort blanksteg och radbyten från patientdatan
    list_as_string = ','.join(templist)             # Skapar en lång strängvariabel av alla patienternas data
    patientdata = list_as_string.split(",")         # Skapar en stor lista med alla patienternas data tillsnyggat
    return patientdata

# Modifierad funktion som tar en lista och ett heltal som parameter och returnerar en lista av tupler där varje tupel representerar en patient med n (5) antal element
# Orginell kod: https://tagmerge.com/question/split-a-list-in-half
def list_split(listA, n):
    for x in range(0, len(listA), n):
        every_chunk = listA[x: n+x]
        if len(every_chunk) < n:
            every_chunk = every_chunk + \
                [None for y in range(n-len(every_chunk))]
        yield tuple(every_chunk)

# Funktion som tar bort patienter som inte uppfyller kravet "arrivaldate >= 7.6.2006"
def arrival_condition(listA):
    startdate = datetime.strptime("7.6.2006", '%d.%m.%Y')
    loopint = 0
    while loopint < len(listA):
        arrdate = datetime.strptime(listA[loopint][1], '%d.%m.%Y')
        if not arrdate >= startdate:
            listA.remove(listA[loopint])
            loopint -= 1
        loopint += 1
    return listA

# Funktion som ändrar datumen till formatet YYYY-MM-DD så att det sätts in korrekta datum i databasen
def date_format(listA):
    intindex = 0
    for patient in listA:
        # Arrivaldate
        arrdatum = patient[1]
        arrtemp = arrdatum.split(".")
        tempvar = arrtemp[0]                # Byter plats på år och dag
        arrtemp[0] = arrtemp[2]
        arrtemp[2] = tempvar
        newarr = '.'.join(arrtemp)          # Arrivaldate i nytt format

        # Releasedate
        reldatum = patient[2]
        reltemp = reldatum.split(".")
        if reltemp != ['']:                 # Villkor: Om releasedate existerar, d.v.s om patienten inte längre är inskriven på sjukhuset
            tempvar = reltemp[0]            # Byter plats på år och dag
            reltemp[0] = reltemp[2]
            reltemp[2] = tempvar
        newrel = '.'.join(reltemp)          # Releasedate i nytt format

        # Uppdaterar patientdatan med nyformaterade arrivaldate och releasedate
        listA[intindex] = (listA[intindex][0], newarr, newrel, listA[intindex][3], listA[intindex][4])

        intindex += 1
    return listA

# Kör programmet
if __name__ == '__main__':
    main()