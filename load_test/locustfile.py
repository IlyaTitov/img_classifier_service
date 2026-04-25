"""
Locust load test for Image Classifier Service.

Scenarios:
- UploadUser  (weight=3) – heavy user: registers, uploads photos, polls results
- ArchiveUser (weight=2) – reader: logs in, browses archive with filters / sorting
- StatusUser  (weight=1) – poller: re-checks statuses of already-uploaded images

Run locally against a running stack:
    locust -f locustfile.py --host http://localhost:8000

Run via Docker Compose (loadtest profile):
    docker compose --profile loadtest up locust
Then open http://localhost:8089
"""

from __future__ import annotations

import os
import random
import string
from datetime import date, timedelta

import gevent  # bundled with locust (gevent-based)
from locust import HttpUser, between, events, task
from locust.exception import StopUser

# ── Test image ──────────────────────────────────────────────────────────────
_HERE = os.path.dirname(__file__)
_IMAGE_PATH = os.path.join(_HERE, "test_image.png")

with open(_IMAGE_PATH, "rb") as _f:
    TEST_IMAGE_BYTES = _f.read()

TEST_IMAGE_NAME = "test_image.png"
TEST_IMAGE_MIME = "image/png"

# ── Shared state (uploaded image IDs accessible across users) ───────────────
_shared_image_ids: list[int] = []
_MAX_SHARED_IDS = 200


def _rand_suffix(n: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


# ── Base user ────────────────────────────────────────────────────────────────

class _BaseUser(HttpUser):
    abstract = True

    token: str | None = None
    username: str = ""
    password: str = "Locust#123"
    my_image_ids: list[int]

    def on_start(self) -> None:
        self.my_image_ids = []
        self.username = f"lt_{_rand_suffix()}"
        self._register_and_login()

    def _register_and_login(self) -> None:
        payload = {"login": self.username, "password": self.password}

        # Register (ignore 400 – user may already exist)
        with self.client.post(
            "/v1/auth/register",
            json=payload,
            catch_response=True,
            name="POST /v1/auth/register",
        ) as resp:
            if resp.status_code not in (201, 400):
                resp.failure(f"register: unexpected {resp.status_code}")
                raise StopUser()
            resp.success()

        # Login
        with self.client.post(
            "/v1/auth/login",
            json=payload,
            catch_response=True,
            name="POST /v1/auth/login",
        ) as resp:
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                resp.success()
            else:
                resp.failure(f"login: {resp.status_code} {resp.text[:100]}")
                raise StopUser()

    @property
    def _auth(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}


# ── Upload user (weight = 3) ─────────────────────────────────────────────────

class UploadUser(_BaseUser):
    """Simulates a user who actively uploads photos and waits for results."""

    weight = 3
    wait_time = between(1, 4)

    @task(5)
    def upload_photo(self) -> None:
        """Upload test_image.png and immediately start polling for results."""
        with self.client.post(
            "/v1/image/upload",
            files={"file": (TEST_IMAGE_NAME, TEST_IMAGE_BYTES, TEST_IMAGE_MIME)},
            headers=self._auth,
            catch_response=True,
            name="POST /v1/image/upload",
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"upload: {resp.status_code} {resp.text[:120]}")
                return
            resp.success()
            image_id: int = resp.json()["id"]

        # Register in local & shared pools
        self.my_image_ids.append(image_id)
        if len(self.my_image_ids) > 50:
            self.my_image_ids.pop(0)

        _shared_image_ids.append(image_id)
        if len(_shared_image_ids) > _MAX_SHARED_IDS:
            _shared_image_ids.pop(0)

        # Poll until processing_complete or timeout (non-blocking via gevent)
        gevent.spawn(self._poll_until_done, image_id)

    def _poll_until_done(
        self, image_id: int, max_polls: int = 40, interval: float = 1.5
    ) -> None:
        for _ in range(max_polls):
            gevent.sleep(interval)
            with self.client.get(
                f"/v1/image/{image_id}",
                headers=self._auth,
                catch_response=True,
                name="GET /v1/image/[id] (poll)",
            ) as resp:
                if resp.status_code == 200:
                    resp.success()
                    if resp.json().get("processing_complete"):
                        return
                elif resp.status_code == 404:
                    resp.success()  # already cleaned up – not a failure
                    return
                else:
                    resp.failure(f"poll: {resp.status_code}")
                    return

    @task(2)
    def view_archive(self) -> None:
        self.client.get(
            "/v1/image/",
            headers=self._auth,
            name="GET /v1/image/ (archive)",
        )

    @task(1)
    def view_archive_by_detections(self) -> None:
        self.client.get(
            "/v1/image/?sort_by=detection_count&order=desc",
            headers=self._auth,
            name="GET /v1/image/?sort_by=detection_count",
        )


# ── Archive user (weight = 2) ─────────────────────────────────────────────────

class ArchiveUser(_BaseUser):
    """Simulates a read-heavy user who browses the archive with filters."""

    weight = 2
    wait_time = between(2, 6)

    @task(4)
    def browse_archive_default(self) -> None:
        self.client.get(
            "/v1/image/?sort_by=created_at&order=desc",
            headers=self._auth,
            name="GET /v1/image/ (default)",
        )

    @task(3)
    def browse_archive_by_detections(self) -> None:
        self.client.get(
            "/v1/image/?sort_by=detection_count&order=desc",
            headers=self._auth,
            name="GET /v1/image/?sort_by=detection_count",
        )

    @task(2)
    def browse_archive_last_week(self) -> None:
        today = date.today().isoformat()
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        self.client.get(
            f"/v1/image/?date_from={week_ago}&date_to={today}",
            headers=self._auth,
            name="GET /v1/image/?date_from=…&date_to=…",
        )

    @task(2)
    def browse_archive_asc(self) -> None:
        self.client.get(
            "/v1/image/?sort_by=created_at&order=asc",
            headers=self._auth,
            name="GET /v1/image/?order=asc",
        )

    @task(1)
    def upload_one_photo(self) -> None:
        """Archive users occasionally upload a photo too."""
        with self.client.post(
            "/v1/image/upload",
            files={"file": (TEST_IMAGE_NAME, TEST_IMAGE_BYTES, TEST_IMAGE_MIME)},
            headers=self._auth,
            catch_response=True,
            name="POST /v1/image/upload (archive-user)",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
                _shared_image_ids.append(resp.json()["id"])
            else:
                resp.failure(f"{resp.status_code}")


# ── Status poller user (weight = 1) ──────────────────────────────────────────

class StatusUser(_BaseUser):
    """Simulates a user that repeatedly checks statuses of known images."""

    weight = 1
    wait_time = between(0.5, 2)

    @task(5)
    def check_random_image(self) -> None:
        if not _shared_image_ids:
            return
        image_id = random.choice(_shared_image_ids)
        with self.client.get(
            f"/v1/image/{image_id}",
            headers=self._auth,
            catch_response=True,
            name="GET /v1/image/[id] (status)",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"status: {resp.status_code}")

    @task(1)
    def check_archive(self) -> None:
        self.client.get(
            "/v1/image/",
            headers=self._auth,
            name="GET /v1/image/ (status-user)",
        )


# ── Custom stats event ────────────────────────────────────────────────────────

@events.test_stop.add_listener
def on_test_stop(environment, **_kwargs) -> None:
    print(f"\n[locust] Test finished. Shared image pool size: {len(_shared_image_ids)}")
