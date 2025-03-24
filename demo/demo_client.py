import grpc
import demo_pb2
import demo_pb2_grpc

def run_unary(stub):
    response = stub.UnaryCall(demo_pb2.Request(message="Hello Unary"))
    print("UnaryCall received:", response.message)

def run_server_streaming(stub):
    responses = stub.ServerStreamingCall(demo_pb2.Request(message="Hello Server Streaming"))
    for response in responses:
        print("ServerStreamingCall received:", response.message)

def run_client_streaming(stub):
    def request_generator():
        for msg in ["Hello", "Client", "Streaming"]:
            yield demo_pb2.Request(message=msg)
    response = stub.ClientStreamingCall(request_generator())
    print("ClientStreamingCall received:", response.message)

def run_bidi_streaming(stub):
    def request_generator():
        for msg in ["Hello", "Bidi", "Streaming"]:
            yield demo_pb2.Request(message=msg)
    responses = stub.BidiStreamingCall(request_generator())
    for response in responses:
        print("BidiStreamingCall received:", response.message)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = demo_pb2_grpc.DemoServiceStub(channel)
        run_unary(stub)
        run_server_streaming(stub)
        run_client_streaming(stub)
        run_bidi_streaming(stub)

if __name__ == '__main__':
    run()
