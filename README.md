# 📊 Sales Analysis and Forecasting Dashboard with Streamlit

This interactive dashboard is built using **Streamlit** and **NeuralProphet**, designed to analyze and visualize sales data from an SQL Server database. With flexible date inputs and detailed breakdowns by customers, stock codes, and lot numbers, this tool helps businesses make data-driven decisions with ease.

## 🚀 Features

- 📅 Flexible date input: Supports Day-Month-Year, Month-Year, and Year-only formats.
- 🧮 Smart date parsing using Python's `datetime` and `calendar`.
- 📦 Data fetched dynamically via parameterized SQL queries.
- 🔍 Top 10 analysis:
  - Customers with the highest sales
  - Most sold stock codes
  - Most sold lot numbers
- 📉 Clean and readable horizontal bar charts with value labels.
- 🔐 Secure connection to Microsoft SQL Server using `pyodbc`.

