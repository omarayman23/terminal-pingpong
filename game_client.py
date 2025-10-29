import curses
import time
import os
import json
import random
import asyncio
import websockets

SAVE_PATH = "saves"
os.makedirs(SAVE_PATH, exist_ok=True)

def save_progress(username, score, level):
    with open(f"{SAVE_PATH}/{username}.json", "w") as f:
        json.dump({"score": score, "level": level}, f)

def load_progress(username):
    path = f"{SAVE_PATH}/{username}.json"
    if not os.path.exists(path):
        return {"score": 0, "level": 1}
    with open(path, "r") as f:
        return json.load(f)

def main_menu(stdscr):
    options = ["Single Player", "Multiplayer", "Quit"]
    selected = 0
    curses.curs_set(0)
    stdscr.nodelay(0)

    while True:
        stdscr.clear()
        stdscr.addstr(2, 4, "🏓 Terminal Ping Pong", curses.A_BOLD)
        for i, opt in enumerate(options):
            attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
            stdscr.addstr(4 + i, 6, opt, attr)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in [10, 13]:  # Enter
            return options[selected]

def singleplayer_menu(stdscr, username):
    options = ["Start New Game", "Load Saved Game", "Back"]
    selected = 0
    while True:
        stdscr.clear()
        stdscr.addstr(2, 4, f"🎮 Single Player - {username}", curses.A_BOLD)
        for i, opt in enumerate(options):
            attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
            stdscr.addstr(4 + i, 6, opt, attr)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in [10, 13]:
            return options[selected]

def single_player(stdscr, username, load=False):
    curses.curs_set(0)
    stdscr.nodelay(1)

    if load:
        data = load_progress(username)
        score, level = data["score"], data["level"]
    else:
        score, level = 0, 1

    sh, sw = stdscr.getmaxyx()
    paddle_y = sh // 2
    paddle_x = sw - 3
    ball_y = sh // 2
    ball_x = sw // 3
    ball_dir_y = random.choice([-1, 1])
    ball_dir_x = 1

    speed = max(25, 80 - (level * 5))
    lives = 3

    while True:
        stdscr.clear()
        stdscr.border()
        stdscr.addstr(0, 2, f"Score: {score}  Level: {level}  Lives: {lives}")
        stdscr.addstr(0, sw - 20, f"Player: {username}")

        for i in range(-2, 3):
            if 0 < paddle_y + i < sh - 1:
                stdscr.addstr(paddle_y + i, paddle_x, "|")
        stdscr.addstr(ball_y, ball_x, "O")

        key = stdscr.getch()
        if key == curses.KEY_UP and paddle_y > 3:
            paddle_y -= 1
        elif key == curses.KEY_DOWN and paddle_y < sh - 4:
            paddle_y += 1
        elif key == ord("q"):
            save_progress(username, score, level)
            break

        # Move ball
        ball_y += ball_dir_y
        ball_x += ball_dir_x

        # Bounce top/bottom
        if ball_y <= 1 or ball_y >= sh - 2:
            ball_dir_y *= -1

        # Left wall
        if ball_x <= 1:
            ball_dir_x *= -1

        # Paddle collision
        if ball_x == paddle_x - 1 and paddle_y - 2 <= ball_y <= paddle_y + 2:
            ball_dir_x *= -1
            score += 1
            if score % 10 == 0:
                level += 1
                speed = max(10, speed - 5)

        # Miss
        if ball_x >= sw - 1:
            lives -= 1
            if lives == 0:
                stdscr.addstr(sh // 2, sw // 2 - 5, "GAME OVER!")
                stdscr.refresh()
                time.sleep(2)
                save_progress(username, score, level)
                break
            ball_x, ball_y = sw // 2, sh // 2
            ball_dir_x, ball_dir_y = -1, random.choice([-1, 1])

        stdscr.refresh()
        time.sleep(speed / 1000)

async def multiplayer_client(username, opponent, uri):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"username": username, "invite": opponent}))
        print(f"🔗 Sent invite to {opponent}... waiting for response.")
        while True:
            msg = await websocket.recv()
            print("Server:", msg)

def main(stdscr):
    username = "Player" + str(random.randint(1000, 9999))
    while True:
        choice = main_menu(stdscr)
        if choice == "Quit":
            break
        elif choice == "Single Player":
            sub = singleplayer_menu(stdscr, username)
            if sub == "Start New Game":
                single_player(stdscr, username, load=False)
            elif sub == "Load Saved Game":
                single_player(stdscr, username, load=True)
        elif choice == "Multiplayer":
            curses.endwin()
            opponent = input("Enter opponent username to invite: ")
            asyncio.run(multiplayer_client(username, opponent, "ws://localhost:8765"))

if __name__ == "__main__":
    curses.wrapper(main)
