# Raspberry Pi Alarm Project

## Overview
This project implements a full-screen alarm clock for a Raspberry Pi. It displays the current time, date, weather information, and upcoming calendar events. An animated emoji and a looping alarm sound ensure that the user wakes on time.

## Features
- **Digital Clock:** Displays hours, minutes, and seconds in a retro style.
- **Weather Updates:** Retrieves weather data from the WeatherUnlocked API.
- **Calendar Integration:** Fetches today's events from a connected Google Calendar.
- **Alarm Functionality:** Plays an alarm sound in loop until manually stopped.
- **Touch-Friendly UI:** Designed for easy use on touch-enabled devices.
- **Animated Emoji Display:** Adds a visual retro effect.

## Dependencies
- Python 3.x
- PyQt5
- pygame
- python-vlc
- requests
- google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client

## Installation
1. Clone the repository.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install system dependencies (for example, on Debian/Raspbian):
   ```bash
   sudo apt-get install python3-pyqt5 python3-vlc
   ```

## Configuration
- **Google Calendar:** Place your `credentials.json` file in the project's base directory and ensure tokens are managed via `token.pickle`.
- **Paths:** Configure paths for fonts, logs, and the alarm sound in `paths_config.py`.
- **Weather API:** Update your WeatherUnlocked API credentials directly in the source code or via configuration.

## Usage
Run the project by executing:
```bash
python src/main.py
```
The alarm will trigger at the configured time and the sound will loop until the "DETENER ALARMA" button is pressed.

## Project Structure
- **src/main_window.py:** Main UI and alarm logic.
- **src/calendar_handler.py:** Google Calendar integration.
- **paths_config.py:** File paths configuration.
- **settings_window.py:** UI for setting the alarm time.
- **emoji_animation.py:** Handles the animated emoji display.

## Troubleshooting
- **Alarm Sound:** If the alarm sound is not looping, verify that VLC and the alarm sound file are correctly configured.
- **Calendar Issues:** Ensure your Google credentials are valid and that the token file is up-to-date.
- **Weather Data:** Check your API keys and network connection for weather fetch errors.

## License
This project is licensed under the MIT License.

```
MIT License

Copyright (c) [year] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

## Contributing
Contributions are welcome. Please follow the coding standards and include tests for any new functionality.
