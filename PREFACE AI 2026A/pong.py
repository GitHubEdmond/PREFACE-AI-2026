"""
Simple Pong game in Python using the built-in turtle module.

How to run:
1. Activate your venv (optional).
2. In a terminal, cd into the folder that contains this file.
3. Run:  python pong.py
"""

import turtle

# ----- Screen setup -----
wn = turtle.Screen()
wn.title("Pong - PREFACE AI 2026A")
wn.bgcolor("black")
wn.setup(width=800, height=600)
wn.tracer(0)  # Turns off automatic screen updates for smoother animation

# ----- Score -----
score_a = 0
score_b = 0

# ----- Paddle A (left) -----
paddle_a = turtle.Turtle()
paddle_a.speed(0)              # Animation speed (0 = fastest)
paddle_a.shape("square")
paddle_a.color("white")
paddle_a.shapesize(stretch_wid=5, stretch_len=1)  # 5x height, 1x width
paddle_a.penup()
paddle_a.goto(-350, 0)         # Start near left edge

# ----- Paddle B (right) -----
paddle_b = turtle.Turtle()
paddle_b.speed(0)
paddle_b.shape("square")
paddle_b.color("white")
paddle_b.shapesize(stretch_wid=5, stretch_len=1)
paddle_b.penup()
paddle_b.goto(350, 0)          # Start near right edge

# ----- Ball -----
ball = turtle.Turtle()
ball.speed(0)
ball.shape("circle")
ball.color("white")
ball.penup()
ball.goto(0, 0)

# Ball movement in x and y directions
ball.dx = 0.25
ball.dy = 0.25

# ----- Pen (scoreboard) -----
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Player A: 0  Player B: 0",
          align="center", font=("Courier", 18, "normal"))


# ----- Paddle movement functions -----

def paddle_a_up():
    """Move left paddle up."""
    y = paddle_a.ycor()  # current y
    y += 20
    if y > 250:          # keep paddle inside window
        y = 250
    paddle_a.sety(y)


def paddle_a_down():
    """Move left paddle down."""
    y = paddle_a.ycor()
    y -= 20
    if y < -250:
        y = -250
    paddle_a.sety(y)


def paddle_b_up():
    """Move right paddle up."""
    y = paddle_b.ycor()
    y += 20
    if y > 250:
        y = 250
    paddle_b.sety(y)


def paddle_b_down():
    """Move right paddle down."""
    y = paddle_b.ycor()
    y -= 20
    if y < -250:
        y = -250
    paddle_b.sety(y)


# ----- Keyboard bindings -----
wn.listen()
wn.onkeypress(paddle_a_up, "w")
wn.onkeypress(paddle_a_down, "s")
wn.onkeypress(paddle_b_up, "Up")
wn.onkeypress(paddle_b_down, "Down")


# ----- Main game loop -----
while True:
    wn.update()  # Manually update the screen each loop

    # Move the ball
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Top border check
    if ball.ycor() > 290:
        ball.sety(290)
        ball.dy *= -1  # reverse direction

    # Bottom border check
    if ball.ycor() < -290:
        ball.sety(-290)
        ball.dy *= -1

    # Right border (Player A scores)
    if ball.xcor() > 390:
        ball.goto(0, 0)
        ball.dx *= -1
        score_a += 1
        pen.clear()
        pen.write(f"Player A: {score_a}  Player B: {score_b}",
                  align="center", font=("Courier", 18, "normal"))

    # Left border (Player B scores)
    if ball.xcor() < -390:
        ball.goto(0, 0)
        ball.dx *= -1
        score_b += 1
        pen.clear()
        pen.write(f"Player A: {score_a}  Player B: {score_b}",
                  align="center", font=("Courier", 18, "normal"))

    # ----- Paddle and ball collisions -----

    # Collision with right paddle (paddle_b)
    if (340 < ball.xcor() < 350 and
            paddle_b.ycor() - 50 < ball.ycor() < paddle_b.ycor() + 50):
        ball.setx(340)
        ball.dx *= -1

    # Collision with left paddle (paddle_a)
    if (-350 < ball.xcor() < -340 and
            paddle_a.ycor() - 50 < ball.ycor() < paddle_a.ycor() + 50):
        ball.setx(-340)
        ball.dx *= -1

