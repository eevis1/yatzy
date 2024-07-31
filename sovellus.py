from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:PythonOnKaarme.24@localhost/yatzy_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

CATEGORIES = ['ykkoset', 'kakkoset', 'kolmoset', 'neloset', 'vitoset', 'kutonen',
              'pari', 'kaksi_paria', 'kolme_samaa', 'nelja_samaa', 'pieni_suora',
              'iso_suora', 'tayskasi', 'yatzy', 'sattuma']

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    completed_game_id = db.Column(db.Integer, db.ForeignKey('completed_game.id'), nullable=True)
    used_categories = db.relationship('Category', backref='player', lazy=True)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False, default='ongoing')
    current_player_index = db.Column(db.Integer, default=0)
    players = db.relationship('Player', backref='game', lazy=True)
    dice = db.Column(db.ARRAY(db.Integer), default=lambda: [random.randint(1, 6) for _ in range(5)])
    rolls = db.Column(db.Integer, default=0)
    held_dice = db.Column(db.ARRAY(db.Boolean), default=lambda: [False] * 5)
    categories = db.relationship('Category', backref='game', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

class CompletedGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    players = db.relationship('Player', backref='completed_game', lazy=True)
    final_scores = db.Column(db.JSON, nullable=False)

class PlayerCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

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
            game_id = request.form['game_id']
            game = Game.query.get(game_id)
            if game:
                session['current_game_id'] = game.id
                session['current_player_index'] = game.current_player_index
                session['dice'] = game.dice
                session['rolls'] = game.rolls
                session['held_dice'] = game.held_dice
                session['players'] = [{'name': player.name, 'score': player.score, 'used_categories': {}} for player in game.players]
                return redirect(url_for('index'))
            else:
                return "Game not found", 404

        num_players = int(request.form['num_players'])
        session['players'] = [{'name': request.form[f'name_{i}'], 'score': 0, 'used_categories': {}} for i in range(num_players)]
        session['current_player_index'] = 0
        session['dice'] = roll_dice()
        session['rolls'] = 0
        session['held_dice'] = [False] * 5
        
        game = Game(status='ongoing', current_player_index=0, dice=session['dice'], rolls=session['rolls'], held_dice=session['held_dice'])
        db.session.add(game)
        db.session.commit()
        session['current_game_id'] = game.id
        
        for player in session['players']:
            player_obj = Player(name=player['name'], game_id=game.id)
            db.session.add(player_obj)
        db.session.commit()
        
        return redirect(url_for('index'))
    return render_template('setup.html')

@app.route('/end_game', methods=['POST'])
def end_game():
    game_id = session.get('current_game_id')
    if game_id:
        game = Game.query.get(game_id)
        if game:
            game.status = 'completed'
            db.session.commit()
            session.clear()
            return f"Game ended. Your game ID is {game_id}. Save this ID to continue later."
    return "No game in progress", 400

@app.route('/continue', methods=['GET', 'POST'])
def continue_game():
    if request.method == 'POST':
        game_id = request.form['game_id']
        game = Game.query.get(game_id)
        if game and game.status == 'ongoing':
            session['current_game_id'] = game.id
            session['current_player_index'] = game.current_player_index
            session['dice'] = game.dice
            session['rolls'] = game.rolls
            session['held_dice'] = game.held_dice
            session['players'] = [{'name': player.name, 'score': player.score, 'used_categories': {}} for player in game.players]
            return redirect(url_for('index'))
        else:
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

        session['rolls'] = 0
        session['held_dice'] = [False] * 5
        session['dice'] = roll_dice()

        session['current_player_index'] = (session['current_player_index'] + 1) % len(session['players'])
        
        game_id = session.get('current_game_id')
        if game_id:
            game = Game.query.get(game_id)
            if game:
                game.current_player_index = session['current_player_index']
                game.dice = session['dice']
                game.rolls = session['rolls']
                game.held_dice = session['held_dice']
                db.session.commit()
    return redirect(url_for('index'))

# Pisteytysfunktiot
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
        return max(pairs) * 2 if pairs else 0
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
    with app.app_context():
        db.create_all()
    app.run(debug=True)
