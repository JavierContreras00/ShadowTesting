import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'https://your-production-url.com'; // Replace with your production URL

export const options = {
    stages: [
        { duration: '5m', target: 100 }, // Ramp up to 100 users over 5 minutes
        { duration: '10m', target: 100 }, // Stay at 100 users for 10 minutes
        { duration: '5m', target: 0 },    // Ramp down to 0 users
    ],
};

export default function () {
    let response;

    // Test successful login
    response = http.post(`${BASE_URL}/login`, JSON.stringify({
        username: 'validUsername', // Replace with a valid username
        password: 'validPassword'   // Replace with a valid password
    }), { headers: { 'Content-Type': 'application/json' } });

    check(response, {
        'successful login status': (r) => r.status === 200,
        'login response received': (r) => r.json().token !== '',
    });

    sleep(1);

    // Test failed login
    response = http.post(`${BASE_URL}/login`, JSON.stringify({
        username: 'invalidUsername',
        password: 'invalidPassword'
    }), { headers: { 'Content-Type': 'application/json' } });

    check(response, {
        'failed login status': (r) => r.status === 401,
        'error message returned': (r) => r.json().error === 'Invalid credentials',
    });

    sleep(1);
}