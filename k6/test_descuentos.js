import { check } from "k6";
import http from "k6/http";

export default function () {
    const url = 'https://api.example.com/discounts';
    const payload = JSON.stringify({
        product_id: 123,
        quantity: 2
    });

    const params = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    let response = http.post(url, payload, params);

    check(response, {
        'discount applied': (res) => res.json().discount > 0,
        'response status was 200': (res) => res.status === 200
    });
}