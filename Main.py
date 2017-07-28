#!/usr/bin/python

'''
    ************************************************************************
    *   FILE NAME:      main.py
    *   AUTHOR:         Yu Dong (Peter) Feng, Dylan Vogel
    *   PURPOSE:        This file contains the script used to run the GUI.
    ************************************************************************
'''


import sys
import controller

if __name__ == "__main__":

    app = controller.QtWidgets.QApplication(sys.argv)
    window = controller.MainWindow()
    window.show()
    sys.exit(app.exec_())

    work_temp = window.temp
    P_center = window.P_center
    I_center = window.I_center
    D_center = window.D_center

    P_edge = window.P_edge
    I_edge = window.I_edge
    D_edge = window.D_edge




