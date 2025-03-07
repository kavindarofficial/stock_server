import finnhub

FINNHUB_API_KEY = "cv48q2pr01qn2ga8psrgcv48q2pr01qn2ga8pss0"
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

def get_stock_price(symbol):
    try:
        response = finnhub_client.quote(symbol)
        print(response.get("c",None))
        return response.get("c", None)  # Return current price
    except Exception as e:
        return None
