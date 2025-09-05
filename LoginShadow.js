import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

let loginTrend = new Trend('Tiempo_de_login');

// Configuración del test
export let options = {
  vus: 10,
  duration: '15s',
};

export default function () {
  const url = 'http://127.0.0.1:5001';
  const payload = JSON.stringify({
    username: 'admin',
    password: '1234'
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Realizar login
  let loginRes = http.post(url, payload, params);
  loginTrend.add(loginRes.timings.duration);

  check(loginRes, {
    'login exitoso': (res) => res.status === 200,
  });

  sleep(1);
}