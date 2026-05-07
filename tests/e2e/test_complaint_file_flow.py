from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


@pytest.mark.anyio
async def test_complaint_upload_and_get_files_flow(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=9801, username="complainer")
    await db_helpers.auth_as(client, user)

    create_response = await client.post(
        "/api/v1/complaints",
        data={"text": "Washer is leaking"},
        files={"files": ("evidence.png", b"png-bytes", "image/png")},
    )

    assert create_response.status_code == 201
    created = create_response.json()
    complaint_id = created["id"]
    assert created["text"] == "Washer is leaking"
    assert len(created["files"]) == 1

    complaint_response = await client.get(f"/api/v1/complaints/{complaint_id}")
    assert complaint_response.status_code == 200
    assert complaint_response.json()["id"] == complaint_id

    files_response = await client.get(f"/api/v1/complaints/{complaint_id}/files")
    assert files_response.status_code == 200
    files_payload = files_response.json()
    assert len(files_payload) == 1
    assert files_payload[0]["original_filename"] == "evidence.png"
