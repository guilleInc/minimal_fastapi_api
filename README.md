# Pets API

Simple CRUD API for pets using FastAPI.

## Production Docker image on EC2

The image runs the API on port `8000`. The SQLite database and uploaded images are kept on the EC2 host so they survive container replacement.

### Build the image

```bash
docker build -t pets-api:latest .
```

### Prepare persistent directories

```bash
sudo mkdir -p /srv/minimal-pets-api/db /srv/minimal-pets-api/uploads
```

The container uses these directories for the SQLite database and uploaded images.

### Configure secrets

Create an environment file outside the repository, for example `/etc/minimal-pets-api.env`:

```dotenv
ENVIRONMENT=production
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
```

Do not commit this file or bake it into the image.

### Run the container

```bash
docker run -d \
  --name pets-api \
  --restart unless-stopped \
  --publish 127.0.0.1:8000:8000 \
  --env-file /etc/minimal-pets-api.env \
  --volume /srv/minimal-pets-api/db:/data \
  --volume /srv/minimal-pets-api/uploads:/uploads \
  pets-api:latest
```

The API is available locally on the EC2 host at `http://127.0.0.1:8000`. Keep it bound to localhost when a reverse proxy such as Nginx or Caddy handles HTTPS. To expose it directly, change the publish option to `--publish 8000:8000` and configure the EC2 security group accordingly.

### Create the first user

After the container starts, create an application user interactively:

```bash
docker exec -it pets-api python -m scripts.create_user
```

The database uses SQLite, so run a single application container. Use a server database such as PostgreSQL before scaling to multiple replicas. Back up `/srv/minimal-pets-api/db` and `/srv/minimal-pets-api/uploads` or the underlying EBS volume.
