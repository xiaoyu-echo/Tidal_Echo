# 使用轻量级的 Python 3.11 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制后端依赖文件
COPY backend/requirements.txt ./backend/

# 安装依赖（换国内源，加速下载）
RUN pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制整个后端代码
COPY backend/ ./backend/

# 设置启动命令（直接进入backend文件夹启动）
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
