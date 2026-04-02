# CV_GRAM Frontend

This folder contains the Vue frontend for CV_GRAM.

For the full project documentation, including backend setup, single-port deployment, email-link behavior, and search seed data, use the repo-level README:

- [README.md](/C:/Users/Calin/PycharmProjects/CVgram/README.md)

## Frontend Commands

```powershell
npm install
npm run dev
npm run build
```

## API Base

During local Vite development, the frontend defaults to the backend on `http://localhost:8000`.

In bundled production mode, it uses `window.location.origin`, so the frontend and backend can be served from the same port.
