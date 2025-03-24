from concurrent import futures
import time
import grpc

import hello_pb2
import hello_pb2_grpc

class HelloServiceServicer(hello_pb2_grpc.HelloServiceServicer):
    def SayHello(self, request, context):
        # Unary RPC: single request and single response.
        reply_message = f"Hello, {request.greeting}"
        return hello_pb2.HelloResponse(reply=reply_message)

    def LotsOfReplies(self, request, context):
        # Server streaming RPC: one request, multiple responses.
        for i in range(5):
            reply_message = f"Response {i+1}: Hello, {request.greeting}"
            yield hello_pb2.HelloResponse(reply=reply_message)
            time.sleep(1)  # simulate delay

    def LotsOfGreetings(self, request_iterator, context):
        # Client streaming RPC: multiple requests, one response.
        greetings = []
        for request in request_iterator:
            greetings.append(request.greeting)
        reply_message = "Hello, " + ", ".join(greetings)
        return hello_pb2.HelloResponse(reply=reply_message)

    def BidiHello(self, request_iterator, context):
        # Bidirectional streaming RPC: streaming requests and responses.
        for request in request_iterator:
            reply_message = f"Hello, {request.greeting}"
            yield hello_pb2.HelloResponse(reply=reply_message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_HelloServiceServicer_to_server(HelloServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051...")
    try:
        while True:
            time.sleep(86400)  # keep server alive for one day
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
