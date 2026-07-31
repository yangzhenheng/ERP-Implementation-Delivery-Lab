# CASE03 FastAPI 未启动

安全边界：仅用于本地演示。

## 现象

`curl http://127.0.0.1:8000/health` 无法连接。

## 日志

`logs/uvicorn.log` 可能出现依赖缺失、端口占用或数据库初始化失败。

## 检查命令

```bash
ps aux | grep uvicorn
tail -n 100 logs/uvicorn.log
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 根因

服务未启动、依赖缺失、端口被占用或启动初始化失败。

## 解决

安装依赖，释放端口，重新启动：

```bash
bash deploy/linux/restart.sh
curl http://127.0.0.1:8000/health
```
