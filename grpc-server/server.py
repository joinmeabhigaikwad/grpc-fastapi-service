import grpc
from concurrent import futures
import os

# Add the protos directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'protos')))

import file_pb2
import file_pb2_grpc

class FileServiceServicer(file_pb2_grpc.FileServiceServicer):
    def UploadFile(self, request, context):
        file_path = os.path.join('data', request.file_name)
        with open(file_path, 'wb') as f:
            f.write(request.file_content)
        return file_pb2.UploadFileResponse(message=f'File {request.file_name} uploaded successfully')

    def GetFile(self, request, context):
        file_path = os.path.join('data', request.file_name)
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_pb2.GetFileResponse(file_content=file_content)

def serve():
    # Increase max message size to 1GB (adjust as needed)
    options = [
        ('grpc.max_send_message_length', 1 * 1024 * 1024 * 1024),  # 1GB max send size
        ('grpc.max_receive_message_length', 1 * 1024 * 1024 * 1024),  # 1GB max receive size
    ]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    file_pb2_grpc.add_FileServiceServicer_to_server(FileServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started, listening on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    serve()
