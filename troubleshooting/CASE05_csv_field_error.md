# CASE05 CSV 字段错误

安全边界：仅用于本地模拟 CSV 数据。

## 现象

执行 `python scripts/import_data.py` 后提示部分行导入失败。

## 日志

`logs/import.log` 记录文件名、行号和错误原因。

## 检查命令

```bash
python scripts/import_data.py --folder data/import
tail -n 100 logs/import.log
```

## 根因

必填字段缺失、编码重复、数字格式错误、文件编码错误，或订单引用的客户/产品不存在。

## 解决

修复 CSV 源文件，保存为 UTF-8，重新导入并核对数量：

```sql
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sales_orders;
```
