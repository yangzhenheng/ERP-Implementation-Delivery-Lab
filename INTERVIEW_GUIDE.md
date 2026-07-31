# Interview Guide

## 30 Seconds

This is my independently built Manufacturing ERP Implementation Delivery Lab. It is not a real customer project. I use it to demonstrate the complete implementation chain: requirements, environment check, deployment, MySQL, data migration, API testing, troubleshooting, training and go-live acceptance.

## 60 Seconds

The system is a FastAPI ERP demo with customers, products, inventory, sales orders, implementation tasks and issue tracking. In dev mode it runs on SQLite for quick interview demonstration. In demo mode it can run with Docker Compose, MySQL 8, Redis and Nginx. The key flow is sales order creation, inventory validation, inventory deduction and transaction recording. If stock is insufficient, the system creates an issue. I also prepared SQL scripts, CSV import, backup/restore, Linux checks and troubleshooting cases.

## 3 Minutes

I built this project to practice real ERP implementation delivery work without pretending to have a commercial customer case. The business background is a manufacturing company moving from Excel/manual registration to ERP-style master data and order inventory control. The code demonstrates API, database and data validation. The deployment files demonstrate how I would check Linux, start services, configure Nginx, use Redis as optional middleware, verify MySQL and prepare backup/restore. The docs demonstrate implementation planning, migration, training, go-live and acceptance. The current local automated test result is 9 passed.

## Key Honest Answer

Q: Do you have real ERP implementation engineer work experience?

A: I do not claim formal commercial ERP implementation engineer experience. This is an independently built implementation lab. I built and ran the MySQL/deployment/data migration/API/logging/troubleshooting chain to show that I understand the work process and can operate the basic tools honestly.

## Interview Questions And Practical Answers

1. Why did you build this project?  
To practice the whole implementation delivery workflow instead of only writing code.

2. What does an ERP implementation engineer do?  
Requirements, installation, configuration, data migration, testing, training, troubleshooting, go-live and acceptance.

3. How do you do requirements research?  
Interview roles, record current process, confirm master data, confirm reports, identify gaps and get written confirmation.

4. How do you check Linux CPU?  
Use `top`, `lscpu` or `nproc`.

5. How do you check memory?  
Use `free -h` and `top`.

6. How do you check disk?  
Use `df -h` and check log/data directories.

7. How do you check processes?  
Use `ps aux | grep <name>` or `systemctl status`.

8. How do you check ports?  
Use `ss -lntp`.

9. Nginx 502怎么办?  
Check Nginx config, app health, port, Docker network and logs.

10. Database cannot connect怎么办?  
Check host, port, credentials, database name, grants and service health.

11. What is SQL JOIN?  
It combines related rows, for example orders with customers.

12. MySQL backup怎么做?  
Use `mysqldump --single-transaction`.

13. MySQL restore怎么做?  
Use `mysql database < backup.sql`, then verify counts and APIs.

14. Data migration怎么做?  
Mapping, cleaning, test import, reconciliation, formal import and business confirmation.

15. Duplicate data怎么办?  
Use unique business keys, query duplicates, clean source, then reimport.

16. CSV乱码怎么办?  
Confirm encoding, save UTF-8, test import, validate sample rows.

17. Go-live前准备什么?  
Environment, backup, config, data import, tests, user confirmation and rollback plan.

18. Customer does not cooperate怎么办?  
Clarify risks, split confirmations, escalate politely with evidence.

19. Change request怎么办?  
Record scope, impact, priority, approval and schedule.

20. Bug怎么处理?  
Reproduce, check logs, locate root cause, fix, test and record.

21. Major go-live issue怎么办?  
Stabilize service, assess impact, rollback if necessary, communicate timeline and document root cause.

22. How to write a manual?  
Role-based steps, screenshots or API examples, common issues and contacts.

23. How to do training?  
Use real workflow demo, let users operate, collect questions.

24. How to do acceptance?  
Use checklist, verify function/data/report/interface and get confirmation.

25. Why accept travel?  
Implementation work often needs on-site communication, environment check and user training.

26. Why transfer to ERP implementation?  
It combines business process, communication, SQL, deployment and troubleshooting.

27. How does manufacturing experience help?  
It helps understand products, inventory, orders, warehouses and process control.

28. What is Redis?  
An in-memory middleware often used for cache/status/session. In this lab it is optional.

29. What is middleware?  
A service between application and infrastructure that provides common capability like cache or queue.

30. What is REST API?  
HTTP endpoints using methods like GET/POST/PUT to operate resources.

31. What is HTTP 500?  
Server-side error; check application logs and traceback.

32. 401和403区别?  
401 means not authenticated; 403 means authenticated but no permission.

33. How do you read logs?  
Use time, request_id, module, error message and traceback to trace one operation.
