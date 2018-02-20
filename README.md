instructions:
    to run the program:
        python calcStats.py --inputFile=trades.csv --outputFile=enrichedTrades.csv
    if you want to store the stdout in "stdout.txt":
        python calcStats.py --inputFile=trades.csv --outputFile=enrichedTrades.csv >> stdout.txt

Assumption:
    1. assuming all types in different fields are consistent
    2. no missing data (though I dealt with the missing value in trades.csv, it's a naive check. The assumption that there's
       no missing data has to be said)

Notes:
    - SymbolPosition: Thought it was Long/Short/Flat instead of actual number at fist due to the second part of description
    - I'm storing all FillSize in a list to calculate the median. With large data set, there might an issue
    - This script is developed in python 2.7, using python3 to run this can run into problem (i.e. iteritems())
    
