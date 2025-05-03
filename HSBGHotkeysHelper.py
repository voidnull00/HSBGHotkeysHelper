"""
Hearthstone Battlegrounds Hotkey Script - Fast and Reliable
==========================================================
Created by: Julian
Updated: 05/05/2025 (Final optimized version)

Features:
- Instant mouse movements with precise clicks
- Returns mouse to original position after each action
- Configurable hotkeys via config.json
- Randomized click positions within target areas
- Minimal delays for fastest possible actions
- Toggle for position restoration
- Hero power hotkey support
- Clear keybind display on startup
"""

import json
import os
import random
import time
import keyboard
import pyautogui as pag
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
        "click_delay": 0.05,
        "return_to_original": True
    }
}

class MouseUtils:
    def __init__(self):
        self.original_position = None
        
    def click(self, position=None, button='left', delay=0.05, restore_position=True):
        """
        Optimized click method with position restoration
        """
        try:
            if restore_position:
                self.original_position = pag.position()
            
            if position:
                pag.moveTo(position)
                time.sleep(0.01)  # Tiny pause after movement
            
            # More reliable than single click() command
            pag.mouseDown(button=button)
            time.sleep(0.02)  # Physical click duration
            pag.mouseUp(button=button)
            time.sleep(max(0, delay - 0.02))  # Remaining delay
            
        finally:
            if restore_position and self.original_position:
                try:
                    pag.moveTo(self.original_position)
                except:
                    pass  # Fail silently if mouse gets moved during cleanup
                self.original_position = None

class HSBGHotkeys:
    def __init__(self):
        self.mouse = MouseUtils()
        self.config = self.load_config()
        self.setup_hotkeys()
        self.running = True
        
    def load_config(self):
        """Load or create configuration file with validation"""
        if not os.path.exists(CONFIG_FILE):
            print(f"Creating default config file: {CONFIG_FILE}")
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG
        
        with open(CONFIG_FILE) as f:
            try:
                config = json.load(f)
                # Validate config structure
                for section, defaults in DEFAULT_CONFIG.items():
                    if section not in config:
                        config[section] = defaults
                    else:
                        for key, value in defaults.items():
                            if key not in config[section]:
                                config[section][key] = value
                return config
            except json.JSONDecodeError:
                print("Error: Invalid config file, using defaults")
                return DEFAULT_CONFIG
    
    def setup_hotkeys(self):
        """Setup all hotkeys from config"""
        try:
            # Tavern actions
            keyboard.add_hotkey(self.config["hotkeys"]["refresh_tavern"], self.refresh_tavern)
            keyboard.add_hotkey(self.config["hotkeys"]["freeze_tavern"], self.freeze_tavern)
            keyboard.add_hotkey(self.config["hotkeys"]["upgrade_tavern"], self.upgrade_tavern)
            
            # Hero power
            keyboard.add_hotkey(self.config["hotkeys"]["hero_power"], self.hero_power)
            
            # Control hotkeys
            keyboard.add_hotkey("ctrl+shift+q", self.stop)
            keyboard.add_hotkey("ctrl+shift+r", self.reload_config)
        except KeyError as e:
            print(f"Error: Missing hotkey in config - {e}")

    def reload_config(self):
        """Reload configuration safely"""
        print("Reloading config...")
        try:
            keyboard.unhook_all_hotkeys()
            self.config = self.load_config()
            self.setup_hotkeys()
            print("Config reloaded successfully!")
            self.print_keybinds()
        except Exception as e:
            print(f"Error reloading config: {e}")
            keyboard.unhook_all_hotkeys()
            self.setup_hotkeys()  # Try to restore previous bindings
    
    def stop(self):
        """Stop the hotkey listener"""
        print("Stopping hotkey listener...")
        self.running = False
    
    def get_target_position(self, button_name):
        """Get randomized target position with validation"""
        try:
            pos_config = self.config["positions"][button_name]
            x = pos_config.get("x", 0)
            y = pos_config.get("y", 0)
            variance = pos_config.get("variance", 0)
            
            if variance > 0:
                x += random.randint(-variance, variance)
                y += random.randint(-variance, variance)
                
            return (x, y)
        except KeyError:
            print(f"Warning: No position configured for {button_name}")
            return None
    
    def print_keybinds(self):
        """Display the current keybind configuration"""
        print("\nCurrent Keybinds:")
        print("-----------------")
        for action, key in self.config["hotkeys"].items():
            print(f"{action.replace('_', ' ').title():<15}: {key}")
        print("\nControl Hotkeys:")
        print("Ctrl+Shift+Q: Quit")
        print("Ctrl+Shift+R: Reload config")
        print("-----------------")
    
    # Action methods
    def refresh_tavern(self):
        """Refresh tavern action"""
        if target := self.get_target_position("refresh_button"):
            self.mouse.click(
                position=target,
                delay=self.config["mouse_settings"]["click_delay"],
                restore_position=self.config["mouse_settings"]["return_to_original"]
            )
    
    def freeze_tavern(self):
        """Freeze tavern action"""
        if target := self.get_target_position("freeze_button"):
            self.mouse.click(
                position=target,
                delay=0.03,
                restore_position=self.config["mouse_settings"]["return_to_original"]
            )
    
    def upgrade_tavern(self):
        """Upgrade tavern action"""
        if target := self.get_target_position("upgrade_button"):
            self.mouse.click(
                position=target,
                delay=0.03,
                restore_position=self.config["mouse_settings"]["return_to_original"]
            )
    
    def hero_power(self):
        """Hero power action"""
        if target := self.get_target_position("hero_power_button"):
            self.mouse.click(
                position=target,
                delay=0.03,
                restore_position=self.config["mouse_settings"]["return_to_original"]
            )
    
    def run(self):
        """Main execution loop"""
        print("\nHearthstone Battlegrounds Hotkeys running...")
        self.print_keybinds()
        
        try:
            while self.running:
                time.sleep(0.1)
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            keyboard.unhook_all()

if __name__ == "__main__":
    # Safety settings
    pag.FAILSAFE = True
    pag.PAUSE = 0.01  # Small default pause after pyautogui actions
    
    try:
        hotkeys = HSBGHotkeys()
        hotkeys.run()
    except KeyboardInterrupt:
        print("\nScript stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        keyboard.unhook_all()
        print("Cleanup complete")
