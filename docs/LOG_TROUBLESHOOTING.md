# Log Troubleshooting

The application writes request and operation traces under `logs/`.

## What To Look For

- Time of user error.
- API path and HTTP status.
- `x-request-id` response header.
- Module name, exception message and traceback.
- Database or Redis connection errors.

## Example Flow

1. Ask the user for operation time and screen/API error.
2. Reproduce the same operation.
3. Capture `x-request-id`.
4. Search application logs.
5. Check related operation_logs rows.
6. Confirm whether it is data, configuration, network or code.
7. Fix and verify through API.

```bash
tail -f logs/app.log
grep "request_id=<id>" logs/app.log
```

```sql
SELECT * FROM operation_logs WHERE request_id = '<id>';
```
