# AIgift_work

## API Endpoints

- `GET /health` - Simple health check.
- `POST /recommend` - Provide `{"text": "...", "budget": 100}` and receive a list of up to five matching products.
- `POST /plan` - Same payload as `/recommend` but returns a PDF file summarizing the recommended products.
