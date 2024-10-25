# 使用Python基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . .

# 设置工作目录权限
RUN chmod -R 777 /app

# 安装依赖库
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用程序运行的端口
EXPOSE 3000

# 设置容器启动时运行的命令
CMD ["python", "main.py"]
