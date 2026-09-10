from flask import Flask, render_template, request, session
from flask_session import Session
import sqlite3

app = Flask(__name__)
app.config.from_object('config')
Session(app)

def get_db():
    return sqlite3.connect(app.config.get("DATABASE_FILENAME"))


def executeSQL(command, inputs = None):
    
    with get_db() as con:
        cursor = con.cursor()
        result = cursor.execute(command).fetchall() if inputs == None else cursor.execute(command, inputs).fetchall()
        con.commit()
        
    return result
  
  
def completedTweets():
    return executeSQL('''SELECT COUNT(*)
                        FROM RESPONSES
                        WHERE FIRST_NAME = ? AND LAST_NAME = ?;
                    ''', (session["FIRST_NAME"], session["LAST_NAME"]))[0][0]


@app.route('/', methods=['GET'])
def start_page():
    if not session.get("FIRST_NAME") or not session.get("LAST_NAME") or not session.get("TWEETS"):
        return app.redirect("/login")
    else:
        return app.redirect("/label")


@app.route('/logout', methods=['POST'])
def logout():
    """Make sure user is logged out."""
    session.clear()
    return app.redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        FIRST_NAME = request.form['FIRST_NAME']
        LAST_NAME = request.form['LAST_NAME']
        session["FIRST_NAME"] = FIRST_NAME
        session["LAST_NAME"] = LAST_NAME
        session["NUM_TO_COMPLETE"] = max(0, 5 - completedTweets())
        
        executeSQL("INSERT OR IGNORE INTO USERS \
            (FIRST_NAME, LAST_NAME) VALUES (?,?)", (FIRST_NAME, LAST_NAME))
        
        # Find X random tweets the user hasn't done out of five
        
        session["TWEETS"] = executeSQL('''SELECT TWEET, TWEET_ID FROM TWEETS T
                                            WHERE T.TWEET_ID NOT IN 
                                            (SELECT TWEET_ID FROM RESPONSES R WHERE R.FIRST_NAME = ? AND R.LAST_NAME = ?)
                                            ORDER BY RANDOM()
                                            LIMIT ?
                                            ''', (FIRST_NAME, LAST_NAME, session.get("NUM_TO_COMPLETE")))
        return app.redirect("/label")
    else:   
        return render_template("login.html")
    
    
@app.route('/label', methods=['GET', 'POST'])
def label():
    if request.method == 'POST':
        executeSQL('''INSERT INTO RESPONSES VALUES(?,?,?,?);''', 
                    (session["FIRST_NAME"], session["LAST_NAME"], request.form['TWEET_ID'], request.form['EMOTION_ID']))
        session["TWEETS"].pop()
        return app.redirect("/label")
    else:
        if len(session["TWEETS"]) == 0:
            return render_template("done.html", TOTAL_COMPLETED=completedTweets())
        else:
            TWEET, TWEET_ID = session["TWEETS"][-1]
            EMOTIONS = executeSQL('''SELECT * FROM EMOTIONS;''')
            return render_template("label.html", EMOTIONS = EMOTIONS, TWEET = TWEET, TWEET_ID = TWEET_ID, 
                                   percent = completedTweets() / 5 * 100, USER = session.get("FIRST_NAME") + " " + session.get("LAST_NAME"))

@app.route('/history', methods=['GET', 'POST']) 
def history():
    if request.method == 'GET':
        RESPONSES = executeSQL('''SELECT T.TWEET, T.TWEET_ID, E.EMOTION FROM RESPONSES AS R
                               JOIN TWEETS AS T JOIN EMOTIONS AS E
                               ON T.TWEET_ID = R.TWEET_ID AND E.EMOTION_ID = R.EMOTION_ID
                               WHERE R.FIRST_NAME = ? AND R.LAST_NAME = ?''',
                               (session.get("FIRST_NAME"), session.get("LAST_NAME")))
        return render_template("history.html", RESPONSES = RESPONSES, TOTAL_COMPLETED = len(RESPONSES), 
                               FIRST_NAME = session.get("FIRST_NAME"), LAST_NAME = session.get("LAST_NAME"))
    else:
        return render_template("history.html")


if __name__ == '__main__':
    app.run(debug=True)