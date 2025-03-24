import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';

// Download quickpizza.proto for grpc-quickpizza.grafana.com, located at:
// https://raw.githubusercontent.com/grafana/quickpizza/refs/heads/main/proto/quickpizza.proto
// and put it in the same folder as this script.
const client = new grpc.Client();
client.load(null, 'quickpizza.proto');

export default () => {
  client.connect('grpc-quickpizza.grafana.com:443', {
    // plaintext: false
  });

  const data = { ingredients: ['Cheese'], dough: 'Thick' };
  const response = client.invoke('quickpizza.GRPC/RatePizza', data);

  check(response, {
    'status is OK': (r) => r && r.status === grpc.StatusOK,
  });

  console.log(JSON.stringify(response.message));

  client.close();
  sleep(1);
};