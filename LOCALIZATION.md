# Localization System

This document describes the gettext-based localization system implemented for all agents in the multiagent-telegram project.

## Overview

The localization system uses the standard gettext approach with PO (Portable Object) and MO (Machine Object) files. Each agent has its own translation files in a `locale` folder structure.

## Directory Structure

```
Agents/
├── WeatherAgent/
│   └── locale/
│       ├── en/
│       │   └── LC_MESSAGES/
│       │       ├── messages.po
│       │       └── messages.mo
│       └── pl/
│           └── LC_MESSAGES/
│               ├── messages.po
│               └── messages.mo
├── TimeAgent/
│   └── locale/
│       ├── en/
│       │   └── LC_MESSAGES/
│       │       ├── messages.po
│       │       └── messages.mo
│       └── pl/
│           └── LC_MESSAGES/
│               ├── messages.po
│               └── messages.mo
├── DefaultAgent/
│   └── locale/
│       ├── en/
│       │   └── LC_MESSAGES/
│       │       ├── messages.po
│       │       └── messages.mo
│       └── pl/
│           └── LC_MESSAGES/
│               ├── messages.po
│               └── messages.mo
└── ConfigurationAgent/
    └── locale/
        ├── en/
        │   └── LC_MESSAGES/
        │       ├── messages.po
        │       └── messages.mo
        └── pl/
            └── LC_MESSAGES/
                ├── messages.po
                └── messages.mo
```

## How It Works

### 1. Base Agent Class

The `AgentBase` class provides localization functionality:

- `_get_user_language()`: Gets the user's preferred language from questionnaire answers
- `_get_translator()`: Creates a gettext translator for the user's language
- `_(message)`: Translation function that wraps gettext

### 2. Language Detection

- Default language is "en" (English)
- User language is stored in `questionnaire_answers['language']`
- If no translation exists for the user's language, English is used as fallback

### 3. Translation Usage

In agent code, use the `_()` function for translatable strings:

```python
def some_method(self):
    return self._("Hello, welcome to the weather service!")
```

For strings with variables:

```python
def some_method(self, city_name):
    return self._("Weather forecast for {city}").format(city=city_name)
```

### 4. Response Formatter Pattern

For utility functions like response formatters that don't have direct access to the agent's translation context, pass the translation function as a parameter:

```python
# In the agent
response = format_weather_response(weather_data, lat, lon, city_name, self._)

# In the response formatter
def format_weather_response(weather_data, lat, lon, city_name, translate_func):
    return translate_func("Weather forecast for {city}").format(city=city_name)
```

This pattern ensures that all user-facing strings can be localized while maintaining clean separation of concerns.

## Supported Languages

Currently supported:
- **en**: English (default)
- **pl**: Polish

## Adding New Languages

To add a new language (e.g., German):

1. Create the locale directory structure:
   ```bash
   mkdir -p Agents/WeatherAgent/locale/de/LC_MESSAGES
   ```

2. Copy the English PO file and translate it:
   ```bash
   cp Agents/WeatherAgent/locale/en/LC_MESSAGES/messages.po Agents/WeatherAgent/locale/de/LC_MESSAGES/
   ```

3. Edit the German PO file and translate the `msgstr` entries

4. Compile the PO file to MO:
   ```bash
   cd Agents/WeatherAgent/locale/de/LC_MESSAGES
   msgfmt messages.po -o messages.mo
   ```

5. Update the base agent class to include the new language

## Translation Management

### Using the Management Script

The project includes a `manage_translations.py` script for managing translations:

```bash
# Update all translations (compile PO to MO)
python manage_translations.py update-all

# Update specific agent
python manage_translations.py update WeatherAgent

# Extract messages from source files
python manage_translations.py extract-all

# Extract messages from specific agent
python manage_translations.py extract WeatherAgent
```

### Manual Commands

#### Compile PO to MO
```bash
cd Agents/WeatherAgent/locale/pl/LC_MESSAGES
msgfmt messages.po -o messages.mo
```

#### Create POT file from source
```bash
cd Agents/WeatherAgent
xgettext --from-code=UTF-8 --keyword=_ --keyword=gettext --output=locale/messages.pot *.py
```

#### Update PO file with new POT
```bash
cd Agents/WeatherAgent/locale/pl/LC_MESSAGES
msgmerge --update messages.po ../messages.pot
```

## Best Practices

1. **Always use the `_()` function** for user-facing strings
2. **Use placeholders for variables** instead of string concatenation
3. **Keep translations context-aware** - the same English string might need different translations in different contexts
4. **Test translations** with native speakers when possible
5. **Maintain consistent terminology** across all agents
6. **For utility functions**, pass the translation function as a parameter to maintain localization support

## Troubleshooting

### Common Issues

1. **Translation not working**: Check if the MO file exists and is compiled correctly
2. **Wrong language displayed**: Verify the user's language setting in questionnaire_answers
3. **Missing translations**: Ensure all strings are wrapped with `_()`
4. **Response formatter not translated**: Make sure to pass the translation function as a parameter

### Debug Mode

To debug localization issues, you can temporarily modify the base agent to log language detection:

```python
def _get_user_language(self) -> str:
    user_lang = self.questionnaire_answers.get('language', 'en') if self.questionnaire_answers else 'en'
    print(f"Debug: User language detected as: {user_lang}")
    return user_lang
```

## Dependencies

The localization system requires:
- `gettext` (system package)
- `gettext-tools` (Python package, for the management script)

Install system dependencies:
```bash
# macOS
brew install gettext

# Ubuntu/Debian
sudo apt-get install gettext

# CentOS/RHEL
sudo yum install gettext
```

## Future Enhancements

Potential improvements:
- Automatic language detection from user messages
- Support for more languages
- Translation memory and consistency checking
- Integration with translation services (Google Translate, DeepL)
- Pluralization support for languages with complex plural rules
