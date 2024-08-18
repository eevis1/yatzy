CREATE TABLE game (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'ongoing',
    current_player_index INTEGER DEFAULT 0,
    dice INTEGER[] DEFAULT ARRAY[1, 1, 1, 1, 1],
    rolls INTEGER DEFAULT 0,
    held_dice BOOLEAN[] DEFAULT ARRAY[FALSE, FALSE, FALSE, FALSE, FALSE]
);

CREATE TABLE player (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    score INTEGER DEFAULT 0,
    game_id INTEGER REFERENCES game(id) ON DELETE CASCADE,
    completed_game_id INTEGER REFERENCES completed_game(id) ON DELETE CASCADE
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    score INTEGER NOT NULL,
    player_id INTEGER REFERENCES player(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES game(id) ON DELETE CASCADE
);

CREATE TABLE completed_game (
    id SERIAL PRIMARY KEY,
    final_scores JSON NOT NULL
);

CREATE TABLE player_category (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES player(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES category(id) ON DELETE CASCADE
);
