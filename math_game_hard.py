#pip install pillow
import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import random
import time
import sqlite3
from datetime import datetime

current_username=None
game_name="Math Hard"
high_score=0
database_path="database.db"

def connect_db():
    return sqlite3.connect(database_path)

def get_progress(username, game_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT best_level FROM progress_tracking WHERE username=? AND game_name=?''',
        (username, game_name)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def set_progress(username, game_name, level):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now()
    
    cursor.execute(
        'SELECT best_level FROM progress_tracking WHERE username=? AND game_name=?',
        (username, game_name)
    )
    existing = cursor.fetchone()
    if existing:
        best_level = existing[0]
        if level > best_level:
            cursor.execute(
                '''
                UPDATE progress_tracking
                SET best_level=?, last_played=?
                WHERE username=? AND game_name=?
                ''',
                (level, now, username, game_name)
            )
    else:
        cursor.execute(
            '''
            INSERT INTO progress_tracking (username, game_name, best_level, last_played)
            VALUES (?, ?, ?, ?)
            ''',
            (username, game_name, level, now)
        )
    conn.commit()
    conn.close()


def math_hard(current_username_param):
    global current_username, high_score
    current_username=current_username_param

    high_score=get_progress(current_username, game_name)
    
    question_number=1
    first_number, second_number, operation, correct_answer, symbol = 0, 0, 0, 0, " "
    answers=[]
    achievement_5levels=False
    achievement_10levels=False
    achievement_15levels=False

    def generate_equation():
        nonlocal first_number, second_number, operation, correct_answer,symbol, answers

        first_number=random.randint(1,19)
        second_number= random.randint (1,19)
        operation=random.randint(1,2) #will decide if equation will be summation or subtraction
        symbol="+"
        answers=[]

        if operation==1: #summation
            symbol="+"
            while first_number+second_number > 19: #making sure the sum is one-digit number
                if first_number==19:
                    first_number=random.randint(1,18)
                second_number= random.randint (1,18)
            correct_answer=first_number+second_number
        
        if operation == 2: #subtraction
            symbol="-"
            while first_number-second_number<1: #making sure the result is positive number
                if first_number==1:
                    first_number=random.randint(2,19)
                second_number=random.randint(1,18)
            correct_answer=first_number-second_number
        
        answers=[correct_answer]

        #part below generates the possible answers
        q=1
        while q<4: #fills array with 3 other distinct possible answers
            random_number=0
            if operation==1:
                random_number=random.randint(2,19)
            else:
                random_number= random.randint(1,18)
            if random_number not in answers:
                answers.append(random_number)
                q=q+1

        random.shuffle(answers) #randomizes the order of answers in the array 

    #displays new values for equation
    def update_equation():
        label_first.config(text=str(first_number))
        label_operation.config(text=symbol)
        label_second.config(text=str(second_number))
        question_label.config(text=f"   Question {question_number}:     ")
        label_question.config(text="?")

    #displays new values for answers 
    def update_answers():
        answer1.config(text=str(answers[0]))
        answer2.config(text=str(answers[1]))
        answer3.config(text=str(answers[2]))
        answer4.config(text=str(answers[3]))

    #Method for checking answers and code for correct answer
    def check_answer(selected):
        nonlocal question_number
        if selected==correct_answer:
            question_number=question_number+1
            label_question.config(text=str(correct_answer))
            
            #Setting the color of the correct answer to green
            if selected == int(answer1['text']):
                answer1.config(bg="#2dc435")
            elif selected == int(answer2['text']):
                answer2.config(bg="#2dc435")
            elif selected == int(answer3['text']):
                answer3.config(bg="#2dc435")
            elif selected == int(answer4['text']):
                answer4.config(bg="#2dc435")

            window.after(1000, lambda:(
                generate_equation(),
                update_equation(),
                update_answers(),
                #Resetting the colors back to beige
                answer1.config(bg="#f7e7ce"),
                answer2.config(bg="#f7e7ce"),
                answer3.config(bg="#f7e7ce"),
                answer4.config(bg="#f7e7ce")
            ))
        else:
            game_over()

    #if answer is not correct  
    def game_over():
        nonlocal achievement_5levels, achievement_10levels, achievement_15levels

        if question_number-1 > high_score:
            high_score=question_number-1
            set_progress(current_username, game_name, high_score)

        main_frame.pack_forget()

        border_frame=tk.Frame(window, bg="#2C8102") #green border
        border_frame.pack(expand=True, fill="both", padx=15, pady=15)

        gameover_frame=tk.Frame (border_frame, bg="#D26155") #main frame where widgets will go on, red color
        gameover_frame.pack(expand=True, fill="both")

        gameover_label= tk.Label(gameover_frame, text="You made a mistake", font=("Arial", 60, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
        gameover_label.pack(pady=150)

        correct_answers_label= tk.Label(gameover_frame, text=f"You had {question_number - 1} correct answers.", font=("Arial", 40), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
        correct_answers_label.pack()
        
        try_again_button=tk.Button(gameover_frame, text="Try again", font=("Arial", 40), bg="#2c8102", fg="white", bd=2, relief="solid", command=lambda: restart_game(border_frame) )
        try_again_button.pack(pady=50)


        if question_number>=6 and achievement_5levels==False:
            achievement_5levels=True
            achievement_unlocked_label=tk.Label(gameover_frame, text="Achievement unlocked: Beat 5 Levels! ", font=("Arial", 40), bg="#f9c74f", fg="white", bd=2, relief="solid")
            achievement_unlocked_label.pack(pady=50)
            
        if question_number>=11 and achievement_10levels==False:
            achievement_10levels=True
            achievement_unlocked_label=tk.Label(gameover_frame, text="Achievement unlocked: Beat 10 levels! ", font=("Arial", 40), bg="#f9c74f", fg="white", bd=2, relief="solid")
            achievement_unlocked_label.pack(pady=50)
            
        if question_number>=16 and achievement_15levels==False:
            achievement_15levels=True
            achievement_unlocked_label=tk.Label(gameover_frame, text="Achievement unlocked: Beat 15 levels ", font=("Arial", 40), bg="#f9c74f", fg="white", bd=2, relief="solid")
            achievement_unlocked_label.pack(pady=50)

    def restart_game(frame):
        nonlocal question_number
        question_number=1
        frame.destroy()

        question_frame.pack_forget()
        equation_frame.pack_forget()
        answers_frame.pack_forget()

        main_frame.pack(expand=True, fill="both")

        question_frame.pack(pady=30)
        equation_frame.pack(pady=30)
        answers_frame.pack(pady=40)
        
        question_label.config(text=f"   Question {question_number}:     ", font=("Arial", 20), fg="#233d24")

        generate_equation()
        update_equation()
        update_answers()

    #FRONT END
    window=tk.Tk()
    window.title("SmartSprouts Math Game")
    window.configure(bg="#2C8102") #green color, will be seen as border
    window.state("zoomed")
    window.resizable(False,False)

    main_frame=tk.Frame(window, bg="#D26155") #red color for filling
    main_frame.pack(expand=True, fill="both", padx=15, pady=15)

    #Logo and question frame
    question_frame=tk.Frame(main_frame, bg="#f7e7ce", highlightbackground="#2C8102", highlightcolor="#2C8102", highlightthickness=3 )
    question_frame.pack(pady=30)

    """logo= Image.open("Logo.png")
    logo=logo.resize((140,100))
    logo=ImageTk.PhotoImage(logo)
    logo_label=tk.Label(question_frame,image=logo) 
    logo_label.pack(side="left")"""


    question_label=tk.Label(question_frame, text=f"   Question {question_number}:     ", font=("Arial",20), bg="#f7e7ce", fg="#233d24")
    question_label.pack(side="left")

    #displaying the equation
    equation_frame=tk.Frame(main_frame, bg="#D26155")
    equation_frame.pack(pady=30)

    label_first=tk.Label(equation_frame, font=("Arial",80,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_operation=tk.Label(equation_frame, font=("Arial",60,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_second=tk.Label(equation_frame, font=("Arial",80,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_equality=tk.Label(equation_frame,text="=", font=("Arial",60,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_question=tk.Label(equation_frame,text="?", font=("Arial",80,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")

    label_first.pack(side="left", padx=10)
    label_operation.pack(side="left", padx=10)
    label_second.pack(side="left", padx=10)
    label_equality.pack(side="left", padx=10)
    label_question.pack(side="left", padx=10)

    #answer buttons
    answers_frame=tk.Frame(main_frame,bg="#D26155")
    answers_frame.pack(pady=40)

    answer1=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer1['text'])))
    answer2=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer2['text'])))
    answer3=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer3['text'])))
    answer4=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer4['text'])))

    answer1.pack(side="left", padx=10)
    answer2.pack(side="left", padx=10)
    answer3.pack(side="left", padx=10)
    answer4.pack(side="left", padx=10)

    generate_equation()
    update_equation()
    update_answers()
    window.mainloop()


    #displays new values for equation
    def update_equation():
        label_first.config(text=str(first_number))
        label_operation.config(text=symbol)
        label_second.config(text=str(second_number))
        question_label.config(text=f"   Question {question_number}:     ")
        label_question.config(text="?")

    #displays new values for answers 
    def update_answers():
        answer1.config(text=str(answers[0]))
        answer2.config(text=str(answers[1]))
        answer3.config(text=str(answers[2]))
        answer4.config(text=str(answers[3]))

    #Method for checking answers and code for correct answer
    def check_answer(selected):
        global question_number
        if selected==correct_answer:
            question_number=question_number+1
            label_question.config(text=str(correct_answer))
            
            #Setting the color of the correct answer to green
            if selected == int(answer1['text']):
                answer1.config(bg="#2dc435")
            elif selected == int(answer2['text']):
                answer2.config(bg="#2dc435")
            elif selected == int(answer3['text']):
                answer3.config(bg="#2dc435")
            elif selected == int(answer4['text']):
                answer4.config(bg="#2dc435")

            window.after(1000, lambda:(
                generate_equation(),
                update_equation(),
                update_answers(),
                #Resetting the colors back to beige
                answer1.config(bg="#f7e7ce"),
                answer2.config(bg="#f7e7ce"),
                answer3.config(bg="#f7e7ce"),
                answer4.config(bg="#f7e7ce")
            ))
        else:
            game_over()

    #if answer is not correct  
    def game_over():
        main_frame.pack_forget()

        border_frame=tk.Frame(window, bg="#2C8102") #green border
        border_frame.pack(expand=True, fill="both", padx=15, pady=15)

        gameover_frame=tk.Frame (border_frame, bg="#D26155") #main frame where widgets will go on, red color
        gameover_frame.pack(expand=True, fill="both")

        gameover_label= tk.Label(gameover_frame, text="You made a mistake", font=("Arial", 60, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
        gameover_label.pack(pady=150)

        correct_answers_label= tk.Label(gameover_frame, text=f"You had {question_number - 1} correct answers.", font=("Arial", 40), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
        correct_answers_label.pack()
        
        try_again_button=tk.Button(gameover_frame, text="Try again", font=("Arial", 40), bg="#2c8102", fg="white", bd=2, relief="solid", command=lambda: restart_game(border_frame) )
        try_again_button.pack(padx=280)

    def restart_game(frame):
        global question_number
        question_number=1
        frame.destroy()

        question_frame.pack_forget()
        equation_frame.pack_forget()
        answers_frame.pack_forget()

        main_frame.pack(expand=True, fill="both")

        question_frame.pack(pady=30)
        equation_frame.pack(pady=30)
        answers_frame.pack(pady=40)
        
        question_label.config(text=f"   Question {question_number}:     ", font=("Arial", 20), fg="#233d24")

        generate_equation()
        update_equation()
        update_answers()

    #FRONT END
    window=tk.Tk()
    window.title("SmartSprouts Math Game")
    window.configure(bg="#2C8102") #green color, will be seen as border
    window.state("zoomed")
    window.resizable(False,False)

    main_frame=tk.Frame(window, bg="#D26155") #red color for filling
    main_frame.pack(expand=True, fill="both", padx=15, pady=15)

    #Logo and question frame
    question_frame=tk.Frame(main_frame, bg="#f7e7ce", highlightbackground="#2C8102", highlightcolor="#2C8102", highlightthickness=3 )
    question_frame.pack(pady=30)

    logo= Image.open("Logo.png")
    logo=logo.resize((140,100))
    logo=ImageTk.PhotoImage(logo)
    logo_label=tk.Label(question_frame,image=logo) 
    logo_label.pack(side="left")


    question_label=tk.Label(question_frame, text=f"   Question {question_number}:     ", font=("Arial",20), bg="#f7e7ce", fg="#233d24")
    question_label.pack(side="left")

    #displaying the equation
    equation_frame=tk.Frame(main_frame, bg="#D26155")
    equation_frame.pack(pady=30)

    label_first=tk.Label(equation_frame, font=("Arial",80,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_operation=tk.Label(equation_frame, font=("Arial",60,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_second=tk.Label(equation_frame, font=("Arial",80,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_equality=tk.Label(equation_frame,text="=", font=("Arial",60,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")
    label_question=tk.Label(equation_frame,text="?", font=("Arial",80,"bold"), width=2, bg="#f7e7ce", fg="#233d24", bd=2, relief="solid")

    label_first.pack(side="left", padx=10)
    label_operation.pack(side="left", padx=10)
    label_second.pack(side="left", padx=10)
    label_equality.pack(side="left", padx=10)
    label_question.pack(side="left", padx=10)

    #answer buttons
    answers_frame=tk.Frame(main_frame,bg="#D26155")
    answers_frame.pack(pady=40)

    answer1=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer1['text'])))
    answer2=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer2['text'])))
    answer3=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer3['text'])))
    answer4=tk.Button(answers_frame, font=("Arial",80, "bold"), bg="#f7e7ce", fg="#233d24", bd=2, relief="solid", command=lambda: check_answer(int(answer4['text'])))

    answer1.pack(side="left", padx=10)
    answer2.pack(side="left", padx=10)
    answer3.pack(side="left", padx=10)
    answer4.pack(side="left", padx=10)

    generate_equation()
    update_equation()
    update_answers()
    window.mainloop()
