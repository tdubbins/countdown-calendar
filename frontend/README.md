# Frontend

Ionic Vue PWA.

## Setup

```bash
npm install
cp .env.example .env.development
```

## Run

```bash
npm run dev
# http://localhost:8080
```

## Build

```bash
npm run build
# Output in dist/
```

## Test

```bash
npm run test:unit
npm run lint
```

## Structure

```
src/
├── views/        # Pages
├── components/   # Reusable UI
├── composables/  # Vue composition functions
├── router/       # Routes
├── theme/        # CSS themes
└── utils/        # Helpers
```
