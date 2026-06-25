name: Skin Price Report

on:
  workflow_dispatch:

jobs:
  send-price-report:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Run price checker
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
        run: python price_checker.py

      - name: Save prices
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add last_prices.json
          git diff --staged --quiet || git commit -m "Update prices"
          git push
