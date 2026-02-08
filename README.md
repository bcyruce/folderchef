# 🍳 FolderChef — AI-Powered Reverse Meal Planner

> **Save money on groceries by cooking with what's on sale.**

FolderChef is an AI-driven "Reverse Meal Planner" built for the Dutch market. Instead of
choosing recipes and then shopping, FolderChef flips the process: it starts with **weekly
supermarket discounts** (Albert Heijn & Jumbo) and uses AI to generate **optimized,
budget-friendly recipes** based on those deals.

---

## 🎯 Problem We Solve

- Food inflation makes groceries expensive
- People waste food because they buy ingredients they don't use
- Traditional meal planners ignore what's actually on sale

## 💡 How It Works

1. **Scrape** — We fetch the latest weekly discounts from Albert Heijn and Jumbo
2. **Clean** — AI processes and categorises the raw discount data
3. **Generate** — An AI Agent creates structured recipe JSONs using discounted items
4. **Serve** — Users browse personalised, low-cost meal plans on web (and soon mobile)

---

## 🏗️ Project Structure

```
folderchef/
├── backend/                  # Python FastAPI server
│   ├── app/
│   │   ├── main.py           # App entry point
│   │   ├── config.py         # Settings & env variables
│   │   ├── models/           # Pydantic data models
│   │   ├── routers/          # API endpoint definitions
│   │   ├── scrapers/         # Supermarket discount scrapers
│   │   ├── services/         # Business logic & AI integration
│   │   └── database/         # Database connection & queries
│   ├── tests/                # Backend tests
│   ├── requirements.txt      # Python dependencies
│   └── Procfile              # Railway deployment command
│
├── frontend/                 # Next.js React web app
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # Reusable UI components
│   │   ├── lib/              # Utility functions & API client
│   │   └── types/            # TypeScript type definitions
│   ├── public/               # Static assets
│   └── package.json          # Node.js dependencies
│
├── .gitignore                # Files Git should ignore
└── README.md                 # This file!
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **An OpenAI API Key** — [Get one](https://platform.openai.com/api-keys)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/folderchef.git
cd folderchef
```

### 2. Start the Backend

```bash
cd backend
python -m venv venv              # Create virtual environment
venv\Scripts\activate            # Activate it (Windows)
# source venv/bin/activate       # Activate it (Mac/Linux)
pip install -r requirements.txt  # Install dependencies
cp .env.example .env             # Create your env file
# Edit .env and add your API keys
uvicorn app.main:app --reload    # Start the server
```

The API will be live at **http://localhost:8000**
API docs at **http://localhost:8000/docs**

### 3. Start the Frontend

```bash
cd frontend
npm install                      # Install dependencies
cp .env.example .env.local       # Create your env file
npm run dev                      # Start the dev server
```

The web app will be live at **http://localhost:3000**

---

## 🚂 Deploying to Railway

This project is configured for [Railway](https://railway.app/) deployment.
Each folder (`backend/` and `frontend/`) can be deployed as a separate Railway service.

1. Create a new Railway project
2. Add a **PostgreSQL** database service
3. Add the **backend** service (point to `/backend` directory)
4. Add the **frontend** service (point to `/frontend` directory)
5. Set environment variables in Railway dashboard

See `backend/railway.toml` and `frontend/railway.toml` for deployment configs.

---

## 📱 Mobile (Coming Soon)

The backend API is designed to be **platform-agnostic** — the same API that powers
the web app will also power future iOS and Android apps.

---

## 🛠️ Tech Stack

| Layer      | Technology           | Why                                      |
|------------|----------------------|------------------------------------------|
| Backend    | Python + FastAPI     | Fast, modern, great for AI integration   |
| Frontend   | Next.js + React      | Best React framework, great DX           |
| Database   | PostgreSQL           | Reliable, Railway-native support         |
| AI         | OpenAI GPT           | Best-in-class text generation            |
| Styling    | Tailwind CSS         | Rapid UI development                     |
| Deployment | Railway              | Simple, affordable hosting               |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
