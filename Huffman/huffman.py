import heapq

class HuffmanNode:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
        
    def __lt__(self, other):
        return self.freq < other.freq

class Huffman:
    def __init__(self):
        self.codes = {}

    def build_tree(self, text):
        if not text: return None
        
        freqs = {}
        for char in text:
            freqs[char] = freqs.get(char, 0) + 1
            
        pq = []
        for char, freq in freqs.items():
            heapq.heappush(pq, HuffmanNode(char, freq))
            
        while len(pq) > 1:
            left = heapq.heappop(pq)
            right = heapq.heappop(pq)
            parent = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(pq, parent)
            
        root = heapq.heappop(pq)
        self.generate_codes(root, "")
        return root

    def generate_codes(self, node, code):
        if not node: return
        if not node.left and not node.right:
            self.codes[node.char] = code
            return
        self.generate_codes(node.left, code + "0")
        self.generate_codes(node.right, code + "1")

    def encode(self, text):
        self.codes = {}
        self.build_tree(text)
        return "".join([self.codes[c] for c in text])
    
    def get_stats(self, text):
        if not text: return {"original_bits": 0, "compressed_bits": 0, "ratio": 0}
        encoded = self.encode(text)
        original_bits = len(text) * 8
        compressed_bits = len(encoded)
        ratio = ((1 - compressed_bits / original_bits) * 100) if original_bits > 0 else 0
        return {"original_bits": original_bits, "compressed_bits": compressed_bits, "ratio": round(ratio, 1)}
