import heapq
from typing import List, Dict, Any, Tuple

class TopKHeap:
    """
    Efficient Top-K Product Extractor using a Min-Heap.
    
    Time Complexity:
      - Heap construction & maintenance: O(N log K) where N is total items and K is target limit.
      - Contrast with Full Sort O(N log N). When N=1,000,000 and K=10, O(N log K) requires 3.3M operations vs 20M operations.
      
    Space Complexity:
      - O(K) memory to store the heap of top K elements.
    """
    
    @staticmethod
    def get_top_k_products(items: List[Dict[str, Any]], k: int = 10, metric_key: str = "sales_count") -> List[Dict[str, Any]]:
        if k <= 0 or not items:
            return []
        
        # Min-heap stores tuples: (metric_value, item_dict)
        # Using item index or ID as tie-breaker to prevent dictionary comparisons
        min_heap: List[Tuple[float, int, Dict[str, Any]]] = []
        
        for idx, item in enumerate(items):
            val = float(item.get(metric_key, 0))
            if len(min_heap) < k:
                heapq.heappush(min_heap, (val, idx, item))
            else:
                if val > min_heap[0][0]:
                    heapq.heappushpop(min_heap, (val, idx, item))
        
        # Extract and sort top K in descending order
        result = [entry[2] for entry in min_heap]
        result.sort(key=lambda x: float(x.get(metric_key, 0)), reverse=True)
        return result
