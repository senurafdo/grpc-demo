import unittest
import time
import grpc
from concurrent import futures

import hello_pb2
import hello_pb2_grpc
from server import HelloServiceServicer  # or import your servicer appropriately

# If your generated file doesn't have the helper, you can define it here:
def add_HelloServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'SayHello': grpc.unary_unary_rpc_method_handler(
            servicer.SayHello,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
        'LotsOfReplies': grpc.unary_stream_rpc_method_handler(
            servicer.LotsOfReplies,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
        'LotsOfGreetings': grpc.stream_unary_rpc_method_handler(
            servicer.LotsOfGreetings,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
        'BidiHello': grpc.stream_stream_rpc_method_handler(
            servicer.BidiHello,
            request_deserializer=hello_pb2.HelloRequest.FromString,
            response_serializer=hello_pb2.HelloResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'hello.HelloService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


class E2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create and start an in-process gRPC server on a test port.
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_HelloServiceServicer_to_server(HelloServiceServicer(), cls.server)
        cls.port = 50052  # Use a test port different from your production server.
        cls.server.add_insecure_port(f'[::]:{cls.port}')
        cls.server.start()
        # Give the server a moment to start up.
        time.sleep(1)
        cls.channel = grpc.insecure_channel(f'localhost:{cls.port}')
        cls.stub = hello_pb2_grpc.HelloServiceStub(cls.channel)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop(0)

    def test_SayHello(self):
        # Test the unary RPC.
        response = self.stub.SayHello(hello_pb2.HelloRequest(greeting="E2E"))
        self.assertEqual(response.reply, "Hello, E2E")

    def test_LotsOfReplies(self):
        # Test the server streaming RPC.
        responses = list(self.stub.LotsOfReplies(hello_pb2.HelloRequest(greeting="Stream")))
        self.assertEqual(len(responses), 5)
        self.assertTrue(all(response.reply.startswith("Response") for response in responses))

    def test_LotsOfGreetings(self):
        # Test the client streaming RPC.
        def request_generator():
            for greeting in ["Alice", "Bob", "Charlie"]:
                yield hello_pb2.HelloRequest(greeting=greeting)
        response = self.stub.LotsOfGreetings(request_generator())
        self.assertEqual(response.reply, "Hello, Alice, Bob, Charlie")

    def test_BidiHello(self):
        # Test the bidirectional streaming RPC.
        def request_generator():
            for greeting in ["X", "Y", "Z"]:
                yield hello_pb2.HelloRequest(greeting=greeting)
        responses = list(self.stub.BidiHello(request_generator()))
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0].reply, "Hello, X")

if __name__ == '__main__':
    unittest.main()
