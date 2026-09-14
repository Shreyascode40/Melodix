# Melodix — Full-Stack Music Streaming & Playlist Platform

Premium, minimal music dashboard where you can search, play, like, and manage playlists — plus create a playlist automatically from a screenshot of any playlist.

> Inspired by the soft light-gray + white premium dashboard direction, with circular artwork, subtle shadows, and spacious layout — not a clone of Spotify/Apple Music.

**Live stack:** React 19 + TypeScript + Vite + Tailwind CSS (via CSS variables) · Django 5.2 + DRF + SimpleJWT · SQLite (dev) / PostgreSQL (prod) · Audius + Jamendo (pluggable) · MusicBrainz for metadata · Redis (optional) · PaddleOCR / Tesseract fallback

**Repo:** https://github.com/Shreyascode40/Melodix

---

## Features

- **Auth:** Register / Login / Logout / `GET /api/auth/me/` / `PATCH /api/auth/profile/` with avatar
- **Music:** Provider-agnostic `music/services/` ( `audius.py` , `jamendo.py` , `music_service.py` ) normalizes to `{id, provider, title, artist, album, cover_url, duration, stream_url, language, musicbrainz_id, match_score, playable}`
- **Search:** `GET /api/music/search/?q=&page=&limit=&provider=` with debounce (350ms), AbortController, front-cache, Redis-backed backend cache, query normalization (Unicode-safe), lightweight ranking (title/artist/penalize `remix/cover`)
- **Player:** Persistent global `PlayerContext` — Play/Pause/Prev/Next/Seek/Volume/Mute/Shuffle/Repeat/Queue/Progress, HTML5 Audio `preload="metadata"`, auto-next, handles empty `stream_url` by fetching via search
- **Playlists:** `Playlist` (name/description/cover/is_public) + `Song` (unique `provider+provider_song_id`) + `PlaylistSong` (position) — CRUD, add/remove/reorder (`PATCH /reorder/`), duplicate, public/private
- **Library:** Liked Songs / Recently Played (recorded on play) / My Playlists
- **Screenshot → Playlist:** Upload → validate → preprocess (invert dark UI) → OCR (PaddleOCR → pytesseract/Tesseract 5.5) → extract `title/artist` (handles YouTube Music `•` 2-line rows) → MusicBrainz enrichment → Audius matching → confidence + `Needs review` (<70) → user confirmation → create playlist preserving order

---

## Architecture

```
React (Vite)
  ↓  /api (axios + JWT refresh, AbortController, debounce, frontCache)
Django REST (DRF + SimpleJWT)
  ├─ accounts/ (auth/profile)
  ├─ music/  services/{audius,jamendo,session} + search/{normalizer,ranking,matcher} + musicbrainz.py
  ├─ playlists/ (CRUD + reorder)
  ├─ library/ (like/recent)
  └─ screenshot_import/ services/{image_processor,ocr,song_extractor,song_matcher,confidence}
       ↓ provider abstraction (BaseProvider: search_tracks/get_track/get_trending/get_stream_url)
       ↓ Session pooling (keep-alive, 2.5s connect /5s read, 429 respect Retry-After)
       ↓ Cache (django.core.cache → Redis if REDIS_URL else LocMem, TTL 900s, stale fallback)
```

**Provider-agnostic:** Add `NapsterProvider` etc. by implementing `BaseProvider`, registering in `music_service._providers`, no UI change.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, TypeScript, Vite, React Router 7, Axios, Context API, CSS variables (light/dark) |
| Backend | Python 3.11, Django 5.2, DRF, SimpleJWT + blacklist, Pillow, requests, python-dotenv, django-cors-headers |
| DB | SQLite (dev, `backend/db.sqlite3`) / PostgreSQL (prod via `DATABASE_URL` or docker-compose) |
| Cache | `django-redis` + `redis` if `REDIS_URL` else `LocMemCache` |
| OCR | `pytesseract` + `Tesseract 5.5` binary (required), `PaddleOCR` optional, `Pillow` |

---

## Installation

```bash
git clone https://github.com/Shreyascode40/Melodix.git
cd Melodix
```

