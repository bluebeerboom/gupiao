#!/bin/bash

echo "========================================"
echo "           股票分析系统启动脚本"
echo "========================================"
echo ""
echo "本系统包含以下功能："
echo "1. 股票列表 - 查看所有股票信息"
echo "2. 市场统计 - 市场涨跌分布分析"
echo "3. 高涨幅股票 - 涨幅超过7%且创新高的股票"
echo "4. 股票检查 - 检查股票是否为今日最高价"
echo ""
echo "正在启动后端服务..."
echo ""

# 启动后端服务
cd backend
python main.py &
BACKEND_PID=$!

echo "等待后端服务启动..."
sleep 3

echo ""
echo "正在启动前端服务..."
echo ""

# 启动前端服务
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "服务启动完成！"
echo "========================================"
echo ""
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务..."

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait 