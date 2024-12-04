from fastapi import FastAPI, HTTPException, Response, UploadFile, File
import grpc
import os
import sys
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'protos')))
import file_pb2
import file_pb2_grpc
import uvicorn

app = FastAPI()

# Define the maximum message size (1GB)
MAX_MESSAGE_LENGTH = 1 * 1024 * 1024 * 1024

# gRPC client setup with increased message size limits
channel = grpc.insecure_channel(
    'grpc-server:50051',
    options=[
        ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
    ]
)
client = file_pb2_grpc.FileServiceStub(channel)

@app.post("/document_store")
async def document_store(files: List[UploadFile] = File(...)):
    try:
        messages = []
        for file in files:
            file_content = await file.read()
            response = client.UploadFile(
                file_pb2.UploadFileRequest(file_name=file.filename, file_content=file_content)
            )
            messages.append(response.message)
        return {"messages": messages}
    except grpc.RpcError as e:
        error_details = e.details() or "Unknown error"
        raise HTTPException(status_code=500, detail=f"gRPC Error: {error_details}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)}")

@app.get("/files")
def list_files():
    try:
        # Correct path within the Docker container
        data_dir = '/app/data'
        print(f"Data directory: {data_dir}")  # Log data directory path

        # Check if the data directory exists
        if not os.path.exists(data_dir):
            print("Data directory does not exist")  # More descriptive logging
            raise HTTPException(status_code=500, detail="Data directory does not exist")

        # Check permissions
        if not os.access(data_dir, os.R_OK):
            print("Data directory is not readable")
            raise HTTPException(status_code=500, detail="Data directory is not readable")

        # List files in the data directory of gRPC server
        files = os.listdir(data_dir)
        print(f"Files: {files}")  # Log files list

        if not files:
            print("No files found in the data directory")
            raise HTTPException(status_code=404, detail="No files found in the data directory")

        return {"files": files}
    except Exception as e:
        print(f"Exception: {e}")  # Log the exception with more detail
        raise HTTPException(status_code=500, detail=f"Exception: {e}")

@app.get("/document_store_download/{file_name}")
def document_store_download(file_name: str):
    try:
        response = client.GetFile(file_pb2.GetFileRequest(file_name=file_name))
        if not response.file_content:
            raise HTTPException(status_code=404, detail="File not found")
        return Response(
            content=response.file_content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except grpc.RpcError as e:
        error_details = e.details() or "Unknown error"
        raise HTTPException(status_code=500, detail=f"gRPC Error: {error_details}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)}")

if __name__ == '__main__':
    if not os.path.exists('downloaded_files'):
        os.makedirs('downloaded_files')
    uvicorn.run(app, host="0.0.0.0", port=8101)
