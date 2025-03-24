import grpc

import hello_pb2
import hello_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = hello_pb2_grpc.HelloServiceStub(channel)

    # Unary RPC call.
    unary_response = stub.SayHello(hello_pb2.HelloRequest(greeting="World"))
    print("SayHello response:", unary_response.reply)

    # Server streaming RPC call.
    print("\nLotsOfReplies responses:")
    for response in stub.LotsOfReplies(hello_pb2.HelloRequest(greeting="World")):
        print(response.reply)

    # Client streaming RPC call.
    def generate_greetings():
        for name in ["Alice", "Bob", "Charlie"]:
            yield hello_pb2.HelloRequest(greeting=name)

    client_stream_response = stub.LotsOfGreetings(generate_greetings())
    print("\nLotsOfGreetings response:", client_stream_response.reply)

    # Bidirectional streaming RPC call.
    def bidi_greetings():
        for name in ["Dave", "Eve", "Frank"]:
            yield hello_pb2.HelloRequest(greeting=name)

    print("\nBidiHello responses:")
    for response in stub.BidiHello(bidi_greetings()):
        print(response.reply)

if __name__ == '__main__':
    run()
