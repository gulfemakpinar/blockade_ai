# blockade_ai
Blockade game agent

•	In order to run the game in human vs human mode:

python3 game.py human human

•	In order to run the game in human vs agent mode:

python3 alphabeta_agent.py -b localhost -p 8001

python3 game.py human http://localhost:8001

•	In order to run the game in agent vs human mode:

python3 alphabeta_agent.py -b localhost -p 8001

python3 game.py http://localhost:8001 human

•	In order to run the game in agent vs random agent mode:

python3 alphabeta_agent.py -b localhost -p 8001

python3 random.py -b localhost -p 8002

python3 game.py http://localhost:8001 http://localhost:8002


•	In order to run the game in random agent vs agent mode:

python3 random.py -b localhost -p 8002

python3 alphabeta_agent.py -b localhost -p 8001

python3 game.py http://localhost:8002 http://localhost:8001

 
