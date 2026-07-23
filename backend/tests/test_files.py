import io
import json
from tests.test_incidents import _setup_users, _get_token

def test_file_upload_and_download(client, db, session):
    citizen, staff, officer = _setup_users(db)
    citizen_token = _get_token(client, "citizendev@test.com")
    
    headers = {"Authorization": f"Bearer {citizen_token}"}
    
    # Simulate a file payload
    file_data = {
        "file": (io.BytesIO(b"fake image data here"), "photo.jpg")
    }
    
    # 1. Upload File
    res = client.post(
        "/api/v1/files/upload",
        data=file_data,
        headers=headers,
        content_type="multipart/form-data"
    )
    
    assert res.status_code == 201
    res_data = json.loads(res.data)
    assert res_data["success"] is True
    stored_name = res_data["data"]["stored_name"]
    
    # 2. Download File
    download_res = client.get(
        f"/api/v1/files/download/{stored_name}",
        headers=headers
    )
    assert download_res.status_code == 200
    assert download_res.data == b"fake image data here"
