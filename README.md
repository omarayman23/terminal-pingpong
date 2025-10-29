# terminal-pingpong
Play single player AND multi player ping pong on ur terminal with friends!
# How to set-up.
- create a file named pingpong in ur desktop and add these game_client.py & game_server.py
- open ur terminal and change the directory to ping pong: cd Desktop/pingpong
- then install websockets: For macOS(pip3 install websocket) for windows (pip install websockets)
- IF THAT DOESNT WORK FOLLOW THESE STEPS:
  --  RUN these commands all togather:
  cd ~/Desktop/pingpong
  python3 -m venv venv
  source venv/bin/activate
  -- You should see: (venv) name@name-Air pingpong %
  -- now copy and paste: pip install websockets
- Final step, run: python game_client.py


