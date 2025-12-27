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
            
        if len(pq) == 1:
            node = heapq.heappop(pq)
            self.codes[node.char] = "0"
            return node

        while len(pq) > 1:
            left = heapq.heappop(pq)
            right = heapq.heappop(pq)
            parent = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(pq, parent)
            
        root = heapq.heappop(pq)
        self.codes = {}
        self.generate_codes(root, "")
        return root

    def generate_codes(self, node, current_code):
        if node is None:
            return
        if node.char is not None:
            self.codes[node.char] = current_code
        self.generate_codes(node.left, current_code + "0")
        self.generate_codes(node.right, current_code + "1")

    def get_encoded_size(self, text):
        self.build_tree(text)
        size = 0
        for char in text:
            size += len(self.codes.get(char, ""))
        return size
