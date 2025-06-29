import random
import re
from collections import defaultdict, Counter
import numpy as np

class TextMarkovChain:
    def __init__(self, order=1):
        """
        Initialize Markov chain for text generation
        order: length of the context (n-gram size - 1)
        """
        self.order = order
        self.transitions = defaultdict(Counter)
        self.starters = []
    
    def train(self, text):
        """Train the Markov chain on input text"""
        # Clean and tokenize text
        words = self._tokenize(text)
        
        if len(words) <= self.order:
            raise ValueError(f"Text too short for order {self.order}")
        
        # Store sentence starters
        self.starters = [tuple(words[i:i+self.order]) 
                        for i in range(len(words)) 
                        if words[i][0].isupper()]
        
        # Build transition table
        for i in range(len(words) - self.order):
            context = tuple(words[i:i + self.order])
            next_word = words[i + self.order]
            self.transitions[context][next_word] += 1
    
    def _tokenize(self, text):
        """Simple tokenization"""
        # Split on whitespace and punctuation, keep punctuation
        tokens = re.findall(r'\w+|[.!?;,]', text)
        return [token for token in tokens if token.strip()]
    
    def generate(self, max_length=50, seed=None):
        """Generate text using the trained Markov chain"""
        if not self.transitions:
            return "Model not trained yet!"
        
        # Choose starting context
        if seed:
            current = tuple(seed.split()[-self.order:])
            if current not in self.transitions:
                current = random.choice(list(self.transitions.keys()))
        elif self.starters:
            current = random.choice(self.starters)
        else:
            current = random.choice(list(self.transitions.keys()))
        
        result = list(current)
        
        for _ in range(max_length - self.order):
            if current not in self.transitions:
                break
            
            # Choose next word based on probabilities
            candidates = self.transitions[current]
            total = sum(candidates.values())
            
            if total == 0:
                break
            
            # Weighted random selection
            rand_val = random.randint(1, total)
            cumulative = 0
            next_word = None
            
            for word, count in candidates.items():
                cumulative += count
                if cumulative >= rand_val:
                    next_word = word
                    break
            
            if next_word is None:
                break
            
            result.append(next_word)
            
            # Update context for next iteration
            current = tuple(result[-self.order:])
            
            # Stop at sentence endings
            if next_word in '.!?':
                break
        
        return ' '.join(result)
    
    def get_transition_probabilities(self, context):
        """Get transition probabilities for a given context"""
        if isinstance(context, str):
            context = tuple(context.split())
        
        if context not in self.transitions:
            return {}
        
        candidates = self.transitions[context]
        total = sum(candidates.values())
        
        return {word: count/total for word, count in candidates.items()}
    
    def analyze_chain(self):
        """Analyze the Markov chain properties"""
        print(f"Markov Chain Analysis (Order {self.order})")
        print("=" * 40)
        print(f"Total contexts: {len(self.transitions)}")
        print(f"Total transitions: {sum(len(v) for v in self.transitions.values())}")
        
        # Most common contexts
        context_counts = {k: sum(v.values()) for k, v in self.transitions.items()}
        top_contexts = sorted(context_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print("\nMost common contexts:")
        for context, count in top_contexts:
            print(f"  '{' '.join(context)}': {count} occurrences")
        
        # Show transition probabilities for top context
        if top_contexts:
            top_context = top_contexts[0][0]
            probs = self.get_transition_probabilities(top_context)
            print(f"\nTransition probabilities from '{' '.join(top_context)}':")
            for word, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  → '{word}': {prob:.3f}")

# Example usage and demonstration
def demo_text_generation():
    # Sample training text
    training_text = """
    The quick brown fox jumps over the lazy dog. The dog was sleeping peacefully.
    A brown fox is very clever and quick. The lazy dog enjoys sleeping in the sun.
    Quick movements help the fox catch prey. The dog prefers to rest and relax.
    Brown animals are common in the forest. Lazy afternoons are perfect for napping.
    The fox runs through the forest quickly. The dog sleeps under the warm sun.
    """
    
    print("Text Generation Markov Chain Demo")
    print("=" * 40)
    
    # Train different order models
    for order in [1, 2]:
        print(f"\n--- Order {order} Model ---")
        markov = TextMarkovChain(order=order)
        markov.train(training_text)
        
        # Analyze the model
        markov.analyze_chain()
        
        # Generate text
        print(f"\nGenerated text (order {order}):")
        for i in range(3):
            generated = markov.generate(max_length=15)
            print(f"  {i+1}: {generated}")

# Advanced example: Page Rank simulation
class PageRankMarkov:
    def __init__(self, damping_factor=0.85):
        self.damping_factor = damping_factor
        self.graph = defaultdict(list)
        self.nodes = set()
    
    def add_link(self, from_page, to_page):
        """Add a link from one page to another"""
        self.graph[from_page].append(to_page)
        self.nodes.add(from_page)
        self.nodes.add(to_page)
    
    def build_transition_matrix(self):
        """Build the transition matrix for the web graph"""
        n = len(self.nodes)
        node_to_idx = {node: i for i, node in enumerate(sorted(self.nodes))}
        idx_to_node = {i: node for node, i in node_to_idx.items()}
        
        # Initialize matrix
        matrix = np.zeros((n, n))
        
        # Fill transition probabilities
        for from_node in self.nodes:
            from_idx = node_to_idx[from_node]
            outlinks = self.graph[from_node]
            
            if outlinks:
                # Distribute probability among outlinks
                prob = 1.0 / len(outlinks)
                for to_node in outlinks:
                    to_idx = node_to_idx[to_node]
                    matrix[from_idx][to_idx] = prob
            else:
                # Dead end: distribute equally to all pages
                matrix[from_idx] = 1.0 / n
        
        # Apply damping factor
        teleport_matrix = np.ones((n, n)) / n
        final_matrix = (self.damping_factor * matrix + 
                       (1 - self.damping_factor) * teleport_matrix)
        
        return final_matrix, node_to_idx, idx_to_node
    
    def calculate_pagerank(self, iterations=100):
        """Calculate PageRank using power iteration"""
        matrix, node_to_idx, idx_to_node = self.build_transition_matrix()
        n = len(self.nodes)
        
        # Initial distribution
        rank = np.ones(n) / n
        
        # Power iteration
        for _ in range(iterations):
            rank = np.dot(rank, matrix)
        
        # Convert back to dictionary
        pagerank = {idx_to_node[i]: rank[i] for i in range(n)}
        return pagerank

def demo_pagerank():
    print("\n" + "=" * 50)
    print("PageRank Markov Chain Demo")
    print("=" * 50)
    
    # Create a simple web graph
    pr = PageRankMarkov()
    
    # Add links (simplified web structure)
    links = [
        ('A', 'B'), ('A', 'C'),
        ('B', 'A'), ('B', 'C'), ('B', 'D'),
        ('C', 'A'), ('C', 'D'),
        ('D', 'A'), ('D', 'B'), ('D', 'C')
    ]
    
    for from_page, to_page in links:
        pr.add_link(from_page, to_page)
    
    # Calculate PageRank
    pagerank = pr.calculate_pagerank()
    
    print("Web graph links:")
    for from_page, to_page in links:
        print(f"  {from_page} → {to_page}")
    
    print("\nPageRank scores:")
    for page, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
        print(f"  Page {page}: {score:.4f}")

if __name__ == "__main__":
    demo_text_generation()
    demo_pagerank()

