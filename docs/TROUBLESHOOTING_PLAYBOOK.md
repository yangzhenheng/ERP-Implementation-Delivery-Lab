# Troubleshooting Playbook

Use this flow for every demo incident:

User feedback -> reproduce -> check service -> check network -> check port -> check logs -> check database -> determine root cause -> fix -> verify -> record.

## Basic Commands

```bash
docker compose ps
docker compose logs app
docker compose logs mysql
docker compose logs nginx
ss -lntp
curl http://localhost/health
tail -f logs/app.log
mysql -h 127.0.0.1 -P 3306 -u erp_user -p erp_demo
```

## Safety Rules

- Only run cases in the local demo environment.
- Do not test on a real customer system.
- Keep every failure recoverable.
- Record what was changed and how it was restored.
