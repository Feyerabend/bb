from k_simple_interpreter import evaluate_expression, register_standard_operations, global_variables
import random

# Initialize the interpreter
register_standard_operations()

# Financial data setup: Simulated stock prices for 3 stocks over 5 days
stock_prices = [
    [100.0, 102.0, 101.5, 103.0, 104.5],  # Stock A
    [50.0, 51.0, 49.5, 52.0, 53.0],      # Stock B
    [75.0, 76.5, 74.0, 77.0, 78.5]       # Stock C
]

# Portfolio weights (summing to 1)
weights = [0.4, 0.3, 0.3]

# Store data in global variables
global_variables['prices'] = stock_prices
global_variables['weights'] = weights

def calculate_daily_returns():
    transposed_prices = global_variables['transposed_prices']
    daily_returns = []
    
    for i in range(1, len(transposed_prices)):
        try:
            print(f"Evaluating day_i: ['transposed_prices', '@', {i}]")
            day_i = evaluate_expression(["transposed_prices", "@", i])
            print(f"Result day_i: {day_i}")
            print(f"Evaluating day_prev: ['transposed_prices', '@', {i-1}]")
            day_prev = evaluate_expression(["transposed_prices", "@", i-1])
            print(f"Result day_prev: {day_prev}")
            print(f"Evaluating diff: [{day_i}, '-', {day_prev}]")
            diff = evaluate_expression([day_i, "-", day_prev])
            print(f"Result diff: {diff}")
            print(f"Evaluating returns: [{diff}, '%', {day_prev}]")
            returns = evaluate_expression([diff, "%", day_prev])
            print(f"Result returns: {returns}")
            daily_returns.append(returns)
        except Exception as e:
            print(f"Error in calculate_daily_returns for day {i}: {e}")
            raise
    
    return daily_returns

def portfolio_metrics():
    daily_returns = calculate_daily_returns()
    global_variables['returns'] = daily_returns
    
    portfolio_returns = []
    for i in range(len(daily_returns)):
        try:
            print(f"Evaluating returns_at_i: ['returns', '@', {i}]")
            returns_at_i = evaluate_expression(["returns", "@", i])
            print(f"Result returns_at_i: {returns_at_i}")
            print(f"Evaluating weighted_returns: ['weights', '*', {returns_at_i}]")
            weighted_returns = evaluate_expression(["weights", "*", returns_at_i])
            print(f"Result weighted_returns: {weighted_returns}")
            print(f"Evaluating sum: ['+', {weighted_returns}]")
            portfolio_return = evaluate_expression(["+", weighted_returns])
            print(f"Result portfolio_return: {portfolio_return}")
            portfolio_returns.append(portfolio_return)
        except Exception as e:
            print(f"Error in portfolio_metrics for return {i}: {e}")
            raise
    
    print(f"Evaluating avg_return: ['%', {portfolio_returns}]")
    avg_return = evaluate_expression(["%", portfolio_returns])
    print(f"Result avg_return: {avg_return}")
    
    print(f"Evaluating mean_subtracted: [{portfolio_returns}, '-', {avg_return}]")
    mean_subtracted = evaluate_expression([portfolio_returns, "-", avg_return])
    print(f"Result mean_subtracted: {mean_subtracted}")
    print(f"Evaluating squared_diff: [{mean_subtracted}, '*', {mean_subtracted}]")
    squared_diff = evaluate_expression([mean_subtracted, "*", mean_subtracted])
    print(f"Result squared_diff: {squared_diff}")
    print(f"Evaluating variance: ['%', {squared_diff}]")
    variance = evaluate_expression(["%", squared_diff])
    print(f"Result variance: {variance}")
    volatility = variance ** 0.5  # Python sqrt
    
    sharpe_ratio = avg_return / volatility if volatility != 0 else 0
    
    return {
        'daily_portfolio_returns': portfolio_returns,
        'average_return': avg_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio
    }

def simulate_portfolio_optimization():
    best_sharpe = -float('inf')
    best_weights = None
    best_metrics = None
    
    for _ in range(10):
        w = [random.random() for _ in range(3)]
        w = [x / sum(w) for x in w]
        global_variables['weights'] = w
        
        try:
            metrics = portfolio_metrics()
            if metrics['sharpe_ratio'] > best_sharpe:
                best_sharpe = metrics['sharpe_ratio']
                best_weights = w
                best_metrics = metrics
        except Exception as e:
            print(f"Error in optimization iteration: {e}")
            continue
    
    return best_weights, best_metrics

def main():
    try:
        print("Evaluating transposed_prices: ['.', 'prices']")
        global_variables['transposed_prices'] = evaluate_expression([".", "prices"])
        print(f"Result transposed_prices: {global_variables['transposed_prices']}")
        
        metrics = portfolio_metrics()
        
        print("\nPortfolio Analysis Results:")
        print(f"Daily Portfolio Returns: {[round(r, 6) for r in metrics['daily_portfolio_returns']]}")
        print(f"Average Daily Return: {metrics['average_return']:.6f}")
        print(f"Volatility: {metrics['volatility']:.6f}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.6f}")
        
        best_weights, best_metrics = simulate_portfolio_optimization()
        
        if best_metrics:
            print("\nOptimized Portfolio:")
            print(f"Best Weights: {[round(w, 3) for w in best_weights]}")
            print(f"Optimized Average Return: {best_metrics['average_return']:.6f}")
            print(f"Optimized Volatility: {best_metrics['volatility']:.6f}")
            print(f"Optimized Sharpe Ratio: {best_metrics['sharpe_ratio']:.6f}")
        else:
            print("\nOptimization failed to find valid weights.")
    
    except Exception as e:
        print(f"Error during execution: {e}")
        raise

if __name__ == "__main__":
    main()