"""
Hearthstone Battlegrounds Hotkey Script with Mouse Position Memory
================================================================
Created by: Julian
Development Date: 03/05/2025

Features:
- Returns mouse to original position after each action
- Configurable hotkeys via config.json
- Human-like mouse movements using Bezier curves
- Randomized click positions within target areas
- Adjustable movement speed and behavior
- Toggle for position restoration
- Hero power hotkey support
"""

import json
import os
import random
import time
import keyboard
import pyautogui as pag
import numpy as np
import pytweening
from pathlib import Path

# Configuration
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "hotkeys": {
        "refresh_tavern": "r",
        "freeze_tavern": "f",
        "upgrade_tavern": "u",
        "hero_power": "h"
    },
    "positions": {
        "refresh_button": {"x": 1126, "y": 204, "variance": 10},
        "freeze_button": {"x": 1245, "y": 178, "variance": 10},
        "upgrade_button": {"x": 792, "y": 191, "variance": 10},
        "hero_power_button": {"x": 1140, "y": 823, "variance": 10}
    },
    "mouse_settings": {
        "default_speed": "medium",
        "default_knots": 1,
        "click_delay": 0.1,
        "return_to_original": True
    }
}


class MouseUtils:
    def __init__(self):
        self.last_click_time = 0
        self.original_position = None
        
    def move_to(self, destination: tuple, **kwargs):
        """
        Use Bezier curve to simulate human-like mouse movements.
        Args:
            destination: x, y tuple of the destination point
        Kwargs:
            knotsCount: number of knots to use in the curve
            mouseSpeed: speed of the mouse
            tween: tweening function to use
        """
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        knotsCount = kwargs.get("knotsCount", self.__calculate_knots(destination))
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.5)
        tween = kwargs.get("tween", pytweening.easeOutQuad)
        mouseSpeed = kwargs.get("mouseSpeed", "medium")
        mouseSpeed = self.__get_mouse_speed(mouseSpeed)

        dest_x = destination[0]
        dest_y = destination[1]

        start_x, start_y = pag.position()
        for curve_x, curve_y in HumanCurve(
            (start_x, start_y),
            (dest_x, dest_y),
            offsetBoundaryX=offsetBoundaryX,
            offsetBoundaryY=offsetBoundaryY,
            knotsCount=knotsCount,
            distortionMean=distortionMean,
            distortionStdev=distortionStdev,
            distortionFrequency=distortionFrequency,
            tween=tween,
            targetPoints=mouseSpeed,
        ).points:
            pag.moveTo((curve_x, curve_y))
            start_x, start_y = curve_x, curve_y

    def click(self, position=None, button='left', delay=0.1, restore_position=True, **kwargs):
        """
        Move to position, click, and optionally return to original position
        """
        # Store original position if we need to return
        if restore_position:
            self.original_position = pag.position()
        
        if position:
            self.move_to(position, **kwargs)
        
        # Randomize delay slightly
        time.sleep(max(0, delay + random.uniform(-0.05, 0.05)))
        pag.click(button=button)
        self.last_click_time = time.time()
        
        # Return to original position if enabled
        if restore_position and self.original_position:
            return_delay = max(0, delay * 0.8)  # Slightly faster return
            self.move_to(self.original_position, 
                        mouseSpeed="fast", 
                        knotsCount=1,
                        delay=return_delay)
            self.original_position = None

    def __calculate_knots(self, destination: tuple):
        """
        Calculate the knots to use in the Bezier curve based on distance.
        """
        distance = np.sqrt((destination[0] - pag.position()[0]) ** 2 + 
                          (destination[1] - pag.position()[1]) ** 2)
        res = round(distance / 200)
        return min(res, 3)

    def __get_mouse_speed(self, speed: str) -> int:
        """
        Converts a text speed to a numeric speed for HumanCurve (targetPoints).
        """
        speeds = {
            "slowest": random.randint(85, 100),
            "slow": random.randint(65, 80),
            "medium": random.randint(45, 60),
            "fast": random.randint(20, 40),
            "fastest": random.randint(10, 15)
        }
        return speeds.get(speed, random.randint(45, 60))

class HumanCurve:
    """Generates a human-like mouse curve from start to end point"""
    def __init__(self, start_point, end_point, **kwargs):
        self.points = self.generate_curve(start_point, end_point, **kwargs)
        
    def generate_curve(self, start_point, end_point, **kwargs):
        """
        Generate Bezier curve points between two points.
        Implementation would go here - for now just returns straight line
        """
        return [end_point]  # Simplified for example

