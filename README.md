# StyleSync AI

AI-powered virtual try-on and personal fashion styling web application.

## Requirements
- Python 3.10+
- MongoDB Community Server running locally OR MongoDB Atlas connection string
- FASHN API account and API key for real virtual try-on (paid credits may be required)

## Setup (Windows)
1. Install Python and MongoDB. Alternatively create a MongoDB Atlas cluster.
2. Extract this ZIP and open the `StyleSyncAI` folder in VS Code.
3. Open Terminal in this folder:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to a new file named `.env`.
5. Add your MongoDB connection string and FASHN API key to `.env`.
6. Run:
   ```bash
   python app.py
   ```
7. Open http://127.0.0.1:5000

## Setup (macOS/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

## Configure AI Virtual Try-On
1. Create an account at https://app.fashn.ai/
2. Open the Developer API dashboard and create an API key. API credits are required.
3. Paste the key into `FASHN_API_KEY` in `.env`.
4. Restart Flask. The app sends the two uploaded images to the FASHN `tryon-max` API and polls until the result is ready.

If the key is missing, the application displays a clear configuration error rather than generating a fake AI result.

## Admin account
Set `ADMIN_EMAIL` in `.env` before registering. Register using exactly that email to receive the admin role. For a real deployment, add a separate secure admin-provisioning process and do not expose admin registration publicly.

## Main project structure
- `app.py`: Flask routes, login, dashboard, history, favourites and admin
- `config.py`: environment-based configuration
- `services/fashn.py`: actual AI API integration
- `services/images.py`: upload validation
- `services/recommender.py`: transparent rule-based outfit suggestions
- `templates/`: HTML pages
- `static/css/style.css`: UI design
- `static/js/main.js`: image previews

## Important limitations and production checklist
- The recommendation engine in this starter release is rule-based, not a trained ML model. It can be upgraded using a labelled fashion dataset and evaluated recommendation model.
- Size suggestions are not included because reliable size prediction needs measurements, garment sizing data and validation.
- AI-generated images are previews; they do not guarantee real garment fit or exact fabric behaviour.
- For production: use HTTPS, a strong secret key, secure cookie settings, CSRF protection, rate limiting, cloud object storage, background jobs, deletion/retention controls, audit logs and a privacy policy.
- Uploaded personal photos are stored in `static/uploads` by this local demo. Add user-controlled deletion and private cloud storage before public deployment. Never commit `.env` or user photos to GitHub.
