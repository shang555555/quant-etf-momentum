## 🚀 Key Results

- 📈 年化收益：12.57%（全样本）
- 🔁 Walk-forward（滚动测试）：平均年化 ~3%，胜率 70%
- ⚠️ 最大回撤：-25.35%

👉 结论：策略在长期趋势市场有效，但在震荡市表现较弱
# ETF 动量轮动策略研究（Momentum Rotation Strategy on ETFs）

📈 ETF 动量轮动策略研究（Momentum Rotation Strategy on ETFs）
📌 项目简介
本项目基于中国市场多只ETF（如沪深300、中证500、创业板等），构建了一个动量轮动策略（Momentum 
Rotation Strategy），并实现完整的量化研究流程：
    Signal → Portfolio → Backtest → Performance
策略核心是在风险可控的前提下，动态选择表现最强的资产进行配置，以获取超额收益。
  
🧠 策略逻辑
1️⃣ 动量选股（Momentum）
    • 计算各ETF过去 N 日收益率（lookback window）
    • 选择动量最高的ETF作为持仓

2️⃣ 趋势过滤（Trend Filter）
基于沪深300指数：
    • 若价格跌破 MA200 → 切换至防御资产（如债券ETF）
    • 若均线斜率为负 → 降低风险暴露
👉 目的：控制回撤，避免趋势反转带来的损失

3️⃣ 调仓机制
    • 调仓频率：每周
    • 持仓：单资产（Top 1）

📊 回测结果
📈 策略净值 vs 基准（沪深300）

📉 参数稳定性分析

⚖️ 策略对比：动量 vs 均值回归

📊 绩效指标（示例）
指标	数值
年化收益	XX%
Sharpe	XX
最大回撤	XX%
Calmar	XX

### 📊 Rolling Backtest（Walk-Forward）

采用滚动向前测试（Walk-forward）验证策略稳定性：

- 训练期：5年
- 测试期：1年
- 滚动窗口：逐年推进

#### 结果总结：

- 平均年化收益：约 3%
- 胜率：70%
- 平均 Calmar：1.51

👉 说明策略在不同时间段具有一定稳定性，但在部分震荡市场中表现较弱。


🔍 策略验证与研究
✅ 为什么选择动量策略？
通过统计检验：
    • ADF检验：序列非平稳
    • Hurst指数：H > 0.5（趋势性）
👉 结论：单资产ETF更适合趋势策略，而非均值回归

❌ 为什么放弃均值回归？
    • 构建布林带/均值回归策略
    • 回测表现弱于动量策略
👉 因此最终选择动量作为主策略

📈 稳定性分析
    • 测试不同 lookback（5 / 10 / 20 / 60）
    • 策略收益对参数不敏感
👉 说明策略具有一定鲁棒性

🏗️ 项目结构
project/
│
├── data/                  # ETF数据
├── output/                # 回测结果图
├── strategies/
│   └── momentum/
│       ├── signal.py      # 指标计算
│       ├── portfolio.py   # 持仓生成
│       ├── backtest.py    # 回测逻辑
│       └── performance.py # 绩效指标
│
├── main.py                # 主程序入口
└── utils.py               # 公共函数

⚙️ 运行方式
python main.py
输出：
    • 净值曲线（output/）
    • 绩效指标（控制台）

🛠️ 技术栈
    • Python
    • Pandas / NumPy
    • Matplotlib

🎯 项目亮点
    • ✔ 完整量化研究流程（非简单策略实现）
    • ✔ 引入趋势过滤（MA200 + slope）控制风险
    • ✔ 对比验证（动量 vs 均值回归）
    • ✔ 参数稳定性分析（避免过拟合）
    • ✔ 模块化结构（可扩展多因子策略）

📌 后续优化方向
    • 多因子模型（动量 + 波动率）
    • 协整/配对交易（统计套利）
    • 滚动回测（Walk-forward）
    • 交易成本与滑点建模


本项目用于展示动量轮动策略的量化研究成果，图表精简为三张核心结果图，便于简历与作品集展示。

## 核心图表

- Equity Curve（主结果）：`output/equity_curve.png`，策略净值 vs CSI300，起点对齐为 1，统一时间索引并前向填充缺失值。
- Rolling Test（稳健性）：`output/rolling_test.png`，Walk-forward out-of-sample 年化收益柱状图。
- Parameter Stability（鲁棒性）：`output/parameter_stability.png`，动量窗口参数的稳定性表现。
