# 情侣记账与可视化分析 Web 应用

这是一个基于 Python/Flask 的轻量级 Web 应用，用于情侣共同管理收支、查看分担情况以及进行数据可视化分析。

## 功能概览

- ✍️ 快速录入每笔收入或支出，支持选择参与者、分类、日期和备注。
- 📊 自动汇总总收入、总支出与结余，并按参与者展示收入/支出/净贡献。
- 📈 使用 Chart.js 绘制月度趋势折线图、支出分类环形图以及情侣分担柱状图。
- 🗂 提供明细表，可按需删除记录。
- 💾 数据存储使用 SQLite 数据库，开箱即用。

## 环境准备

1. 确保已安装 Python 3.10+。
2. 克隆或下载项目代码。
3. 创建虚拟环境并安装依赖：

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

## 运行应用

```bash
flask --app app run
```

默认会在 `http://127.0.0.1:5000/` 启动应用。首次运行时会自动创建 `couple_budget.db` 数据库文件。

> 📌 **提示：** 出于安全考虑，请在生产环境中通过环境变量或配置文件修改 `SECRET_KEY`。

## 自定义

- **参与者名称**：在 `app.py` 中修改 `PARTNER_CHOICES` 即可替换显示名称。
- **分类建议**：编辑 `CATEGORY_SUGGESTIONS`，添加常用的支出或收入分类。
- **数据库位置**：设置环境变量 `SQLALCHEMY_DATABASE_URI`（例如 `sqlite:///data.db`）以改变默认位置。

## 数据备份

应用使用 SQLite 存储数据，备份时只需复制 `couple_budget.db` 文件即可；恢复时同样放回项目目录。

## 许可证

本项目以 MIT License 发布，欢迎自由使用与扩展。
