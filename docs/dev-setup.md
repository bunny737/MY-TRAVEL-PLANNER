# Local Dev Setup

## 1. Ports (non-default on purpose)
The PG-MANAGEMENT-WEB project already owns 3000, 5433, 6379 and 8000 on this machine.

| Service | Host port | Container port | URL / connection |
|---------|-----------|----------------|------------------|
| web (Django) | **8100** | 8000 | http://localhost:8100 |
| db (Postgres 16) | **5440** | 5432 | `localhost:5440`, db `travel_platform` |

Override with `WEB_HOST_PORT` / `DB_HOST_PORT` in `.env`. Compose project name is `tours-and-travels`, so its
containers and `pgdata` volume are separate from the other project. There is no Redis or Celery here.

## 2. First run
```bash
cp .env.example .env            # then set SECRET_KEY (any long random string)
docker compose up -d db
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
docker compose up -d web
```
Create the starting content (Araku Valley, Lambasingi and Vizag destinations, and a DRAFT package page for each; nothing is published until you do it in admin):
```bash
docker compose run --rm web python manage.py seed_launch_content
```
Then the rest of the launch set: 34 more DRAFT pages (packages, cabs, stays, guides, blog articles) and the Vanjangi and Maredumilli
destinations. Safe to run twice; it never publishes, never sets a price and never overwrites a page:
```bash
docker compose run --rm web python manage.py seed_site_content
```
To show a price on a package, cab or stay page, enter it in that page's "Price (from a dated partner quote)" section in admin, from a quote the
partner gave you; it hides itself after `PRICE_MAX_AGE_DAYS` (90) days. The nine launch package prices from the partner can be filled in one go
(create the Partner row in admin first; it never overwrites a price that is already set):
```bash
docker compose run --rm web python manage.py set_partner_prices --partner "Partner business name"
```
It fills 16 pages (packages and the four hotel pages) with their "from" amount and option lists. After a change to `apps/core/seed/prices.py`, add
`--refresh` to rewrite the pages that this same partner priced (a price you entered yourself under another partner is never touched).
Everyday commands: `docker compose logs -f web`, `docker compose exec web python manage.py shell`,
`docker compose run --rm web python manage.py test`.

## 3. DBeaver / psql
```
Host: localhost   Port: 5440   Database: travel_platform
```
| User | Password | Use for |
|------|----------|---------|
| `app_user` | `app_password` | Same non-superuser the app uses |
| `postgres` | `POSTGRES_ADMIN_PASSWORD` from `.env` | Admin tasks |

The `lead` table contains real people's phone numbers once live — do not export or screenshot it casually.

## 4. ERD
`django-extensions` + `pydot` are in `requirements/dev.txt` (graphviz is in the Dockerfile). After any model change:
```bash
docker compose exec web python manage.py graph_models -a -o erd.png
mv backend/erd.png docs/erd.png
```
Commit `docs/erd.png` with the model change (CLAUDE.md workflow step 5).

## 5. Testing tracking locally
Tag IDs are blank in `.env.example`, so pages render with no Google tags. To test conversions use a real
GA4 / Ads ID on a staging host only, never in unit tests (CLAUDE.md invariant 4).

## 6. Adding a photo
Only photos you may legally reuse: CC0, CC BY or CC BY-SA (check the licence on the photo's own page), your own, or a partner's with written consent.
Never NC/ND, never a photo with an identifiable person, never hot-link another site's image.
```bash
# 1. put the original somewhere outside the project, then (Pillow is a dev-only requirement)
docker compose run --rm -v "/path/to/originals:/raw:ro" web \
  python scripts/optimize_photo.py /raw/my-photo.jpg my-key --crop 0,0.2,1,0.8     # --crop is optional (fractions)
# 2. open static/img/photos/my-key-800.webp and -1600.webp and look at them
# 3. add an entry for my-key to PHOTOS in backend/apps/core/images.py (alt text, author, licence, source URL, sizes)
# 4. docker compose run --rm web python manage.py test apps.core.test_photos
```
The optimiser drops EXIF/GPS, never upscales, and writes only the widths the source can support. The admin dropdown and `/photo-credits/` pick the photo up automatically.

## 7. Admin MFA, the production image and backups (Module 07)
- Locally the admin accepts the password alone. To try the authenticator step set `ADMIN_REQUIRE_MFA=True` in `.env`,
  `docker compose up -d --force-recreate web`, sign in at `/admin/`, scan the QR code. Lost your phone: `docker compose run --rm web python manage.py reset_admin_mfa <username>`.
- Production image (same one Cloud Run runs): `docker build -f backend/Dockerfile.prod -t travel-web-prod backend`. It needs env vars (see
  `deploy/cloudrun/env.prod.yaml.example`) and refuses to start without them.
- Backups: `deploy/backup/restore_check.sh <file.dump.gpg>` tests a backup against the local database (never prints personal data);
  `deploy/backup/download_backup.sh` makes one from production. Details: docs/deployment.md §6.
- `docker-compose.yml` mounts `deploy/` read-only at `/deploy` so the tests can check those files.

## 8. Opening the dev server from a phone
Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `.env` to include your LAN IP or tunnel host, e.g.
`ALLOWED_HOSTS=localhost,127.0.0.1,web,192.168.1.4` and `CSRF_TRUSTED_ORIGINS=http://192.168.1.4:8100`, then
`docker compose up -d web`. Check the form and the WhatsApp link on a real phone before launch.