### Backend setup

```powershell
cd D:\MyMusic\backend
python -m venv venv
.\venv\Scripts\activate
.\venv\Scripts\python -m pip install -r requirements.txt
# requires: Django djangorestframework djangorestframework-simplejwt django-cors-headers Pillow requests python-dotenv redis django-redis rapidfuzz pytesseract
copy .env.example .env  # fill real keys, see Environment
.\venv\Scripts\python manage.py migrate
.\venv\Scripts\python manage.py runserver  # http://localhost:8000
```

**Tesseract (Windows):** Install `https://github.com/UB-Mannheim/tesseract/wiki` → `tesseract-ocr-w64-setup-5.5.x.exe` → add `C:\Program Files\Tesseract-OCR` to PATH → verify `tesseract --version`. The code reads `TESSERACT_CMD` from `.env` and auto-inverts dark UI screenshots.

### Frontend setup

```powershell
cd D:\MyMusic\frontend
npm install
npm run dev      # http://localhost:5173 (proxies /api → :8000)
npm run build    # production
```

---

## Environment Variables

`backend/.env` (gitignored, never commit) — see `backend/.env.example`:

```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
AUDIUS_API_KEY=
AUDIUS_BEARER_TOKEN=           # for https://api.audius.co (optional, fallback to discoveryprovider)
AUDIUS_API_BASE=https://discoveryprovider.audius.co
AUDIUS_API_AUTH_BASE=https://api.audius.co
JAMENDO_CLIENT_ID=              # from developer.jamendo.com
REDIS_URL=                      # empty → LocMem (dev); redis://localhost:6379/0 when Redis 6+ running
MUSICBRAINZ_APP_NAME=MyMusicPlatform
MUSICBRAINZ_APP_VERSION=1.0.0
MUSICBRAINZ_CONTACT_EMAIL=your-email@example.com  # → UA: MyMusicPlatform/1.0.0 (your-email@example.com)
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

Generate secret: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

---

## Database Setup

- **Dev:** SQLite auto-created `backend/db.sqlite3` on `migrate` — indexes on `Song(provider, provider_song_id)`, `title`, `artist`, `Playlist(user)`, `PlaylistSong(playlist, position)`
- **Prod:** Set `DATABASE_URL` or use `docker-compose.yml` (PostgreSQL) — `python manage.py migrate` applies indexes via migrations

---

## API Documentation

Base `http://localhost:8000/api`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register/` | no | `{username,email,password,display_name}` → `{user, access, refresh}` |
| POST | `/auth/login/` | no | `{username,password}` → `{access, refresh}` |
| POST | `/auth/logout/` | yes | `{refresh}` → blacklist |
| GET | `/auth/me/` | yes | current user |
| PATCH | `/auth/profile/` | yes | multipart `display_name, avatar, email, username` |
| GET | `/music/search/?q=&page=1&limit=12&provider=audius&enriched=1` | no | normalized results, `X-Cache: HIT/MISS`, ranked, `playable` flag |
| GET | `/music/trending/?provider=audius&limit=12` | no | trending |
| GET | `/music/track/<provider>/<id>/` | no | single track |
| POST | `/music/resolve/` | yes | dedup `Song` |
| GET/POST | `/playlists/?mine=1` | optional | list/create |
| GET/PATCH/DELETE | `/playlists/<id>/` | owner/public | retrieve/update/delete |
| POST | `/playlists/<id>/songs/` | owner | `{provider, provider_song_id, title...}` |
| DELETE | `/playlists/<id>/songs/<song_id>/` | owner | remove |
| PATCH | `/playlists/<id>/reorder/` | owner | `{order:[song_id...]}` |
| POST | `/playlists/<id>/duplicate/` | owner/public | copy |
| POST | `/library/like/` | yes | like |
| DELETE | `/library/unlike/<id>/` | yes | unlike |
| GET | `/library/liked/` | yes | liked list |
| GET | `/library/recent/` | yes | recently played (capped 100) |
| POST | `/library/play/` | yes | record play |
| POST | `/screenshot/analyze/` | yes | multipart `image` → `{lines,candidates,matched}` |
| POST | `/screenshot/confirm/` | yes | `{name, songs:[track...]}` → playlist |

