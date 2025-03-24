How to Run

1. Generate gRPC Python files:
Run the following command in the directory containing demo.proto:
`` python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. demo.proto
``

2. Start the Server:
Run the server in one terminal:
``python demo_server.py
 ``

3. Run the Client:
In another terminal, run:
``python demo_client.py
``

4. Run Automated Tests:
To run the tests, execute:
``python test_demo.py
``
5. grpcbin: gRPC Request & Response Service
``https://grpcbin.test.k6.io/``

