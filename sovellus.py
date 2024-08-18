from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import random
from os import getenv

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')

DATABASE_URL = getenv('DATABASE_URL')

# Luodaan yhteys tietokantaan
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

CATEGORIES = ['ykkoset', 'kakkoset', 'kolmoset', 'neloset', 'vitoset', 'kutonen',
              'pari', 'kaksi_paria', 'kolme_samaa', 'nelja_samaa', 'pieni_suora',
              'iso_suora', 'tayskasi', 'yatzy', 'sattuma']

def roll_dice(held_dice=None):
    if held_dice is None:
        held_dice = [False] * 5
    return [random.randint(1, 6) if not held else dice for held, dice in zip(held_dice, session.get('dice', [1, 1, 1, 1, 1]))]

@app.route('/')
def index():
    if 'players' not in session:
        return redirect(url_for('setup'))
    current_player = session['players'][session['current_player_index']]
    return render_template('index.html', dice=session['dice'], rolls=session['rolls'],
                           categories=CATEGORIES, used_categories=current_player['used_categories'],
                           players=session['players'], current_player=current_player, held_dice=session['held_dice'])

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        session.clear()  # Nollaa session

        if 'continue' in request.form:
            game_id_str = request.form['game_id']
            game_id = int(game_id_str) 
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM game WHERE id = %s AND status = %s', (game_id, 'ongoing'))
            game = cur.fetchone()
            if game:
                session['current_game_id'] = game[0]
                session['current_player_index'] = game[2]
                session['dice'] = game[3]
                session['rolls'] = game[4]
                session['held_dice'] = game[5]

                cur.execute('SELECT name, score FROM player WHERE game_id = %s', (game_id,))
                players = cur.fetchall()
                session['players'] = [{'name': player[0], 'score': player[1], 'used_categories': {}} for player in players]
                
                cur.close()
                conn.close()
                return redirect(url_for('index'))
            else:
                print(type(game_id))  # pitäisi olla <class 'int'>
                print(game)
                print(game_id)
                cur.close()
                conn.close()
                return "Game not found", 404

        num_players = int(request.form['num_players'])
        session['players'] = [{'name': request.form[f'name_{i}'], 'score': 0, 'used_categories': {}} for i in range(num_players)]
        session['current_player_index'] = 0
        session['dice'] = roll_dice()
        session['rolls'] = 0
        session['held_dice'] = [False] * 5
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO game (status, current_player_index, dice, rolls, held_dice) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                    ('ongoing', 0, session['dice'], session['rolls'], session['held_dice']))
        game_id = cur.fetchone()[0]
        conn.commit()
        session['current_game_id'] = game_id
        
        for player in session['players']:
            cur.execute('INSERT INTO player (name, score, game_id) VALUES (%s, %s, %s)', (player['name'], player['score'], game_id))
        conn.commit()
        
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('setup.html')

@app.route('/continue_later', methods=['POST'])
def continue_later():
    game_id = session.get('current_game_id')
    if game_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE game SET status = %s WHERE id = %s', ('ongoing', game_id))
        conn.commit()
        cur.close()
        conn.close()
        session.clear()
        return f"Game paused. Your game ID is {game_id}. Save this ID to continue later."
    return "No game in progress", 400

@app.route('/end_game', methods=['POST'])
def end_game():
    game_id = session.get('game_id')
    
    if game_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Poista peli tietokannasta
        cursor.execute("DELETE FROM game WHERE id = %s", (game_id,))
        conn.commit()
        conn.close()
    
    session.pop('game_id', None)  # Tyhjennä sessio
    
    return redirect('/')

@app.route('/continue', methods=['GET', 'POST'])
def continue_game():
    if request.method == 'POST':
        game_id = request.form['game_id']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM game WHERE id = %s AND status = %s', (game_id, 'ongoing'))
        game = cur.fetchone()
        if game:
            session['current_game_id'] = game[0]
            session['current_player_index'] = game[2]
            session['dice'] = game[3]
            session['rolls'] = game[4]
            session['held_dice'] = game[5]

            cur.execute('SELECT name, score FROM player WHERE game_id = %s', (game_id,))
            players = cur.fetchall()
            session['players'] = [{'name': player[0], 'score': player[1], 'used_categories': {}} for player in players]
            
            cur.close()
            conn.close()
            return redirect(url_for('index'))
        else:
            cur.close()
            conn.close()
            return "Game not found or already completed", 404
    return render_template('continue.html')

@app.route('/roll', methods=['POST'])
def roll():
    if 'rolls' in session and session['rolls'] < 3:
        held_dice_indices = request.form.getlist('held_dice')
        session['held_dice'] = [str(i) in held_dice_indices for i in range(5)]
        session['dice'] = roll_dice(session['held_dice'])
        session['rolls'] += 1
    return redirect(url_for('index'))

@app.route('/choose_category', methods=['POST'])
def choose_category():
    category = request.form['category']
    current_player = session['players'][session['current_player_index']]
    if category not in current_player['used_categories']:
        score = calculate_score(session['dice'], category)
        current_player['score'] += score
        current_player['used_categories'][category] = score

        session['rolls'] = 1
        session['held_dice'] = [False] * 5
        session['dice'] = roll_dice()

        session['current_player_index'] = (session['current_player_index'] + 1) % len(session['players'])
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE game SET current_player_index = %s, dice = %s, rolls = %s, held_dice = %s WHERE id = %s',
                    (session['current_player_index'], session['dice'], session['rolls'], session['held_dice'], session['current_game_id']))
        cur.execute('UPDATE player SET score = %s WHERE name = %s AND game_id = %s',
                    (current_player['score'], current_player['name'], session['current_game_id']))
        conn.commit()
        
        cur.close()
        conn.close()
    return redirect(url_for('index'))

def calculate_score(dice, category):
    if category == 'ykkoset':
        return dice.count(1) * 1
    elif category == 'kakkoset':
        return dice.count(2) * 2
    elif category == 'kolmoset':
        return dice.count(3) * 3
    elif category == 'neloset':
        return dice.count(4) * 4
    elif category == 'vitoset':
        return dice.count(5) * 5
    elif category == 'kutonen':
        return dice.count(6) * 6
    elif category == 'pari':
        pairs = [d for d in set(dice) if dice.count(d) >= 2]
        if pairs:
            return max(pairs) * 2
        else:
            return 0
    elif category == 'kaksi_paria':
        pairs = [d for d in set(dice) if dice.count(d) >= 2]
        if len(pairs) >= 2:
            return sum(sorted(pairs, reverse=True)[:2]) * 2
        else:
            return 0
    elif category == 'kolme_samaa':
        for d in set(dice):
            if dice.count(d) >= 3:
                return d * 3
        return 0
    elif category == 'nelja_samaa':
        for d in set(dice):
            if dice.count(d) >= 4:
                return d * 4
        return 0
    elif category == 'pieni_suora':
        return 15 if sorted(dice) == [1, 2, 3, 4, 5] else 0
    elif category == 'iso_suora':
        return 20 if sorted(dice) == [2, 3, 4, 5, 6] else 0
    elif category == 'tayskasi':
        three_of_a_kind = None
        pair = None
        for d in set(dice):
            if dice.count(d) == 3:
                three_of_a_kind = d
            elif dice.count(d) == 2:
                pair = d
        return (three_of_a_kind * 3 + pair * 2) if three_of_a_kind and pair else 0
    elif category == 'yatzy':
        return 50 if len(set(dice)) == 1 else 0
    elif category == 'sattuma':
        return sum(dice)
    else:
        return 0

if __name__ == '__main__':
    app.run(debug=True)