**Error shape:** `{detail: "Music provider temporarily unavailable", results:[]}` (never leaks keys)

---

## How to Run Dev Server

```powershell
# terminal 1 — backend
cd D:\MyMusic\backend; .\venv\Scripts\activate; .\venv\Scripts\python manage.py runserver
# terminal 2 — frontend
cd D:\MyMusic\frontend; npm run dev
# open http://localhost:5173
# test users: demo/Demo12345 , testshot/Test12345 , shreyas/Shreyas123 (reset via shell if needed)
```

---

## Screenshot Import Explained

1. **Validate** 5MB, JPEG/PNG/WebP (allows `image/jpg`, extension fallback)
2. **Preprocess** auto-invert dark UI (`mean<100`), resize to 2048, JPEG 92
3. **OCR** `PaddleOCR` (if installed) → `pytesseract` with `_enhance` (grayscale, upscale to 900px, autocontrast, 1.6 contrast, binarize) trying `psm 6,3,1`; `TESSERACT_CMD` from env, logs `Tesseract binary missing` with hint
4. **Extract** `song_extractor.py` handles ` - / by / | / • / ·` and YouTube Music 2-line `Title` + `Artist • Album`, strips `1.`, `4:28`, `rs`, filters chrome (`music.youtube.com`, `WE 2731 @ Buildm`, `Search songs…`, `Episodes for later`)
5. **Match** `song_matcher.py` → `MusicBrainz search_recordings` (1/s throttle, 30m cache) → `Audius` search `title+artist` → `matcher.py` (RapidFuzz `title*0.4 + artist*0.3 + combined*0.2 + duration*0.1`, penalize `remix/cover` -22) → `best` + `matches`; fallback `musicbrainz-only` (`provider:musicbrainz`, `playable:false`) or `detected-only` if no MB
6. **Confirm** UI shows `Detected: raw`, `Matched: title — artist`, `Confidence: 94%`, `source: musicbrainz+audius`, checkbox, `playable` badge; `Create Playlist` always creates (even metadata-only, player auto-fetches stream on play)

---

## Music Provider Configuration

- **Audius** (public, no key required for `discoveryprovider`; `AUDIUS_BEARER_TOKEN` for `api.audius.co` trending) — streams via `.../v1/tracks/<id>/stream`, `Session` pooling, `429` respect
- **Jamendo** — needs `JAMENDO_CLIENT_ID`, pass `?provider=jamendo`
- **MusicBrainz** — **no API key**, only `MUSICBRAINZ_USER_AGENT` from 3 env vars, `BASE_URL=https://musicbrainz.org/ws/2`, `fmt=json`, 1 req/s
- Add new provider: implement `BaseProvider` in `music/services/new.py` → register in `music_service._providers`

---

## Security Notes

- `backend/.env` gitignored (`.gitignore` has `backend/.env`, `db.sqlite3`, `media/`, `__pycache__/`, `venv/`); `.env.example` is template with empty secrets
- JWT blacklist on logout, `CORS_ALLOWED_ORIGINS`, `IsAuthenticated` + owner checks for playlists/profile
- `MultiPartParser` image validation (type/size), `Pillow` `verify`, `ImageOps` invert, ORM only (no raw SQL)
- Never expose `AUDIUS_API_KEY`, `MUSICBRAINZ_*` to React (only Django headers)

---

## Testing

```bash
cd D:\MyMusic\backend
.\venv\Scripts\python manage.py test music.tests_mb music.tests_search --verbosity=2  # 8 tests: unicode, remix penalty, cache, MB mock
.\venv\Scripts\python manage.py check
cd ..\frontend; npm run build; npm run lint
```

---

## Project Structure (required)

```
music-platform/
  backend/{manage.py,requirements.txt,.env.example,config/,accounts/,music/,playlists/,screenshot_import/,library/,media/}
  frontend/{package.json,vite.config.ts,index.html,src/{components/{layout,music,player,playlists,screenshot},pages,services,context,hooks,utils}}
  .gitignore  README.md  docker-compose.yml
```
