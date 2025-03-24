import grpc
import unittest
import threading
import time

import demo_pb2
import demo_pb2_grpc
from demo_server import serve  # Import the serve() function

class GRPCTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the gRPC server in a background thread
        cls.server_thread = threading.Thread(target=serve, daemon=True)
        cls.server_thread.start()
        # Give the server a moment to start
        time.sleep(1)
        cls.channel = grpc.insecure_channel('localhost:50051')
        cls.stub = demo_pb2_grpc.DemoServiceStub(cls.channel)

    @classmethod
    def tearDownClass(cls):
        cls.channel.close()

    def test_unary_call(self):
        response = self.stub.UnaryCall(demo_pb2.Request(message="Test Unary"))
        self.assertIn("Test Unary", response.message)

    def test_server_streaming_call(self):
        responses = list(self.stub.ServerStreamingCall(demo_pb2.Request(message="Test Server Streaming")))
        self.assertEqual(len(responses), 5)
        for response in responses:
            self.assertIn("Test Server Streaming", response.message)

    def test_client_streaming_call(self):
        def request_generator():
            for msg in ["Test", "Client", "Streaming"]:
                yield demo_pb2.Request(message=msg)
        response = self.stub.ClientStreamingCall(request_generator())
        self.assertIn("Test", response.message)
        self.assertIn("Client", response.message)
        self.assertIn("Streaming", response.message)

    def test_bidi_streaming_call(self):
        messages = ["Test", "Bidi", "Streaming"]
        def request_generator():
            for msg in messages:
                yield demo_pb2.Request(message=msg)
        responses = list(self.stub.BidiStreamingCall(request_generator()))
        self.assertEqual(len(responses), len(messages))
        for msg, response in zip(messages, responses):
            self.assertIn(msg, response.message)

if __name__ == '__main__':
    unittest.main()
