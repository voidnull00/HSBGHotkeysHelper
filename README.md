# Hearthstone Battlegrounds Hotkey Helper

A Python script that provides quality-of-life hotkeys for Hearthstone Battlegrounds with human-like mouse movements and position memory.

## Features

- **Configurable Hotkeys**: Customize all hotkeys via `config.json`
- **Position Memory**: Returns mouse to original position after each action
- **Human-like Movements**: Uses Bezier curves for natural mouse motion
- **Randomized Clicks**: Adds slight variance to click positions within target areas
- **Adjustable Settings**: Control movement speed, delay, and behavior
- **Hero Power Support**: Dedicated hotkey for hero power activation

## Installation

1. **Prerequisites**:
   - Python 3.11 or later
   - Hearthstone running in 1920x1080 resolution (default positions are calibrated for this)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