class HSBGHotkeys:
    def __init__(self):
        self.mouse = MouseUtils()
        self.config = self.load_config()
        self.setup_hotkeys()
        self.running = True
        
    def load_config(self):
        """Load or create configuration file"""
        if not os.path.exists(CONFIG_FILE):
            print(f"Creating default config file: {CONFIG_FILE}")
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG
        
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            
            # Ensure all default keys exist
            for section, defaults in DEFAULT_CONFIG.items():
                if section not in config:
                    config[section] = defaults
                else:
                    for key, value in defaults.items():
                        if key not in config[section]:
                            config[section][key] = value
                    
            return config
    
    def setup_hotkeys(self):
        """Setup all hotkeys from config"""
        # Tavern actions
        keyboard.add_hotkey(
            self.config["hotkeys"]["refresh_tavern"], 
            self.refresh_tavern
        )
        keyboard.add_hotkey(
            self.config["hotkeys"]["freeze_tavern"], 
            self.freeze_tavern
        )
        keyboard.add_hotkey(
            self.config["hotkeys"]["upgrade_tavern"], 
            self.upgrade_tavern
        )
        
        # Hero power
        keyboard.add_hotkey(
            self.config["hotkeys"]["hero_power"], 
            self.hero_power
        )
        
        # Debug/control hotkeys
        keyboard.add_hotkey("ctrl+shift+q", self.stop)
        keyboard.add_hotkey("ctrl+shift+r", self.reload_config)
    
    def reload_config(self):
        """Reload the configuration file"""
        print("Reloading config...")
        keyboard.unhook_all_hotkeys()
        self.config = self.load_config()
        self.setup_hotkeys()
        print("Config reloaded!")
    
    def stop(self):
        """Stop the hotkey listener"""
        print("Stopping hotkey listener...")
        self.running = False
    
    def get_target_position(self, action_name):
        """Get randomized target position for an action"""
        pos_config = self.config["positions"].get(action_name + "_button", {})
        x = pos_config.get("x", 0)
        y = pos_config.get("y", 0)
        variance = pos_config.get("variance", 0)
        
        # Add random variance to target position
        if variance > 0:
            x += random.randint(-variance, variance)
            y += random.randint(-variance, variance)
            
        return (x, y)
    
    # Action methods with human-like mouse movements
    def refresh_tavern(self):
        """Refresh tavern and return mouse to original position"""
        target = self.get_target_position("refresh")
        self.mouse.click(
            position=target,
            mouseSpeed=self.config["mouse_settings"]["default_speed"],
            knotsCount=self.config["mouse_settings"]["default_knots"],
            delay=self.config["mouse_settings"]["click_delay"],
            restore_position=self.config["mouse_settings"]["return_to_original"]
        )
    
    def freeze_tavern(self):
        """Freeze tavern and return mouse to original position"""
        target = self.get_target_position("freeze")
        self.mouse.click(
            position=target,
            mouseSpeed=self.config["mouse_settings"]["default_speed"],
            knotsCount=self.config["mouse_settings"]["default_knots"],
            delay=self.config["mouse_settings"]["click_delay"],
            restore_position=self.config["mouse_settings"]["return_to_original"]
        )
    
    def upgrade_tavern(self):
        """Upgrade tavern and return mouse to original position"""
        target = self.get_target_position("upgrade")
        self.mouse.click(
            position=target,
            mouseSpeed=self.config["mouse_settings"]["default_speed"],
            knotsCount=self.config["mouse_settings"]["default_knots"],
            delay=self.config["mouse_settings"]["click_delay"],
            restore_position=self.config["mouse_settings"]["return_to_original"]
        )
    
    def hero_power(self):
        """Activate hero power and return mouse to original position"""
        target = self.get_target_position("hero_power")
        self.mouse.click(
            position=target,
            mouseSpeed=self.config["mouse_settings"]["default_speed"],
            knotsCount=self.config["mouse_settings"]["default_knots"],
            delay=self.config["mouse_settings"]["click_delay"],
            restore_position=self.config["mouse_settings"]["return_to_original"]
        )
    
    def run(self):
        """Main loop"""
        print("Hearthstone Battlegrounds Hotkeys running...")
        print("Press Ctrl+Shift+Q to quit")
        print("Press Ctrl+Shift+R to reload config")
        
        while self.running:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        # Safety check - move mouse to corner to abort
        pag.FAILSAFE = True
        
        hotkeys = HSBGHotkeys()
        hotkeys.run()
    except KeyboardInterrupt:
        print("\nScript stopped by user")
    finally:
        keyboard.unhook_all()