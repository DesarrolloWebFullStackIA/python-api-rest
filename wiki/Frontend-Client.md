# Frontend Web Client Architecture

This document describes the structure, styling conventions, state management, and Axios consumption of the **VaporStore** client application.

---

## Technical Stack & Philosophy

The web client is built according to standard Web Platform standards without unnecessary heavy frontend frameworks:
- **HTML5**: Semantic tags (`<header>`, `<main>`, `<section>`, `<article>`, `<dialog>`).
- **CSS3**: Custom properties (`:root`), mobile-first responsive layout (Flexbox and Grid), glassmorphism, accessible dark gaming palette.
- **JavaScript**: Modular Vanilla ES6+ (`import`/`export`), asynchronous `async`/`await`, debounced input controllers.
- **HTTP Client**: **Axios** (via CDN) with response error interceptors and baseURL auto-discovery.

---

## File Organization (`frontend/`)

```text
frontend/
├── index.html         # Single-page interface & interactive API explorer
├── css/
│   └── styles.css     # Dark gaming theme, custom variables, responsive grid
└── js/
    ├── api.js         # Modular Axios instance, interceptors & typed services
    └── app.js         # State machine, DOM controllers, modal handlers, debounce
```

---

## Architecture of `frontend/js/api.js`

### 1. Base URL Auto-Discovery
Automatically determines the API URL based on runtime context:
```javascript
const getBaseApiUrl = () => {
  // If served directly through FastAPI static mounting (/client/)
  if (window.location.pathname.startsWith('/client')) {
    return '/api/v1';
  }
  // Fallback for standalone dev server
  return 'http://127.0.0.1:8000/api/v1';
};
```

### 2. Error Response Interceptor
Normalizes both standard FastAPI string errors (`{"detail": "Not found"}`) and Pydantic validation error lists into readable user messages:
```javascript
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let formattedMessage = 'An unexpected server error occurred.';
    if (error.response && error.response.data && error.response.data.detail) {
      const detail = error.response.data.detail;
      formattedMessage = typeof detail === 'string'
        ? detail
        : detail.map((err) => `${err.loc.join('.')}: ${err.msg}`).join(' | ');
    }
    error.userMessage = formattedMessage;
    return Promise.reject(error);
  }
);
```

### 3. Service Modules
- `categoriesApi`: `getAll()`, `getById(id)`, `create(data)`, `update(id, data)`, `delete(id)`.
- `gamesApi`: `getAll(params)`, `getById(id)`, `create(data)`, `update(id, data)`, `delete(id)`.
- `healthApi`: `check()`, `getRoot()`.
- `steamApi`: `search(query, limit)`, `importGame(appId)`, `getStats(gameId)`.

---

## State Management & DOM Controllers (`frontend/js/app.js`)

### 1. State Machine
```javascript
const state = {
  page: 1,
  pageSize: 6,
  total: 0,
  totalPages: 1,
  search: '',
  categoryId: '',
  minRating: '',
  maxPrice: '',
  categories: [],
  editingGameId: null,
  pendingDeleteAction: null
};
```

### 2. Debounced Search (350ms)
Prevents excessive network traffic while typing in the catalog search bar:
```javascript
const debouncedSearch = debounce((query) => {
  state.search = query;
  state.page = 1;
  fetchGames();
}, 350);
```

### 3. Accessible Native `<dialog>` Modals
All modal dialogs (`gameModal`, `categoryModal`, `confirmModal`, `steamModal`) utilize the HTML5 `<dialog closedby="any">` standard:
- Backdrop blur via `dialog::backdrop { backdrop-filter: blur(8px); }`.
- Automatic platform dismissal (`Esc` key handling).
- Light-dismiss fallback polyfill for older browsers.
- Focus trapping and accessible labeling (`aria-labelledby`).

---

## Interactive API Explorer Tab

The client features an embedded **Interactive API Documentation Portal**:
- Each endpoint card documents its HTTP method badge (GET, POST, PUT, DELETE), URL path, description, parameters, and sample JSON payloads.
- Includes a **"▶ Test in Browser"** button that executes live Axios calls against the running backend and displays formatted JSON responses with latency metrics.
