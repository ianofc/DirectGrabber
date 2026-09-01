# DirectGrabber 📸🎬

Aplicação full-stack moderna para extração, backup e download automático de fotos e vídeos MP4 de conversas diretas (**Instagram DMs**), combinando uma API assíncrona em **FastAPI + Playwright** com um painel interativo em **React + Tailwind CSS**.

---

## 🚀 Tecnologias

### Backend
- **FastAPI**: API assíncrona com documentação automática Swagger (`/api/v1/docs`).
- **Playwright**: Motor headless com interceptação de rede (GraphQL/CDN) e auto-scroll com rate limiting resiliente.
- **SQLAlchemy (Async)** + **aiosqlite**: Banco de dados SQLite assíncrono para persistência de tarefas e mídias.
- **httpx** + **aiofiles**: Downloader assíncrono de fotos e vídeos MP4 em alta resolução.

### Frontend
- **React 18** + **TypeScript** + **Vite**.
- **Tailwind CSS**: Interface moderna inspirada na estética do Instagram no modo escuro.
- **Lucide Icons**: Ícones modernos e consistentes.
- **Lightbox**: Visualizador integrado de fotos e reprodução de vídeos MP4.

---

## 📂 Estrutura do Projeto

```text
directgrabber/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/        # auth, tasks, media
│   │   ├── core/                    # config.py (Pydantic Settings)
│   │   ├── db/                      # database.py, models.py
│   │   ├── dao/                     # base.py, task_dao.py, media_dao.py
│   │   ├── schemas/                 # Pydantic models de request/response
│   │   ├── services/                # playwright_engine.py, media_downloader.py, session_manager.py
│   │   └── main.py                  # Instância FastAPI + CORS + Static Files
│   ├── assets/sessions/             # Armazenamento de session.json (ignorado no git)
│   ├── storage/downloads/           # Mídias salvas organizadas por ID da thread
│   ├── tests/                       # Testes automatizados com pytest
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/              # Button, Input, Modal, TaskMonitor, MediaGallery, Lightbox
│   │   ├── hooks/                   # useTask, useMedia
│   │   ├── pages/                   # Dashboard, SessionAuth, Gallery
│   │   ├── services/                # api.ts (Axios)
│   │   └── types/                   # Interfaces TypeScript
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🛠️ Como Executar Localmente

### 1. Pré-requisitos
- Python 3.11+
- Node.js 18+ e npm

### 2. Backend (FastAPI + Playwright)

```bash
# Entre na pasta do backend
cd backend

# Crie um ambiente virtual (recomendado)
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Instale os binários do Chromium para o Playwright
playwright install chromium

# Inicie o servidor FastAPI
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em: `http://localhost:8000`
Documentação interativa Swagger: `http://localhost:8000/api/v1/docs`

---

### 3. Frontend (React + Vite)

```bash
# Em outro terminal, acesse a pasta do frontend
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento Vite
npm run dev
```

O painel estará disponível em: `http://localhost:5173`

---

## 🐳 Executando com Docker Compose

```bash
docker-compose up --build
```

---

## 💡 Como Usar

1. Acesse o painel em `http://localhost:5173`.
2. Vá até a aba **Sessão / Login** e clique em **Abrir Navegador e Fazer Login**.
3. O Chromium abrirá na tela. Faça login na sua conta do Instagram. O sistema detectará o login e salvará o arquivo de cookies seguro em `backend/assets/sessions/session.json`.
4. Volte à aba **Extrator**, cole o link da conversa (ex: `https://www.instagram.com/direct/t/1234567890/`) e clique em **Extrair Mídias**.
5. Acompanhe a barra de progresso em tempo real.
6. Ao finalizar, clique em **Ver na Galeria** ou navegue até a aba **Galeria** para visualizar e baixar as fotos e vídeos MP4 extraídos!

---

## 🧪 Testes Automatizados

```bash
cd backend
pytest tests/
```
