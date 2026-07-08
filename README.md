# 🍽️ EchoEats – AI Voice Assistant Food Ordering Platform

EchoEats is a full-stack food ordering web application that combines a modern user interface with an AI-powered voice assistant. Users can browse food items, interact using voice commands, manage their cart, and place orders through an easy-to-use interface.

---

## ✨ Features

- 🎤 AI-powered Voice Assistant using Groq API
- 🍕 Browse food categories
- 🔍 Search food items
- 🛒 Add and remove items from cart
- 💳 Razorpay payment integration
- 📱 Responsive design
- ⚡ Fast React + Vite frontend
- 🐍 Django backend

## 🛠️ Tech Stack

### Frontend
- React.js
- Vite
- JavaScript
- CSS

### Backend
- Django
- Python

### APIs
- Groq API
- Razorpay

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/rachanakadlewad-oss/EchoEats-Voice-Assistant.git
```

### Backend Setup

```bash
cd Backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py runserver
```

---

### Frontend Setup

```bash
cd FrontEnd

npm install

npm run dev
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory.

```env
GROQ_API_KEY=your_groq_api_key

RAZORPAY_KEY_ID=your_key_id

RAZORPAY_KEY_SECRET=your_secret

