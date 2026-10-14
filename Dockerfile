# Headless test/CI image for the Tetris desktop game.
#
# The game itself needs a desktop display for Tkinter.  This image runs only
# the domain-logic test suite, which has no display, network or input deps.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The GUI is not started here on purpose (it needs a host display).
CMD ["python", "-m", "pytest", "-q"]
