// Fetch products from the backend
async function loadProducts() {
    const response = await fetch('http://localhost:5000/api/products');
    const products = await response.json();
    const productList = document.getElementById('product-list');
    products.forEach(product => {
        const productDiv = document.createElement('div');
        productDiv.className = 'product';
        productDiv.innerHTML = `
            <h3>${product.name}</h3>
            <p>${product.description}</p>
            <p>Price: $${product.price.toFixed(2)}</p>
            <button onclick="addToCart('${product.name}', ${product.price})">Add to Cart</button>
        `;
        productList.appendChild(productDiv);
    });
}

const stripe = Stripe('your_public_key_here'); // Replace with your actual Stripe public key

// Call loadProducts on shop.html
document.getElementById('payment-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const cardElement = document.getElementById('card-element');
    const { paymentMethod, error } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
    });

    if (error) {
        // Show error to your customer (e.g., insufficient funds)
        document.getElementById('payment-result').innerText = error.message;
    } else {
        // Send paymentMethod.id to your server (e.g., to create a payment)
        const response = await fetch('http://localhost:5000/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                payment_method_id: paymentMethod.id,
                amount: 5000, // Example amount in cents
            }),
        });

        const paymentResult = await response.json();
        if (paymentResult.error) {
            document.getElementById('payment-result').innerText = paymentResult.error;
        } else {
            document.getElementById('payment-result').innerText = 'Payment successful!';
            // Optionally, create an order in the database here
        }
    }
});
if (document.getElementById('product-list')) {
    loadProducts ();
}

// Update registerUser  and signInUser  functions to call the backend
async function registerUser (event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
    });

    if (response.ok) {
        alert("User  registered successfully!");
    } else {
        alert("Registration failed.");
    }
}

async function signInUser (event) {
    event.preventDefault();
    const email = document.getElementById('signinEmail').value;
    const password = document.getElementById('signinPassword').value;

    const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
        alert("User  logged in successfully!");
    } else {
        alert("Invalid credentials.");
    }
}

function addToCart(productName, productPrice) {
    // Logic to add the product to the cart
    alert(`${productName} added to cart at $${productPrice.toFixed(2)}`);
}