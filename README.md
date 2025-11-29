# Amirhossein Naderi Portfolio

Django-based portfolio site with:
- Three sample projects (GitHub AI Chatbot, Wikipedia scraper, Weather app)
- Live Gemini 2.5 Flash chatbot (via separate Flask backend)
- IMDB Top movies scraper displayed directly on the site
- Iran timezone clock
- Theme switcher (Ocean, Sunny, Night Sky) and Dark mode toggle
- About, Education, Skills, and Contact sections

## Running Django

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Running Gemini Flask backend

```bash
cd gemini_chatbot_flask
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python app.py
```

Then adjust Django JS to call the correct backend URL (for example, proxy `/gemini/api/chat` to the Flask server).
