#!/usr/bin/env python3
"""
Quick test of CRO alert without monitoring loop
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simple_cro_alert import SimpleCROAlert

def quick_test():
    """Just test the price check once."""
    print("🧪 Testing Simple CRO Alert...")
    
    cro_alert = SimpleCROAlert()
    print(f"Target price: ${cro_alert.target_price}")
    
    # Check current price
    result = cro_alert.check_cro_price()
    
    if result:
        print("✅ Alert would be sent!")
    else:
        print("⏳ Target not reached yet, monitoring would continue...")
    
    print("✅ Test complete!")

if __name__ == "__main__":
    quick_test()