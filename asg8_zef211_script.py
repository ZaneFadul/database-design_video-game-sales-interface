# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 15:03:13 2020

I just started coding and didn't stop...

@author: Zane Fadul
"""

import time
import subprocess
import os
from tabulate import tabulate
from textwrap import wrap

try:
    import matplotlib.pyplot as plt; plt.rcdefaults()
except:
    try:
        subprocess.check_call(['py','-m','pip','install','matplotlib'])
    except:
        print('Cannot load matplotlib. Please download on your own.')
        time.sleep(0.5)
        raise Exception


COLOR = 'white'
plt.rcParams['text.color'] = COLOR
plt.rcParams['axes.labelcolor'] = COLOR
plt.rcParams['xtick.color'] = COLOR
plt.rcParams['ytick.color'] = COLOR
plt.rcParams['figure.figsize'] = 10, 10
plt.rcParams["legend.loc"] = 'upper right'
plt.rcParams['toolbar'] = 'None'


def clearScreen():
    try:
        os.system('cls')
    except:
        os.system('clear')
    finally:
        pass
    
#States
BREAK = 255
LOOP = 1

#Commands
GRAPH = 'r'
LINE = 'g'
DELETE = 'd'
EXIT = 'e'

#Error Messages
ELENEX = 2
EIMPROPER = 3
ENOTAVAIL = 4
ENOTFOUND = 5
EINVALIDGEN = 6
ESAMEGEN = 7

clearScreen()

NETID = input('NETID: ')
ASGNUM = input('ASSIGNMENT NUMBER: ')
EXPORT_FILE_SUFFIX = f'asg{ASGNUM}_{NETID}_'

clearScreen()

HISTORY = [] #history of user commands for printing
FILE_EXPORT = [] #keeps track of all pdfs of graphs created
DATA = {}  #Dictionary of PRIMARY KEY, COLUMN PAIRS
CSVFILE = 'vgsales.csv'
CSVPASS = True


while not CSVPASS:
    CSVFILE = input('PATH TO CSV: ')
    try:
        file = open(CSVFILE,'r')
    except:
        print('Invalid file path. Please try again.')
        CSVFILE = input('PATH TO CSV: ')
    else:
        CSVPASS = True
        file.close()

class VGE:

    def __init__(self, ID):
        self.ID = ID
        self.columns = {}

    def setItem(self, column_name, column_value):
        self.columns[column_name.lower()] = column_value

    def getItem(self, column_name):
        return self.columns[column_name]
    
    def __str__(self):
        return f'{[(key, value) for (key, value) in self.columns.items()]}'
            

def export_graph(name):
    export_file = f'{EXPORT_FILE_SUFFIX}{name}.png'
    plt.rcParams['savefig.facecolor'] = 'black'
    plt.savefig(export_file, dpi=500)
    FILE_EXPORT.append(export_file)
    
def delete_file(file='', delete_all=False):
    try:
        if delete_all:
            for i in FILE_EXPORT:
                os.unlink(f'{i}')
                FILE_EXPORT.remove(i)
                if len(FILE_EXPORT) > 0:
                    delete_file('',True)
            return 0
        else:
            if '.pdf' in file:
                os.unlink(f'{file}')
                FILE_EXPORT.remove(file)
    except:
        return -ENOTFOUND
    return 0
        
    
def extract_data():
    csv_file = open(CSVFILE, 'r')
    csv = csv_file.readlines()
    csv_file.close()
    return csv

def parse_data(data):
    data = [line.strip().split(',') for line in data]
    HEADERS = data.pop(0)
    ID_index = HEADERS.index('Rank')
    for line in data:
        new_entry = VGE(line[ID_index])
        DATA[new_entry.ID] = new_entry
        for element in range(len(HEADERS)):
            if element != ID_index:
                new_entry.setItem(HEADERS[element],line[element])
    
    #clean up
    extraneous_entries = []
    for entry in DATA:
        if not entry.isdigit():
            extraneous_entries.append(entry)
    for entry in extraneous_entries:
        del DATA[entry]

    
def displayPublisherGraph(ranking_floor):
    rank = ranking_floor
    rotation = (-100 + rank)//2 
    if rotation > 90:
        rotation = 90
    size = 10 - (-100 + rank)//500
    try:
        if ranking_floor > len(DATA):
            return -ELENEX

        publishers = {}
        rank_counter = 1
        
        while rank_counter <= ranking_floor:
            try:
                vge = DATA[f"{rank_counter}"]
            except:
                print(f'Key Error for index {rank_counter}')
                rank_counter += 1
                ranking_floor += 1
                continue 
            vge_publisher = vge.getItem('publisher')
            if vge_publisher not in publishers:
                publishers[f"{vge_publisher}"] = 1
            else:
                publishers[f"{vge_publisher}"] += 1
            rank_counter += 1
        
        #initialize
        fig = plt.figure()
        ax = fig.add_subplot(111)
        fig.set_facecolor('black')
        ax.set_facecolor('black')
        
        publishers = sorted((int(value), '\n'.join(wrap(key, width = 15))) for (key, value) in publishers.items())
        pub_outlier_val = max([publishers[i][0] for i in range(len(publishers))])
        outliers = 0
        to_iterate = len(publishers)
        i = 0
        while i < to_iterate:
            if publishers[i][0] == pub_outlier_val:
                outliers += 1
            to_iterate = len(publishers)
            i += 1

        xticks = [publishers[i][1] for i in range(len(publishers))]
        yticks = [publishers[i][0] for i in range(len(publishers))]

        ax.set_title(f'Publishers of the Top {rank} Games', visible=True)
        ax.set_xlabel('Publishers') 
        ax.set_ylabel('Number of Consoles within this Ranking')
        ax.set_yticks(yticks)
        ax.set_xticklabels(xticks, rotation=rotation, visible = True)
        ax.tick_params(labeltop=False, axis='both',labelsize=size)
        colors = ['white' for i in range(len(publishers) - outliers)]
        for i in range(outliers):
            colors.append('red')
        ax.bar(xticks, yticks, color=colors)
        export_graph(f'top{rank}games')
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.show()
        
    except Exception as e:
        HISTORY.append(str(e))
        return -EIMPROPER

    return 0

def displayGenreLine(genre1, genre2=None):
    try:
        genre2None = False
        export_script = ''
        if genre1 == genre2:
            return -ESAMEGEN
        
        if genre2 == None:
            genre2None = True
            genre2 = genre1
            export_script = f'{genre1}trend'
        else:
            export_script = f'{genre1}vs{genre2}'
            
        genre1 = genre1.lower()
        genre2 = genre2.lower()
        genres = []
        for vge in DATA.values():
            curr_genre = vge.getItem('genre').lower()
            if curr_genre not in genres:
                genres.append(curr_genre)
        
        if genre1 not in genres or genre2 not in genres:
            return -EINVALIDGEN
        
        genre1vals = {}
        genre2vals = {}
        xticks = [i for i in range(1970, 2020)]

        for vge in DATA.values():
            release = vge.getItem('year')
            if release == 'N/A':
                continue
            genre = vge.getItem('genre').lower()
            curr_sales = float(vge.getItem('global_sales'))
            curr_sales = round(curr_sales, 3)
            
            #add globalsales for game based on genre
            if genre == genre1 and release not in genre1vals:
                genre1vals[release] = curr_sales
            elif genre == genre1 and release in genre1vals:
                genre1vals[release] += curr_sales
                
            if genre == genre2 and release not in genre2vals:
                genre2vals[release] = curr_sales
            elif genre == genre2 and release in genre2vals:
                genre2vals[release] += curr_sales
        
        genre1vals = sorted((key, value) for (key,value) in genre1vals.items())
        genre1x = [genre1vals[i][0] for i in range(len(genre1vals))]
        genre1y = [genre1vals[i][1] for i in range(len(genre1vals))]
        
        genre2vals = sorted((key, value) for (key,value) in genre2vals.items())
        genre2x = [genre2vals[i][0] for i in range(len(genre2vals))]
        genre2y = [genre2vals[i][1] for i in range(len(genre2vals))]
        
        #initialize
        fig = plt.figure()
        ax = plt.axes()
        fig.set_facecolor('black')
        ax.set_facecolor('black')
        
        if genre2None:
            ax.set_title(f'Trend of {genre1.title()} Games')
        else:
            ax.set_title(f'Comparison of {genre1.title()} games and {genre2.title()} games', visible=True)
        ax.set_xlabel('Year') 
        ax.set_ylabel('Sum of Global Sales (in $ Millions)')
        #ax.set_xticks(xticks)
        ax.set_xticklabels(xticks, visible=True, color='white')
        ax.grid()
        ax.tick_params(labeltop=False, axis='both')
        plt.plot(genre1x, genre1y, color='red', label=f'{genre1.title()} Games')
        if not genre2None:
            plt.plot(genre2x, genre2y, color='white', label=f'{genre2.title()} Games')
        ax.legend()
        export_graph(export_script)
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.show()
        
                    
    except Exception as e:
        print(e)
        HISTORY.append(str(e))
        return -EIMPROPER
    return 0








def generateCommands():
    table = tabulate([
            ['command','argument1','argument2','description'],
            [GRAPH,'<n>','.','display graph of publisher games within the top n games'],
            [LINE,'<genre1>','<opt genre2>','compares 1-2 genres\' popularity over time'],
            [DELETE,'<opt flag -a, --all>','<filename>','removes previously generated graphs'],
            [EXIT,'.','.','exit']
            ])
    return f'COMMAND KEYS\n {table}'

def parseCommand(command):
    command = command.split()
    for i in range(len(command)):
        if command[i].isdigit():
            command[i] = int(command[i])
    return command

def processCommand(args):
    command = args[0]
    output = -ENOTAVAIL
    try:
        if(command == GRAPH):
            output = displayPublisherGraph(args[1])
        if(command == LINE):
            if len(args) > 2:
                output = displayGenreLine(args[1], args[2])
            else:
                output = displayGenreLine(args[1])
        if(command == DELETE):
            if args[1] == '-a' or args[1] == '--all':
                output = delete_file('',True)
            elif '.pdf' in args[1]:
                output = delete_file(args[1], False)
        if(command == EXIT):
            output = BREAK
    except:
        output = -EIMPROPER

    return output

def setup():
    parse_data(extract_data())

def loop():
    clearScreen()
    print(generateCommands())
    for command in HISTORY:
        if 'INPROPER' not in command:
            print(f'> {command}')
        else:
            print(f'{command}')
        
    command = input('> ').lower()
    if command.strip() == '':
        command = '_'
    while len(HISTORY) > 10:
        HISTORY.pop(0)
    HISTORY.append(command)
    
    command = parseCommand(command)
    output = processCommand(command)
    if output < 0:
        error = 'unknown error'
        output = -output
        if output == ENOTAVAIL:
            error = 'Command not available!'
        if output == ELENEX:
            error = 'Length exceeds dataset length.'
        if output == ENOTFOUND:
            error = 'File not found.'
        if output == EINVALIDGEN:
            genres = []
            for vge in DATA.values():
                curr_genre = vge.getItem('genre').lower()
                if curr_genre not in genres:
                    genres.append(curr_genre)
            error = f'Genre does not exist in this dataset. Here are valid genres: {genres}'
        if output == ESAMEGEN:
            error = 'Really? Comparing the same genre with itself?'
            
        HISTORY.append(f'INPROPER USAGE: {error}')
        
    if output == BREAK:
        return 0
    
    return LOOP
    
def main():
    clearScreen()
    STATE = LOOP
    while STATE:
        STATE = loop()
    
    print('Bye bye!')
    time.sleep(.8)
    return
    
if __name__ == '__main__':
    setup()
    main()