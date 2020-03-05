from tkinter import *
import cv2
import os
import numpy as np
from tkinter import messagebox
import sqlite3
import time
import datetime
import pyttsx3

datet = str(datetime.datetime.now())



db = sqlite3.connect("Dataset.db")
cr = db.cursor()

face_classifer = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")



d = {}
d1 = {}


def addFaces():
    def submit():

        user_name = nameEntry.get()
        user_id = idEntry.get()

        print(user_name)
        print(user_id)





        """cr.execute('''CREATE TABLE student_info
                        (id int not null,
                        name text);''')
                        """
        #cr.execute("CREATE TABLE attendence_sheet (date text , roll int , name text , Status text)")

        cr.execute("INSERT INTO student_info(id , name) VALUES(?,?)" , (user_id , user_name))
        cr.execute("INSERT INTO attendence_sheet(roll , name ) VALUES(? , ?)" , (user_id , user_name))
        db.commit()


        cap = cv2.VideoCapture(0)
        cap.set(3,640)
        cap.set(4,480)
        count = 0

        while(1):
            _ , frame = cap.read()
            frame = cv2.flip(frame , 1)
            gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)

            faces = face_classifer.detectMultiScale(gray , 1.3 , 5)

            for(x,y,w,h) in faces:
                cv2.rectangle(frame , (x,y) , (x+w , y+h) , (255,0,0) , 2)
                count+=1



                file_path = r"C:\\Face Collector\\" + str(user_name) + "."+str(user_id)+ '.' + str(count)+ '.jpg'

                cv2.imwrite(file_path , gray[y:y+h , x:x+w])

                cv2.imshow("Images" , frame)

            if cv2.waitKey(1) ==27 or count==100:
                break
        messagebox.showinfo("Dataset" , "Collecting Face Samples Successfully. You can Check your Data  at C:\Face Collector")
        cap.release()
        cv2.destroyAllWindows()
        top.destroy()


    top = Toplevel(root)
    top.geometry("300x200+700+200")

    war = Label(top , text = "Please Clear id after input new id." , bg = 'red')
    war.place(x=0,y=0)

    Name = Label(top , text = "Name" , bg = "light green")
    Name.place(x = 50 , y = 50)

    nameEntry = Entry(top , bg = "pink")
    nameEntry.place(x = 100 , y =50)


    Id = Label(top , text = "ID" , bg = "light green")
    Id.place(x = 50 , y = 100)

    idEntry = Entry(top , bg = 'pink')
    idEntry.place(x = 100 , y = 100)

    ok = Button(top , text = "Submit" ,bg = "cyan", command = submit)
    ok.place(x = 100 ,y = 150)



    top.config(bg = "light green")
    top.mainloop()


def startRecognition():

    path = r"C:\\Face Collector\\"
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    def getImageandLabel(path):

        imagepath = [os.path.join(path,f) for f in os.listdir(path)]

        faceSamples = []
        ids = []

        for imagePath in imagepath:
            gray = cv2.imread(imagePath , 0)

            image_array = np.array(gray , dtype=np.uint8)

            id = int(os.path.split(imagePath)[-1].split(".")[1])

            faces = face_classifer.detectMultiScale(image_array)


            for(x,y,w,h) in faces:
                faceSamples.append(image_array[y:y+h , x:x+w])
                ids.append(id)
        print(ids)
        return faceSamples, ids

    faces , ids = getImageandLabel(path)
    recognizer.train(faces , np.array(ids))

    recognizer.write("trainer.yml")

    recognizer.read("trainer.yml")

    cam = cv2.VideoCapture(0)
    cam.set(3,740)
    cam.set(4,680)

    while(1):

        _ , frame = cam.read()

        gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)

        faces = face_classifer.detectMultiScale(gray , 1.2 , 5)

        for(x,y,w,h) in faces:
            cv2.rectangle(frame , (x,y) , (x+w, y+h) , (0,255,0) , 2)

            idt , confidence = recognizer.predict(gray[y:y+h , x:x+w])
            idt = int(idt)
            if confidence < 100:

                for row in cr.execute("SELECT id , name FROM student_info"):
                    d[row[0]] = row[1]



                name = d[idt]

                if confidence < 60:
                    cv2.putText(frame , name , (x+5 , y+25) , cv2.FONT_HERSHEY_COMPLEX , 1 , (0,0,255) , 1)
                else:
                    cv2.putText(frame , "Unknown" , (x+5 , y+h) , cv2.FONT_HERSHEY_COMPLEX , 1 , (0,255,0) , 1)

                for row in cr.execute("SELECT roll , Status from attendence_sheet"):
                   d1[row[0]] = row[1]

                p= "Present"
                if d1[idt] == None:
                    cr.execute("UPDATE attendence_sheet SET Status = ?  WHERE roll = ?" , (p , idt))
                    db.commit()
                    text = "Thank You" + name

                else:
                    pass


        frame = cv2.putText(frame , datet , (10,50) ,cv2.FONT_HERSHEY_COMPLEX ,1 , (0,0,255) ,2)
        cv2.imshow("Live" , frame)

        if cv2.waitKey(1) == 27:
            break
    cam.release()
    cv2.destroyAllWindows()

def Exit():
    a = messagebox.askquestion("Exit" , "Do you Really Want to Exit")
    if a == "yes":
        root.destroy()



    else:
        pass


def start_attendece():
    startRecognition()

root = Tk()
root.geometry("400x200+400+200")

faces = Label(root , text = "Faces" , bg = "orange")
faces.place(x = 50 ,y = 40)

Recognition = Label(root , text = "Recognition" , bg = "orange")
Recognition.place(x = 50 , y = 80)

GetAttendece = Label(root , text = "Start Attendence" , bg = "orange")
GetAttendece.place(x = 50 , y = 120)

faceButton = Button(root , text = "Add Faces"  ,bg = "cyan" ,  command = addFaces)
faceButton.place(x = 150 , y = 40)


RecognitionButton = Button(root , text = "Start Recognition"  ,bg = "cyan", command = startRecognition)
RecognitionButton.place(x = 150 , y = 80)

Attendence_button = Button(root , text = "Ready" , bg = "cyan" , command = start_attendece)
Attendence_button.place(x = 150 , y = 120)


exit = Button(root , text = "Exit" , bg = "cyan" , bd = 5 , command = Exit)
exit.place(x = 300 , y = 150)

root.config(bg = "orange")
root.mainloop()

