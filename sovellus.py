from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import random
from scoring import calculate_score
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
        session['rolls'] = 1
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
        
        # Asetetaan viesti, joka näytetään setup-sivulla
        flash(f"Game paused. Your game ID is {game_id}. Save this ID to continue later.")
        
        # Ohjataan käyttäjä takaisin setup-sivulle
        return redirect(url_for('setup'))
    
    flash("No game in progress")
    return redirect(url_for('setup')), 400

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
    
    return redirect('/setup')

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

        # Tarkista, onko kaikilla pelaajilla käytetty kaikki kategoriat
        all_categories_used = all(len(player['used_categories']) == len(CATEGORIES) for player in session['players'])

        if all_categories_used:
            # Jos peli päättyy, siirrytään lopputulossivulle
            return redirect(url_for('end_game_results'))

        # Siirry seuraavaan pelaajaan
        session['rolls'] = 0
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

@app.route('/end_game_results')
def end_game_results():
    # Järjestetään pelaajat pisteiden perusteella
    sorted_players = sorted(session['players'], key=lambda p: p['score'], reverse=True)
    
    # Tyhjennä peliin liittyvät tiedot sessiosta, mutta säilytä tulokset
    game_results = session['players']
    session.clear()
    session['game_results'] = game_results

    return render_template('end_game.html', players=sorted_players)

if __name__ == '__main__':
    app.run(debug=True)
