import grpc
from concurrent import futures
import time

import demo_pb2
import demo_pb2_grpc

class DemoServiceServicer(demo_pb2_grpc.DemoServiceServicer):
    def UnaryCall(self, request, context):
        # Unary: one request, one response
        return demo_pb2.Response(message=f"Unary response to: {request.message}")

    def ServerStreamingCall(self, request, context):
        # Server streaming: one request, multiple responses
        for i in range(5):
            yield demo_pb2.Response(message=f"Stream {i} response to: {request.message}")
            time.sleep(0.5)  # simulate delay

    def ClientStreamingCall(self, request_iterator, context):
        # Client streaming: multiple requests, one response
        messages = []
        for req in request_iterator:
            messages.append(req.message)
        return demo_pb2.Response(message=" ".join(messages))

    def BidiStreamingCall(self, request_iterator, context):
        # Bidirectional streaming: multiple requests, multiple responses
        for req in request_iterator:
            yield demo_pb2.Response(message=f"Bidi response to: {req.message}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    demo_pb2_grpc.add_DemoServiceServicer_to_server(DemoServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
