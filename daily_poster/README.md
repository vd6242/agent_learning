# Daily Poster

Cycles through the 10 slides in `assets/slides.pptx` (the Graphology class
deck) and emails one rendered slide-as-poster per run. State is kept in
`state.json` so each run advances to the next slide and loops back to slide 1
after slide 10.

Slides are re-rendered with python-pptx + Pillow (no LibreOffice dependency)
because LibreOffice headless conversion was unavailable in the dev sandbox.

## Setup

```bash
cd daily_poster
pip install -r requirements.txt
```

### Email credentials (Gmail App Password recommended)

1. Enable 2-Step Verification on the Google account.
2. Create an App Password: https://myaccount.google.com/apppasswords
3. Export these env vars (e.g. in `~/.bashrc` or a local `.env` you source
   before running):

```bash
export POSTER_SMTP_HOST=smtp.gmail.com
export POSTER_SMTP_PORT=587
export POSTER_SMTP_USER=your_address@gmail.com
export POSTER_SMTP_PASSWORD=your_16_char_app_password
export POSTER_TO_EMAIL=your_address@gmail.com   # optional, defaults to POSTER_SMTP_USER
```

If you use a different provider, swap `POSTER_SMTP_HOST`/`POSTER_SMTP_PORT`
accordingly (e.g. Outlook: `smtp.office365.com:587`).

## Run manually

```bash
python3 send_daily_poster.py
```

## Schedule with cron (runs daily at 8am)

```bash
crontab -e
```

Add (adjust paths and make sure env vars are available to cron, e.g. by
sourcing a credentials file):

```
0 8 * * * source /path/to/poster_env.sh && cd /path/to/daily_poster && /usr/bin/python3 send_daily_poster.py >> /tmp/daily_poster.log 2>&1
```

Where `poster_env.sh` exports the `POSTER_*` variables above.
