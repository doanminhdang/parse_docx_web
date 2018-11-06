#!/usr/bin/env python
import sys
import os
import csv
import difflib
import re

def read_csv_table(csvFile):
    """
    Read a CSV file, export as a table: table[row][column]
    """
    table = []
    with open(csvFile, 'rt') as file_in:
        csv_reader = csv.reader(file_in, delimiter='\t')
        for r, row in enumerate(csv_reader):
            table.append(row)
    return table

def transpose_table(table):
    table_transpose = [[row[i] for row in table] for i in range(len(table[0]))]
    return table_transpose

def parse_table_column(table, numberColumn):
    #import time # testing with a table of 94044 rows, 4 columns
    columns = [[] for _ in range(numberColumn)]
    #start=time.time()
    for k in range(numberColumn):
        columns[k] = []
    for row in table:
        for k in range(numberColumn):
            columns[k].append(row[k])
    #end=time.time()
    #print(end-start) # 0.07465
    #start=time.time()
    #table_transpose = [[row[i] for row in table] for i in range(len(table[0]))]
    #end=time.time()
    #print(end-start) # 0.01496
    #start=time.time()
    #table_transpose2 = map(list, zip(*table))
    #end=time.time()
    #print(end-start) # 0.05046
    return columns
    
def compare_text_columns(table, column1Position, column2Position):
    similarity = list()
    for i in range(len(table)):
        sourceSentence = table[i][column1Position]
        targetSentence = table[i][column2Position]
        # Remove hyphen due to line break in German
        sourceSentence = re.sub(r'([A-Za-z])\- +(?!und |oder |bzw\. )([a-z])', r'\1\2', sourceSentence)
        table[i][column1Position] = sourceSentence
        targetSentence = re.sub(r'([A-Za-z])\- +(?!und |oder |bzw\. )([a-z])', r'\1\2', targetSentence)
        table[i][column2Position] = targetSentence
        similarity += [difflib.SequenceMatcher(None, sourceSentence, targetSentence).ratio()]
    return table, similarity


def insert_column_table(table, position, newColumn):
    # Insert newColumn as a list to table as a 2-dimension list, before column #position
    for i in range(len(table)):
        table[i].insert(position, newColumn[i])
    return table


def insert_blank_column_table(table, position):
    # Insert a blank column to table as a 2-dimension list, before column #position
    for i in range(len(table)):
        table[i].insert(position, '')
    return table


def write_table_csv(exportFile, table):
    with open(exportFile, 'wt') as csvfile:
        textWriter = csv.writer(csvfile, delimiter='\t')
        for i in range(len(table)):
            textWriter.writerow(table[i])
