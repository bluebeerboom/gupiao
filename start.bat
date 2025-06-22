@echo off
echo ========================================
echo           股票分析系统启动脚本
echo ========================================
echo.
echo 本系统包含以下功能：
echo 1. 股票列表 - 查看所有股票信息
echo 2. 市场统计 - 市场涨跌分布分析
echo 3. 高涨幅股票 - 涨幅超过7%且创新高的股票
echo 4. 股票检查 - 检查股票是否为今日最高价
echo.
echo 正在启动后端服务...
echo.

cd backend
start "后端服务" python main.py

echo 等待后端服务启动...
timeout /t 3 /nobreak > nul

echo.
echo 正在启动前端服务...
echo.

cd ..\frontend
start "前端服务" npm run dev

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:8000
echo.
echo 按任意键退出...
pause > nul 