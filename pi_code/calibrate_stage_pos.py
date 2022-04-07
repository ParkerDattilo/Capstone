#!/usr/bin/python3
import sys
import os

def main():
    # this function overwrites the current position of the stage to 0. It is intended that this be used when drift occurs to the system. Run this script after moving the stage as close to the front as possible
    ft = open(path+"table.txt", "w")
    ft.write("pos_val\n")

    fpos = open(path+"pos.txt", "w")
    fpos.write("0.00")

main()
