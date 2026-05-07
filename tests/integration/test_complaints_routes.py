from __future__ import annotations

import pytest

from src.core.enums.complaints import ComplaintStatus

pytestmark = pytest.mark.integration


@pytest.mark.anyio
async def test_create_complaint_with_file_persists_and_returns_file(
    client, db_helpers, fake_s3
) -> None:
    user = await db_helpers.create_user(telegram_id=9401, username="complainer")
    await db_helpers.auth_as(client, user)

    response = await client.post(
        "/api/v1/complaints",
        data={"text": "Machine is broken"},
        files={"files": ("photo.png", b"binary-image", "image/png")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["text"] == "Machine is broken"
    assert len(body["files"]) == 1
    assert body["files"][0]["original_filename"] == "photo.png"

    assert any(key.endswith("/photo.png") for key in fake_s3.files.keys())


@pytest.mark.anyio
async def test_get_my_complaints_filters_by_status_and_search(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=9402, username="complainer")
    await db_helpers.create_complaint_row(
        user_id=user.id, text_value="Need washer repair", status_value=ComplaintStatus.SENT
    )
    await db_helpers.create_complaint_row(
        user_id=user.id, text_value="Dryer ok", status_value=ComplaintStatus.SOLVED
    )
    await db_helpers.auth_as(client, user)

    response = await client.get("/api/v1/complaints/me")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["text"] == "Dryer ok"


@pytest.mark.anyio
async def test_get_complaint_and_files_returns_download_urls(client, db_helpers) -> None:
    user = await db_helpers.create_user(telegram_id=9403, username="complainer")
    complaint = await db_helpers.create_complaint_row(
        user_id=user.id, text_value="Leak detected", status_value=ComplaintStatus.SENT
    )
    await db_helpers.create_complaint_file_row(
        complaint_id=complaint.id,
        object_key=f"complaints/{complaint.id}/evidence.png",
        filename="evidence.png",
    )
    await db_helpers.auth_as(client, user)

    get_response = await client.get(f"/api/v1/complaints/{complaint.id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == str(complaint.id)

    files_response = await client.get(f"/api/v1/complaints/{complaint.id}/files")
    assert files_response.status_code == 200
    assert files_response.json()[0]["original_filename"] == "evidence.png"
    assert files_response.json()[0]["download_url"].endswith("/evidence.png")


@pytest.mark.anyio
async def test_update_delete_and_admin_status_change_work(client, db_helpers) -> None:
    admin = await db_helpers.create_user(telegram_id=9404, username="admin", is_admin=True)
    user = await db_helpers.create_user(telegram_id=9405, username="owner")
    complaint = await db_helpers.create_complaint_row(
        user_id=user.id, text_value="Old text", status_value=ComplaintStatus.SENT
    )

    await db_helpers.auth_as(client, user)

    update_response = await client.patch(
        f"/api/v1/complaints/{complaint.id}", data={"text": "Updated complaint text"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["text"] == "Updated complaint text"
    assert update_response.json()["status"] == "Updated"

    await db_helpers.auth_as(client, admin)
    status_response = await client.patch(
        f"/api/v1/complaints/{complaint.id}/status", json={"status": "Solved"}
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "Solved"

    list_response = await client.get("/api/v1/complaints", params={"status": "Solved"})
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    delete_response = await client.delete(f"/api/v1/complaints/{complaint.id}")
    assert delete_response.status_code == 204
