from cProfile import run
from turtle import Turtle
import PySimpleGUI as sg
import cv2

motions = {}
run_text = "RUN"

layout = [
    [sg.Text("Hello")],
    [
        sg.Radio("Hand", "RADIO1", key=0, default=True), 
        sg.Radio("Head", "RADIO1", key=1)
    ],
    [sg.Image(filename="", key="-IMAGE-", size=(400, 200))],
    [sg.Text("Key bind:"), sg.InputText(key="-IN-", enable_events=True)],
    [sg.Button("SAVE")],
    [sg.Button("RUN", key="-RUN-")],
    [sg.Button("Exit")],
]

window = sg.Window("Motion", layout, element_justification="c")
cap = cv2.VideoCapture(0)

while True:
    event, values = window.read(timeout=20)
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
    ret, frame = cap.read()

    if len(values["-IN-"]) > 1:
        window.Element("-IN-").update(values["-IN-"][-1])

    imgbytes = cv2.imencode(".png", frame)[1].tobytes()
    if (event == "SAVE" and values["-IN-"]):
        motions[values["-IN-"]] = imgbytes
        sg.Popup("saved")
        print(motions.keys())
        window.Element("-IN-").update("")
    elif (event == "-RUN-"):
        run_text = "RUN" if run_text == "STOP" else "STOP"
        window.Element("-RUN-").update(run_text)
    window["-IMAGE-"].update(data=imgbytes, size=(400, 200))

window.close()