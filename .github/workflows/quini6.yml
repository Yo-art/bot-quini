name: Control Quini 6

on:
  schedule:
    # Lunes y jueves a las 12:00 UTC = 09:00 hora Argentina (UTC-3)
    - cron: "0 12 * * 1,4"
  workflow_dispatch: {}  # permite ejecutarlo manualmente para probar

jobs:
  controlar-quini6:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Instalar dependencias
        run: pip install requests

      - name: Ejecutar bot
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python quini6_bot.py
