class Stock:
    def __init__(self, symbol, price):
        self.symbol = symbol
        self._price = price
        self._observers = []

    def add_observer(self, observer, priority=0):
        self._observers.append((observer, priority))
        self._observers.sort(key=lambda x: x[1], reverse=True)  # sort by priority (higher first)

    def remove_observer(self, observer):
        self._observers = [(obs, pri) for obs, pri in self._observers if obs != observer]

    def set_price(self, price):
        old_price = self._price
        self._price = price
        if old_price != price:
            self._notify_observers()

    def get_price(self):
        return self._price

    def _notify_observers(self):
        for observer, _ in self._observers:
            observer.update(self)


class Observer:
    def update(self, stock):
        pass


class Trader(Observer):
    def __init__(self, name, threshold):
        self.name = name
        self.threshold = threshold

    def update(self, stock):
        price_change = stock.get_price() * 0.05  # Assume 5% change for demo
        if price_change / stock.get_price() * 100 >= self.threshold:
            print(f"{self.name} (Trader): {stock.symbol} price changed significantly to ${stock.get_price():.2f}! Executing trade.")
        else:
            print(f"{self.name} (Trader): {stock.symbol} price at ${stock.get_price():.2f}, no action needed.")


class Analyst(Observer):
    def __init__(self, name):
        self.name = name
        self.reports = []

    def update(self, stock):
        report = f"Analysis for {stock.symbol}: Current price ${stock.get_price():.2f}"
        self.reports.append(report)
        print(f"{self.name} (Analyst): Generated report - {report}")


class PortfolioManager:
    def __init__(self):
        self.stocks = {}

    def add_stock(self, stock):
        self.stocks[stock.symbol] = stock

    def update_stock_price(self, symbol, price):
        if symbol in self.stocks:
            self.stocks[symbol].set_price(price)
        else:
            print(f"Stock {symbol} not found in portfolio.")


# example
def main():
    portfolio = PortfolioManager()

    apple = Stock("AAPL", 150.00)
    google = Stock("GOOGL", 2800.00)
    portfolio.add_stock(apple)
    portfolio.add_stock(google)

    trader1 = Trader("Alice", threshold=3.0)  # Trades if price changes > 3%
    trader2 = Trader("Bob", threshold=10.0)   # Trades if price changes > 10%
    analyst = Analyst("Charlie")

    # Attach observers with priorities (higher number = notified first)
    apple.add_observer(analyst, priority=2)
    apple.add_observer(trader1, priority=1)
    apple.add_observer(trader2, priority=0)
    google.add_observer(analyst, priority=1)

    # Simulate price changes
    print("=== Price Update 1 ===")
    portfolio.update_stock_price("AAPL", 160.00)  # 6.67% increase
    print("\n=== Price Update 2 ===")
    portfolio.update_stock_price("GOOGL", 2900.00)  # 3.57% increase
    print("\n=== Price Update 3 ===")
    portfolio.update_stock_price("AAPL", 162.00)  # 1.25% increase

    # Show analyst's reports
    print(f"\nAnalyst {analyst.name}'s reports: {analyst.reports}")


if __name__ == "__main__":
    main()

